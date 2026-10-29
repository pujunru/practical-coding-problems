class GangScheduler:
    def __init__(self, gpus: int, max_skips: int | None = None):
        """max_skips from Level 2."""
        pass

    def submit(self, job: str, size: int, priority: int = 0) -> bool:
        """priority from Level 3."""
        raise NotImplementedError

    def finish(self, job: str) -> list[str]:
        raise NotImplementedError

    def status(self, job: str) -> str:
        raise NotImplementedError

    def free(self) -> int:
        raise NotImplementedError

    def running(self) -> list[str]:
        raise NotImplementedError

    def skips(self, job: str) -> int:
        """Level 2."""
        raise NotImplementedError
