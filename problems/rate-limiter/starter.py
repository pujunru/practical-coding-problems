class RateLimiter:
    def __init__(self, limit: int, window: float, tiers: dict | None = None):
        # Level 4: tiers maps a tier name to (limit, window); limit None = unlimited.
        pass

    def allow(self, client_id: str, now: float, tier: str | None = None) -> bool:
        """Levels 1-2: is this request allowed? An allowed request is recorded."""
        raise NotImplementedError

    def retry_after(self, client_id: str, now: float, tier: str | None = None) -> float:
        """Level 3: seconds until a request would be allowed (0.0 if now)."""
        raise NotImplementedError

    def count(self, client_id: str) -> int:
        """Level 4: how many requests from this client have been allowed."""
        raise NotImplementedError
