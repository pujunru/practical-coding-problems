import math

EXPIRE, ADD, CHARGE = 0, 1, 2  # order of events that share a timestamp


class CreditLedger:
    def __init__(self):
        self.events = []  # (timestamp, kind, seq, amount, expires_at)

    def _replay(self, until, stop_seq=None):
        """Replay events with time <= until in time order.

        Returns (balance at `until`, whether charge `stop_seq` succeeded).
        """
        timeline = []
        for t, kind, seq, amount, expires_at in self.events:
            timeline.append((t, kind, seq, amount, expires_at))
            if kind == ADD and expires_at is not None:
                timeline.append((expires_at, EXPIRE, seq, 0, None))
        timeline.sort(key=lambda e: (e[0], e[1], e[2]))

        grants = {}  # seq -> [remaining, expires_at or inf, start]
        verdict = None
        for t, kind, seq, amount, expires_at in timeline:
            if t > until:
                break
            if kind == EXPIRE:
                grants.pop(seq, None)
            elif kind == ADD:
                grants[seq] = [amount, math.inf if expires_at is None else expires_at, t]
            else:
                ok = sum(g[0] for g in grants.values()) >= amount
                if ok:
                    for g_seq in sorted(grants, key=lambda s: (grants[s][1], grants[s][2], s)):
                        used = min(amount, grants[g_seq][0])
                        grants[g_seq][0] -= used
                        amount -= used
                        if not grants[g_seq][0]:
                            del grants[g_seq]
                        if not amount:
                            break
                if seq == stop_seq:
                    verdict = ok
        return sum(g[0] for g in grants.values()), verdict

    def add(self, timestamp, amount, expires_at=None):
        self.events.append((timestamp, ADD, len(self.events), amount, expires_at))

    def charge(self, timestamp, amount):
        seq = len(self.events)
        self.events.append((timestamp, CHARGE, seq, amount, None))
        return self._replay(timestamp, seq)[1]

    def balance(self, timestamp):
        return self._replay(timestamp)[0]
