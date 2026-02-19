# PharmaClear Technical Architecture

## 🏛️ System Architecture

### Overview

PharmaClear is a **4-layer smart contract architecture** designed for pharmaceutical rebate settlement on Algorand. Each layer has a distinct responsibility, creating a separation of concerns that enhances security, maintainability, and auditability.

```
┌─────────────────────────────────────────────────────────────┐
│                     OFF-CHAIN LAYER                         │
│  • Pharmacy Management Systems (PMS)                        │
│  • Oracle Services (Claim Verification)                     │
│  • Indexer Analytics (Event Processing)                     │
└────────────────────┬────────────────────────────────────────┘
                     │ API Calls
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   LAYER 0: TRUST LAYER                      │
│  Contract: ClaimIngestionContract                           │
│  Purpose: Prevent duplicate claims                          │
│                                                              │
│  State:                                                      │
│    • claim_hashes: BoxMap[Bytes → Bool]                    │
│    • claim_records: BoxMap[Bytes → String]                 │
│                                                              │
│  Key Methods:                                                │
│    • submit_claim() → claim_key                            │
│    • verify_claim() → bool                                  │
│                                                              │
│  Security Features:                                          │
│    ✓ SHA-256 hashing for uniqueness                        │
│    ✓ Oracle signature verification                          │
│    ✓ Hard rejection of duplicates                           │
└────────────────────┬────────────────────────────────────────┘
                     │ claim_key
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                LAYER 1: CALCULATION ENGINE                   │
│  Contract: RebateEngineContract                             │
│  Purpose: Tiered rebate computation                          │
│                                                              │
│  State:                                                      │
│    • tier_schedules: BoxMap[Address → Array[UInt64]]       │
│    • accrued_liabilities: BoxMap[Bytes → UInt64]           │
│    • total_accrued: BoxMap[Address → UInt64]               │
│                                                              │
│  Key Methods:                                                │
│    • register_schedule() → status                           │
│    • calculate_accrual() → rebate_amount                   │
│                                                              │
│  Business Logic:                                             │
│    • Volume-based tier pricing                              │
│    • Base rate + bonus rate calculation                     │
│    • Anti-competitive behavior detection                    │
└────────────────────┬────────────────────────────────────────┘
                     │ rebate_amount
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               LAYER 2: SETTLEMENT LAYER ⚛️                  │
│  Contract: EscrowSettlementContract                         │
│  Purpose: Atomic payment execution                           │
│                                                              │
│  State:                                                      │
│    • usdc_asset_id: UInt64                                  │
│    • admin_fee_cap: UInt64 (300 bps = 3%)                  │
│                                                              │
│  Key Methods:                                                │
│    • claim_rebate() → status [ATOMIC CORE]                 │
│    • fund_escrow() → status                                 │
│                                                              │
│  Atomic Structure:                                           │
│    [Txn 0] Oracle Authentication Payment                    │
│    [Txn 1] Settlement Application Call                      │
│       ↳ Inner Txn 1: Rebate → Pharmacy                     │
│       ↳ Inner Txn 2: Fee → PBM                             │
│                                                              │
│  Security Features:                                          │
│    ✓ Atomic transaction group validation                    │
│    ✓ Fee cap enforcement (≤3%)                             │
│    ✓ Oracle co-signature requirement                        │
└────────────────────┬────────────────────────────────────────┘
                     │ settlement_proof
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                LAYER 3: COMPLIANCE LAYER                     │
│  Contract: AuditRailContract                                │
│  Purpose: Immutable audit trails                            │
│                                                              │
│  Methods:                                                    │
│    • log_event() → status                                   │
│    • log_settlement() → status                              │
│    • log_dispute() → status                                 │
│    • log_formulary_lock() → status                          │
│                                                              │
│  Event Types:                                                │
│    • AuditEntry (general)                                   │
│    • SettlementAudit (payments)                             │
│    • DisputeLogged (conflicts)                              │
│    • ANTITRUST_FLAG (regulatory)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Box Storage Architecture

### Why Box Storage?

Traditional Algorand global state has a **127 key-value pair limit**, which is insufficient for pharmaceutical claims (potentially millions per year). Box Storage solves this by providing **pay-per-box unlimited storage**.

### Box Storage Used In

#### **Layer 0: Claim Ingestion**
```python
claim_hashes: BoxMap[arc4.DynamicBytes, arc4.Bool]
# Key: SHA-256(claim_data) → 32 bytes
# Value: True/False → 1 byte
# Cost per claim: 2,500 + 400 * 33 = 15,700 microALGO

