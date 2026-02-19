#!/usr/bin/env python3
"""Integration tests for Layer 1 claim submission client."""

import hashlib
import os
import sys
from pathlib import Path

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent / ".."))

from tools.submit_claim import compute_claim_hash


def test_compute_claim_hash():
    """Test SHA256 hash computation."""
    claim_text = "This is a test pharmaceutical claim"
    expected_hash = hashlib.sha256(claim_text.encode("utf-8")).hexdigest()
    
    computed_hash = compute_claim_hash(claim_text)
    
    assert computed_hash == expected_hash
    assert len(computed_hash) == 64  # SHA256 produces 64 hex characters
    assert all(c in "0123456789abcdef" for c in computed_hash)
    print(f"✓ Hash computation verified: {computed_hash[:16]}...")


def test_claim_hash_deterministic():
    """Test that same claim always produces same hash."""
    claim = "Patient ID: 12345, Drug: Aspirin, Qty: 100"
    
    hash1 = compute_claim_hash(claim)
    hash2 = compute_claim_hash(claim)
    hash3 = compute_claim_hash(claim)
    
    assert hash1 == hash2 == hash3
    print(f"✓ Hash computation is deterministic")


def test_claim_hash_changes_with_content():
    """Test that different claims produce different hashes."""
    claim1 = "Claim number 1"
    claim2 = "Claim number 2"
    
    hash1 = compute_claim_hash(claim1)
    hash2 = compute_claim_hash(claim2)
    
    assert hash1 != hash2
    print(f"✓ Different claims produce different hashes")


if __name__ == "__main__":
    print("Running Layer 1 client integration tests...\n")
    
    try:
        test_compute_claim_hash()
        test_claim_hash_deterministic()
        test_claim_hash_changes_with_content()
        
        print("\n✅ All Layer 1 tests passed!")
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)
