# PharmaClear Deployment Guide

## 📋 Prerequisites

Before deploying PharmaClear, ensure you have:

1. **AlgoKit Installed**
   ```bash
   # macOS
   brew install algorandfoundation/tap/algokit

   # Windows/Linux
   pipx install algokit
   ```

2. **Docker Running** (for LocalNet)
   ```bash
   docker --version  # Should show version 20.x or higher
   ```

3. **Python 3.10+**
   ```bash
   python --version  # Should show 3.10 or higher
   ```

4. **Dependencies Installed**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Deployment Steps

### Option 1: LocalNet (Development)

#### Step 1: Start LocalNet
```bash
algokit localnet start
```

**Verify LocalNet is running:**
```bash
algokit localnet status
# Expected: algod, indexer, and postgres containers running
```

#### Step 2: Compile Contracts
```bash
# Navigate to project root
cd PharmaClear

# Compile all contracts
algokit compile python smart_contracts/layer0_ingestion.py
algokit compile python smart_contracts/layer1_rebate.py
algokit compile python smart_contracts/layer2_escrow.py
algokit compile python smart_contracts/layer3_audit.py
```

**Generated Artifacts:**
- `*.approval.teal` - Approval program
- `*.clear.teal` - Clear state program
- `*.arc32.json` - ABI specification

#### Step 3: Run Demo Flow
```bash
python scripts/demo_flow.py
```

**Expected Terminal Output:**
```
🏗️  PharmaClear Demo Initialization
Deployer: ABCD1234...
Manufacturer: EFGH5678...
Pharmacy: IJKL9012...

💵 Creating Test USDCa Asset...
✅ Created USDCa Asset ID: 1001

🚀 Deploying Smart Contracts...
✅ Layer 0 Deployed (App ID: 1002)
✅ Layer 1 Deployed (App ID: 1003)
✅ Layer 2 Deployed (App ID: 1004)
✅ Layer 3 Deployed (App ID: 1005)

⚛️  Executing Atomic Settlement Transaction Group...
✅ Atomic Settlement Complete

💰 Pharmacy Received: $97.00 USDCa
```

---

### Option 2: TestNet (Pre-Production)

#### Step 1: Fund Your Deployer Account
```bash
# Get your deployer address
algokit goal account list

# Visit TestNet dispenser
# https://bank.testnet.algorand.network/
# Request 100 ALGO for your deployer address
```

#### Step 2: Set TestNet Environment Variables
```bash
export ALGOD_TOKEN=""
export ALGOD_SERVER="https://testnet-api.algonode.cloud"
export INDEXER_SERVER="https://testnet-idx.algonode.cloud"
```

#### Step 3: Deploy to TestNet
```bash
# Modify demo_flow.py to use TestNet client
python scripts/demo_flow.py
```

**Important Notes:**
- TestNet transactions are permanent
- TestNet resets periodically (check Algorand docs)
- Use TestNet USDCa (not real USDC)

---

### Option 3: MainNet (Production)

⚠️ **CRITICAL: DO NOT DEPLOY TO MAINNET WITHOUT FULL AUDIT**

Production deployment requires:
1. **Security Audit:** External smart contract audit
2. **Oracle Integration:** Replace dummy oracle with production-grade solution
3. **Real USDC:** Integrate with actual USDCa (Asset ID: 31566704)
4. **Regulatory Review:** Legal compliance verification
5. **Insurance:** Smart contract insurance policy

**MainNet Deployment Checklist:**
- [ ] All contracts audited by reputable firm
- [ ] Oracle service SLA in place
- [ ] Multi-sig deployment keys
- [ ] Emergency pause mechanism tested
- [ ] Comprehensive test coverage (>90%)
- [ ] Legal opinion obtained
- [ ] Bug bounty program launched

---

## 🔧 Manual Deployment (Advanced)

If you need fine-grained control:

