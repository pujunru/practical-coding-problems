class Bank:
    def __init__(self):
        self.balance = {}      # account -> current balance
        self.outgoing = {}     # account -> total successfully sent
        self.history = {}      # account -> [(time, balance or None)]
        self.pending = []      # [exec_time, seq, payment_id, account, amount]
        self.owner = {}        # payment_id -> account, while pending
        self.next_payment = 1

    # ---- helpers
    def _record(self, account, t):
        self.history.setdefault(account, []).append((t, self.balance.get(account)))

    def _process(self, t):
        due = sorted(p for p in self.pending if p[0] <= t)
        self.pending = [p for p in self.pending if p[0] > t]
        for exec_time, _, pid, _, amount in due:
            account = self.owner.pop(pid)
            if self.balance[account] >= amount:
                self.balance[account] -= amount
                self.outgoing[account] += amount
                self._record(account, exec_time)

    # ---- level 1
    def create_account(self, timestamp, account_id):
        self._process(timestamp)
        if account_id in self.balance:
            return False
        self.balance[account_id] = 0
        self.outgoing[account_id] = 0
        self._record(account_id, timestamp)
        return True

    def deposit(self, timestamp, account_id, amount):
        self._process(timestamp)
        if account_id not in self.balance:
            return None
        self.balance[account_id] += amount
        self._record(account_id, timestamp)
        return self.balance[account_id]

    def transfer(self, timestamp, source_id, target_id, amount):
        self._process(timestamp)
        if (source_id == target_id or source_id not in self.balance
                or target_id not in self.balance or self.balance[source_id] < amount):
            return None
        self.balance[source_id] -= amount
        self.balance[target_id] += amount
        self.outgoing[source_id] += amount
        self._record(source_id, timestamp)
        self._record(target_id, timestamp)
        return self.balance[source_id]

    # ---- level 2
    def top_spenders(self, timestamp, n):
        self._process(timestamp)
        ranked = sorted(self.outgoing.items(), key=lambda kv: (-kv[1], kv[0]))
        return [f"{account}({total})" for account, total in ranked[:n]]

    # ---- level 3
    def schedule_payment(self, timestamp, account_id, amount, delay):
        self._process(timestamp)
        if account_id not in self.balance:
            return None
        pid = f"payment{self.next_payment}"
        self.pending.append([timestamp + delay, self.next_payment, pid, account_id, amount])
        self.owner[pid] = account_id
        self.next_payment += 1
        return pid

    def cancel_payment(self, timestamp, account_id, payment_id):
        self._process(timestamp)
        if self.owner.get(payment_id) != account_id:
            return False
        del self.owner[payment_id]
        self.pending = [p for p in self.pending if p[2] != payment_id]
        return True

    # ---- level 4
    def merge_accounts(self, timestamp, account_id_1, account_id_2):
        self._process(timestamp)
        if (account_id_1 == account_id_2 or account_id_1 not in self.balance
                or account_id_2 not in self.balance):
            return False
        self.balance[account_id_1] += self.balance.pop(account_id_2)
        self.outgoing[account_id_1] += self.outgoing.pop(account_id_2)
        for pid, account in self.owner.items():
            if account == account_id_2:
                self.owner[pid] = account_id_1
        self._record(account_id_1, timestamp)
        self._record(account_id_2, timestamp)  # balance is now None: gone
        return True

    def get_balance(self, timestamp, account_id, time_at):
        self._process(timestamp)
        result = None
        for t, balance in self.history.get(account_id, []):
            if t > time_at:
                break
            result = balance
        return result
