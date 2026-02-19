"""
PharmaClear Layer 2: Escrow Settlement Contract (The Settlement Layer)
Executes atomic rebate settlements with fee caps and oracle verification.
"""

from algopy import (
    ARC4Contract,
    Account,
    Asset,
    Global,
    Txn,
    UInt64,
    arc4,
    gtxn,
    itxn,
)


class EscrowSettlementContract(ARC4Contract):
    """
    The Settlement Layer - Executes atomic rebate payments using inner transactions.
    Enforces fee caps and requires oracle authentication via atomic groups.
    """

    def __init__(self) -> None:
        """Initialize the escrow settlement contract"""
        # State is managed through global state, not box storage for constants
        pass

    @arc4.abimethod
    def initialize(
        self,
        usdc_asset_id: arc4.UInt64,
        admin_fee_cap_bps: arc4.UInt64,
    ) -> arc4.String:
        """
        Initialize the settlement contract parameters.

        Args:
            usdc_asset_id: Algorand Asset ID for USDCa (or test token)
            admin_fee_cap_bps: Maximum admin fee in basis points (default: 300 = 3%)

        Returns:
            status: Confirmation message
        """
        # Store USDC asset ID in global state
        self.usdc_asset_id = usdc_asset_id

        # Cap admin fees at maximum (anti-rent-seeking mechanism)
        assert admin_fee_cap_bps.native <= 300, "Admin fee cannot exceed 3%"
        self.admin_fee_cap = admin_fee_cap_bps

        arc4.emit("SettlementInitialized", usdc_asset_id, admin_fee_cap_bps)

        return arc4.String("Settlement contract initialized")

    @arc4.abimethod
    def claim_rebate(
        self,
        claim_key: arc4.DynamicBytes,
        rebate_amount: arc4.UInt64,
        pharmacy_addr: arc4.Address,
        pbm_addr: arc4.Address,
        oracle_txn_index: arc4.UInt64,
    ) -> arc4.String:
        """
        Execute atomic settlement of a rebate claim.

        CRITICAL: This method MUST be called as part of an atomic transaction group
        that includes an oracle authentication transaction.

        Args:
            claim_key: The unique claim identifier
            rebate_amount: Total rebate amount in microUSD
            pharmacy_addr: Pharmacy's receiving address
            pbm_addr: PBM's fee collection address
            oracle_txn_index: Index of oracle auth txn in the group

        Returns:
            status: Settlement confirmation

        Atomic Group Structure:
            [0] Oracle Payment/Auth Transaction
            [1] This Application Call

        Inner Transactions:
            1. Transfer (rebate - fee) to pharmacy
            2. Transfer admin fee to PBM
        """
        # CRITICAL: Atomic group validation
        # Verify this transaction is part of a group
        assert Global.group_size > 1, "Must be part of atomic group"

        # Verify oracle transaction exists at specified index
        oracle_txn = gtxn.Transaction(oracle_txn_index.native)

        # Oracle must be a payment transaction (simplified auth mechanism)
        # In production, verify signature or specific oracle address
        assert oracle_txn.type == gtxn.TransactionType.Payment, "Oracle txn must be payment"
        assert oracle_txn.amount >= 1000, "Oracle must stake minimum amount"

        # Calculate admin fee (capped at admin_fee_cap)
        admin_fee = (rebate_amount.native * self.admin_fee_cap.native) // 10000

        # CRITICAL: Fee cap enforcement
        max_allowed_fee = (rebate_amount.native * 300) // 10000  # Hard cap at 3%
        assert admin_fee <= max_allowed_fee, "Admin fee exceeds 3% cap"

        # Calculate pharmacy payout
        pharmacy_payout = rebate_amount.native - admin_fee

        # Ensure contract has sufficient balance
        # (In production, verify manufacturer funding)

        # INNER TRANSACTION 1: Transfer rebate to pharmacy
        itxn.AssetTransfer(
            xfer_asset=Asset(self.usdc_asset_id.native),
            asset_amount=pharmacy_payout,
            asset_receiver=Account(pharmacy_addr),
            fee=0,  # Fee paid by outer transaction
        ).submit()

        # INNER TRANSACTION 2: Transfer admin fee to PBM
        if admin_fee > 0:
            itxn.AssetTransfer(
                xfer_asset=Asset(self.usdc_asset_id.native),
                asset_amount=admin_fee,
                asset_receiver=Account(pbm_addr),
                fee=0,
            ).submit()

        # Emit ARC-28 settlement event
        arc4.emit(
            "RebateSettled",
            claim_key,
            pharmacy_addr,
            pbm_addr,
            arc4.UInt64(pharmacy_payout),
            arc4.UInt64(admin_fee),
            arc4.UInt64(Global.latest_timestamp),
        )

        return arc4.String(
            f"Settlement complete: {pharmacy_payout} to pharmacy, {admin_fee} fee"
        )

    @arc4.abimethod
    def fund_escrow(self, payment: gtxn.AssetTransferTransaction) -> arc4.String:
        """
        Fund the escrow contract with USDCa.

        Args:
            payment: Asset transfer transaction to this contract

        Returns:
            status: Funding confirmation
        """
        # Verify payment is to this contract
        assert payment.asset_receiver == Global.current_application_address, "Invalid receiver"
        assert payment.xfer_asset.id == self.usdc_asset_id.native, "Invalid asset"

        arc4.emit("EscrowFunded", arc4.Address(payment.sender), arc4.UInt64(payment.asset_amount))

        return arc4.String(f"Escrow funded: {payment.asset_amount} microUSD")

    @arc4.abimethod(readonly=True)
    def get_balance(self) -> arc4.UInt64:
        """
        Get the USDCa balance of the escrow contract.

        Returns:
            balance: Current USDCa balance in microUSD
        """
        # Get the asset balance of this contract
        balance = op.AssetBalance(
            Global.current_application_address,
            Asset(self.usdc_asset_id.native),
        )
        return arc4.UInt64(balance)
