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
