# Layer 1: Claim Submission Client

Tools for submitting pharmaceutical claims to the PharmaClear contract.

## Overview

`submit_claim.py` is a Python CLI tool for:
- Computing SHA256 hashes of claim documents
- Calling the PharmaClear contract's `submit_claim_hash` ABI method
- Attaching full claim text in transaction notes (for Indexer/Conduit)
- Automatically funding accounts from dispenser (localnet)
- Returning new claim IDs

## Installation

1. Ensure you're in the contracts project venv:
   ```bash
   cd projects/PharmaClear-contracts
   source .venv/bin/activate
   ```

2. The script requires AlgoKit utils (already installed by Poetry).

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

## Future Enhancements

- [ ] Box storage for claim history on-chain
- [ ] Batch claim submissions
- [ ] Claim status tracking
- [ ] Integration with Layer 2 Indexer listener
- [ ] Web/mobile frontend integration
