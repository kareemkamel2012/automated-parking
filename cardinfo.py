class CardInfo:
    def __init__(self, type: str, number: str, exp_month: str, exp_year: str, cvn: str):
        if type not in ["Visa", "MasterCard", "Amex", "Discover"]:
            raise ValueError("Invalid card type")
        if len(exp_year) != 4:
            raise ValueError("Invalid expiration year - must be 4 digits")
        self.type = type
        self.number = number
        self.exp_month = exp_month
        self.exp_year = exp_year
        self.cvn = cvn
