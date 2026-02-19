# PharmaClear - Project Structure

## 📁 Directory Layout

```
PharmaClear/
├── smart_contracts/          # Algorand Python Smart Contracts
│   ├── __init__.py
│   ├── layer0_ingestion.py   # Trust Layer - Claim submission
│   ├── layer1_rebate.py      # Calculation Engine - Rebate logic
│   ├── layer2_escrow.py      # Settlement Layer - Atomic payments
│   └── layer3_audit.py       # Compliance Rail - Audit logs
│
├── scripts/                  # Orchestration & Demo Scripts
│   └── demo_flow.py          # Full demonstration workflow
│
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── .algokit.toml            # AlgoKit configuration
```

## 🏗️ Architecture Overview

### **Layer 0: Claim Ingestion Contract** (`layer0_ingestion.py`)
**Purpose:** Trust Layer - Prevents duplicate claims

**Key Features:**
- SHA-256 claim hashing for uniqueness
- Box storage for infinite scalability
- Oracle signature verification
- ARC-28 event emission

**Critical Methods:**
- `submit_claim()` - Submit verified pharmaceutical claims
- `verify_claim()` - Check claim existence
- `get_claim_metadata()` - Retrieve claim details

---

### **Layer 1: Rebate Engine Contract** (`layer1_rebate.py`)
**Purpose:** Calculation Engine - Tiered rebate computation

**Key Features:**
- Volume-based tier pricing
- Anti-competitive behavior detection
- Per-manufacturer liability tracking
- Bonus tier activation

**Critical Methods:**
- `register_schedule()` - Set manufacturer rebate tiers
- `calculate_accrual()` - Compute rebate amounts
- `get_manufacturer_total()` - Query total liabilities

---

### **Layer 2: Escrow Settlement Contract** (`layer2_escrow.py`)
**Purpose:** Settlement Layer - Atomic payments with fee caps

**Key Features:**
- **Atomic Transaction Groups** for settlement
- **Inner Transactions** for USDCa transfers
- 3% admin fee cap (anti-rent-seeking)
- Oracle authentication via group verification

**Critical Methods:**
- `claim_rebate()` - Execute atomic settlement (CORE METHOD)
- `fund_escrow()` - Load USDCa into contract
- `get_balance()` - Check escrow balance

**Atomic Group Structure:**
```
[Transaction 0] Oracle Authentication Payment
[Transaction 1] Settlement Application Call
    ↳ Inner Txn 1: Rebate → Pharmacy
    ↳ Inner Txn 2: Admin Fee → PBM
```

---

### **Layer 3: Audit Rail Contract** (`layer3_audit.py`)
**Purpose:** Compliance Rail - Immutable audit logs

**Key Features:**
- ARC-28 canonical event emission
- Regulatory compliance records
- Dispute logging
- Anti-competitive flagging

**Critical Methods:**
- `log_event()` - General audit entry
- `log_settlement()` - Settlement-specific audit
- `log_dispute()` - Claim dispute tracking
- `log_formulary_lock()` - Antitrust violation flags

---

## 🚀 Demo Flow (`scripts/demo_flow.py`)

### **Execution Steps:**

1. **Setup Phase**
   - Create test USDCa asset
   - Opt accounts into asset
   - Deploy all 4 contracts

2. **Configuration Phase**
   - Register manufacturer rebate schedule (15% base, 5% bonus)
   - Fund escrow with $1,000 USDCa

3. **Claim Submission (Layer 0)**
   - Generate fake prescription claim
   - Submit with oracle signature
   - Receive unique `claim_key`

4. **Rebate Calculation (Layer 1)**
   - Calculate rebate based on WAC price ($100)
   - Apply tier logic (volume < threshold = 15% only)
   - Store accrued liability

5. **Atomic Settlement (Layer 2)**
   - **Construct Transaction Group:**
     - [0] Oracle auth payment (1000 microALGO)
     - [1] `claim_rebate()` call
   - **Inner Transactions:**
     - Transfer $97 USDCa to pharmacy
     - Transfer $3 admin fee to PBM
   - Submit as atomic group

6. **Audit Logging (Layer 3)**
   - Log settlement event with timestamp
   - Create immutable compliance record

7. **Verification**
   - Check pharmacy USDCa balance
   - Print settlement summary

---

## 🔑 Key Technical Concepts

### **Box Storage**
Used for infinite maps (claims, rebates, schedules). Replaces deprecated global state limits.

### **ARC-4 (Application Binary Interface)**
Ensures type-safe smart contract method calls with standardized encoding.

### **ARC-28 (Event Logging)**
Canonical event emission for indexers and off-chain analytics.

### **Atomic Transaction Groups**
Guarantees all-or-nothing execution. If oracle auth fails, settlement reverts.

### **Inner Transactions**
Smart contracts can initiate transactions (e.g., USDCa transfers) without external signers.

---

## 📊 Data Flow

```
Pharmacy → Layer 0 (submit_claim)
             ↓ claim_key
           Layer 1 (calculate_accrual)
             ↓ rebate_amount
           Layer 2 (claim_rebate) ← Oracle Auth
             ↓ Inner Txns
           [Pharmacy Balance +$97]
           [PBM Balance +$3]
             ↓
           Layer 3 (log_settlement)
             ↓
           [Immutable Audit Record]
```

---

## 🛠️ Development Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Compile Contracts (AlgoKit)
```bash
algokit compile python smart_contracts/layer0_ingestion.py
algokit compile python smart_contracts/layer1_rebate.py
algokit compile python smart_contracts/layer2_escrow.py
algokit compile python smart_contracts/layer3_audit.py
```

### Run Demo
```bash
python scripts/demo_flow.py
```

### Deploy to Localnet
```bash
algokit localnet start
python scripts/demo_flow.py
```

### Deploy to TestNet
```bash
export ALGOD_TOKEN="your-testnet-token"
export ALGOD_SERVER="https://testnet-api.algonode.cloud"
python scripts/demo_flow.py
```

---

## 🔐 Security Features

1. **Duplicate Prevention:** SHA-256 hashing prevents double-submissions
2. **Fee Caps:** Hard-coded 3% maximum admin fee
3. **Atomic Groups:** Settlement cannot be front-run or sandwich-attacked
4. **Oracle Verification:** Requires oracle co-signature via atomic group
5. **Immutable Audits:** All settlements logged to blockchain

---

## 🏆 RIFT 2026 Hackathon Compliance

✅ **Algorand Python (Puya)** - Not PyTEAL
✅ **Box Storage** - Infinite scalability
✅ **ARC-4 Methods** - Type-safe ABI
✅ **ARC-28 Events** - Indexed event emission
✅ **Atomic Logic** - Transaction groups + inner txns
✅ **Real-World Use Case** - Pharmaceutical industry problem

---

## 📝 License

MIT License - RIFT 2026 Hackathon Submission
