class Spreadsheet:
    def __init__(self):
        pass

    def set(self, cell: str, raw: str) -> None:
        raise NotImplementedError

    def get(self, cell: str) -> int | float | str:
        """Level 1: literals. Level 2: formulas. Level 3: dependencies and cycles.
        Level 4: SUM / MAX / MIN over ranges."""
        raise NotImplementedError
