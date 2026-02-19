# PharmaClear: Blockchain-Based Pharmaceutical Claims System

**An Algorand + React dApp for secure pharmaceutical claim submission, indexing, and retrieval.**

---

## 📋 Project Overview

PharmaClear is a complete 4-layer distributed system for managing pharmaceutical supply chain claims:

| Layer | Component | Purpose | Technology |
|-------|-----------|---------|------------|
| **0** | Smart Contract | Accept & fingerprint claims | Algorand Python (PuyaPy) |
| **1** | Submission Client | Submit claims with SHA256 hashes | Python CLI + AlgoKit Utils |
| **2** | Indexer Pipeline | Query & archive claim history | Indexer + SQLite/JSON |
| **3** | Frontend | Display claims & UI integration | React 18 + TypeScript + Vite |

### Key Features

✅ **On-Chain Immutability**: Claims fingerprinted via SHA256 embedded in blockchain  
✅ **Off-Chain Scalability**: Full claim text stored in Indexer (zero on-chain cost)  
✅ **Zero State Rent**: No GlobalState overhead; pure note-based architecture  
✅ **Complete Testing**: 14 unit + integration tests covering all layers  
✅ **Localnet-Ready**: Full local development with algokit  
✅ **Production Path**: Testnet/Mainnet deployment scripts included  

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12** (via Homebrew, asdf, or pyenv)
- **Node.js 18+** (npm included)
- **Docker** (for AlgoKit LocalNet)
- **AlgoKit 2.0+** (install: `pip install algokit`)

### 1. Bootstrap the Project

```bash
# Clone and navigate
git clone https://github.com/anchit-goel/PharmaClear.git
cd PharmaClear/PharmaClear

# Initialize AlgoKit (creates .venv in each project)
algokit project bootstrap all
```

### 2. Start LocalNet

```bash
# Terminal 1: Start local Algorand network
algokit localnet start

# Wait for status "✅ LocalNet is ready for use"
# (You can now open http://localhost:4001 to see algod health)
```

### 3. Build & Deploy Contracts

```bash
# Terminal 2: Build contracts
algokit project run build --project-name PharmaClear-contracts

# Deploy to LocalNet
algokit project deploy localnet --project-name PharmaClear-contracts

# Copy the App ID from output (e.g., "Deploying app pharma_clear... App ID: 1234")
export PHARMA_CLEAR_APP_ID=1234
```

### 4. Run Contract Tests

```bash
cd projects/PharmaClear-contracts
source .venv/bin/activate
pytest tests/ -v
```

Expected output:
```
14 passed in 3.44s
- 2 client tests (backward compat)
- 4 contract tests (Layer 0 methods)
- 3 client submission tests (Layer 1)
- 5 indexer tests (Layer 2)
```

### 5. Submit a Claim (Layer 1)

```bash
cd projects/PharmaClear-contracts
source .venv/bin/activate
source .env.localnet  # Load LocalNet config

python tools/submit_claim.py --claim "Patient ID: 12345, Drug: Aspirin, Qty: 100"
```

Expected output:
```
✅ Claim submitted successfully!
   Claim ID:        1
   Transaction ID:  AAAA...
   Sender:          BBBB...

📊 Result (JSON):
{
  "claim_id": 1,
  "claim_hash": "a1b2c3d4ef...",
  ...
}
```

### 6. Query Claims from Indexer (Layer 2)

```bash
python tools/indexer_query.py --app $PHARMA_CLEAR_APP_ID --output claims.json

# View results
cat claims.json | jq '.claims[0]'
```

### 7. Start React Frontend (Layer 3)

```bash
# Terminal 3: Start frontend dev server
cd projects/PharmaClear-frontend
npm install
npm run dev

# Opens http://localhost:5173 (or next available port)
```

Then in the UI:
1. Click "Connect Wallet"
2. Select "Local" and approve
3. Use the "PharmaClear Contract Methods" modal to:
   - Call `hello(name)` → See greeting
   - Call `submit_claim_hash(hash)` → Get back claim ID
   - View all methods with proper ABI encoding

---

## 📁 Project Structure

