class Job:
    def __init__(self, size, priority, seq):
        self.size = size
        self.priority = priority
        self.seq = seq
        self.state = "queued"
        self.skips = 0
        self.started = -1  # start counter, for picking the most recent eviction

    def key(self):
        return (-self.priority, self.seq)


class GangScheduler:
    def __init__(self, gpus, max_skips=None):
        self.gpus = gpus
        self.free_gpus = gpus
        self.max_skips = max_skips
        self.jobs = {}
        self.starts = 0

    def _get(self, job):
        if job not in self.jobs:
            raise KeyError(job)
        return self.jobs[job]

    def _queue(self):
        return sorted((j for j in self.jobs.values() if j.state == "queued"), key=Job.key)

    def _blocked(self, j):
        return self.max_skips is not None and j.skips >= self.max_skips

    def _start(self, j):
        for q in self.jobs.values():
            if q.state == "queued" and q is not j and q.key() < j.key():
                q.skips += 1
        j.state = "running"
        j.started = self.starts
        self.starts += 1
        self.free_gpus -= j.size

    def _pass(self):
        names = {id(j): n for n, j in self.jobs.items()}
        started, passed = [], []
        for j in self._queue():
            if any(self._blocked(p) for p in passed):
                break
            if j.size <= self.free_gpus:
                self._start(j)
                started.append(names[id(j)])
            else:
                passed.append(j)
        return started

    def submit(self, job, size, priority=0):
        if job in self.jobs:
            raise ValueError(f"job {job} already submitted")
        if size < 1 or size > self.gpus:
            raise ValueError("size must be between 1 and the cluster size")
        j = self.jobs[job] = Job(size, priority, len(self.jobs))
        self._pass()
        if j.state == "queued" and size > self.free_gpus:
            victims = [v for v in self.jobs.values() if v.state == "running" and v.priority < priority]
            if self.free_gpus + sum(v.size for v in victims) >= size:
                for v in sorted(victims, key=lambda v: (v.priority, -v.started)):
                    if self.free_gpus >= size:
                        break
                    v.state = "queued"
                    self.free_gpus += v.size
                self._start(j)
                self._pass()
        return j.state == "running"

    def finish(self, job):
        j = self._get(job)
        if j.state != "running":
            raise ValueError(f"job {job} is not running")
        j.state = "done"
        self.free_gpus += j.size
        return self._pass()

    def status(self, job):
        return self._get(job).state

    def free(self):
        return self.free_gpus

    def running(self):
        return sorted(n for n, j in self.jobs.items() if j.state == "running")

    def skips(self, job):
        return self._get(job).skips
