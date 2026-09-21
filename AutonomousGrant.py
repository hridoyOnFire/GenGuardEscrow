from genlayer import *

@gl_contract
class AutonomousGrant:
    grantor: Address
    applicant: Address
    grant_amount: u256
    github_repo: str
    min_score_required: u256
    approved: bool

    def __init__(self, applicant: Address, github_repo: str, min_score: u256):
        self.grantor = gl.message.sender
        self.applicant = applicant
        self.grant_amount = gl.message.value
        self.github_repo = github_repo
        self.min_score_required = min_score
        self.approved = False

    @gl_public
    def evaluate_and_fund(self) -> None:
        assert gl.message.sender == self.grantor, "Only grantor can trigger evaluation"
        assert not self.approved, "Grant already approved"

        prompt = f"""
        Evaluate the code quality, completeness, and activity of the GitHub repository: {self.github_repo}
        Rate the project on a scale of 1 to 100 based on documentation, commit frequency, and code architecture.
        Respond with ONLY an integer number between 1 and 100.
        """
        
        score_str = gl.exec_prompt(prompt).strip()
        score = int(score_str) if score_str.isdigit() else 0

        if score >= self.min_score_required:
            self.approved = True
            gl.transfer(self.applicant, self.grant_amount)
