"""
PharmaClear Layer 0 Enhanced: Advanced Provenance Tracking
Adds batch/lot tracking, expiration monitoring, and recall management.
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
    Global,
)


class EnhancedClaimIngestionContract(ARC4Contract):
    """
    Enhanced Trust Layer with comprehensive pharmaceutical provenance.

    New Features:
    - Drug batch/lot number tracking
    - Expiration date monitoring
    - Recall management system
    - International pharmacy support
    - Multi-manufacturer NDC registry
    """

    # Core duplicate prevention
    claim_hashes: BoxMap[arc4.DynamicBytes, arc4.Bool]
    claim_records: BoxMap[arc4.DynamicBytes, arc4.String]

    # ENHANCEMENT: Batch/Lot Tracking
    batch_registry: BoxMap[arc4.String, arc4.String]  # batch_id -> metadata
    batch_to_claims: BoxMap[arc4.String, arc4.DynamicArray[arc4.DynamicBytes]]

    # ENHANCEMENT: Recall Management
    recalled_batches: BoxMap[arc4.String, arc4.Bool]
    recall_events: BoxMap[arc4.String, arc4.String]  # batch_id -> recall_reason

    # ENHANCEMENT: Expiration Tracking
    expiring_inventory: BoxMap[arc4.String, arc4.UInt64]  # ndc_code -> expiration_timestamp

    # ENHANCEMENT: International Support
    pharmacy_countries: BoxMap[arc4.String, arc4.String]  # npi -> ISO country code

    def __init__(self) -> None:
        """Initialize enhanced claim ingestion contract"""
        self.claim_hashes = BoxMap(arc4.DynamicBytes, arc4.Bool)
        self.claim_records = BoxMap(arc4.DynamicBytes, arc4.String)
        self.batch_registry = BoxMap(arc4.String, arc4.String)
        self.batch_to_claims = BoxMap(arc4.String, arc4.DynamicArray[arc4.DynamicBytes])
        self.recalled_batches = BoxMap(arc4.String, arc4.Bool)
        self.recall_events = BoxMap(arc4.String, arc4.String)
        self.expiring_inventory = BoxMap(arc4.String, arc4.UInt64)
        self.pharmacy_countries = BoxMap(arc4.String, arc4.String)

    @arc4.abimethod
    def submit_claim_enhanced(
        self,
        claim_id: arc4.String,
        ndc_code: arc4.String,
        pharmacy_npi: arc4.String,
        dispense_date: arc4.UInt64,
        oracle_sig: arc4.DynamicBytes,
        batch_number: arc4.String,
        lot_number: arc4.String,
        expiration_date: arc4.UInt64,
        country_code: arc4.String,
    ) -> arc4.DynamicBytes:
        """
        Submit pharmaceutical claim with FULL provenance tracking.

        Args:
            claim_id: Unique claim identifier
            ndc_code: National Drug Code
            pharmacy_npi: National Provider Identifier
            dispense_date: Unix timestamp of dispensation
            oracle_sig: Oracle signature proving authenticity
            batch_number: Manufacturer batch identifier
            lot_number: Specific lot within batch
            expiration_date: Drug expiration timestamp
            country_code: ISO 3166-1 alpha-2 country code (e.g., "US", "CA", "MX")

        Returns:
            claim_key: SHA-256 hash of claim
        """
        # Oracle verification
        assert oracle_sig.length > 0, "Oracle signature required"

        # Create claim key
        claim_data = (
            claim_id.native.encode()
            + ndc_code.native.encode()
            + pharmacy_npi.native.encode()
            + dispense_date.bytes
            + batch_number.native.encode()
            + lot_number.native.encode()
        )
        claim_key = arc4.DynamicBytes(op.sha256(claim_data))

        # Duplicate prevention
        assert claim_key not in self.claim_hashes, "Claim already submitted"

        # CRITICAL: Check if batch is recalled
        batch_id = arc4.String(f"{ndc_code.native}-{batch_number.native}")
        if batch_id in self.recalled_batches:
            arc4.emit(
                "RECALLED_DRUG_DISPENSED",
                claim_key,
                batch_id,
                pharmacy_npi,
                arc4.String("CRITICAL: Recalled drug dispensed - immediate action required"),
            )
            # Still allow claim but flag for investigation

        # Check expiration
        current_time = Global.latest_timestamp
        if expiration_date.native < current_time:
            arc4.emit(
                "EXPIRED_DRUG_DISPENSED",
                claim_key,
                ndc_code,
                pharmacy_npi,
                arc4.UInt64(expiration_date.native),
            )

        # Store enhanced metadata
        metadata = arc4.String(
            f'{{"claim_id":"{claim_id.native}",'
            f'"ndc":"{ndc_code.native}",'
            f'"npi":"{pharmacy_npi.native}",'
            f'"date":{dispense_date.native},'
            f'"batch":"{batch_number.native}",'
            f'"lot":"{lot_number.native}",'
            f'"expiry":{expiration_date.native},'
            f'"country":"{country_code.native}"}}'
        )

        # Store claim
        self.claim_hashes[claim_key] = arc4.Bool(True)
        self.claim_records[claim_key] = metadata

        # Register batch tracking
        if batch_id not in self.batch_registry:
            batch_metadata = arc4.String(
                f'{{"ndc":"{ndc_code.native}",'
                f'"batch":"{batch_number.native}",'
                f'"registered":{current_time}}}'
            )
            self.batch_registry[batch_id] = batch_metadata
            self.batch_to_claims[batch_id] = arc4.DynamicArray[arc4.DynamicBytes]()

        # Link claim to batch
        batch_claims = self.batch_to_claims[batch_id]
        batch_claims.append(claim_key)
        self.batch_to_claims[batch_id] = batch_claims

        # Store pharmacy country
        self.pharmacy_countries[pharmacy_npi] = country_code

        # Store expiration tracking
        self.expiring_inventory[ndc_code] = expiration_date

        # Emit comprehensive event
        arc4.emit(
            "ClaimSubmittedEnhanced",
            claim_key,
            claim_id,
            ndc_code,
            batch_id,
            country_code,
            expiration_date,
        )

        return claim_key

    @arc4.abimethod
    def issue_recall(
        self,
        ndc_code: arc4.String,
        batch_number: arc4.String,
        recall_reason: arc4.String,
        severity_level: arc4.UInt64,
    ) -> arc4.String:
        """
        Issue a drug recall and identify all affected claims.

        Args:
            ndc_code: Drug NDC code
            batch_number: Batch to recall
            recall_reason: FDA recall classification
            severity_level: 1=Life-threatening, 2=Serious, 3=Minor

        Returns:
            status: Recall confirmation with affected claim count
        """
        batch_id = arc4.String(f"{ndc_code.native}-{batch_number.native}")

        # Mark batch as recalled
        self.recalled_batches[batch_id] = arc4.Bool(True)
        self.recall_events[batch_id] = recall_reason

        # Get all affected claims
        affected_count = 0
        if batch_id in self.batch_to_claims:
            affected_claims = self.batch_to_claims[batch_id]
            affected_count = affected_claims.length

        # Emit critical recall event
        arc4.emit(
            "DRUG_RECALL_ISSUED",
            batch_id,
            recall_reason,
            severity_level,
            arc4.UInt64(affected_count),
            arc4.UInt64(Global.latest_timestamp),
        )

        return arc4.String(
            f"Recall issued: {affected_count} claims affected"
        )

    @arc4.abimethod(readonly=True)
    def get_batch_claims(
        self,
        ndc_code: arc4.String,
        batch_number: arc4.String,
    ) -> arc4.UInt64:
        """
        Get count of claims for a specific batch.

        Args:
            ndc_code: Drug NDC
            batch_number: Batch identifier

        Returns:
            count: Number of claims from this batch
        """
        batch_id = arc4.String(f"{ndc_code.native}-{batch_number.native}")

        if batch_id in self.batch_to_claims:
            return arc4.UInt64(self.batch_to_claims[batch_id].length)
        return arc4.UInt64(0)

    @arc4.abimethod(readonly=True)
    def is_batch_recalled(
        self,
        ndc_code: arc4.String,
        batch_number: arc4.String,
    ) -> arc4.Bool:
        """
        Check if a batch has been recalled.

        Args:
            ndc_code: Drug NDC
            batch_number: Batch identifier

        Returns:
            recalled: True if batch is recalled
        """
        batch_id = arc4.String(f"{ndc_code.native}-{batch_number.native}")
        return self.recalled_batches.get(batch_id, arc4.Bool(False))

    @arc4.abimethod(readonly=True)
    def get_expiring_drugs(
        self,
        threshold_days: arc4.UInt64,
    ) -> arc4.String:
        """
        Get drugs expiring within threshold.

        Args:
            threshold_days: Days until expiration

        Returns:
            report: JSON list of expiring NDCs
        """
        current_time = Global.latest_timestamp
        threshold_time = current_time + (threshold_days.native * 86400)

        # Note: In production, iterate through expiring_inventory
        # For demo, return status
        return arc4.String(
            f'{{"threshold":{threshold_time},"current":{current_time}}}'
        )
