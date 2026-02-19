"""
PharmaClear Layer 1: Rebate Engine Contract (Calculation Engine)
Implements tiered rebate schedules and calculates manufacturer liabilities.
"""

from algopy import (
    ARC4Contract,
    BoxMap,
    Bytes,
    Txn,
    UInt64,
    arc4,
    op,
)


class RebateEngineContract(ARC4Contract):
    """
    The Calculation Engine - Manages rebate schedules and computes accruals.
    Supports volume-based tier pricing with anti-competitive flags.
    """

    # Manufacturer rebate schedules: manufacturer_addr -> [base_bps, threshold, bonus_bps]
    tier_schedules: BoxMap[arc4.Address, arc4.DynamicArray[arc4.UInt64]]

    # Per-claim accrued liabilities: claim_key -> rebate_amount
    accrued_liabilities: BoxMap[arc4.DynamicBytes, arc4.UInt64]

    # Total accrued per manufacturer: manufacturer_addr -> total_liability
    total_accrued: BoxMap[arc4.Address, arc4.UInt64]

    def __init__(self) -> None:
        """Initialize the rebate engine contract"""
        self.tier_schedules = BoxMap(arc4.Address, arc4.DynamicArray[arc4.UInt64])
        self.accrued_liabilities = BoxMap(arc4.DynamicBytes, arc4.UInt64)
        self.total_accrued = BoxMap(arc4.Address, arc4.UInt64)

    @arc4.abimethod
    def register_schedule(
        self,
        base_bps: arc4.UInt64,
        threshold: arc4.UInt64,
        bonus_bps: arc4.UInt64,
        excludes_biosimilars: arc4.Bool,
    ) -> arc4.String:
        """
        Register a tiered rebate schedule for a manufacturer.

        Args:
            base_bps: Base rebate rate in basis points (e.g., 1500 = 15%)
            threshold: Volume threshold to unlock bonus tier (in units)
            bonus_bps: Additional bonus rate in basis points
            excludes_biosimilars: If True, emits anti-competitive warning

        Returns:
            status: Confirmation message

        Note:
            bps = basis points (1/100th of a percent, so 10000 = 100%)
        """
        manufacturer = arc4.Address(Txn.sender)

        # CRITICAL: Anti-competitive flag detection
        # If manufacturer excludes biosimilars, emit regulatory warning event
        if excludes_biosimilars.native:
            arc4.emit(
                "FORMULARY_LOCK_EVENT",
                manufacturer,
                base_bps,
                arc4.String("Biosimilar exclusion detected - regulatory review required"),
            )

        # Store schedule as dynamic array: [base_bps, threshold, bonus_bps]
        schedule = arc4.DynamicArray[arc4.UInt64](base_bps, threshold, bonus_bps)
        self.tier_schedules[manufacturer] = schedule

        # Initialize total accrued to 0 if not exists
        if manufacturer not in self.total_accrued:
            self.total_accrued[manufacturer] = arc4.UInt64(0)

        # Emit registration event
        arc4.emit("ScheduleRegistered", manufacturer, base_bps, threshold, bonus_bps)

        return arc4.String("Schedule registered successfully")

    @arc4.abimethod
    def calculate_accrual(
        self,
        claim_key: arc4.DynamicBytes,
        manufacturer: arc4.Address,
        wac_price: arc4.UInt64,
        current_volume: arc4.UInt64,
    ) -> arc4.UInt64:
        """
        Calculate rebate accrual for a specific claim using tiered pricing.

        Args:
            claim_key: Unique claim identifier from Layer 0
            manufacturer: Manufacturer's Algorand address
            wac_price: Wholesale Acquisition Cost in microUSD (6 decimals)
            current_volume: Cumulative dispensed units for this manufacturer

        Returns:
            rebate_amount: Calculated rebate in microUSD

        Logic:
            - If volume > threshold: rebate = price * (base + bonus) / 10000
            - Else: rebate = price * base / 10000
        """
        # Fetch manufacturer's rebate schedule
        assert manufacturer in self.tier_schedules, "Manufacturer not registered"
        schedule = self.tier_schedules[manufacturer]

        # Extract schedule parameters
        base_bps = schedule[0].native
        threshold = schedule[1].native
        bonus_bps = schedule[2].native

        # Determine applicable rebate rate based on volume tier
        if current_volume.native > threshold:
            # Volume exceeds threshold: apply base + bonus
            effective_rate = base_bps + bonus_bps
            arc4.emit("BonusTierActivated", claim_key, manufacturer, current_volume)
        else:
            # Standard tier: use base rate only
            effective_rate = base_bps

        # Calculate rebate: (price * rate) / 10000
        # Using integer division to avoid floating point
        rebate_amount = (wac_price.native * effective_rate) // 10000

        # Store claim-specific accrual
        self.accrued_liabilities[claim_key] = arc4.UInt64(rebate_amount)

        # Update manufacturer's total liability
        current_total = self.total_accrued[manufacturer].native
        self.total_accrued[manufacturer] = arc4.UInt64(current_total + rebate_amount)

        # Emit calculation event for analytics
        arc4.emit(
            "RebateCalculated",
            claim_key,
            manufacturer,
            wac_price,
            arc4.UInt64(effective_rate),
            arc4.UInt64(rebate_amount),
        )

        return arc4.UInt64(rebate_amount)

    @arc4.abimethod(readonly=True)
    def get_accrual(self, claim_key: arc4.DynamicBytes) -> arc4.UInt64:
        """
        Retrieve the accrued rebate for a specific claim.

        Args:
            claim_key: Unique claim identifier

        Returns:
            rebate_amount: The calculated rebate in microUSD
        """
        assert claim_key in self.accrued_liabilities, "Claim not calculated"
        return self.accrued_liabilities[claim_key]

    @arc4.abimethod(readonly=True)
    def get_manufacturer_total(self, manufacturer: arc4.Address) -> arc4.UInt64:
        """
        Get total accrued liabilities for a manufacturer.

        Args:
            manufacturer: Manufacturer's Algorand address

        Returns:
            total_liability: Total rebates owed in microUSD
        """
        return self.total_accrued.get(manufacturer, arc4.UInt64(0))
