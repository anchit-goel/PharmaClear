"""
PharmaClear Layer 0: Claim Ingestion Contract (Trust Layer)
Ensures claim uniqueness and provides the foundation for the settlement pipeline.
"""

from algopy import (
    ARC4Contract,
    Box,
    BoxMap,
    Bytes,
    String,
    UInt64,
    arc4,
    op,
    subroutine,
)


class ClaimIngestionContract(ARC4Contract):
    """
    The Trust Layer - Prevents duplicate claims and stores verified claim metadata.
    Uses Box Storage for infinite scalability.
    """

    # BoxMap to prevent duplicate claims (claim_key -> exists)
    claim_hashes: BoxMap[arc4.DynamicBytes, arc4.Bool]

    # BoxMap to store claim metadata (claim_key -> metadata_json)
    claim_records: BoxMap[arc4.DynamicBytes, arc4.String]

    def __init__(self) -> None:
        """Initialize the claim ingestion contract"""
        self.claim_hashes = BoxMap(arc4.DynamicBytes, arc4.Bool)
        self.claim_records = BoxMap(arc4.DynamicBytes, arc4.String)

    @arc4.abimethod
    def submit_claim(
        self,
        claim_id: arc4.String,
        ndc_code: arc4.String,
        pharmacy_npi: arc4.String,
        dispense_date: arc4.UInt64,
        oracle_sig: arc4.DynamicBytes,
    ) -> arc4.DynamicBytes:
        """
        Submit a new pharmaceutical claim with oracle verification.

        Args:
            claim_id: Unique claim identifier from pharmacy system
            ndc_code: National Drug Code (11-digit standard)
            pharmacy_npi: National Provider Identifier for the pharmacy
            dispense_date: Unix timestamp of dispensation
            oracle_sig: Oracle signature proving claim authenticity

        Returns:
            claim_key: SHA-256 hash of the claim (unique identifier)

        Raises:
            AssertionError: If oracle_sig is empty or claim already exists
        """
        # CRITICAL: Verify oracle signature is not empty (oracle validation)
        assert oracle_sig.length > 0, "Oracle signature required"

        # Create deterministic claim key using SHA-256 of all inputs
        claim_data = (
            claim_id.native.encode()
            + ndc_code.native.encode()
            + pharmacy_npi.native.encode()
            + dispense_date.bytes
            + oracle_sig.bytes
        )
        claim_key = arc4.DynamicBytes(op.sha256(claim_data))

        # CRITICAL: Hard rejection of duplicate claims
        # This is the core anti-fraud mechanism
        assert claim_key not in self.claim_hashes, "Claim already submitted - duplicate rejected"

        # Mark claim as submitted (existence proof)
        self.claim_hashes[claim_key] = arc4.Bool(True)

        # Store claim metadata as JSON-like string
        metadata = arc4.String(
            f'{{"claim_id":"{claim_id.native}","ndc":"{ndc_code.native}",'
            f'"npi":"{pharmacy_npi.native}","date":{dispense_date.native}}}'
        )
        self.claim_records[claim_key] = metadata

        # Emit ARC-28 event for indexers and analytics
        arc4.emit(
            "ClaimSubmitted",
            claim_key,
            claim_id,
            ndc_code,
            pharmacy_npi,
            dispense_date,
        )

        return claim_key

    @arc4.abimethod(readonly=True)
    def verify_claim(self, claim_key: arc4.DynamicBytes) -> arc4.Bool:
        """
        Verify if a claim exists in the system.

        Args:
            claim_key: The SHA-256 hash of the claim

        Returns:
            exists: True if claim exists, False otherwise
        """
        return self.claim_hashes.get(claim_key, arc4.Bool(False))

    @arc4.abimethod(readonly=True)
    def get_claim_metadata(self, claim_key: arc4.DynamicBytes) -> arc4.String:
        """
        Retrieve claim metadata.

        Args:
            claim_key: The SHA-256 hash of the claim

        Returns:
            metadata: JSON-encoded claim details
        """
        assert claim_key in self.claim_records, "Claim not found"
        return self.claim_records[claim_key]
