# PharmaClear Contract Tools

## Overview

This directory contains tools for submitting and querying pharmaceutical claims across all three layers:

- **Layer 1**: Claim submission (submit_claim.py)
- **Layer 2**: Indexer-based claim retrieval (indexer_query.py)
- **Layer 3**: Frontend integration (see frontend README)

## Installation

Ensure you're in the contracts project venv:

```bash
cd projects/PharmaClear-contracts
source .venv/bin/activate
```

All tools use AlgoKit utils (installed via Poetry).

---

# Layer 1: Claim Submission Client

## Usage

### Basic Submission (LocalNet)

```bash
python tools/submit_claim.py --claim "Full claim text here..."
```

### With Claim File

```bash
python tools/submit_claim.py --claim-file path/to/claim.txt
```

### Specify Network and Account

```bash
# TestNet with specific app ID
python tools/submit_claim.py \
  --claim "Claim text..." \
  --network testnet \
  --app 12345 \
  --sender-env DEPLOYER

# MainNet with key file
python tools/submit_claim.py \
  --claim "Claim text..." \
  --network mainnet \
  --sender-key /path/to/account.json \
  --app 99999
```

### Help

```bash
python tools/submit_claim.py --help
```

## Features

### Hash Computation
- Uses Python's `hashlib.sha256()` to compute cryptographically secure claim fingerprints
- Produces 64-character hex strings
- Deterministic: same claim always produces same hash

### Transaction Structure
- **ABI Method**: `submit_claim_hash(claim_hash: String) -> UInt64`
- **Claim Hash**: SHA256 of full claim text (passed as ABI argument)
- **Full Claim**: Attached in transaction note field (raw bytes)
  
This separation allows:
- Indexer/Conduit to capture full claim via note field
- On-chain contract to store hash for immutability verification

### Environment Variables

Essential for script operation:

| Variable | Usage | Example |
|----------|-------|---------|
| `ALGOD_SERVER` | Algod endpoint | `http://localhost` |
| `ALGOD_PORT` | Algod port | `4001` |
| `ALGOD_TOKEN` | Algod token | `aaaaaaaaaa...` |
| `DEPLOYER` | Sender account credentials | Base64-encoded account |
| `DISPENSER` | Funding account (localnet) | Base64-encoded account |
| `PHARMA_CLEAR_APP_ID` | Contract app ID | `1234` |

### LocalNet Setup

For local testing, ensure LocalNet is running:

```bash
# Start LocalNet (in another terminal)
algokit localnet start

# Source the localnet .env file
source projects/PharmaClear-contracts/.env.localnet

# Export app ID if set
export PHARMA_CLEAR_APP_ID=1234

# Run submit script
python tools/submit_claim.py --claim "Test claim"
```

## Example Workflow

```bash
# Terminal 1: Start localnet
algokit localnet start

# Terminal 2: Navigate to contracts
cd projects/PharmaClear-contracts
source .venv/bin/activate
source .env.localnet

# Build and deploy contract
algokit project run build --project-name PharmaClear-contracts
algokit project deploy localnet --project-name PharmaClear-contracts

# Extract app ID from deploy output
# Then set it
export PHARMA_CLEAR_APP_ID=<app-id-from-deploy>

# Submit a test claim
python tools/submit_claim.py --claim "Test pharmaceutical claim for patient X"

# Output will show:
# ✅ Claim submitted successfully!
#    Claim ID: 1
#    Transaction ID: <txn-id>
#    Sender: <account-address>
```

## Output

The script returns a JSON object with:
- `claim_id`: UInt64 returned from contract
- `claim_hash`: SHA256 hash submitted (64-char hex)
- `transaction_id`: Algorand transaction ID
- `sender`: Account address that submitted
- `claim_text`: Full claim text (for reference)

Example:
```json
{
  "claim_id": 1,
  "claim_hash": "a1b2c3d4ef5f...",
  "transaction_id": "AAAA...ZZZZ",
  "sender": "AAAAAAAAAAA...BBBBBBBBBB",
  "claim_text": "Full pharmaceutical claim details..."
}
```

## Testing

Run client submission tests:

```bash
cd projects/PharmaClear-contracts
pytest tests/test_client_submission.py -v
```

## Architecture

### Layer 0 Contract Methods

- `submit_claim_hash(claim_hash: String) -> UInt64`
  - Called by this client
  - Returns unique claim ID
  - On-chain state: increment counter, store hash
  
- `get_last_claim_hash() -> String`
  - Read-only getter for most recent hash
  
- `get_claim_count() -> UInt64`
  - Read-only getter for total submitted claims

### Data Flow

```
User Input (claim text)
    ↓
compute_claim_hash() [SHA256]
    ↓
submit_claim() [AlgorandClient call]
    ├─ ABI arg: claim_hash
    └─ Txn note: full claim text
    ↓
PharmaClear contract
    ├─ Stores hash on-chain
    └─ Returns claim_id
    ↓
Indexer captures txn + note
    ↓
Indexer listener (Layer 2) reads both hash + full text
```

---

# Layer 2: Indexer-Based Claim Pipeline

Query and parse pharmaceutical claims from the Algorand Indexer.

## Overview

`indexer_query.py` is a tool for:
- Querying the Algorand Indexer for application call transactions
- Extracting claim hashes from ABI arguments  
- Extracting full claim texts from transaction notes
- Storing claims to JSON files or SQLite databases
- Filtering by round range and other criteria

## Purpose

