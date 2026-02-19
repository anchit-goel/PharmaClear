"""
PharmaClear Layer 4: DAO Governance Contract
Decentralized governance for dispute resolution, fee adjustments, and oracle management.
"""

from algopy import (
    ARC4Contract,
    BoxMap,
    Global,
    Txn,
    UInt64,
    arc4,
)


class GovernanceContract(ARC4Contract):
    """
    DAO Governance Layer - Community-driven protocol management.

    Features:
    - Dispute resolution voting
    - Fee adjustment proposals
    - Oracle selection and removal
    - Protocol parameter changes
    - Treasury management
    """

    # Proposal tracking
    proposals: BoxMap[arc4.UInt64, arc4.String]  # proposal_id -> metadata
    proposal_votes: BoxMap[arc4.UInt64, arc4.UInt64]  # proposal_id -> yes_votes
    proposal_votes_against: BoxMap[arc4.UInt64, arc4.UInt64]  # proposal_id -> no_votes
    proposal_status: BoxMap[arc4.UInt64, arc4.String]  # proposal_id -> status

    # Voting power (stake-weighted)
    voter_power: BoxMap[arc4.Address, arc4.UInt64]  # address -> voting_power
    voter_history: BoxMap[arc4.Address, arc4.DynamicArray[arc4.UInt64]]  # address -> proposal_ids

    # Oracle registry
    approved_oracles: BoxMap[arc4.Address, arc4.Bool]
    oracle_reputation: BoxMap[arc4.Address, arc4.UInt64]  # address -> reputation_score

    # Dispute registry
    disputes: BoxMap[arc4.DynamicBytes, arc4.String]  # claim_key -> dispute_metadata
    dispute_resolutions: BoxMap[arc4.DynamicBytes, arc4.String]  # claim_key -> resolution

    # Fee adjustment history
    fee_proposals: BoxMap[arc4.UInt64, arc4.UInt64]  # proposal_id -> proposed_fee_bps

    # Governance parameters
    proposal_counter: arc4.UInt64
    quorum_threshold: arc4.UInt64  # Minimum votes needed
    approval_threshold: arc4.UInt64  # % yes votes needed

    def __init__(self) -> None:
        """Initialize governance contract"""
        self.proposals = BoxMap(arc4.UInt64, arc4.String)
        self.proposal_votes = BoxMap(arc4.UInt64, arc4.UInt64)
        self.proposal_votes_against = BoxMap(arc4.UInt64, arc4.UInt64)
        self.proposal_status = BoxMap(arc4.UInt64, arc4.String)
        self.voter_power = BoxMap(arc4.Address, arc4.UInt64)
        self.voter_history = BoxMap(arc4.Address, arc4.DynamicArray[arc4.UInt64])
        self.approved_oracles = BoxMap(arc4.Address, arc4.Bool)
        self.oracle_reputation = BoxMap(arc4.Address, arc4.UInt64)
        self.disputes = BoxMap(arc4.DynamicBytes, arc4.String)
        self.dispute_resolutions = BoxMap(arc4.DynamicBytes, arc4.String)
        self.fee_proposals = BoxMap(arc4.UInt64, arc4.UInt64)

        self.proposal_counter = arc4.UInt64(0)
        self.quorum_threshold = arc4.UInt64(10000)  # Initial: 10,000 votes
        self.approval_threshold = arc4.UInt64(6667)  # 66.67% approval needed

    @arc4.abimethod
    def initialize_governance(
        self,
        quorum: arc4.UInt64,
        approval_pct: arc4.UInt64,
    ) -> arc4.String:
        """
        Initialize governance parameters.

        Args:
            quorum: Minimum total votes needed
            approval_pct: Percentage for approval (in basis points, 6667 = 66.67%)

        Returns:
            status: Confirmation
        """
        assert approval_pct.native <= 10000, "Approval cannot exceed 100%"
        assert approval_pct.native >= 5000, "Approval must be at least 50%"

        self.quorum_threshold = quorum
        self.approval_threshold = approval_pct

        arc4.emit("GovernanceInitialized", quorum, approval_pct)

        return arc4.String("Governance initialized")

    @arc4.abimethod
    def create_proposal(
        self,
        proposal_type: arc4.String,
        description: arc4.String,
        target_value: arc4.UInt64,
    ) -> arc4.UInt64:
        """
        Create a governance proposal.

        Args:
            proposal_type: "FEE_ADJUSTMENT", "ORACLE_ADD", "DISPUTE_RESOLUTION", etc.
            description: Detailed proposal description
            target_value: Proposed value (fee in bps, oracle address, etc.)

        Returns:
            proposal_id: Unique proposal identifier
        """
        # Increment proposal counter
        proposal_id = arc4.UInt64(self.proposal_counter.native + 1)
        self.proposal_counter = proposal_id

        # Store proposal metadata
        metadata = arc4.String(
            f'{{"type":"{proposal_type.native}",'
            f'"description":"{description.native}",'
            f'"value":{target_value.native},'
            f'"proposer":"{Txn.sender}",'
            f'"timestamp":{Global.latest_timestamp}}}'
        )
        self.proposals[proposal_id] = metadata
        self.proposal_status[proposal_id] = arc4.String("ACTIVE")

        # Initialize vote counters
        self.proposal_votes[proposal_id] = arc4.UInt64(0)
        self.proposal_votes_against[proposal_id] = arc4.UInt64(0)

        # Store fee proposal if applicable
        if proposal_type.native == "FEE_ADJUSTMENT":
            self.fee_proposals[proposal_id] = target_value

        # Emit proposal created event
        arc4.emit(
            "ProposalCreated",
            proposal_id,
            proposal_type,
            arc4.Address(Txn.sender),
            arc4.UInt64(Global.latest_timestamp),
        )

        return proposal_id

    @arc4.abimethod
    def vote(
        self,
        proposal_id: arc4.UInt64,
        vote_yes: arc4.Bool,
        vote_power: arc4.UInt64,
    ) -> arc4.String:
        """
        Cast vote on a proposal.

        Args:
            proposal_id: Proposal to vote on
            vote_yes: True for yes, False for no
            vote_power: Voting power (based on stake)

        Returns:
            status: Vote confirmation
        """
        voter = arc4.Address(Txn.sender)

        # Verify proposal exists and is active
        assert proposal_id in self.proposal_status, "Proposal not found"
        assert self.proposal_status[proposal_id].native == "ACTIVE", "Proposal not active"

        # Verify voting power (in production, check staked tokens)
        assert vote_power.native > 0, "No voting power"

        # Record vote
        if vote_yes.native:
            current_yes = self.proposal_votes.get(proposal_id, arc4.UInt64(0))
            self.proposal_votes[proposal_id] = arc4.UInt64(
                current_yes.native + vote_power.native
            )
        else:
            current_no = self.proposal_votes_against.get(proposal_id, arc4.UInt64(0))
            self.proposal_votes_against[proposal_id] = arc4.UInt64(
                current_no.native + vote_power.native
            )

        # Track voter history
        if voter not in self.voter_history:
            self.voter_history[voter] = arc4.DynamicArray[arc4.UInt64]()

        history = self.voter_history[voter]
        history.append(proposal_id)
        self.voter_history[voter] = history

        # Emit vote event
        arc4.emit("VoteCast", proposal_id, voter, vote_yes, vote_power)

        return arc4.String("Vote recorded")

    @arc4.abimethod
    def finalize_proposal(
        self,
        proposal_id: arc4.UInt64,
    ) -> arc4.String:
        """
        Finalize a proposal and execute if passed.

        Args:
            proposal_id: Proposal to finalize

        Returns:
            result: PASSED, REJECTED, or QUORUM_NOT_MET
        """
        assert proposal_id in self.proposal_status, "Proposal not found"
        assert self.proposal_status[proposal_id].native == "ACTIVE", "Already finalized"

        yes_votes = self.proposal_votes.get(proposal_id, arc4.UInt64(0)).native
        no_votes = self.proposal_votes_against.get(proposal_id, arc4.UInt64(0)).native
        total_votes = yes_votes + no_votes

        # Check quorum
        if total_votes < self.quorum_threshold.native:
            self.proposal_status[proposal_id] = arc4.String("QUORUM_NOT_MET")
            arc4.emit("ProposalFinalized", proposal_id, arc4.String("QUORUM_NOT_MET"))
            return arc4.String("Quorum not met")

        # Calculate approval percentage
        approval_pct = (yes_votes * 10000) // total_votes

        if approval_pct >= self.approval_threshold.native:
            self.proposal_status[proposal_id] = arc4.String("PASSED")

            # Execute proposal (in production, trigger parameter changes)
            arc4.emit(
                "ProposalPassed",
                proposal_id,
                arc4.UInt64(yes_votes),
                arc4.UInt64(approval_pct),
            )

            return arc4.String("Proposal PASSED")
        else:
            self.proposal_status[proposal_id] = arc4.String("REJECTED")
            arc4.emit("ProposalRejected", proposal_id, arc4.UInt64(approval_pct))
            return arc4.String("Proposal REJECTED")

    @arc4.abimethod
    def register_oracle(
        self,
        oracle_addr: arc4.Address,
        initial_reputation: arc4.UInt64,
    ) -> arc4.String:
        """
        Register a new oracle (requires governance approval in production).

        Args:
            oracle_addr: Oracle's Algorand address
            initial_reputation: Starting reputation score (0-1000)

        Returns:
            status: Registration confirmation
        """
        # In production: assert governance proposal passed

        self.approved_oracles[oracle_addr] = arc4.Bool(True)
        self.oracle_reputation[oracle_addr] = initial_reputation

        arc4.emit("OracleRegistered", oracle_addr, initial_reputation)

        return arc4.String("Oracle registered")

    @arc4.abimethod
    def slash_oracle(
        self,
        oracle_addr: arc4.Address,
        slash_amount: arc4.UInt64,
        reason: arc4.String,
    ) -> arc4.String:
        """
        Reduce oracle reputation for misbehavior.

        Args:
            oracle_addr: Oracle to penalize
            slash_amount: Reputation points to remove
            reason: Reason for slashing

        Returns:
            status: Slashing confirmation
        """
        # Requires governance vote in production

        current_rep = self.oracle_reputation.get(oracle_addr, arc4.UInt64(0)).native
        new_rep = 0 if current_rep < slash_amount.native else current_rep - slash_amount.native

        self.oracle_reputation[oracle_addr] = arc4.UInt64(new_rep)

        # Remove oracle if reputation too low
        if new_rep < 100:
            self.approved_oracles[oracle_addr] = arc4.Bool(False)
            arc4.emit("OracleRemoved", oracle_addr, reason)

        arc4.emit("OracleSlashed", oracle_addr, arc4.UInt64(new_rep), reason)

        return arc4.String(f"Oracle slashed: new reputation {new_rep}")

    @arc4.abimethod
    def file_dispute(
        self,
        claim_key: arc4.DynamicBytes,
        dispute_reason: arc4.String,
        disputed_amount: arc4.UInt64,
    ) -> arc4.String:
        """
        File a dispute for a claim settlement.

        Args:
            claim_key: Claim being disputed
            dispute_reason: Reason for dispute
            disputed_amount: Amount in question

        Returns:
            status: Dispute filed confirmation
        """
        disputer = arc4.Address(Txn.sender)

        metadata = arc4.String(
            f'{{"disputer":"{disputer}",'
            f'"reason":"{dispute_reason.native}",'
            f'"amount":{disputed_amount.native},'
            f'"timestamp":{Global.latest_timestamp}}}'
        )

        self.disputes[claim_key] = metadata

        arc4.emit(
            "DisputeFiled",
            claim_key,
            disputer,
            dispute_reason,
            disputed_amount,
        )

        return arc4.String("Dispute filed - awaiting governance vote")

    @arc4.abimethod(readonly=True)
    def get_proposal_status(
        self,
        proposal_id: arc4.UInt64,
    ) -> arc4.String:
        """
        Get current status of a proposal.

        Args:
            proposal_id: Proposal to query

        Returns:
            status: Current proposal status
        """
        if proposal_id not in self.proposal_status:
            return arc4.String("NOT_FOUND")

        return self.proposal_status[proposal_id]

    @arc4.abimethod(readonly=True)
    def get_vote_count(
        self,
        proposal_id: arc4.UInt64,
    ) -> arc4.String:
        """
        Get vote counts for a proposal.

        Args:
            proposal_id: Proposal to query

        Returns:
            counts: JSON with yes/no vote counts
        """
        yes_votes = self.proposal_votes.get(proposal_id, arc4.UInt64(0)).native
        no_votes = self.proposal_votes_against.get(proposal_id, arc4.UInt64(0)).native

        return arc4.String(f'{{"yes":{yes_votes},"no":{no_votes}}}')
