from collections.abc import Iterator

import pytest
from algopy_testing import AlgopyTestContext, algopy_testing_context

from smart_contracts.pharma_clear.contract import PharmaClear
from algopy import String, UInt64


@pytest.fixture()
def context() -> Iterator[AlgopyTestContext]:
    # provides the algopy testing runtime used by the template
    with algopy_testing_context() as ctx:
        yield ctx


def test_submit_and_query(context: AlgopyTestContext) -> None:
    # Arrange: create some example hashes (strings)
    first_hash = String("hash_abc123")
    second_hash = String("hash_def456")

    contract = PharmaClear()

    # Act: submit claims
    result1 = contract.submit_claim(first_hash)
    result2 = contract.submit_claim(second_hash)
    result3 = contract.verify_claim(first_hash)

    # Assert: verify claim submission and verification work
    assert result1 == String("Claim submitted with hash: hash_abc123")
    assert result2 == String("Claim submitted with hash: hash_def456")
    assert result3 == String("Claim verified: hash_abc123")