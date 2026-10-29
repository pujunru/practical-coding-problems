class Gantt:
    def __init__(self):
        pass

    def add_task(self, name: str, duration: int, depends_on: list[str]) -> None:
        raise NotImplementedError

    def start(self, name: str) -> int:
        raise NotImplementedError

    def finish(self, name: str) -> int:
        raise NotImplementedError

    def length(self) -> int:
        raise NotImplementedError

    def set_duration(self, name: str, duration: int) -> None:
        """Level 2."""
        raise NotImplementedError

    def add_dependency(self, name: str, dep: str) -> bool:
        """Level 2."""
        raise NotImplementedError

    def slack(self, name: str) -> int:
        """Level 2."""
        raise NotImplementedError

    def critical(self) -> list[str]:
        """Level 2."""
        raise NotImplementedError

    def schedule(self, workers: int) -> list[list]:
        """Level 3."""
        raise NotImplementedError
