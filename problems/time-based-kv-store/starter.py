class TimeMap:
    def __init__(self):
        pass

    # Levels 1-2
    def set(self, key: str, value: str, timestamp: int) -> None:
        raise NotImplementedError

    def get(self, key: str, timestamp: int) -> str | None:
        raise NotImplementedError

    # Level 3
    def delete(self, key: str, timestamp: int) -> bool:
        raise NotImplementedError

    # Level 4
    def keys_at(self, timestamp: int) -> list[str]:
        raise NotImplementedError

    def history(self, key: str, start: int, end: int) -> list[str]:
        raise NotImplementedError
