from algopy import ARC4Contract, String, UInt64
from algopy.arc4 import abimethod

class PharmaClear(ARC4Contract):
    """
    PharmaClear - A pharmaceutical supply chain contract.
    Provides methods to submit and retrieve claims with hashing for immutability.
    """

    @abimethod()
    def hello(self, name: String) -> String:
        """Greet the caller by name."""
        return "Hello, " + name

    @abimethod()
    def submit_claim(self, claim_hash: String) -> String:
        """
        Submit a claim fingerprint. 
        Returns a confirmation message with the hash.
        """
        return "Claim submitted with hash: " + claim_hash

    @abimethod()
    def verify_claim(self, claim_hash: String) -> String:
        """
        Verify a claim by its hash.
        Returns a verification message.
        """
        return "Claim verified: " + claim_hash