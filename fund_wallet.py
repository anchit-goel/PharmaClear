#!/usr/bin/env python3
"""Fund a wallet account from LocalNet dispenser"""

import sys
from algokit_utils import AlgorandClient, AlgoAmount, PaymentParams

def fund_account(receiver_address: str, amount_algo: float = 10) -> None:
    """Fund an account from the LocalNet dispenser"""
    
    # Connect to LocalNet
    algorand = AlgorandClient.default_localnet()
    
    # Get dispenser account (this account has initial funds in LocalNet)
    dispenser = algorand.account.from_environment("DISPENSER")
    
    print(f"Dispenser: {dispenser.address}")
    print(f"Funding {receiver_address} with {amount_algo} ALGO...")
    
    # Send payment from dispenser to receiver
    result = algorand.send.payment(
        PaymentParams(
            sender=dispenser.address,
            receiver=receiver_address,
            amount=AlgoAmount.from_algo(amount_algo),
        )
    )
    
    print(f"✅ Successfully funded! Transaction ID: {result.tx_id}")
    print(f"Account {receiver_address} now has {amount_algo} ALGO")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fund_wallet.py <receiver_address> [amount_in_algo]")
        print("Example: python fund_wallet.py BBZCWNBBIV7Y3NRJB3JGWGCBZTV4UMSZU736M26AW7YWSN5NRERX57T36I 10")
        sys.exit(1)
    
    receiver = sys.argv[1]
    amount = float(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    fund_account(receiver, amount)
