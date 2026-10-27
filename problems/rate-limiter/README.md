An internal API gateway fronts a handful of backend services. It has no rate
limiting, and one misbehaving client can starve everyone else. Build the rate
limiter the gateway calls on every request.

The limiter never reads a clock. Every call carries `now`, the current time in
seconds, and calls arrive with non-decreasing `now`.

## The rule

Use a **sliding window**. A request from a client at time `now` is allowed if
that client has had fewer than `limit` **allowed** requests in the half-open
interval `(now - window, now]`. Rejected requests are not counted.

```
limit = 2, window = 10

t=0   allow  → True      in window: [0]
t=5   allow  → True      in window: [0, 5]
t=9   allow  → False     in window: [0, 5]   (full)
t=10  allow  → True      in window: [5, 10]  (0 has left: 0 ≤ 10 - 10)
```

## Level 1 · Single client

```python
limiter = RateLimiter(limit=2, window=10)
limiter.allow("alice", 0)   # True
```

Implement `allow(client_id, now) -> bool` for one client.

## Level 2 · Many clients

Limits are per client. One client using up its budget must not affect any
other client.

## Level 3 · Retry-after

A rejected caller wants to know when to come back. Implement
`retry_after(client_id, now) -> float`:

- `0.0` if a request at `now` would be allowed;
- otherwise the smallest `t > 0` such that a request at `now + t` would be
  allowed.

`retry_after` only looks — it never counts as a request.

## Level 4 · Tiers

Clients are no longer equal. The constructor takes an optional `tiers` map from
tier name to `(limit, window)`, and `allow` and `retry_after` take an optional
`tier`:

```python
limiter = RateLimiter(2, 10, tiers={"free": (2, 10), "pro": (100, 60), "internal": (None, 60)})
limiter.allow("bob", 3, tier="pro")
```

- `tier=None` uses the constructor's `limit` and `window`.
- A limit of `None` means unlimited: always allowed, `retry_after` is `0.0`.
- An unknown tier raises `ValueError`.
- A client's tier can change between requests. History belongs to the client,
  not the tier: requests made under one tier count when the next request is
  judged under another tier's limit and window.
- `count(client_id) -> int` returns how many requests from that client have been
  allowed so far, across all tiers. Unlimited requests still count — the number
  feeds a dashboard.

## Notes

- Memory should not grow without bound for a client that keeps calling: forget
  timestamps no tier could still see.
- Think about where the limit decision lives. The cleanest Level 4 is a policy
  lookup, not an `if tier == ...` ladder inside the counting code.