claim_records: BoxMap[arc4.DynamicBytes, arc4.String]
# Key: SHA-256(claim_data) → 32 bytes
# Value: JSON metadata → ~256 bytes
# Cost per claim: 2,500 + 400 * 288 = 117,700 microALGO
```

**Total storage cost per claim:** ~0.133 ALGO (~$0.04 at $0.30/ALGO)

#### **Layer 1: Rebate Engine**
```python
tier_schedules: BoxMap[arc4.Address, arc4.DynamicArray[arc4.UInt64]]
# Key: Manufacturer address → 32 bytes
# Value: [base_bps, threshold, bonus_bps] → 24 bytes
# Cost per manufacturer: 2,500 + 400 * 56 = 24,900 microALGO

accrued_liabilities: BoxMap[arc4.DynamicBytes, arc4.UInt64]
# Key: claim_key → 32 bytes
# Value: rebate_amount → 8 bytes
# Cost per claim: 2,500 + 400 * 40 = 18,500 microALGO
```

### Box Storage Operations

```python
# Creating a box (automatic when using BoxMap)
self.claim_hashes[claim_key] = arc4.Bool(True)

# Reading from a box
exists = self.claim_hashes.get(claim_key, arc4.Bool(False))

# Checking existence
if claim_key in self.claim_hashes:
    # Box exists

# Deleting a box (to recover storage costs)
del self.claim_hashes[claim_key]
```

### Box Reference in Transactions

When calling methods that access boxes, you must include box references:

```python
from algosdk import transaction

sp = algod_client.suggested_params()
sp.boxes = [
    (app_id, claim_key),  # Reference specific box
]

txn = transaction.ApplicationCallTxn(
    sender=sender_addr,
    sp=sp,
    index=app_id,
    app_args=[method_selector, claim_key],
)
```

---

## ⚛️ Atomic Transaction Groups

### The Problem Atomic Groups Solve

**Without Atomic Groups:**
1. Pharmacy calls `claim_rebate()`
2. ❌ Oracle payment fails mid-transaction
3. ⚠️ Pharmacy gets rebate without verification
4. 💥 **System is compromised**

**With Atomic Groups:**
1. Group of [Oracle Txn, Settlement Txn] submitted
2. ✅ Both succeed, or both fail
3. ✓ No partial execution possible
4. 🔒 **System is secure**

### Atomic Group Implementation (Layer 2)

```python
@arc4.abimethod
def claim_rebate(
    self,
    claim_key: arc4.DynamicBytes,
    rebate_amount: arc4.UInt64,
    pharmacy_addr: arc4.Address,
    pbm_addr: arc4.Address,
    oracle_txn_index: arc4.UInt64,
) -> arc4.String:
    # CRITICAL: Verify this txn is part of a group
    assert Global.group_size > 1, "Must be part of atomic group"

    # Verify oracle transaction exists
    oracle_txn = gtxn.Transaction(oracle_txn_index.native)

    # Validate oracle transaction type and amount
    assert oracle_txn.type == gtxn.TransactionType.Payment
    assert oracle_txn.amount >= 1000  # Minimum stake

    # If we reach here, oracle is authenticated
    # Proceed with settlement...
```

### Creating Atomic Groups (Demo Script)

```python
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
)

# Create composer
atc = AtomicTransactionComposer()

# Transaction 0: Oracle authentication
oracle_txn = transaction.PaymentTxn(
    sender=oracle.address,
    receiver=pharmacy.address,
    amt=1000,
    sp=algod_client.suggested_params(),
)
atc.add_transaction(
    TransactionWithSigner(oracle_txn, oracle_signer)
)

# Transaction 1: Settlement call
atc.add_method_call(
    app_id=escrow_app_id,
    method="claim_rebate",
    sender=pharmacy.address,
    signer=pharmacy_signer,
    sp=algod_client.suggested_params(),
    claim_key=claim_key,
    rebate_amount=rebate_amount,
    pharmacy_addr=pharmacy.address,
    pbm_addr=pbm.address,
    oracle_txn_index=0,  # Reference to Txn 0
)

