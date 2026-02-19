#!/usr/bin/env python3
"""Integration tests for Layer 2 indexer pipeline."""

import sys
from base64 import b64encode
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / ".."))

from tools.indexer_query import Claim, decode_note, extract_claim_hash_from_args


def test_decode_note_valid():
    """Test decoding a valid base64 note."""
    original_text = "This is a pharmaceutical claim"
    encoded = b64encode(original_text.encode("utf-8")).decode("utf-8")
    
    decoded = decode_note(encoded)
    
    assert decoded == original_text
    print(f"✓ decode_note: Valid case works")


def test_decode_note_empty():
    """Test handling empty note."""
    decoded = decode_note(None)
    assert decoded == ""
    
    decoded = decode_note("")
    assert decoded == ""
    
    print(f"✓ decode_note: Empty case handled")


def test_decode_note_invalid():
    """Test handling invalid base64."""
    # Invalid base64 should not crash
    decoded = decode_note("not-valid-base64!@#$%")
    # Should return something (empty or partially decoded)
    assert isinstance(decoded, str)
    
    print(f"✓ decode_note: Invalid base64 handled gracefully")


def test_claim_dataclass():
    """Test Claim data structure."""
    claim = Claim(
        claim_id=1,
        claim_hash="a" * 64,
        claim_text="Test claim",
        transaction_id="txid123",
        sender="SENDER123",
        block_round=1000,
        timestamp=1692345678,
        method="submit_claim_hash",
    )
    
    assert claim.claim_id == 1
    assert len(claim.claim_hash) == 64
    assert claim.claim_text == "Test claim"
    assert claim.method == "submit_claim_hash"
    
    print(f"✓ Claim dataclass: Structure valid")


def test_claim_hash_extraction_empty():
    """Test extracting claim hash from empty args."""
    result = extract_claim_hash_from_args(None)
    assert result == ""
    
    result = extract_claim_hash_from_args([])
    assert result == ""
    
    print(f"✓ extract_claim_hash: Empty args handled")


if __name__ == "__main__":
    print("Running Layer 2 indexer integration tests...\n")
    
    try:
        test_decode_note_valid()
        test_decode_note_empty()
        test_decode_note_invalid()
        test_claim_dataclass()
        test_claim_hash_extraction_empty()
        
        print("\n✅ All Layer 2 tests passed!")
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
