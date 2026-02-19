#!/usr/bin/env python3
"""
Layer 1: Claim Submission Client

CLI tool to submit pharmaceutical claims to the PharmaClear smart contract.

Usage:
    python submit_claim.py --claim "Full claim text here" --sender DEPLOYER --app 1234
    python submit_claim.py --claim "Claim text" --network localnet

Features:
- Computes SHA256 hash of claim text locally
- Submits hash to contract as ABI argument
- Attaches full claim text in transaction note for Indexer/Conduit capture
- Automatically funds account from dispenser if needed (localnet only)
- Returns new claim ID from contract

Configuration:
- Network: localnet, testnet, or mainnet (default: localnet)
- Account: DEPLOYER env var or specify sender account (with .json key file)
- App ID: Auto-detected from latest PharmaClear deployment or specify with --app
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from algokit_utils import AlgorandClient, AlgoAmount
from smart_contracts.artifacts.pharma_clear.pharma_clear_client import (
    PharmaClearClient,
    PharmaClearFactory,
)


def compute_claim_hash(claim_text: str) -> str:
    """
    Compute SHA256 hash of claim text.
    
    Args:
        claim_text: Full pharmaceutical claim details
    
    Returns:
        Hex-encoded SHA256 hash (64 characters)
    """
    hash_obj = hashlib.sha256(claim_text.encode("utf-8"))
    return hash_obj.hexdigest()


def submit_claim(
    claim_text: str,
    app_id: int | None = None,
    network: str = "localnet",
    sender_key: str | None = None,
    sender_env: str = "DEPLOYER",
    fund_if_needed: bool = True,
) -> dict:
    """
    Submit a claim to the PharmaClear contract.
    
    Args:
        claim_text: Full pharmaceutical claim content
        app_id: PharmaClear application ID (auto-detect if None)
        network: Target network - "localnet", "testnet", or "mainnet"
        sender_key: Path to account key file (JSON)
        sender_env: Environment variable name for sender account
        fund_if_needed: Fund account from dispenser if balance insufficient
    
    Returns:
        Dictionary with:
        - claim_id: New claim ID (UInt64) from contract
        - claim_hash: SHA256 hash submitted
        - transaction_id: Transaction ID
        - sender: Account address that submitted
    
    Raises:
        ValueError: If claim submission fails
        FileNotFoundError: If sender key file not found
    """
    # Initialize client
    client = AlgorandClient.from_environment()
    
    # Get sender account
    if sender_key:
        with open(sender_key) as f:
            sender = client.account.from_kmd(json.load(f))
    else:
        sender = client.account.from_environment(sender_env)
    
    print(f"📋 Submitting claim from {sender.address}")
    
    # Fund account if needed (localnet only)
    if fund_if_needed and network == "localnet":
        min_balance = AlgoAmount.from_algo(1)
        client.account.ensure_funded_from_environment(
            account_to_fund=sender.address,
            min_spending_balance=min_balance,
            dispenser_account_name="DISPENSER",
        )
        print(f"✓ Account funded")
    
    # Get or detect app ID
    if app_id is None:
        # Try to get app ID from latest ApplicationFactory deployment
        # For now, require explicit app ID or environment variable
        app_id = int(os.environ.get("PHARMA_CLEAR_APP_ID", "0"))
        if app_id == 0:
            raise ValueError(
                "App ID not specified. Set PHARMA_CLEAR_APP_ID env var or use --app"
            )
    
    print(f"📱 App ID: {app_id}")
    
    # Compute claim hash
    claim_hash = compute_claim_hash(claim_text)
    print(f"🔐 Claim hash (SHA256): {claim_hash}")
    
    # Get typed app client
    factory = client.client.get_typed_app_factory(
        PharmaClearFactory, default_sender=sender.address
    )
    app_client = PharmaClearClient(factory.get_app_client_by_id(app_id))
    
    # Submit claim via ABI method
    # Note: Transaction note will be set via the API call
    print(f"📤 Submitting {len(claim_text)} byte claim to contract...")
    
    try:
        # Call submit_claim_hash with claim hash
        # The full claim text should be attached in the transaction note
        response = app_client.send.submit_claim_hash(
            args={"claim_hash": claim_hash},
            note=claim_text.encode("utf-8"),  # Full claim in transaction note
        )
        
        claim_id = response.abi_return
        txn_id = response.transaction.id
        
        print(f"\n✅ Claim submitted successfully!")
        print(f"   Claim ID:        {claim_id}")
        print(f"   Transaction ID:  {txn_id}")
        print(f"   Sender:          {sender.address}")
        
        return {
            "claim_id": int(claim_id),
            "claim_hash": claim_hash,
            "transaction_id": txn_id,
            "sender": sender.address,
            "claim_text": claim_text,
        }
    
    except Exception as e:
        print(f"\n❌ Error submitting claim: {e}", file=sys.stderr)
        raise ValueError(f"Failed to submit claim: {e}") from e


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Submit pharmaceutical claims to PharmaClear contract",
        epilog="""
Examples:
  python submit_claim.py --claim "Claim for patient X..." --network localnet
  python submit_claim.py --claim-file claim.txt --app 1234 --sender-env DEPLOYER
  python submit_claim.py --claim "..." --sender-key account.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    claim_group = parser.add_mutually_exclusive_group(required=True)
    claim_group.add_argument(
        "--claim",
        type=str,
        help="Claim text to submit (full pharmaceutical claim details)",
    )
    claim_group.add_argument(
        "--claim-file",
        type=Path,
        help="Read claim text from file",
    )
    
    parser.add_argument(
        "--app",
        type=int,
        default=None,
        help="PharmaClear app ID (auto-detected if not specified)",
    )
    
    parser.add_argument(
        "--network",
        type=str,
        default="localnet",
        choices=["localnet", "testnet", "mainnet"],
        help="Target network (default: localnet)",
    )
    
    parser.add_argument(
        "--sender-env",
        type=str,
        default="DEPLOYER",
        help="Environment variable with sender account credentials (default: DEPLOYER)",
    )
    
    parser.add_argument(
        "--sender-key",
        type=Path,
        help="Path to sender account key file (.json from algokit)",
    )
    
    parser.add_argument(
        "--no-fund",
        action="store_true",
        help="Skip automatic funding from dispenser (localnet)",
    )
    
    args = parser.parse_args()
    
    # Get claim text from argument or file
    if args.claim:
        claim_text = args.claim
    elif args.claim_file:
        with open(args.claim_file) as f:
            claim_text = f.read()
    else:
        parser.print_help()
        sys.exit(1)
    
    if not claim_text.strip():
        print("Error: Claim text cannot be empty", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = submit_claim(
            claim_text=claim_text,
            app_id=args.app,
            network=args.network,
            sender_key=args.sender_key,
            sender_env=args.sender_env,
            fund_if_needed=not args.no_fund,
        )
        
        # Print result as JSON for scripting
        print("\n📊 Result (JSON):")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
