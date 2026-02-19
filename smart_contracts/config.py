"""
PharmaClear Contract Compilation Configuration
This file is used by AlgoKit to compile the smart contracts.
"""

# Contract compilation settings
CONTRACTS = [
    {
        "name": "ClaimIngestionContract",
        "path": "smart_contracts/layer0_ingestion.py",
        "description": "Layer 0: Claim submission and duplicate prevention",
    },
    {
        "name": "RebateEngineContract",
        "path": "smart_contracts/layer1_rebate.py",
        "description": "Layer 1: Tiered rebate calculation engine",
    },
    {
        "name": "EscrowSettlementContract",
        "path": "smart_contracts/layer2_escrow.py",
        "description": "Layer 2: Atomic settlement with inner transactions",
    },
    {
        "name": "AuditRailContract",
        "path": "smart_contracts/layer3_audit.py",
        "description": "Layer 3: Regulatory compliance and audit trails",
    },
]

# Network configuration
NETWORKS = {
    "localnet": {
        "algod_url": "http://localhost:4001",
        "algod_token": "a" * 64,
        "indexer_url": "http://localhost:8980",
        "indexer_token": "a" * 64,
    },
    "testnet": {
        "algod_url": "https://testnet-api.algonode.cloud",
        "algod_token": "",
        "indexer_url": "https://testnet-idx.algonode.cloud",
        "indexer_token": "",
    },
    "mainnet": {
        "algod_url": "https://mainnet-api.algonode.cloud",
        "algod_token": "",
        "indexer_url": "https://mainnet-idx.algonode.cloud",
        "indexer_token": "",
    },
}

# Deployment configuration
DEPLOYMENT_CONFIG = {
    "layer0": {
        "app_name": "PharmaClear-Layer0-Ingestion",
        "updatable": False,  # Immutable for security
        "deletable": False,  # Permanent deployment
    },
    "layer1": {
        "app_name": "PharmaClear-Layer1-Rebate",
        "updatable": True,  # Allow schedule updates
        "deletable": False,
    },
    "layer2": {
        "app_name": "PharmaClear-Layer2-Escrow",
        "updatable": False,  # Settlement logic must be immutable
        "deletable": False,
    },
    "layer3": {
        "app_name": "PharmaClear-Layer3-Audit",
        "updatable": False,  # Audit trail must be tamper-proof
        "deletable": False,
    },
}
