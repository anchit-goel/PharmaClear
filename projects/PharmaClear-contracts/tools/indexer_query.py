#!/usr/bin/env python3
"""
Layer 2: Indexer Pipeline

Query the Algorand Indexer for pharmaceutical claims and store them locally.

Usage:
    python indexer_query.py --app 1234 --output claims.json
    python indexer_query.py --app 1234 --no-save (print to stdout)
    python indexer_query.py --app 1234 --db claims.db (SQLite)
"""

import argparse
import json
import os
import sqlite3
import sys
from base64 import b64decode
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from algokit_utils import AlgorandClient


@dataclass
class Claim:
    """Represents a single claim extracted from indexer."""

    claim_id: int
    claim_hash: str
    claim_text: str
    transaction_id: str
    sender: str
    block_round: int
    timestamp: int
    method: str  # submit_claim_hash, submit_claim, etc.


class IndexerQueryError(Exception):
    """Raised when indexer query fails."""

    pass


def decode_note(note_b64: str | None) -> str:
    """
    Decode base64-encoded transaction note.
    
    Args:
        note_b64: Base64-encoded note string (from indexer)
    
    Returns:
        Decoded note text or empty string
    """
    if not note_b64:
        return ""
    try:
        return b64decode(note_b64).decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Warning: Could not decode note: {e}", file=sys.stderr)
        return ""


def extract_claim_hash_from_args(args: list[dict[str, Any]] | None) -> str:
    """
    Extract claim hash from ABI method arguments.
    
    ABI arguments are encoded. For submit_claim_hash, the first argument
    is the claim_hash (String type, ABI-encoded).
    
    Args:
        args: List of ABI-encoded arguments from indexer
    
    Returns:
        Claim hash (64-char hex string) or empty string
    """
    # This is a placeholder - actual ABI decoding would be needed
    # For now, return empty; full implementation requires ABI specification
    if not args or len(args) == 0:
        return ""
    
    # ABI String type encoding: first arg for submit_claim_hash
    # In a real implementation, use algokit_utils to decode ABI arguments
    # based on the contract's arc56.json spec
    #
    # Simplified: assume first 66+ byte arg is the claim hash
    # (ABI encoded string with length prefix)
    try:
        arg0 = args[0]
        if isinstance(arg0, dict) and "uint" in arg0:
            # Numeric argument
            return str(arg0["uint"])
        elif isinstance(arg0, dict) and "bytes" in arg0:
            # Bytes argument - try to decode
            try:
                bytes_b64 = arg0["bytes"]
                decoded = b64decode(bytes_b64).decode("utf-8", errors="replace")
                return decoded[:64]  # First 64 chars (SHA256 hash length)
            except Exception:
                return ""
    except Exception:
        pass
    
    return ""


def query_indexer_for_claims(
    app_id: int,
    indexer_client: Any,
    method: str = "submit_claim_hash",
    min_round: int | None = None,
    max_round: int | None = None,
) -> list[Claim]:
    """
    Query Algorand Indexer for application call transactions.
    
    Args:
        app_id: PharmaClear application ID
        indexer_client: AlgorandClient.indexer instance
        method: Contract method name to filter by (optional)
        min_round: Minimum round to query (optional)
        max_round: Maximum round to query (optional)
    
    Returns:
        List of extracted Claim objects
        
    Raises:
        IndexerQueryError: If query fails
    """
    claims: list[Claim] = []
    
    try:
        # Query for app-call transactions
        query = (
            indexer_client
            .search_transactions()
            .app_id(app_id)
            .txn_type("appl")  # Application call
        )
        
        if min_round is not None:
            query = query.min_round(min_round)
        if max_round is not None:
            query = query.max_round(max_round)
        
        print(f"🔍 Querying indexer for app {app_id} transactions...", file=sys.stderr)
        response = query.execute()
        
        transactions = response.get("transactions", [])
        print(f"📊 Found {len(transactions)} transactions", file=sys.stderr)
        
        for txn in transactions:
            # Extract relevant fields
            txn_id = txn.get("id", "")
            sender = txn.get("sender", "")
            block_round = txn.get("confirmed-round", 0)
            timestamp = txn.get("round-time", 0)
            note_b64 = txn.get("note")  # Base64-encoded note field
            
            # Extract app-call details
            app_call = txn.get("application-call-transaction", {})
            app_args = app_call.get("application-args", [])
            
            # Determine which method was called (first arg is method selector)
            method_name = "unknown"
            claim_hash = ""
            
            if app_args and len(app_args) > 0:
                # First arg is method selector (8 bytes, base64-encoded)
                # Common selectors:
                # submit_claim_hash: specific selector
                # For now, extract from subsequent args
                
                if len(app_args) > 1:
                    # Second arg might be claim_hash
                    claim_hash = extract_claim_hash_from_args(app_args[1:])
                
                # Determine method from method selector or heuristics
                # In production, decode from arc56.json
                method_name = method
            
            # Decode note to get full claim text
            claim_text = decode_note(note_b64)
            
            # Only include transactions that have claim data
            if claim_hash or claim_text:
                claim = Claim(
                    claim_id=len(claims) + 1,  # Sequential ID for this query
                    claim_hash=claim_hash,
                    claim_text=claim_text,
                    transaction_id=txn_id,
                    sender=sender,
                    block_round=block_round,
                    timestamp=timestamp,
                    method=method_name,
                )
                claims.append(claim)
                print(f"  ✓ Claim {claim.claim_id}: {txn_id[:16]}... | "
                      f"hash={claim_hash[:16]}... | "
                      f"text_len={len(claim_text)}", file=sys.stderr)
        
        print(f"\n✅ Extracted {len(claims)} claims from indexer", file=sys.stderr)
        return claims
    
    except Exception as e:
        raise IndexerQueryError(f"Failed to query indexer: {e}") from e