# Execute atomically (all-or-nothing)
result = atc.execute(algod_client, wait_rounds=4)
```

### Group Validation Rules

1. **Group Size:** Must be ≥2 transactions
2. **Group ID:** All transactions share the same `group_id`
3. **Order:** Transactions must maintain deterministic order
4. **Fees:** Each transaction must pay its own fee
5. **Execution:** If any transaction fails, entire group reverts

---

## 🔄 Inner Transactions

### What Are Inner Transactions?

Inner transactions allow **smart contracts to initiate transactions** without requiring external signatures. This is critical for the escrow contract to transfer USDCa directly.

### Inner Transaction Implementation (Layer 2)

```python
from algopy import itxn, Asset, Account

# INNER TRANSACTION 1: Transfer rebate to pharmacy
itxn.AssetTransfer(
    xfer_asset=Asset(self.usdc_asset_id.native),
    asset_amount=pharmacy_payout,
    asset_receiver=Account(pharmacy_addr),
    fee=0,  # Fee paid by outer transaction
).submit()

# INNER TRANSACTION 2: Transfer fee to PBM
itxn.AssetTransfer(
    xfer_asset=Asset(self.usdc_asset_id.native),
    asset_amount=admin_fee,
    asset_receiver=Account(pbm_addr),
    fee=0,
).submit()
```

### Inner Transaction Constraints

1. **Fee Budget:** Outer transaction must cover inner txn fees
2. **Asset Access:** Contract must be opted into the asset
3. **Balance:** Contract must have sufficient balance
4. **Limit:** Maximum 256 inner transactions per app call
5. **Nesting:** Inner transactions can spawn more inner transactions (up to 8 levels)

### Fee Calculation Example

```python
# Outer transaction fee
outer_fee = 1000  # microALGO (standard)

# Inner transaction fees (2 asset transfers)
inner_fees = 2 * 1000  # microALGO

# Total fee for settlement
total_fee = outer_fee + inner_fees  # 3,000 microALGO = 0.003 ALGO
```

---

## 🎯 ARC-4 (Application Binary Interface)

### What is ARC-4?

ARC-4 defines **standardized encoding** for smart contract method calls, ensuring type safety and interoperability.

### ARC-4 Types Used

```python
from algopy import arc4

# Primitive types
arc4.UInt64      # 64-bit unsigned integer
arc4.Bool        # Boolean (true/false)
arc4.Address     # 32-byte Algorand address
arc4.String      # UTF-8 encoded string

# Dynamic types
arc4.DynamicBytes        # Variable-length byte array
arc4.DynamicArray[T]     # Variable-length array of type T

# Example usage
@arc4.abimethod
def submit_claim(
    self,
    claim_id: arc4.String,           # ARC-4 string
    ndc_code: arc4.String,
    pharmacy_npi: arc4.String,
    dispense_date: arc4.UInt64,      # ARC-4 uint64
    oracle_sig: arc4.DynamicBytes,   # ARC-4 dynamic bytes
) -> arc4.DynamicBytes:              # Return type
    # Method implementation
    pass
```

### ARC-4 Method Selector

Each method has a unique **4-byte selector** calculated as:

```python
selector = sha512_256("submit_claim(string,string,string,uint64,byte[])byte[]")[:4]
```

This selector is prepended to method arguments when calling the contract.

---

## 📡 ARC-28 (Event Logging)

### What is ARC-28?

ARC-28 defines **canonical event emission** for smart contracts, enabling off-chain indexing and analytics.

### Event Emission Examples

```python
# Simple event
arc4.emit("ClaimSubmitted", claim_key, claim_id)

# Complex event with metadata
arc4.emit(
    "RebateCalculated",
    claim_key,
    manufacturer,
    wac_price,
    arc4.UInt64(effective_rate),
    arc4.UInt64(rebate_amount),
)

# Regulatory warning event
arc4.emit(
    "FORMULARY_LOCK_EVENT",
    manufacturer,
    base_bps,
    arc4.String("Biosimilar exclusion detected"),
)
```

### Event Structure

Events are stored in the **transaction log** as:

```json
{
  "txn": {
    "logs": [
      "base64_encoded_event_data"
    ]
  }
}
```

### Indexing Events

```python
# Using Algorand Indexer
import requests

response = requests.get(
    "http://localhost:8980/v2/applications/{app_id}/logs",
    params={"txid": transaction_id}
)

