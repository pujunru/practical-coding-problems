class InMemoryDB:
    def __init__(self):
        pass

    # Level 1
    def set(self, key: str, field: str, value: str) -> None:
        raise NotImplementedError

    def get(self, key: str, field: str) -> str | None:
        raise NotImplementedError

    def delete(self, key: str, field: str) -> bool:
        raise NotImplementedError

    # Level 2
    def scan(self, key: str) -> list[str]:
        raise NotImplementedError

    def scan_by_prefix(self, key: str, prefix: str) -> list[str]:
        raise NotImplementedError

    # Level 3
    def set_at(self, key: str, field: str, value: str, timestamp: int) -> None:
        raise NotImplementedError

    def set_at_with_ttl(self, key: str, field: str, value: str, timestamp: int, ttl: int) -> None:
        raise NotImplementedError

    def get_at(self, key: str, field: str, timestamp: int) -> str | None:
        raise NotImplementedError

    def delete_at(self, key: str, field: str, timestamp: int) -> bool:
        raise NotImplementedError

    def scan_at(self, key: str, timestamp: int) -> list[str]:
        raise NotImplementedError

    def scan_by_prefix_at(self, key: str, prefix: str, timestamp: int) -> list[str]:
        raise NotImplementedError

    # Level 4
    def backup(self, timestamp: int) -> int:
        raise NotImplementedError

    def restore(self, timestamp: int, timestamp_to_restore: int) -> None:
        raise NotImplementedError
