from bisect import bisect_right, insort

_DELETED = object()


class TimeMap:
    def __init__(self):
        self.times = {}   # key -> sorted timestamps
        self.values = {}  # key -> {timestamp: value or _DELETED}

    def _write(self, key, value, timestamp):
        versions = self.values.setdefault(key, {})
        if timestamp not in versions:
            insort(self.times.setdefault(key, []), timestamp)
        versions[timestamp] = value

    # ---- levels 1-2
    def set(self, key, value, timestamp):
        self._write(key, value, timestamp)

    def get(self, key, timestamp):
        times = self.times.get(key, [])
        i = bisect_right(times, timestamp)
        if not i:
            return None
        value = self.values[key][times[i - 1]]
        return None if value is _DELETED else value

    # ---- level 3
    def delete(self, key, timestamp):
        existed = self.get(key, timestamp) is not None
        self._write(key, _DELETED, timestamp)
        return existed

    # ---- level 4
    def keys_at(self, timestamp):
        return sorted(k for k in self.times if self.get(k, timestamp) is not None)

    def history(self, key, start, end):
        return [v for t in self.times.get(key, [])
                if start <= t <= end and (v := self.values[key][t]) is not _DELETED]