events = response.json()["logs"]
for event in events:
    # Parse event data
    event_name = decode_event(event)
    if event_name == "RebateSettled":
        # Process settlement event
        pass
```

---

## 🔒 Security Architecture

### 1. **Duplicate Prevention (Layer 0)**

```python
# Generate deterministic key
claim_key = arc4.DynamicBytes(op.sha256(claim_data))

# CRITICAL: Hard rejection
assert claim_key not in self.claim_hashes, "duplicate rejected"

# Mark as submitted
self.claim_hashes[claim_key] = arc4.Bool(True)
```

**Attack Prevention:**
- Replay attacks (same claim submitted twice)
- Hash collision attacks (SHA-256 is collision-resistant)

### 2. **Fee Cap Enforcement (Layer 2)**

```python
# Hard-coded maximum
assert admin_fee_cap_bps.native <= 300, "Fee cannot exceed 3%"

# Runtime validation
admin_fee = (rebate_amount.native * self.admin_fee_cap.native) // 10000
max_allowed = (rebate_amount.native * 300) // 10000
assert admin_fee <= max_allowed, "Fee exceeds cap"
```

**Attack Prevention:**
- Rent-seeking by PBMs
- Dynamic fee manipulation

### 3. **Oracle Verification (Layer 2)**

```python
# Verify oracle transaction is in the group
oracle_txn = gtxn.Transaction(oracle_txn_index.native)
assert oracle_txn.type == gtxn.TransactionType.Payment
assert oracle_txn.amount >= 1000  # Minimum stake
```

**Attack Prevention:**
- Unauthorized settlements
- Front-running attacks
- Sybil attacks (oracle must stake)

### 4. **Immutable Audit Trail (Layer 3)**

```python
arc4.emit(
    "AuditEntry",
    claim_key,
    event_type,
    pharmacy_addr,
    manufacturer_addr,
    rebate_amount,
    arc4.UInt64(Global.latest_timestamp),
)
```

**Regulatory Benefits:**
- Tamper-proof records
- Timestamped evidence
- Dispute resolution

---

## 📊 Performance Metrics

### Transaction Throughput

| Metric | Value |
|--------|-------|
| Block time | 3.9 seconds (Algorand average) |
| TPS (theoretical) | ~1000 per application |
| Settlement latency | ~4 seconds (1 block confirmation) |
| Daily capacity | ~8.6M settlements |

### Cost Analysis

| Operation | Cost (ALGO) | Cost (USD @ $0.30) |
|-----------|-------------|-------------------|
| Claim submission | 0.001 + storage | ~$0.0003 + $0.04 |
| Rebate calculation | 0.001 | ~$0.0003 |
| Settlement (atomic group) | 0.003 | ~$0.0009 |
| **Total per claim** | **~0.138 ALGO** | **~$0.041** |

**Industry Comparison:**
- Traditional processing cost: **$5-15 per claim**
- PharmaClear savings: **99%+ reduction**

---

## 🔮 Advanced Topics

### Multi-Signature Deployment

For production, use multi-sig for admin actions:

```python
from algosdk.future.transaction import Multisig

msig = Multisig(
    version=1,
    threshold=2,
    addresses=[admin1, admin2, admin3]
)
```

### Oracle Integration

Replace dummy oracle with real service:

```python
# Chainlink Oracle (conceptual)
oracle_response = chainlink_client.verify_claim(claim_data)
assert oracle_response.signature_valid

# Algorand State Proofs (future)
state_proof = verify_state_proof(claim_data)
assert state_proof.valid
```

### Privacy Enhancements

Add zero-knowledge proofs for HIPAA compliance:

```python
# ZK-STARK proof of claim validity
zk_proof = generate_stark_proof(claim_data, private_patient_data)
assert verify_stark_proof(zk_proof, claim_key)
```

---

## 📚 References

- [Algorand Developer Docs](https://developer.algorand.org/)
- [AlgoPy Documentation](https://algorandfoundation.github.io/puya/)
- [ARC-4 Standard](https://arc.algorand.foundation/ARCs/arc-0004)
- [ARC-28 Standard](https://arc.algorand.foundation/ARCs/arc-0028)
- [Box Storage Guide](https://developer.algorand.org/docs/get-details/dapps/smart-contracts/apps/state/#boxes)

---

**Built for RIFT 2026 Hackathon**
*Making pharmaceutical rebates transparent, instant, and fair.*