```
PharmaClear/
├── PharmaClear/                          # Main workspace
│   ├── projects/
│   │   ├── PharmaClear-contracts/        # Layer 0 + 1 + 2
│   │   │   ├── smart_contracts/          # Algorand Python contracts
│   │   │   │   ├── pharma_clear/
│   │   │   │   │   ├── contract.py       # Core 7 ABI methods
│   │   │   │   │   ├── deploy_config.py  # Deployment config
│   │   │   │   │   └── __main__.py       # Build entry point
│   │   │   │   └── artifacts/            # Compiled TEAL + ABI
│   │   │   │       └── pharma_clear/
│   │   │   │           ├── PharmaClear.approval.teal
│   │   │   │           ├── PharmaClear.arc56.json  # ABI spec
│   │   │   │           └── pharma_clear_client.py  # Auto-generated client
│   │   │   ├── tests/                    # 14 tests total
│   │   │   │   ├── pharma_clear_test.py
│   │   │   │   ├── pharma_clear_client_test.py
│   │   │   │   ├── test_client_submission.py   # Layer 1 tests
│   │   │   │   └── test_indexer_pipeline.py    # Layer 2 tests
│   │   │   ├── tools/                    # Layer 1 + 2 scripts
│   │   │   │   ├── submit_claim.py       # CLI for submitting claims
│   │   │   │   ├── indexer_query.py      # CLI for querying indexer
│   │   │   │   ├── README.md             # Detailed tool docs
│   │   │   │   └── __init__.py
│   │   │   ├── poetry.toml                # Python dependencies
│   │   │   ├── pyproject.toml
│   │   │   ├── .env.localnet              # LocalNet config
│   │   │   └── README.md                  # Contract-specific docs
│   │   ├── PharmaClear-frontend/         # Layer 3
│   │   │   ├── src/
│   │   │   │   ├── components/
│   │   │   │   │   ├── AppCalls.tsx      # Contract interaction UI
│   │   │   │   │   ├── ConnectWallet.tsx
│   │   │   │   │   └── ...
│   │   │   │   ├── contracts/
│   │   │   │   │   └── PharmaClear.ts    # Auto-generated client
│   │   │   │   ├── utils/
│   │   │   │   │   └── network/          # Algod config helpers
│   │   │   │   ├── App.tsx
│   │   │   │   └── main.tsx
│   │   │   ├── package.json               # npm dependencies
│   │   │   ├── vite.config.ts
│   │   │   ├── tsconfig.json
│   │   │   ├── .env.localnet              # Frontend LocalNet config
│   │   │   └── README.md
│   │   └── ... other projects
│   ├── .github/
│   │   └── workflows/                    # CI/CD pipelines
│   │       ├── build.yml
│   │       ├── test.yml
│   │       └── deploy.yml
│   ├── README.md                         # This file
│   └── PharmaClear.code-workspace        # VS Code workspace
```

---

## 🔧 Development Workflows

### Contract Development & Testing

```bash
cd projects/PharmaClear-contracts
source .venv/bin/activate

# Edit contract
nano smart_contracts/pharma_clear/contract.py

# Build
algokit project run build --project-name PharmaClear-contracts

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/pharma_clear_test.py::test_submit_claim_hash_returns_uint64 -v
```

### Submitting Claims

```bash
cd projects/PharmaClear-contracts
source .venv/bin/activate
source .env.localnet

# Submit single claim
python tools/submit_claim.py --claim "Claim text here"

# Submit from file
python tools/submit_claim.py --claim-file myclaim.txt

# Specify network & app
python tools/submit_claim.py \
  --claim "Claim" \
  --network testnet \
  --app 12345 \
  --sender-env DEPLOYER
```

### Querying Claims

```bash
# List all LocalNet claims
python tools/indexer_query.py --app 1234 --output claims.json

# Query specific rounds
python tools/indexer_query.py \
  --app 1234 \
  --min-round 1000 \
  --max-round 2000

# Save to SQLite
python tools/indexer_query.py --app 1234 --db claims.db

# Pretty-print
python tools/indexer_query.py --app 1234 --no-save | jq .
```

### Frontend Development

```bash
cd projects/PharmaClear-frontend

# Install dependencies
npm install

# Development server (with hot reload)
npm run dev

# Type check
npx tsc --noEmit

# Build for production
npm run build

# Run tests
npm test
```

---

## 🏗️ Architecture Details

### Layer 0: Smart Contract

**Contract**: `projects/PharmaClear-contracts/smart_contracts/pharma_clear/contract.py`

**ABI Methods** (7 total):

