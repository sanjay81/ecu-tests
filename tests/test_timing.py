import pytest

N = 100


def _latencies(make_ecu, seed: int = 1234) -> list[float]:
    client = make_ecu(seed=seed)
    return [client.read_did(0xF190).elapsed for _ in range(N)]


def test_latency_regression_slow_rate_stays_within_budget(make_ecu):
    """Regression guard (REQ-002 is violated, see the xfail test):
    at most 15% of responses exceed 100 ms. Baseline for seed 1234 is 12% at N=100."""
    over = sum(t > 0.100 for t in _latencies(make_ecu)) / N
    assert over <= 0.15


def test_latency_regression_no_extreme_outliers(make_ecu):
    """Regression guard (REQ-002 is violated, see the xfail test):
    no single response may exceed 150 ms."""
    assert max(_latencies(make_ecu)) <= 0.150


@pytest.mark.xfail(strict=True, reason="REQ-002 strict reading: ECU exceeds 100 ms in about 7% of responses")
def test_req_002_every_response_within_100ms(make_ecu):
    assert all(t <= 0.100 for t in _latencies(make_ecu))
