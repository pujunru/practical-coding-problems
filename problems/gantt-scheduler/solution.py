import heapq


class Gantt:
    def __init__(self):
        self.duration = {}
        self.deps = {}        # task -> set of tasks it waits for
        self.dependents = {}  # task -> set of tasks waiting for it

    def add_task(self, name, duration, depends_on):
        if name in self.duration:
            raise ValueError(f"task {name} already exists")
        if any(d not in self.duration for d in depends_on):
            raise ValueError("unknown dependency")
        if duration < 1:
            raise ValueError("duration must be at least 1")
        self.duration[name] = duration
        self.deps[name] = set(depends_on)
        self.dependents[name] = set()
        for d in depends_on:
            self.dependents[d].add(name)

    def _check(self, name):
        if name not in self.duration:
            raise KeyError(name)

    def _order(self):
        """Tasks in dependency order (Kahn's algorithm, names sorted for stability)."""
        waiting = {t: len(self.deps[t]) for t in self.duration}
        ready = sorted(t for t, n in waiting.items() if not n)
        order = []
        while ready:
            t = ready.pop()
            order.append(t)
            for nxt in self.dependents[t]:
                waiting[nxt] -= 1
                if not waiting[nxt]:
                    ready.append(nxt)
        return order

    def _earliest(self):
        start = {}
        for t in self._order():
            start[t] = max((start[d] + self.duration[d] for d in self.deps[t]), default=0)
        return start

    def _tails(self):
        tail = {}
        for t in reversed(self._order()):
            tail[t] = self.duration[t] + max((tail[n] for n in self.dependents[t]), default=0)
        return tail

    def start(self, name):
        self._check(name)
        return self._earliest()[name]

    def finish(self, name):
        return self.start(name) + self.duration[name]

    def length(self):
        start = self._earliest()
        return max((start[t] + self.duration[t] for t in start), default=0)

    def set_duration(self, name, duration):
        self._check(name)
        if duration < 1:
            raise ValueError("duration must be at least 1")
        self.duration[name] = duration

    def _reaches(self, src, dst):
        """Whether dst is src or depends on it, directly or indirectly."""
        stack, seen = [src], {src}
        while stack:
            t = stack.pop()
            if t == dst:
                return True
            for n in self.dependents[t]:
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
        return False

    def add_dependency(self, name, dep):
        self._check(name)
        self._check(dep)
        if self._reaches(name, dep):
            return False
        self.deps[name].add(dep)
        self.dependents[dep].add(name)
        return True

    def slack(self, name):
        self._check(name)
        # Latest start is length - tail: the task's tail must fit before the end.
        return self.length() - self._tails()[name] - self._earliest()[name]

    def critical(self):
        start, tail, end = self._earliest(), self._tails(), self.length()
        return sorted((t for t in start if start[t] + tail[t] == end), key=lambda t: (start[t], t))

    def schedule(self, workers):
        if workers < 1:
            raise ValueError("workers must be at least 1")
        tail = self._tails()
        waiting = {t: len(self.deps[t]) for t in self.duration}
        ready = [(-tail[t], t) for t, n in waiting.items() if not n]
        heapq.heapify(ready)
        running = []  # (finish, name)
        result, day = [], 0
        while ready or running:
            while ready and len(running) < workers:
                _, t = heapq.heappop(ready)
                result.append([t, day, day + self.duration[t]])
                heapq.heappush(running, (day + self.duration[t], t))
            day = running[0][0]
            while running and running[0][0] == day:
                _, t = heapq.heappop(running)
                for n in self.dependents[t]:
                    waiting[n] -= 1
                    if not waiting[n]:
                        heapq.heappush(ready, (-tail[n], n))
        return sorted(result, key=lambda r: (r[1], r[0]))
