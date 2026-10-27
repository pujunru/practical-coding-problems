from solution import RateLimiter

LEVELS = {1: "Single client", 2: "Many clients", 3: "Retry-after", 4: "Tiers"}


def close(a, b):
    return abs(a - b) < 1e-9


# ---------------------------------------------------------------- level 1

def test_l1_allows_up_to_limit():
    """Allows exactly limit requests, then rejects"""
    rl = RateLimiter(3, 10)
    got = [rl.allow("a", t) for t in (0, 1, 2, 3)]
    assert got == [True, True, True, False], f"expected [True, True, True, False], got {got}"


def test_l1_window_slides():
    """Old requests leave the window"""
    rl = RateLimiter(2, 10)
    got = [rl.allow("a", t) for t in (0, 5, 9, 10, 11, 15)]
    expected = [True, True, False, True, False, True]
    assert got == expected, f"times (0, 5, 9, 10, 11, 15): expected {expected}, got {got}"


def test_l1_window_start_is_exclusive():
    """A request exactly one window ago no longer counts"""
    rl = RateLimiter(1, 1)
    got = [rl.allow("a", t) for t in (0, 0.999, 1.0)]
    assert got == [True, False, True], f"times (0, 0.999, 1.0): expected [True, False, True], got {got}"


def test_l1_rejected_requests_do_not_count():
    """Rejected requests are not counted against the limit"""
    rl = RateLimiter(1, 10)
    got = [rl.allow("a", t) for t in (0, 5, 9, 10)]
    assert got == [True, False, False, True], f"times (0, 5, 9, 10): expected [True, False, False, True], got {got}"


def test_l1_same_instant():
    """Many requests at the same instant"""
    rl = RateLimiter(5, 1)
    got = sum(rl.allow("a", 0) for _ in range(7))
    assert got == 5, f"7 requests at t=0 with limit 5: expected 5 allowed, got {got}"


# ---------------------------------------------------------------- level 2

def test_l2_clients_are_isolated():
    """One client's burst does not block another"""
    rl = RateLimiter(2, 10)
    assert rl.allow("a", 0) and rl.allow("a", 0)
    assert not rl.allow("a", 1), "a has used its budget"
    assert rl.allow("b", 1), "b must not be affected by a"


def test_l2_independent_windows():
    """Each client has its own window"""
    rl = RateLimiter(1, 10)
    assert rl.allow("a", 0)
    assert rl.allow("b", 5)
    assert rl.allow("a", 10), "a's request at 0 has left a's window"
    assert not rl.allow("b", 10), "b's request at 5 is still in b's window"
    assert rl.allow("b", 15)


def test_l2_many_clients():
    """A thousand clients each get their own budget"""
    rl = RateLimiter(1, 60)
    allowed = sum(rl.allow(f"client-{i}", i * 0.001) for i in range(1000))
    assert allowed == 1000, f"expected 1000 allowed, got {allowed}"


# ---------------------------------------------------------------- level 3

def test_l3_zero_when_allowed():
    """retry_after is 0.0 when a request would be allowed"""
    rl = RateLimiter(2, 10)
    assert rl.retry_after("a", 0) == 0.0
    rl.allow("a", 0)
    assert rl.retry_after("a", 1) == 0.0


def test_l3_does_not_consume():
    """retry_after only looks; it does not count as a request"""
    rl = RateLimiter(1, 10)
    for _ in range(5):
        rl.retry_after("a", 0)
    assert rl.allow("a", 0), "retry_after must not use up the budget"


def test_l3_real_value():
    """retry_after is derived from the window, and is exact"""
    rl = RateLimiter(2, 10)
    rl.allow("a", 1)
    rl.allow("a", 4)
    wait = rl.retry_after("a", 6)
    assert close(wait, 5), f"requests at 1 and 4, window 10, asked at 6: expected 5, got {wait}"
    assert not rl.allow("a", 6 + wait - 0.01), "still too early just before retry_after"
    assert rl.allow("a", 6 + wait), "a request at now + retry_after must be allowed"


def test_l3_ignores_rejected():
    """Rejected requests do not push retry_after out"""
    rl = RateLimiter(1, 10)
    rl.allow("a", 0)
    rl.allow("a", 3)  # rejected
    wait = rl.retry_after("a", 3)
    assert close(wait, 7), f"expected 7, got {wait}"


def test_l3_per_client():
    """retry_after is per client"""
    rl = RateLimiter(1, 10)
    rl.allow("a", 0)
    assert close(rl.retry_after("a", 2), 8)
    assert rl.retry_after("b", 2) == 0.0


# ---------------------------------------------------------------- level 4

TIERS = {"free": (2, 10), "pro": (5, 10), "internal": (None, 10)}


def test_l4_tier_limits():
    """Each tier has its own limit"""
    rl = RateLimiter(1, 10, tiers=TIERS)
    free = sum(rl.allow("f", 0, tier="free") for _ in range(10))
    pro = sum(rl.allow("p", 0, tier="pro") for _ in range(10))
    default = sum(rl.allow("d", 0) for _ in range(10))
    assert (free, pro, default) == (2, 5, 1), f"expected (free, pro, default) = (2, 5, 1), got {(free, pro, default)}"


def test_l4_unlimited_is_counted():
    """An unlimited tier is always allowed but still counted"""
    rl = RateLimiter(1, 10, tiers=TIERS)
    assert all(rl.allow("svc", 0, tier="internal") for _ in range(100))
    assert rl.retry_after("svc", 0, tier="internal") == 0.0
    assert rl.count("svc") == 100, f"expected count 100, got {rl.count('svc')}"


def test_l4_count_only_allowed():
    """count() counts allowed requests only, across tiers"""
    rl = RateLimiter(1, 10, tiers=TIERS)
    for _ in range(3):
        rl.allow("a", 0, tier="free")
    rl.allow("a", 0, tier="internal")
    assert rl.count("a") == 3, f"2 free + 1 internal allowed: expected 3, got {rl.count('a')}"
    assert rl.count("nobody") == 0


def test_l4_tier_change_keeps_history():
    """History belongs to the client, not the tier"""
    rl = RateLimiter(1, 10, tiers=TIERS)
    assert rl.allow("a", 0, tier="free") and rl.allow("a", 1, tier="free")
    assert not rl.allow("a", 2, tier="free")
    assert rl.allow("a", 2, tier="pro"), "upgraded to pro: 2 of 5 used"
    assert not rl.allow("a", 3, tier="free"), "back on free: 3 requests already in the window"


def test_l4_tier_windows_differ():
    """A long-window tier still sees requests a short-window tier has forgotten"""
    rl = RateLimiter(1, 10, tiers={"burst": (1, 1.0), "slow": (1, 60)})
    assert rl.allow("a", 0, tier="slow")
    assert rl.allow("a", 2, tier="burst"), "burst only looks back 1s"
    assert not rl.allow("a", 30, tier="slow"), "slow still sees the requests at 0 and 2"
    wait = rl.retry_after("a", 30, tier="slow")
    assert close(wait, 32), f"most recent request at 2 leaves the 60s window at 62: expected 32, got {wait}"


def test_l4_unknown_tier():
    """An unknown tier raises ValueError"""
    rl = RateLimiter(1, 10, tiers=TIERS)
    try:
        rl.allow("a", 0, tier="gold")
    except ValueError:
        return
    raise AssertionError("allow(..., tier='gold') should raise ValueError")
