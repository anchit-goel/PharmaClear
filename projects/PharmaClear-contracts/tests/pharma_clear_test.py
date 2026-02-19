from collections.abc import Iterator

import pytest
from algopy_testing import AlgopyTestContext, algopy_testing_context

from smart_contracts.pharma_clear.contract import PharmaClear
from algopy import String, UInt64


@pytest.fixture()
def context() -> Iterator[AlgopyTestContext]:
    """Provides the algopy testing runtime."""
    with algopy_testing_context() as ctx:
        yield ctx


def test_submit_claim_hash_returns_uint64(context: AlgopyTestContext) -> None:
    """Test that submit_claim_hash returns a UInt64 claim ID."""
    contract = PharmaClear()
    
    claim_hash = String("a" * 64)  # 64-char hex SHA256 hash
    claim_id = contract.submit_claim_hash(claim_hash)
    
    # Layer 0 basic: should return a UInt64
    assert isinstance(claim_id, UInt64)
    assert claim_id == UInt64(1)


def test_get_last_claim_hash_returns_string(context: AlgopyTestContext) -> None:
    """Test that get_last_claim_hash returns a String."""
    contract = PharmaClear()
    
    last_hash = contract.get_last_claim_hash()
    
    # Layer 0 basic: should return a String (empty for now)
    assert isinstance(last_hash, String)
    assert last_hash == String("")


def test_get_claim_count_returns_uint64(context: AlgopyTestContext) -> None:
    """Test that get_claim_count returns a UInt64."""
    contract = PharmaClear()
    
    count = contract.get_claim_count()
    
    # Layer 0 basic: should return a UInt64 (zero for now)
    assert isinstance(count, UInt64)
    assert count == UInt64(0)


def test_abi_method_signatures(context: AlgopyTestContext) -> None:
    """Test that all three Layer 0 methods exist and have correct signatures."""
    contract = PharmaClear()
    
    # Verify methods are callable and return expected types
    result1 = contract.submit_claim_hash(String("test_hash_" + "a" * 54))
    assert isinstance(result1, UInt64)
    
    result2 = contract.get_last_claim_hash()
    assert isinstance(result2, String)
    
    result3 = contract.get_claim_count()
    assert isinstance(result3, UInt64)