While Layer 1 submits claims via the contract, Layer 2 reads them back out from the blockchain:
- **Indexer**: Captures full application call transactions (including notes)
- **This tool**: Parses transaction data to reconstruct claims
- **Integration**: Enables frontend to display claim history without on-chain storage

## Usage

### Basic Query (LocalNet)

```bash
python tools/indexer_query.py --app 1234
```

### Save to JSON

```bash
python tools/indexer_query.py --app 1234 --output claims.json
```

### Save to SQLite

```bash
python tools/indexer_query.py --app 1234 --db claims.db
```

### Query Specific Round Range

```bash
python tools/indexer_query.py --app 1234 --min-round 1000 --max-round 2000
```

### Print to stdout (no file save)

```bash
python tools/indexer_query.py --app 1234 --no-save | jq
```

### Help

```bash
python tools/indexer_query.py --help
```

## Output Format

### JSON Output

```json
{
  "exported_at": "2025-02-19T10:30:45.123456",
  "claim_count": 2,
  "claims": [
    {
      "claim_id": 1,
      "claim_hash": "a1b2c3d4ef5f...",
      "claim_text": "Full pharmaceutical claim for patient X...",
      "transaction_id": "AAAA...ZZZZ",
      "sender": "AAAAAAAAAAA...BBBBBBBBBB",
      "block_round": 1234,
      "timestamp": 1692345678,
      "method": "submit_claim_hash"
    },
    ...
  ]
}
```

### SQLite Schema

```sql
CREATE TABLE claims (
  claim_id INTEGER PRIMARY KEY,
  claim_hash TEXT,
  claim_text TEXT,
  transaction_id TEXT UNIQUE,
  sender TEXT,
  block_round INTEGER,
  timestamp INTEGER,
  method TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Complete Workflow

```bash
# Terminal 1: Start localnet
algokit localnet start

# Terminal 2: Deploy contract
cd projects/PharmaClear-contracts
source .venv/bin/activate
source .env.localnet

algokit project run build --project-name PharmaClear-contracts
algokit project deploy localnet --project-name PharmaClear-contracts

# Extract app ID from deploy output
export PHARMA_CLEAR_APP_ID=<app-id>

# Terminal 3: Submit claims
python tools/submit_claim.py --claim "First claim..."
python tools/submit_claim.py --claim "Second claim..."
python tools/submit_claim.py --claim "Third claim..."

# Terminal 2 (same): Query claims from indexer
python tools/indexer_query.py --app $PHARMA_CLEAR_APP_ID --output claims.json

# View results
cat claims.json | jq .claims[0]
```

## Architecture

### Data Flow

```
Layer 1: submit_claim.py
├─ Takes claim text as input
├─ Computes SHA256 hash
├─ Calls contract via ABI
├─ Attaches full text in note field
└─ Returns claim ID

              ↓
        Algorand Network
        - Contract stores hash
        - Note captured by Conduit
        
              ↓
        Indexer (background)
        - Indexes all app calls
        - Archives transaction data
        - Maintains searchable queries

              ↓
Layer 2: indexer_query.py
├─ Queries indexer for app transactions  
├─ Extracts note field (claim text)
├─ Extracts ABI args (claim hash)
├─ Reconstructs claim object
└─ Exports to JSON/SQLite

              ↓
Layer 3: Frontend
├─ Reads from indexer output
├─ Displays claim history
└─ Allows verify/search
```

### Key Differences from On-Chain Storage

| Aspect | On-Chain | Indexer |
|--------|----------|---------|
| **Storage** | GlobalState / Boxes | Indexer database |
| **Cost** | MBR + state rent | Free (read) |
| **Latency** | Immediate | ~5-10 seconds |
| **History** | Limited (overwritten) | Unlimited archival |
| **Querying** | Limited (on-chain logic) | Rich queries |
| **Privacy** | Transparent | Same (all txns public) |

This design separates concerns:
- **Contract**: Proves claim acceptance (on-chain)
- **Indexer**: Archives full history (off-chain query)
- **Frontend**: Displays all claims (via indexer)

## Features

### Automatic Deduplication

Duplicate transactions are skipped (via UNIQUE constraint on transaction_id).

### Flexible Storage

- **JSON**: Portable, human-readable, easy to pipe to other tools
- **SQLite**: Queryable, transactional, good for large datasets
- **stdout**: Pipe to `jq`, grep, awk for further processing

### Filtering

- `--min-round` / `--max-round` for round range
- `--method` to filter by contract method name
- `--network` to switch between localnet/testnet/mainnet

## Integration with Layer 3 (Frontend)

The frontend can:
1. Call `indexer_query.py` as a server-side script
2. Read the output JSON file  
3. Query the SQLite database via API endpoint
4. Display all historical claims to users

## Testing

```bash
cd projects/PharmaClear-contracts
pytest tests/test_client_submission.py -v
```

## Future Enhancements

- [ ] Real-time claim listener (Conduit instead of polling Indexer)
- [ ] ABI argument decoding using arc56.json
- [ ] Claim verification (re-hash text and compare with stored hash)
- [ ] WebSocket listener for live claims
- [ ] CSV export option
- [ ] Prometheus metrics (claim counts, timing, etc.)

---

## Future Enhancements (All Layers)

- [ ] Box storage for claim history on-chain
- [ ] Batch claim submissions
- [ ] Claim status tracking
- [ ] Layer 2 → Layer 3 API endpoint
- [ ] Web/mobile frontend integration
- [ ] Claim auditing and verification
