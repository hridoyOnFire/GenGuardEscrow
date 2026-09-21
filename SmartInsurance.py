from genlayer import *

@gl_contract
class FlightInsurance:
    insured_user: Address
    flight_number: str
    flight_date: str
    premium_amount: u256
    payout_amount: u256
    claimed: bool

    def __init__(self, flight_number: str, flight_date: str, payout_amount: u256):
        self.insured_user = gl.message.sender
        self.flight_number = flight_number
        self.flight_date = flight_date
        self.premium_amount = gl.message.value
        self.payout_amount = payout_amount
        self.claimed = False

    @gl_public
    def claim_insurance(self) -> None:
        assert gl.message.sender == self.insured_user, "Only policyholder can claim"
        assert not self.claimed, "Already claimed"

        prompt = f"""
        Check the flight status for Flight Number: {self.flight_number} on Date: {self.flight_date}.
        Determine if the flight was delayed by more than 3 hours or canceled.
        Respond with ONLY 'YES' if delayed/canceled, or 'NO' if on time.
        """
        
        status_check = gl.exec_prompt(prompt).strip().upper()

        if status_check == "YES":
            self.claimed = True
            gl.transfer(self.insured_user, self.payout_amount)