### Deploy Layer 0 (Claim Ingestion)
```bash
algokit goal app create \
  --creator $DEPLOYER_ADDR \
  --approval-prog smart_contracts/artifacts/layer0_ingestion.approval.teal \
  --clear-prog smart_contracts/artifacts/layer0_ingestion.clear.teal \
  --global-byteslices 0 \
  --global-ints 0 \
  --local-byteslices 0 \
  --local-ints 0 \
  --extra-pages 3
```

### Fund Layer 2 Escrow
```bash
# Get Layer 2 app address
ESCROW_ADDR=$(algokit goal app info --app-id $LAYER2_APP_ID | grep "Application account" | awk '{print $3}')

# Transfer USDCa to escrow
algokit goal asset send \
  --from $MANUFACTURER_ADDR \
  --to $ESCROW_ADDR \
  --assetid $USDC_ASSET_ID \
  --amount 1000000000  # $1,000 USDCa
```

---

## 📊 Verifying Deployment

### Check Contract State
```bash
# Layer 0: Check claim count
algokit goal app read --app-id $LAYER0_APP_ID --global

# Layer 1: Check rebate schedules
algokit goal app read --app-id $LAYER1_APP_ID --global

# Layer 2: Check escrow balance
algokit goal account info --address $ESCROW_ADDR
```

### Query Events (via Indexer)
```bash
# Get all ClaimSubmitted events
curl "http://localhost:8980/v2/applications/$LAYER0_APP_ID/logs"

# Get settlement events
curl "http://localhost:8980/v2/applications/$LAYER2_APP_ID/logs"
```

### Run Integration Tests
```bash
pytest tests/integration/test_full_flow.py -v
```

---

## 🐛 Troubleshooting

### Issue: "Box reference not found"
**Solution:** Increase box budget in transaction parameters:
```python
sp = algod_client.suggested_params()
sp.boxes = [[app_id, claim_key]]  # Add box references
```

### Issue: "Logic eval error: assert failed"
**Cause:** Oracle signature validation failed

**Solution:** Verify atomic group structure:
```python
# Transaction 0 MUST be oracle auth
# Transaction 1 MUST reference txn index 0
```

### Issue: "Insufficient balance"
**Cause:** Escrow contract lacks USDCa

**Solution:** Fund escrow before settlement:
```bash
algokit goal asset send --from $MANUFACTURER --to $ESCROW_ADDR --amount 1000000000
```

---

## 📈 Performance Optimization

### Box Storage Costs
- Each box costs: **2,500 + 400 * num_bytes** microALGO
- Claim record (256 bytes): ~105,000 microALGO = **0.105 ALGO**
- 1,000 claims: ~105 ALGO in storage costs

### Transaction Fees
- Standard txn: 0.001 ALGO
- Atomic group (2 txns): 0.002 ALGO
- Inner txns: 0.001 ALGO each
- **Total settlement cost: ~0.004 ALGO** (~$0.0012 at $0.30/ALGO)

### Scaling Estimates
| Metric | Value |
|--------|-------|
| Claims/second | ~10 (LocalNet), ~5 (TestNet/MainNet) |
| Max claims/year | ~157M (theoretical) |
| Storage cost/1M claims | ~105,000 ALGO (~$31,500) |
| Settlement cost/claim | 0.004 ALGO (~$0.0012) |

---

## 🔒 Security Checklist

Before production deployment:

- [ ] All private keys stored in hardware wallet
- [ ] Multi-signature scheme for admin actions
- [ ] Rate limiting on claim submissions
- [ ] Oracle redundancy (3+ independent oracles)
- [ ] Emergency pause mechanism tested
- [ ] Formal verification of critical logic
- [ ] Penetration testing completed
- [ ] Bug bounty program active
- [ ] Insurance policy obtained
- [ ] Incident response plan documented

---

## 📞 Support

**Deployment Issues:**
- AlgoKit Docs: https://github.com/algorandfoundation/algokit-cli
- Discord: https://discord.gg/algorand

**Smart Contract Questions:**
- Algorand Developer Docs: https://developer.algorand.org/
- Stack Overflow: Tag `algorand`

---

## 📄 License

MIT License - See LICENSE file for details

Built for **RIFT 2026 Hackathon**
