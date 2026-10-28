class Bank:
    def __init__(self):
        pass

    # Level 1
    def create_account(self, timestamp: int, account_id: str) -> bool:
        raise NotImplementedError

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        raise NotImplementedError

    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> int | None:
        raise NotImplementedError

    # Level 2
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        raise NotImplementedError

    # Level 3
    def schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str | None:
        raise NotImplementedError

    def cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool:
        raise NotImplementedError

    # Level 4
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        raise NotImplementedError

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        raise NotImplementedError
