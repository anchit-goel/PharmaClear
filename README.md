# PharmaClear Enhanced - Decentralized Pharmaceutical Rebate Settlement Protocol

<div align="center">

![Algorand](https://img.shields.io/badge/Algorand-Python-blue?style=for-the-badge&logo=algorand)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![RIFT 2026](https://img.shields.io/badge/RIFT-2026-orange?style=for-the-badge)
![Multi-Category](https://img.shields.io/badge/Categories-4+-red?style=for-the-badge)

**A Zero-Trust, Global Settlement Protocol for Pharmaceutical Rebates**

**🏆 Multi-Category Hackathon Submission:**
✅ Supply Chain Tracking • ✅ DAO Governance • ✅ Cross-Border Payments • ✅ DeFi Tools

[Overview](#overview) • [Enhanced Features](#-enhanced-features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Categories](#-hackathon-categories)

</div>

---

## 🎯 Overview

**PharmaClear Enhanced** is a comprehensive blockchain protocol that revolutionizes the **$200+ billion pharmaceutical rebate industry** with:

- 🌍 **Global Supply Chain Tracking** - Batch/lot provenance from manufacturer to patient
- 🗳️ **DAO Governance** - Decentralized dispute resolution and protocol management
- 💱 **Cross-Border Settlements** - Multi-currency rebates in 6+ stablecoins
- ⚛️ **Atomic DeFi** - Inner transaction-based instant settlements

### The Problem

The current pharmaceutical rebate system suffers from:
- ❌ **Opacity:** Manual reconciliation takes 90+ days
- ❌ **Trust Issues:** Centralized intermediaries control $billions
- ❌ **Fraud Risk:** Duplicate claims and data manipulation
- ❌ **Compliance Gaps:** No immutable audit trails
- ❌ **Safety Issues:** No real-time recall tracking
- ❌ **Limited Governance:** No stakeholder participation
- ❌ **Currency Barriers:** Cross-border settlements inefficient

### Our Solution - Enhanced

PharmaClear Enhanced leverages Algorand's blockchain across **4 hackathon categories**:

**🔗 Supply Chain Tracking:**
- ✅ **Batch Provenance:** Track drugs from manufacturer lot to patient claim
- ✅ **Instant Recalls:** Identify all affected pharmacies in <4 seconds
- ✅ **Expiration Monitoring:** Prevent expired drug dispensation
- ✅ � Enhanced Features

### 1. Advanced Provenance Tracking (Layer 0 Enhanced)
```python
submit_claim_enhanced(
    claim_id="CLM-001",
    ndc_code="12345-678-90",
    batch_number="B2026Q1-123",  # NEW: Manufacturer batch
    lot_number="LOT-456",         # NEW: Specific lot
    expiration_date=1767225600,   # NEW: Expiry timestamp
    country_code="US"             # NEW: Jurisdiction
)

# Safety Features
issue_recall(ndc, batch, reason, severity) → Notifies 247 pharmacies instantly
is_batch_recalled(ndc, batch) → True/False
get_expiring_drugs(days=30) → List of drugs expiring soon
```

### 2. DAO Governance System (Layer 4 - NEW)
```python
# Create proposal
proposal_id = create_proposal(
    type="FEE_ADJUSTMENT",
    description="Reduce admin fee to 2.5%",
    value=250  # 250 bps = 2.5%
)
─────┐
│  Layer 0 ENHANCED: Advanced Provenance Tracking 🔗          │
│  • Batch/lot number registry                                 │
│  • Expiration date monitoring                                │
│  • Drug recall management (instant notification)             │
│  • International pharmacy support (50+ countries)            │
│  • Supply chain traceability                                 │
└──────────────────┬───────────────────────────────────────────┘
                   │ claim_key + batch_metadata
                   ▼
┌──────────────────────────────────────────────────────────────┐
│  Layer 1: Rebate Calculation Engine                          │
│  • Tiered pricing (base + volume bonuses)                    │
│  • Anti-competitive detection                                │
│  • Manufacturer liability tracking                           │
└──────────────────┬───────────────────────────────────────────┘
                   │ rebate_amount
                   ▼
┌──────────────────────────────────────────────────────────────┐
│  Layer 2: Atomic Settlement ⚛️ (DeFi Core)                  │
│  • Inner Transactions for instant transfers                  │
│  • Atomic transaction groups                                 │
│  • Fee cap enforcement (jurisdiction-specific)               │
└──────────────────┬───────────────────────────────────────────┘
                   │ settlement_proof
                   ▼
┌──────────────────────────────────────────────────────────────┐
│  Layer 3: Audit Rail (Regulatory Compliance)                 │
│  • ARC-28 event logs                                         │
│  • Immutable compliance records                              │
└──────────────────┬───────────────────────────────────────────┘
                   │
┌──────────────────────────────────────────────────────────────┐
│  Layer 4: DAO Governance 🗳️ (NEW)                           │
│  • Proposal creation & voting (66% threshold)                │
│  • Dispute resolution (stake-weighted)                       │
│  • Oracle selection & reputation management                  │
│  • Fee adjustment proposals                                  │
│  • Protocol parameter governance                             │
└──────────────────┬───────────────────────────────────────────┘
                   │
┌──────────────────────────────────────────────────────────────┐
│  Layer 5: Cross-Border Settlement 💱 (NEW)                  │
│  • Multi-currency support (USD/EUR/GBP/CAD/MXN/JPY)          │
│  • Real-time FX conversion via oracles                       │
│  • KYC/AML compliance checks                                 │
│  • Jurisdiction-specific fee caps                            │
│  • Automatic stablecoin conversion                           │
└─────--

## 🏗️ Enhanced Architecture

PharmaClear now consists of **7
- ✅ **Dispute Resolution:** Community voting on claim disputes
- ✅ **Oracle Management:** Decentralized oracle selection & reputation
- ✅ **Fee Proposals:** Stake-weighted voting on parameter changes
- ✅ **Protocol Upgrades:** Democratic governance of all parameters

**💱 Cross-Border Payments:**
- ✅ **Multi-Currency:** Settle in USD, EUR, GBP, CAD, MXN, JPY
- ✅ **Auto-Conversion:** Real-time FX rates from oracles
- ✅ **KYC/AML:** Built-in compliance checks
- ✅ **Jurisdiction Rules:** Country-specific fee caps

**💰 DeFi Tools:**
- ✅ **Atomic Settlement:** All-or-nothing transaction groups
- ✅ **Inner Transactions:** Smart contract-initiated transfers
- ✅ **Fee Optimization:** Algorithmically enforced caps
- ✅ **Escrow Pools:** Multi-currency liquidity management

---

## 🏗️ Architecture

PharmaClear consists of **4 smart contract layers** working in concert:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 0: CLAIM INGESTION (Trust Layer)                │
│  • Prevents duplicate claims via SHA-256 hashing        │
│  • Stores claim metadata in Box Storage                 │
│  • Emits ClaimSubmitted events                          │
└──────────────────┬──────────────────────────────────────┘
                   │ claim_key
                   ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 1: REBATE ENGINE (Calculation Engine)           │
│  • Tiered rebate schedules (base + bonus)               │
│  • Volume threshold logic                               │
│  • Anti-competitive behavior detection                  │
└──────────────────┬──────────────────────────────────────┘
                   │ rebate_amount
      Enhanced Project Structure

```
PharmaClear/
├── smart_contracts/
│   ├── layer0_ingestion.py      # Original: Basic claim submission
│   ├── layer0_enhanced.py       # 🆕 Batch/recall/expiration tracking
│   ├── layer1_rebate.py         # Tiered rebate calculation
│   ├── layer2_escrow.py         # Atomic settlement (USD)
│   ├── layer3_audit.py          # ARC-28 compliance logging
│   ├── layer4_governance.py     # 🆕 DAO voting & disputes
│   └── layer5_crossborder.py    # 🆕 Multi-currency settlements
│
├── scripts/
│   └── demo_flow.py             # Full orchestration demo
│
├── tests/
│   └── test_integration.py      # Comprehensive test suite
│
├── ENHANCED_FEATURES.md         # 🆕 Complete feature matrix
├── DEPLOYMENT.md                # Deployment guide
├── PROJECT_STRUCTURE.md         # Technical architecture
├── TECHNICAL_ARCHITECTURE.md    # Deep dive
├── requirements.txt             # Python dependencies
└── README.md  ─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install AlgoKit (if not already installed)
brew install algorandfoundation/tap/algokit  # macOS
# OR
pipx install algokit                          # Windows/Linux

# Start Algorand LocalNet
algokit localnet start
```

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/PharmaClear.git
cd PharmaClear

# Install dependencies
pip install -r requirements.txt
```

### Run the Demo

```bash
# Execute the full demonstration flow
python scripts/demo_flow.py
```

**Expected Output:**
```
🏗️  PharmaClear Demo Initialization
Deployer: ABC123...
Manufacturer: DEF456...
Pharmacy: GHI789...

💵 Creating Test USDCa Asset...
✅ Created USDCa Asset ID: 1234

🚀 Deploying Smart Contracts...
✅ Layer 0 Deployed (App ID: 1001)
✅ Layer 1 Deployed (App ID: 1002)
✅ Layer 2 Deployed (App ID: 1003)
✅ Layer 3 Deployed (App ID: 1004)

⚛️  Executing Atomic Settlement Transaction Group...
✅ Atomic Settlement Complete

💰 Pharmacy Received: $97.00 USDCa
✅ All transactions recorded on-chain
```

---

## 📁 Project Structure

```
PharmaClear/
├── smart_contracts/
│   ├── layer0_ingestion.py    # Claim submission & deduplication
│   ├── layer1_rebate.py       # Tiered rebate calculation
│   ├── layer2_escrow.py       # Atomic settlement with inner txns
│   └── layer3_audit.py        # ARC-28 compliance logging
│
├── scripts/
│   └── demo_flow.py           # Full orchestration demo
│
├── requirements.txt           # Python dependencies
├── PROJECT_STRUCTURE.md       # Detailed technical documentation
└── README.md                  # This file
```

---

## 🔬 Technical Highlights

### 1. **Atomic Transaction Groups** (Layer 2)

The settlement is executed as an **indivisible** atomic group:

```python
[Transaction 0] Oracle Authentication Payment (1000 μALGO)
[Transaction 1] Settlement Application Call
    ↳ Inner Txn 1: Transfer $97 USDCa → Pharmacy
    ↳ Inner Txn 2: Transfer $3 Fee → PBM
```

**Why This Matters:**
- If the oracle transaction fails, the entire settlement reverts
- No partial settlements or front-running attacks possible
- True "all-or-nothing" guarantee

### 2. **Box Storage** (Layers 0 & 1)

Uses Algorand's Box Storage for **infinite scalability**:

```python
claim_hashes: BoxMap[arc4.DynamicBytes, arc4.Bool]
claim_records: BoxMap[arc4.DynamicBytes, arc4.String]
```

**Advantages:**
- No 127 key-value pair limit (old global state problem)
- Pay-per-box storage model scales to millions of claims
- Deterministic costs

### 3. **ARC-28 Event Emission** (All Layers)

Every critical action emits standardized events:

```python
arc4.emit(
    "RebateSettled",
    claim_key,
    pharmacy_addr,
    rebate_amount,
    timestamp,
)
```

**Benefits:**
- Indexers can build real-time dashboards
- Regulators get immutable audit trails
- Off-chain analytics without querying state

### 4. **Anti-Competitive Detection** (Layer 1)

Automatically flags potential antitrust violations:

```python
if excludes_biosimilars.native:
    arc4.emit("FORMULARY_LOCK_EVENT", manufacturer, ...)
```

**Real-World Impact:**
- Detects biosimilar exclusion tactics
- Creates regulatory transparency
- Incentivizes fair competition

---

## 📊 Demo Scenario

The `demo_flow.py` script simulates a real-world prescription settlement:

| **Step** | **Action** | **Result** |
|----------|-----------|-----------|
| 1 | Pharmacy dispenses $100 drug (WAC) | Claim ID: `CLM-2026-000123` |
| 2 | Claim submitted to Layer 0 | `claim_key` generated via SHA-256 |
| 3 | Layer 1 calculates rebate (15% base) | $15 rebate accrued |
| 4 | Atomic settlement via Layer 2 | $14.55 → Pharmacy, $0.45 → PBM |
| 5 | Layer 3 logs audit event | Immutable record created |

**Fi� RIFT 2026 Hackathon Categories

### ✅ **Primary Category: Supply Chain / Provenance Tracking**

| Feature | Implementation | Impact |
|---------|----------------|--------|
| Batch Tracking | `layer0_enhanced.py` - Full batch/lot registry | Track drugs from factory to patient |
| Recall System | `issue_recall()` - Instant affected claim ID | <4 sec response time vs. days |
| Expiration Monitoring | `get_expiring_drugs()` - Proactive alerts | Prevent dispensing expired drugs |
| International Support | 50+ country codes supported | Global pharmaceutical supply chain |
| Supply Chain Audit | Immutable ARC-28 events | Complete provenance trail |

**Real-World Scenario:**
> FDA issues Class I recall for contaminated batch B2026-123. PharmaClear instantly identifies 247 affected claims across 89 pharmacies in 12 states. Total response time: **3.7 seconds** vs. traditional **3-7 days**.

---

### ✅ **Secondary Category: DAO Governance Systems**

| Feature | Implementation | Governance Model |
|---------|----------------|------------------|
| Proposal System | `create_proposal()` - On-chain proposals | Open to all stakeholders |
| Voting Mechanism | `vote()` - Stake-weighted voting | 66% approval threshold |
| Dispute Resolution | `file_dispute()` + voting | Community arbitration |
| Oracle Management | `register/slash_oracle()` - Reputation | Decentralized oracle selection |
| Fee Governance | Fee adjustment proposals | Democratic parameter changes |

**Governance Example:**
> Community proposes reducing admin fees from 3% to 2.5%. Proposal receives 15,000 yes votes (83% approval). Auto-executes on finalization.

---

### ✅ **Tertiary Category: Cross-Border Payments & Remittances**

| Feature | Implementation | Benefit |
|---------|----------------|---------|
| Multi-Currency | 6+ stablecoins (USD/EUR/GBP/CAD/MXN/JPY) | Global pharmacy support |
| FX Conversion | Oracle-provided real-time rates | Minimize currency risk |
| KYC/AML | Pre-settlement compliance checks | Regulatory compliance |
| Jurisdiction Caps | Country-specific fee limits | Automatic regulatory adherence |
| Settlement Speed | <4 second finality | Instant global payments |

**Cross-Border Example:**
> Canadian pharmacy dispenses $500 USD drug. PharmaClear: (1) Verifies KYC, (2) Gets 1.35 CAD/USD rate, (3) Converts to 675 CAD, (4) Applies 2% Canada fee, (5) Settles 661.5 CAD to pharmacy in **3.9 seconds**.

---

### ✅ **Additional Category: DeFi Tools**

| Feature | Implementation | DeFi Primitive |
|---------|----------------|----------------|
| Escrow Pools | Multi-currency reserves | Automated market making |
| Atomic Swaps | Inner transaction groups | Trustless exchanges |
| Fee Optimization | Algorithmic cap enforcement | Smart contract automation |
| Liquidity Management | `fund_escrow()` across currencies | Multi-asset pools |

---

## ✅ Technical Requirements Compliance

| **Requirement** | **Implementation** | **Status** |
|-----------------|-------------------|-----------|
| Algorand Python (not PyTEAL) | All 7 contracts use `algopy` | ✅ |
| Box Storage for infinite maps | All layers use `BoxMap` | ✅ |
| ARC-4 ABI methods | All public methods use `@arc4.abimethod` | ✅ |
| ARC-28 event emission | `arc4.emit()` used throughout | ✅ |
| Atomic Transaction Groups | Layers 2 & 5 use atomic groups | ✅ |
| Inner Transactions | `itxn.AssetTransfer()` for settlements | ✅ |
| Real-world use case | $200B pharmaceutical + global supply chain | ✅ |
| Complete working app | Deployable, testable, demonstrable
- **Duplicate Claims:** SHA-256 hashing prevents resubmission
- **Oracle Verification:** Requires co-signed transaction in atomic group
- **Fee Caps:** Hard-coded 3% maximum (cannot be bypassed)

### Transparency Guarantees
- **Open Source:** All contract logic is auditable
- **On-Chain State:** Box storage prevents hidden liabilities
- **Event Logs:** Every settlement creates immutable proof

### Compliance Features
- **ARC-28 Events:** Standard format for regulatory indexers
- **Dispute Logging:** On-chain resolution workflows
- **Antitrust Flags:** Automatic detection of anti-competitive practices

---

## 🎯 RIFT 2026 Hackathon Criteria

| **Requirement** | **Implementation** | **Status** |
|-----------------|-------------------|-----------|
| Algorand Python (not PyTEAL) | All contracts use `algopy` | ✅ |
| Box Storage for infinite maps | Layers 0 & 1 use `BoxMap` | ✅ |
| ARC-4 ABI methods | All public methods use `@arc4.abimethod` | ✅ |
| ARC-28 event emission | `arc4.emit()` used throughout | ✅ |
| Atomic Transaction Groups | Layer 2 settlement is atomic | ✅ |
| Inner Transactions | Layer 2 uses `itxn.AssetTransfer()` | ✅ |
| Real-world use case | Solves $200B pharmaceutical problem | ✅ |

---

## 🔮 Future Enhancements

1. **Multi-Manufacturer Pooling:** Aggregate rebates across manufacturers
2. **Dispute Resolution DAO:** Decentralized arbitration for claim disputes
3. **Real Oracle Integration:** Chainlink or Algorand State Proofs
4. **Privacy Layers:** Zero-knowledge proofs for HIPAA compliance
5. **Cross-Chain Bridges:** Settle in USDC on other chains

---

## 📄 License

MIT License - Copyright (c) 2026 PharmaClear Team

Built for **RIFT 2026 Hackathon** on **Algorand Blockchain**.

---

## 🤝 Contributing

We welcome contributions! Please see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed technical documentation.

---

<div align="center">

**Built with ❤️ on Algorand**

*Making pharmaceutical rebates transparent, instant, and fair.*

</div>
