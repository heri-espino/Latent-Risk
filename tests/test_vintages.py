"""Release-date handling must not peek into future publications."""
import pandas as pd
import pytest

from latent_risk.data import available_as_of, validate_long_panel


@pytest.fixture
def panel():
    return pd.DataFrame(
        [
            dict(country="MEX", observation_date="2020-01-31",
                 available_date="2020-02-07", variable="m2", value=123.4, source="Banxico"),
            dict(country="MEX", observation_date="2020-02-29",
                 available_date="2020-03-07", variable="m2", value=125.0, source="Banxico"),
        ]
    )


def test_vintage_filter_hides_unpublished(panel):
    assert available_as_of(panel, "2020-01-31").empty
    assert len(available_as_of(panel, "2020-02-07")) == 1


def test_nonmonotone_release_rejected(panel):
    panel.loc[0, "available_date"] = "2020-01-01"
    with pytest.raises(ValueError, match="precede"):
        validate_long_panel(panel)


def test_duplicate_rejected(panel):
    with pytest.raises(ValueError, match="duplicate"):
        validate_long_panel(pd.concat([panel, panel.iloc[[0]]], ignore_index=True))


def test_future_observation_does_not_leak(panel):
    early = available_as_of(panel, "2020-02-15")
    assert len(early) == 1
    assert float(early.iloc[0]["value"]) == 123.4
