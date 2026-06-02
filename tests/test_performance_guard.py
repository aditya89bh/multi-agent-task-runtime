from benchmarks.performance_guard import compare_performance


def test_performance_guard_allows_minor_variance():
    baseline = {"suite": {"events_per_second": 1000, "regression_threshold": 0.5}}
    result = {"suite": {"events_per_second": 700}}

    assert compare_performance(result, baseline)["passed"] is True


def test_performance_guard_fails_large_regressions():
    baseline = {"suite": {"events_per_second": 1000, "regression_threshold": 0.5}}
    result = {"suite": {"events_per_second": 400}}

    comparison = compare_performance(result, baseline)

    assert comparison["passed"] is False
    assert comparison["failures"][0]["metric"] == "events_per_second"
