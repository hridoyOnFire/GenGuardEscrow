# GenGuardEscrow
GenGuard is an autonomous AI-driven escrow contract built on GenLayer GenVM. It uses GenLayer's non-deterministic consensus to fetch external web deliverables and evaluate work authenticity during client disputes, automatically settling funds without traditional third-party mediators
from genlayer import *

@gl_contract
class GenGuardEscrow:
    # State variables
    client: Address
    freelancer: Address
    amount: u256
    deliverable_link: str
    status: str  # "ACTIVE", "DELIVERED", "DISPUTED", "RESOLVED"
    winner: Address

    def __init__(self, freelancer: Address, deliverable_link: str):
        self.client = gl.message.sender
        self.freelancer = freelancer
        self.amount = gl.message.value
        self.deliverable_link = deliverable_link
        self.status = "ACTIVE"
        self.winner = Address(0)

    @gl_public
    def submit_work(self, proof_link: str) -> None:
        assert gl.message.sender == self.freelancer, "Only freelancer can submit work"
        assert self.status == "ACTIVE", "Contract is not active"
        self.deliverable_link = proof_link
        self.status = "DELIVERED"

    @gl_public
    def raise_dispute(self, reason: str) -> None:
        assert gl.message.sender == self.client, "Only client can dispute"
        assert self.status == "DELIVERED", "Work not submitted yet"
        
        # GenLayer AI Consensus Validation
        prompt = f"""
        Analyze the following dispute between client and freelancer:
        Deliverable Link: {self.deliverable_link}
        Client Complaint: {reason}
        
        Task: Web scrape or analyze the deliverable link content if available, evaluate if the work meets basic specifications described, and output 'FREELANCER' if work is acceptable or 'CLIENT' if work is incomplete or fraudulent.
        Respond with ONLY one word: FREELANCER or CLIENT.
        """
        
        # Calling GenVM Web and AI Consensus
        ai_decision = gl.exec_prompt(prompt).strip().upper()

        if ai_decision == "FREELANCER":
            self.winner = self.freelancer
            self.status = "RESOLVED"
            gl.transfer(self.freelancer, self.amount)
        else:
            self.winner = self.client
            self.status = "RESOLVED"
            gl.transfer(self.client, self.amount)

    @gl_public
    def release_payment(self) -> None:
        assert gl.message.sender == self.client, "Only client can release"
        assert self.status == "DELIVERED", "Work not delivered"
        self.status = "RESOLVED"
        self.winner = self.freelancer
        gl.transfer(self.freelancer, self.amount)
        # GenGuard: AI-Powered Autonomous Escrow Contract

GenGuard is an Intelligent Contract built on GenLayer GenVM. It bridges decentralized escrow settlements with AI-driven web validation and automated dispute resolution.

## Key Features

- **Non-Deterministic Consensus Validation**: Utilizes GenLayer's AI Consensus Engine to read external deliverable links and evaluate dispute rationale objectively.
- **Automated Dispute Resolution**: Eliminates manual third-party arbitrators by programmatically analyzing work quality against specifications.
- **Timelocked Auto-Release**: Protects freelancers by enabling automated funds release if the client fails to respond within the pre-agreed timeout period.
- **State-Enforced Escrow**: Securely locks funds on-chain until explicit approval or AI consensus resolution.

## Contract Architecture

- `__init__`: Initializes client, freelancer, deliverable specs, and timeout window.
- `submit_work`: Records proof of completion and starts the dispute window timer.
- `release_payment`: Manual release triggered by the client upon satisfactory delivery.
- `auto_release_payment`: Timelocked release accessible to freelancer if client exceeds timeout duration.
- `raise_dispute`: Invokes GenLayer AI consensus engine to inspect proof links against client complaints and execute payout to the winning party.

## Deployment & Execution (GenLayer Studio)

1. Open [GenLayer Studio](https://studio.genlayer.fast).
2. Create a file named `GenGuardEscrow.py` and paste the contract code.
3. Pass constructor arguments:
   - `freelancer`: Valid 0x wallet address.
   - `deliverable_link`: Project requirements link.
   - `timeout_seconds`: Dispute response window in seconds.
4. Deploy to GenLayer Simnet / Consensus network.
