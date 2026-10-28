class OrderService:
    def __init__(self, stock: dict | None = None):
        # Level 2: stock maps item -> units on hand; None means unlimited.
        pass

    def place_order(self, user_id: str, key: str, item: str, quantity: int) -> str:
        """Level 1: create an order once per idempotency key; return its id."""
        raise NotImplementedError

    def order_count(self) -> int:
        """Level 1: how many orders have actually been created."""
        raise NotImplementedError

    def get_stock(self, item: str) -> int:
        """Level 2."""
        raise NotImplementedError

    def restock(self, item: str, quantity: int) -> None:
        """Level 2."""
        raise NotImplementedError

    def cancel(self, order_id: str) -> bool:
        """Level 4: cancel an order; safe to retry."""
        raise NotImplementedError

    def status(self, order_id: str) -> str:
        """Level 4: "placed" or "cancelled"."""
        raise NotImplementedError