def save_to_json(claims: list[Claim], output_file: Path) -> None:
    """
    Save claims to JSON file.
    
    Args:
        claims: List of Claim objects
        output_file: Path to output JSON file
    """
    data = {
        "exported_at": datetime.now().isoformat(),
        "claim_count": len(claims),
        "claims": [asdict(c) for c in claims],
    }
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Saved {len(claims)} claims to {output_file}", file=sys.stderr)


def save_to_sqlite(claims: list[Claim], db_file: Path) -> None:
    """
    Save claims to SQLite database.
    
    Args:
        claims: List of Claim objects
        db_file: Path to SQLite database file
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS claims (
            claim_id INTEGER PRIMARY KEY,
            claim_hash TEXT,
            claim_text TEXT,
            transaction_id TEXT UNIQUE,
            sender TEXT,
            block_round INTEGER,
            timestamp INTEGER,
            method TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    # Insert claims (skip duplicates)
    for claim in claims:
        try:
            cursor.execute(
                """
                INSERT INTO claims 
                (claim_id, claim_hash, claim_text, transaction_id, sender,
                 block_round, timestamp, method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    claim.claim_id,
                    claim.claim_hash,
                    claim.claim_text,
                    claim.transaction_id,
                    claim.sender,
                    claim.block_round,
                    claim.timestamp,
                    claim.method,
                ),
            )
        except sqlite3.IntegrityError:
            # Transaction already exists, skip
            pass
    
    conn.commit()
    conn.close()
    
    print(f"💾 Saved {len(claims)} claims to SQLite: {db_file}", file=sys.stderr)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Query Indexer for PharmaClear claims",
        epilog="""
Examples:
  python indexer_query.py --app 1234
  python indexer_query.py --app 1234 --output claims.json
  python indexer_query.py --app 1234 --db claims.db
  python indexer_query.py --app 1234 --no-save (print to stdout)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--app",
        type=int,
        required=True,
        help="PharmaClear application ID",
    )
    
    parser.add_argument(
        "--network",
        type=str,
        default="localnet",
        choices=["localnet", "testnet", "mainnet"],
        help="Target network (default: localnet)",
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file (creates if doesn't exist)",
    )
    
    parser.add_argument(
        "--db",
        type=Path,
        help="Output SQLite database file",
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save to file, print to stdout instead",
    )
    
    parser.add_argument(
        "--min-round",
        type=int,
        help="Minimum round to query",
    )
    
    parser.add_argument(
        "--max-round",
        type=int,
        help="Maximum round to query",
    )
    
    parser.add_argument(
        "--method",
        type=str,
        default="submit_claim_hash",
        help="Contract method name to filter (default: submit_claim_hash)",
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize client
        client = AlgorandClient.from_environment()
        indexer_client = client.indexer
        
        # Query claims
        claims = query_indexer_for_claims(
            app_id=args.app,
            indexer_client=indexer_client,
            method=args.method,
            min_round=args.min_round,
            max_round=args.max_round,
        )
        
        # Output results
        if args.no_save:
            # Print to stdout
            output = {
                "exported_at": datetime.now().isoformat(),
                "claim_count": len(claims),
                "claims": [asdict(c) for c in claims],
            }
            print(json.dumps(output, indent=2))
        
        elif args.db:
            save_to_sqlite(claims, args.db)
        
        else:
            # Default to JSON
            output_file = args.output or Path("claims.json")
            save_to_json(claims, output_file)
        
        print(f"\n✅ Query completed successfully!")
        print(f"   {len(claims)} claims found and processed")
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