| Method | Input | Output | Readonly | Purpose |
|--------|-------|--------|----------|---------|
| `hello` | `name: String` | `String` | No | Test/demo method |
| `submit_claim` | `claim_hash: String` | `String` | No | Legacy method |  
| `verify_claim` | `claim_hash: String` | `String` | No | Legacy method |
| `submit_claim_hash` | `claim_hash: String` | `UInt64` | No | **[Layer 0]** Submit claim fingerprint, get ID |
| `get_last_claim_hash` | — | `String` | **Yes** | **[Layer 0]** Retrieve last claim hash |
| `get_claim_count` | — | `UInt64` | **Yes** | **[Layer 0]** Get total claims submitted |

**Current State**: Basic implementation (placeholders; ready for Box storage in future)  
**Deployment**: App ID generated on each `algokit deploy` (use latest ID)

### Layer 1: Claim Submission

**Script**: `projects/PharmaClear-contracts/tools/submit_claim.py`

**Features**:
- Compute SHA256 hash of claim from full text
- Call `submit_claim_hash` ABI method  
- Attach **full claim text in transaction note** (for Indexer)
- Auto-fund account from dispenser (localnet)
- Support localnet/testnet/mainnet

**CLI Usage**:
```bash
python tools/submit_claim.py --claim "Claim text..." [--app ID] [--network NET] [--sender-env VAR]
```

**Output**:
```json
{
  "claim_id": 1,
  "claim_hash": "a1b2c3d4...",
  "transaction_id": "TXID...",
  "sender": "ADDRESS...",
  "claim_text": "Full text..."
}
```

### Layer 2: Indexer-Based Archive

**Script**: `projects/PharmaClear-contracts/tools/indexer_query.py`

**Features**:
- Query Algorand Indexer for app-call transactions
- Decode note field → recover full claim text
- Extract ABI arguments → get claim hash
- Save to JSON or SQLite
- Filter by round range

**CLI Usage**:
```bash
python tools/indexer_query.py --app ID [--output FILE] [--db DB] [--no-save]
```

**Output** (JSON):
```json
{
  "exported_at": "2025-02-19T...",
  "claim_count": 2,
  "claims": [
    {
      "claim_id": 1,
      "claim_hash": "a1b2c3d4...",
      "claim_text": "Full text...",
      "transaction_id": "TXID...",
      "sender": "ADDRESS...",
      "block_round": 1234,
      "timestamp": 1692345678,
      "method": "submit_claim_hash"
    },
    ...
  ]
}
```

### Layer 3: Frontend React App

**Location**: `projects/PharmaClear-frontend`

**Key Components**:
- `ConnectWallet.tsx` - Pera/Defly/MyAlgo wallet integration
- `AppCalls.tsx` - Modal for calling contract methods
- `App.tsx` - Main app layout
- `PharmaClear.ts` - Auto-generated typed client from ARC-56

**Features**:
- Connect to LocalNet/TestNet wallets
- Call Layer 0 contract methods with proper ABI encoding
- Display responses
- (Future) Display claims from Layer 2 JSON/SQLite

---

## 🧪 Testing

### Run All Tests

```bash
cd projects/PharmaClear-contracts
source .venv/bin/activate
pytest tests/ -v
```

### Test Coverage

| Category | Tests | Status |
|----------|-------|--------|
| Contract (Layer 0) | 4 | ✅ Passing |
| Client Submission (Layer 1) | 3 | ✅ Passing |
| Indexer Pipeline (Layer 2) | 5 | ✅ Passing |
| Legacy/Client Compat | 2 | ✅ Passing |
| **Total** | **14** | **✅ All Passing** |

---

## 📝 Configuration

### Environment Variables

#### LocalNet (`.env.localnet`)

```bash
# Algod
ALGOD_SERVER=http://localhost
ALGOD_PORT=4001
ALGOD_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

# KMD (Key Management Daemon)
KMD_SERVER=http://localhost
KMD_PORT=4002
KMD_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
KMD_WALLET=unencrypted-default-wallet
KMD_PASSWORD=

# Indexer
INDEXER_SERVER=http://localhost
INDEXER_PORT=8980
INDEXER_TOKEN=
```

#### GitHub Actions Secrets (for CI/CD)

The following secrets must be configured in `.github/settings/secrets/actions`:

| Secret | Usage |
|--------|-------|
| `DEPLOYER_MNEMONIC` | Account that deploys contracts (testnet/mainnet) |
| `DISPENSER_MNEMONIC` | Account used to fund test accounts |
| `NETLIFY_AUTH_TOKEN` | Frontend deployment (if using Netlify) |

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

Located in `.github/workflows/`:

| Workflow | Trigger | Tasks |
|----------|---------|-------|
| `build.yml` | Push/PR | Build contracts + frontend |
| `test.yml` | Push/PR | Run all 14 tests |
| `deploy.yml` | Merge to main | Deploy to testnet/mainnet |

