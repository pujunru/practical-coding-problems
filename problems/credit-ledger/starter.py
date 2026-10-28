class CreditLedger:
    def __init__(self):
        pass

    def add(self, timestamp: int, amount: int, expires_at: int | None = None) -> None:
        """Level 1; expires_at from Level 2."""
        raise NotImplementedError

    def charge(self, timestamp: int, amount: int) -> bool:
        raise NotImplementedError

    def balance(self, timestamp: int) -> int:
        raise NotImplementedError
