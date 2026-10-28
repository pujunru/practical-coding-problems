class InMemoryDB:
    def __init__(self):
        self.data = {}     # key -> {field: (value, expires_at or None)}
        self.backups = []  # [(time, {key: {field: (value, remaining ttl or None)}})]

    def _live(self, key, t):
        fields = self.data.get(key, {})
        return {f: v for f, (v, exp) in fields.items() if t is None or exp is None or t < exp}

    def _format(self, fields, prefix=""):
        return [f"{f}({v})" for f, v in sorted(fields.items()) if f.startswith(prefix)]

    # ---- level 1
    def set(self, key, field, value):
        self.set_at(key, field, value, None)

    def get(self, key, field):
        return self.get_at(key, field, None)

    def delete(self, key, field):
        return self.delete_at(key, field, None)

    # ---- level 2
    def scan(self, key):
        return self._format(self._live(key, None))

    def scan_by_prefix(self, key, prefix):
        return self._format(self._live(key, None), prefix)

    # ---- level 3
    def set_at(self, key, field, value, timestamp):
        self.data.setdefault(key, {})[field] = (value, None)

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        self.data.setdefault(key, {})[field] = (value, timestamp + ttl)

    def get_at(self, key, field, timestamp):
        return self._live(key, timestamp).get(field)

    def delete_at(self, key, field, timestamp):
        if field not in self._live(key, timestamp):
            return False
        del self.data[key][field]
        return True

    def scan_at(self, key, timestamp):
        return self._format(self._live(key, timestamp))

    def scan_by_prefix_at(self, key, prefix, timestamp):
        return self._format(self._live(key, timestamp), prefix)

    # ---- level 4
    def backup(self, timestamp):
        snapshot = {}
        for key, fields in self.data.items():
            live = {f: (v, None if exp is None else exp - timestamp)
                    for f, (v, exp) in fields.items() if exp is None or timestamp < exp}
            if live:
                snapshot[key] = live
        self.backups.append((timestamp, snapshot))
        return len(snapshot)

    def restore(self, timestamp, timestamp_to_restore):
        chosen = None
        for t, snapshot in self.backups:
            if t <= timestamp_to_restore:
                chosen = snapshot
        self.data = {
            key: {f: (v, None if rem is None else timestamp + rem) for f, (v, rem) in fields.items()}
            for key, fields in (chosen or {}).items()
        }