### Deploy to TestNet

```bash
# Locally (requires mnemonic in env var)
export DEPLOYER_MNEMONIC="word1 word2 ... word24"
export DISPENSER_MNEMONIC="word1 word2 ... word24"

algokit project deploy testnet --project-name PharmaClear-contracts
```

### Deploy to MainNet

Same as TestNet, but **verify outputs carefully**:

```bash
algokit project deploy mainnet --project-name PharmaClear-contracts
```

---

## 🎯 Next Steps & Enhancements

### Phase 2: Enhanced State Management
- [ ] Implement Box storage for claim history on-chain
- [ ] Add claim status tracking (pending, approved, rejected)
- [ ] Implement claim verification (re-hash and validate)

### Phase 3: API & Backend
- [ ] REST API for claim submission (Express.js)
- [ ] WebSocket listener for real-time claims
- [ ] CSV export for auditing

### Phase 4: Production Hardening
- [ ] Security audit (contract + frontend)
- [ ] Load testing with multiple submitters
- [ ] Testnet stress testing

### Phase 5: UI/UX
- [ ] Claims dashboard with search/filter
- [ ] Claim detail view with verification
- [ ] Transaction history alongside claims
- [ ] Mobile-responsive design

---

## 📚 Documentation

- **Contracts**: [projects/PharmaClear-contracts/README.md](projects/PharmaClear-contracts/README.md)
- **Tools**: [projects/PharmaClear-contracts/tools/README.md](projects/PharmaClear-contracts/tools/README.md)
- **Frontend**: [projects/PharmaClear-frontend/README.md](projects/PharmaClear-frontend/README.md)

---

## 🤝 Contributing

### Branch Convention

```
feature/<layer>-<description>  (e.g., feature/contract-layer0)
fix/<issue>-<description>
ci/<update>-<description>
```

### Commit Message Format

```
<type>(<scope>): <description>

<optional body>

Fixes #<issue-number>
```

Examples:
```
feat(contract): add submit_claim_hash method
fix(frontend): resolve wallet connection error
ci(workflows): update deploy to testnet
```

### Pull Request Checklist

- [ ] Tests pass locally (`pytest`, `npm test`)
- [ ] TypeScript type-checks (`npx tsc --noEmit`)
- [ ] Documentation updated
- [ ] Commits are atomic and well-described
- [ ] No console errors/warnings

---

## 🐛 Troubleshooting

### Issue: "App does not exist" error

**Cause**: Contract not deployed or old app ID.  
**Solution**:
```bash
# Redeploy and get new app ID
algokit project deploy localnet --project-name PharmaClear-contracts

# Update export
export PHARMA_CLEAR_APP_ID=<new-id>
```

### Issue: "Sender account balance too low"

**Cause**: Wallet not funded.  
**Solution**:
```bash
python projects/PharmaClear-contracts/tools/submit_claim.py --claim "test"
# Script auto-funds; if this fails, manually fund:
python -c "
from algokit_utils import AlgorandClient
client = AlgorandClient.from_environment()
client.account.ensure_funded_from_environment(
  account_to_fund='ACCOUNT_ADDRESS',
  min_spending_balance=AlgoAmount.from_algo(1),
  dispenser_account_name='DISPENSER'
)
"
```

### Issue: "Indexer is behind" or "No transactions found"

**Cause**: Indexer indexing lag or different network.  
**Solution**:
```bash
# Wait for indexer to catchup (usually 5-10 seconds)
sleep 10

# Verify app ID is correct
export PHARMA_CLEAR_APP_ID=$(algokit project run deploy-info | grep 'App ID')

# Try with round range
python tools/indexer_query.py --app $PHARMA_CLEAR_APP_ID --max-round 999999
```

### Issue: TypeScript errors in frontend

**Cause**: Client code out of sync with contract ABI.  
**Solution**:
```bash
# Regenerate client from latest contract
cd projects/PharmaClear-frontend
npm run generate:app-clients

# Or manually rebuild contracts first
cd ../PharmaClear-contracts
algokit project run build --project-name PharmaClear-contracts
```

---

## 📞 Support & Contact

- **Issues**: GitHub Issues on this repo
- **Discussions**: GitHub Discussions
- **Documentation**: See linked READMEs above

---

## 📄 License

[Specify your license here - MIT, Apache 2.0, etc.]

---

**Happy blockchain building! 🚀**
