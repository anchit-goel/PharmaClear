from algopy import ARC4Contract, String, UInt64
from algopy.arc4 import abimethod


class PharmaClear(ARC4Contract):
    """
    PharmaClear - A pharmaceutical supply chain contract.
    
    Layer 0: Claim Ingestion
    Tracks incoming pharmaceutical claims with fingerprints (SHA256 hashes).
    
    This layer provides the core ABI interface for:
    - Submitting claim hashes (SHA256 of full claim text)
    - Retrieving claim metadata
    
    Full claim text is stored in transaction notes for Indexer/Conduit to capture.
    
    Methods:
    - hello: Legacy test method (for backward compatibility)
    - submit_claim & verify_claim: Legacy methods (transitioning to Layer 0)
    - submit_claim_hash: Core Layer 0 method to submit claim fingerprint
    - get_last_claim_hash: Core Layer 0 method (read-only)
    - get_claim_count: Core Layer 0 method (read-only)
    """

    @abimethod()
    def hello(self, name: String) -> String:
        """
        Greet caller by name (temporary test method).
        
        Args:
            name: Name to greet
        
        Returns:
            Greeting string
        """
        return "Hello, " + name

    @abimethod()
    def submit_claim(self, claim_hash: String) -> String:
        """
        Legacy method: Submit a claim (will be phased out).
        Use submit_claim_hash instead.
        """
        return "Claim submitted with hash: " + claim_hash

    @abimethod()
    def verify_claim(self, claim_hash: String) -> String:
        """
        Legacy method: Verify a claim (will be phased out).
        Use get_last_claim_hash instead.
        """
        return "Claim verified: " + claim_hash

    @abimethod()
    def submit_claim_hash(self, claim_hash: String) -> UInt64:
        """
        Submit a claim fingerprint (SHA256 hash).
        
        Full claim text must be included in the transaction note field
        so that Indexer and Conduit can capture it alongside this hash.
        
        Args:
            claim_hash: SHA256 hash of the complete claim text (typically 64-char hex string)
        
        Returns:
            UInt64: Unique claim ID (proof of ingestion)
        
        On-chain behavior:
        - Increments global claim counter
        - Stores the hash as the most recent claim
        - Returns the new claim ID
        """
        # Layer 0 basic implementation - returns success indicator
        # Full state management with counter + history will be in Box storage
        return UInt64(1)

    @abimethod(readonly=True)
    def get_last_claim_hash(self) -> String:
        """
        Retrieve the most recently submitted claim hash.
        
        Returns:
            String: The last claim hash submitted, or empty string if none
        """
        # Layer 0 basic implementation - returns placeholder
        # Full state will be read from Box storage in Layer 1
        return String("")

    @abimethod(readonly=True)
    def get_claim_count(self) -> UInt64:
        """
        Retrieve the total number of claims submitted so far.
        
        Returns:
            UInt64: Total claim count
        """
        # Layer 0 basic implementation - returns placeholder
        # Full state will be read from Box storage in Layer 1
        return UInt64(0)