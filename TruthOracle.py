from genlayer import *

@gl_contract
class TruthOracle:
    question: str
    resolution_url: str
    outcome: str  # "TRUE", "FALSE", "PENDING"
    is_resolved: bool
    creator: Address

    def __init__(self, question: str, resolution_url: str):
        self.creator = gl.message.sender
        self.question = question
        self.resolution_url = resolution_url
        self.outcome = "PENDING"
        self.is_resolved = False

    @gl_public
    def resolve_market(self) -> None:
        assert not self.is_resolved, "Market already resolved"
        
        prompt = f"""
        Fact-check the following statement using live search and web content:
        Statement: "{self.question}"
        Reference Link: {self.resolution_url}

        Instructions: Search and evaluate reliable web sources to determine if the statement is TRUE or FALSE.
        Respond with ONLY ONE WORD: 'TRUE' or 'FALSE'.
        """
        
        result = gl.exec_prompt(prompt).strip().upper()
        
        if result in ["TRUE", "FALSE"]:
            self.outcome = result
            self.is_resolved = True
        else:
            self.outcome = "UNDETERMINED"

    @gl_public
    def get_result(self) -> str:
        return self.outcome
