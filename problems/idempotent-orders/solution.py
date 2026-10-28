REJECTED = "rejected"


class OrderService:
    def __init__(self, stock=None):
        self.stock = None if stock is None else dict(stock)
        self.results = {}  # (user_id, key) -> (request, outcome)
        self.orders = {}   # order_id -> {"item", "quantity", "status"}

    def place_order(self, user_id, key, item, quantity):
        scope = (user_id, key)
        request = (item, quantity)
        # 1. Read: has this key been seen before?
        if scope in self.results:
            seen, outcome = self.results[scope]
            # 2. Judge: same key must mean the same request.
            if seen != request:
                raise ValueError(f"key {key!r} was used for a different request")
            return outcome
        # 3. Process once, then record the outcome under the key.
        if self.stock is not None and self.stock.get(item, 0) < quantity:
            outcome = REJECTED
        else:
            if self.stock is not None:
                self.stock[item] -= quantity
            outcome = f"order-{len(self.orders) + 1}"
            self.orders[outcome] = {"item": item, "quantity": quantity, "status": "placed"}
        self.results[scope] = (request, outcome)
        return outcome

    def order_count(self):
        return len(self.orders)

    def get_stock(self, item):
        return self.stock.get(item, 0)

    def restock(self, item, quantity):
        self.stock[item] = self.stock.get(item, 0) + quantity

    def cancel(self, order_id):
        order = self.orders.get(order_id)
        if order is None:
            return False
        if order["status"] == "placed":
            order["status"] = "cancelled"
            if self.stock is not None:
                self.stock[order["item"]] = self.stock.get(order["item"], 0) + order["quantity"]
        return True

    def status(self, order_id):
        if order_id not in self.orders:
            raise KeyError(order_id)
        return self.orders[order_id]["status"]
