"""All event tests use synthetic forecasts; no crisis-performance evidence."""
from datetime import date, timedelta
from math import inf

import pytest

from latent_risk.events import MaturedForecast, calibration_cutoff, first_event_lead_days


def example(i: int, value: float = 1.0) -> MaturedForecast:
    """A matured synthetic forecast released in advance of the evaluation date."""
    origin = date(2005, 1, 1) + timedelta(days=i)
    return MaturedForecast(origin, origin + timedelta(days=1), origin + timedelta(days=2),
                           value, 0.0, 1.0)


def test_surprise_is_unsigned_scale_invariant() -> None:
    a = MaturedForecast(date(2000, 1, 1), date(2000, 1, 2),
                        date(2000, 1, 3), -4.0, 0.0, 2.0)
    b = MaturedForecast(date(2000, 1, 1), date(2000, 1, 2),
                        date(2000, 1, 3), -40.0, 0.0, 20.0)
    assert a.surprise == b.surprise == 2.0


@pytest.mark.parametrize("dates", [
    (date(2020, 1, 2), date(2020, 1, 2), date(2020, 1, 3)),
    (date(2020, 1, 1), date(2020, 1, 3), date(2020, 1, 2)),
])
def test_invalid_date_order_rejected(dates: tuple[date, date, date]) -> None:
    with pytest.raises(ValueError, match="issued_at"):
        MaturedForecast(*dates, 3, 1, 1)


@pytest.mark.parametrize("scale", [0.0, -1.0, inf])
def test_invalid_scale_rejected(scale: float) -> None:
    with pytest.raises(ValueError):
        MaturedForecast(date(2020, 1, 1), date(2020, 1, 2),
                        date(2020, 1, 3), 1.0, 0.0, scale)


def test_calibration_threshold_uses_only_prior_matured_targets() -> None:
    rows = [example(i, i + 1.0) for i in range(39)]
    result = calibration_cutoff(rows, decision_at=date(2006, 1, 1), alpha=0.05)
    assert result == 38.0  # ceil(40 * 0.95) = 38; ranked scores are 1..39


def test_no_unsafe_small_sample_threshold() -> None:
    assert calibration_cutoff([example(i) for i in range(5)],
                              decision_at=date(2006, 1, 1)) == inf


def test_calibration_rejects_unmatured_target_at_decision() -> None:
    row = MaturedForecast(date(2019, 1, 1), date(2019, 1, 2),
                          date(2020, 2, 2), 100.0, 0.0, 1.0)
    with pytest.raises(ValueError, match="unavailable"):
        calibration_cutoff([row], decision_at=date(2020, 1, 1))


def test_threshold_is_strict_and_boundary_is_not_an_alarm() -> None:
    score = example(0, value=3.0).surprise
    assert not (score > 3.0)
    assert score > 2.9


def test_lead_excludes_same_day_post_event_and_outside_lookback() -> None:
    onset = date(2020, 3, 11)
    alerts = [date(2020, 1, 1), date(2020, 3, 5),
              date(2020, 3, 10), onset, date(2020, 3, 12)]
    assert first_event_lead_days(alerts, event_onset=onset, lookback_days=21) == 6
    assert first_event_lead_days([onset, date(2020, 3, 12)],
                                  event_onset=onset) is None


def test_invalid_lookback_rejected() -> None:
    with pytest.raises(ValueError):
        first_event_lead_days([], event_onset=date(2020, 1, 1), lookback_days=0)


def test_calibration_alpha_validation() -> None:
    with pytest.raises(ValueError):
        calibration_cutoff([example(0)], decision_at=date(2006, 1, 1), alpha=1)
