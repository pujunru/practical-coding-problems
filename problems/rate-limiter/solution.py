from bisect import bisect_right
from collections import defaultdict


class RateLimiter:
    def __init__(self, limit, window, tiers=None):
        self.default = (limit, window)
        self.tiers = dict(tiers or {})
        self.horizon = max([window, *(w for _, w in self.tiers.values())])
        self.log = defaultdict(list)  # client -> sorted timestamps of allowed requests
        self.allowed = defaultdict(int)

    def _policy(self, tier):
        if tier is None:
            return self.default
        try:
            return self.tiers[tier]
        except KeyError:
            raise ValueError(f"unknown tier: {tier!r}") from None

    def _in_window(self, client_id, now, window):
        log = self.log[client_id]
        del log[: bisect_right(log, now - self.horizon)]  # nothing can see these any more
        return log[bisect_right(log, now - window):]

    def allow(self, client_id, now, tier=None):
        limit, window = self._policy(tier)
        recent = self._in_window(client_id, now, window)
        if limit is not None and len(recent) >= limit:
            return False
        self.log[client_id].append(now)
        self.allowed[client_id] += 1
        return True

    def retry_after(self, client_id, now, tier=None):
        limit, window = self._policy(tier)
        recent = self._in_window(client_id, now, window)
        if limit is None or len(recent) < limit:
            return 0.0
        return recent[-limit] + window - now

    def count(self, client_id):
        return self.allowed[client_id]
