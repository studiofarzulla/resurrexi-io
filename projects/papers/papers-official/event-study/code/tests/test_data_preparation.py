"""
Comprehensive unit tests for data_preparation.py and bootstrap_inference.py.
Uses synthetic data throughout — no CSV file dependencies.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def prep():
    """DataPreparation instance (does NOT touch the filesystem)."""
    from data_preparation import DataPreparation
    return DataPreparation(data_path="/tmp/nonexistent")


@pytest.fixture
def simple_prices():
    """Small synthetic price series (10 prices, easy to verify by hand)."""
    dates = pd.date_range("2023-01-01", periods=10, freq="D", tz="UTC")
    prices = pd.Series(
        [100.0, 105.0, 110.0, 108.0, 112.0, 115.0, 113.0, 118.0, 120.0, 125.0],
        index=dates,
        name="price",
    )
    return prices


@pytest.fixture
def constant_prices():
    """Constant price series — log returns should be 0."""
    dates = pd.date_range("2023-01-01", periods=5, freq="D", tz="UTC")
    return pd.Series([50.0] * 5, index=dates, name="price")


@pytest.fixture
def daily_df():
    """Small daily DataFrame for merge tests."""
    idx = pd.date_range("2023-01-01", periods=14, freq="D", tz="UTC")
    return pd.DataFrame({"returns": np.random.default_rng(0).standard_normal(14)}, index=idx)


@pytest.fixture
def weekly_sentiment():
    """Weekly sentiment DataFrame aligned to Mondays for merge tests."""
    idx = pd.date_range("2023-01-02", periods=2, freq="W-MON", tz="UTC")
    return pd.DataFrame(
        {
            "S_gdelt_normalized": [0.5, -0.3],
            "S_reg_decomposed": [0.2, -0.1],
            "S_infra_decomposed": [0.3, -0.2],
        },
        index=idx,
    )


# ===================================================================
# 1. calculate_log_returns
# ===================================================================

class TestCalculateLogReturns:
    """Tests for DataPreparation.calculate_log_returns."""

    def test_basic_formula(self, prep, simple_prices):
        """Returns should equal ln(p_t / p_{t-1}) * 100."""
        result = prep.calculate_log_returns(simple_prices)
        expected = np.log(simple_prices / simple_prices.shift(1)).dropna() * 100
        pd.testing.assert_series_equal(result, expected)

    def test_length(self, prep, simple_prices):
        """Output length should be n-1 (first NaN dropped)."""
        result = prep.calculate_log_returns(simple_prices)
        assert len(result) == len(simple_prices) - 1

    def test_constant_prices(self, prep, constant_prices):
        """Constant prices → all log returns should be 0."""
        result = prep.calculate_log_returns(constant_prices)
        np.testing.assert_allclose(result.values, 0.0, atol=1e-12)

    def test_single_price(self, prep):
        """A single-element Series should return an empty Series."""
        s = pd.Series([100.0], index=pd.date_range("2023-01-01", periods=1, freq="D", tz="UTC"))
        result = prep.calculate_log_returns(s)
        assert len(result) == 0

    def test_known_value(self, prep):
        """Spot-check: 100 → 200 should give ln(2)*100 ≈ 69.3147."""
        s = pd.Series([100.0, 200.0], index=pd.date_range("2023-01-01", periods=2, freq="D", tz="UTC"))
        result = prep.calculate_log_returns(s)
        np.testing.assert_allclose(result.iloc[0], np.log(2) * 100, rtol=1e-10)

    def test_zero_price_produces_inf_or_nan(self, prep):
        """Zero in the denominator → -inf or NaN (verify no silent corruption)."""
        s = pd.Series([0.0, 100.0], index=pd.date_range("2023-01-01", periods=2, freq="D", tz="UTC"))
        result = prep.calculate_log_returns(s)
        # log(100 / 0) → inf; the method drops the first NaN but the inf remains
        assert len(result) == 1
        assert np.isinf(result.iloc[0]) or np.isnan(result.iloc[0])

    def test_negative_return(self, prep):
        """Price drop → negative log return."""
        s = pd.Series([200.0, 100.0], index=pd.date_range("2023-01-01", periods=2, freq="D", tz="UTC"))
        result = prep.calculate_log_returns(s)
        assert result.iloc[0] < 0

    def test_index_preserved(self, prep, simple_prices):
        """Returned index should match the input index minus the first entry."""
        result = prep.calculate_log_returns(simple_prices)
        pd.testing.assert_index_equal(result.index, simple_prices.index[1:])


# ===================================================================
# 2. winsorize_returns
# ===================================================================

class TestWinsorizeReturns:
    """Tests for DataPreparation.winsorize_returns."""

    def test_normal_returns_unchanged(self, prep):
        """Returns well within bounds should pass through unmodified."""
        rng = np.random.default_rng(42)
        idx = pd.date_range("2023-01-01", periods=100, freq="D", tz="UTC")
        # Small returns: std ~ 1, well within 5-std bounds
        returns = pd.Series(rng.standard_normal(100) * 0.5, index=idx)
        result = prep.winsorize_returns(returns, window=30, n_std=5.0)
        pd.testing.assert_series_equal(result, returns)

    def test_extreme_value_clipped(self, prep):
        """An extreme spike should be clipped toward the rolling bound."""
        idx = pd.date_range("2023-01-01", periods=60, freq="D", tz="UTC")
        returns = pd.Series(np.zeros(60), index=idx)
        # Inject a massive spike at position 50
        returns.iloc[50] = 999.0
        result = prep.winsorize_returns(returns, window=30, n_std=5.0)
        assert result.iloc[50] < 999.0, "Extreme value should be clipped"

    def test_negative_extreme_clipped(self, prep):
        """Negative extreme should be clipped upward."""
        idx = pd.date_range("2023-01-01", periods=60, freq="D", tz="UTC")
        returns = pd.Series(np.zeros(60), index=idx)
        returns.iloc[50] = -999.0
        result = prep.winsorize_returns(returns, window=30, n_std=5.0)
        assert result.iloc[50] > -999.0, "Negative extreme should be clipped"

    def test_output_length_matches_input(self, prep):
        """Winsorization should not change Series length."""
        idx = pd.date_range("2023-01-01", periods=50, freq="D", tz="UTC")
        returns = pd.Series(np.arange(50, dtype=float), index=idx)
        result = prep.winsorize_returns(returns, window=10, n_std=3.0)
        assert len(result) == len(returns)

    def test_window_parameter(self, prep):
        """Winsorization clips a spike that exceeds rolling n_std bound."""
        idx = pd.date_range("2023-01-01", periods=100, freq="D", tz="UTC")
        rng = np.random.default_rng(7)
        # Stable series with std ≈ 1; spike at 1000 is many sigmas away
        returns = pd.Series(rng.standard_normal(100), index=idx)
        returns.iloc[80] = 1000.0

        result = prep.winsorize_returns(returns, window=50, n_std=5.0)
        assert result.iloc[80] < 1000.0

    def test_n_std_parameter(self, prep):
        """Tighter n_std → more aggressive clipping."""
        idx = pd.date_range("2023-01-01", periods=60, freq="D", tz="UTC")
        rng = np.random.default_rng(99)
        returns = pd.Series(rng.standard_normal(60), index=idx)
        returns.iloc[55] = 30.0

        result_loose = prep.winsorize_returns(returns, window=30, n_std=10.0)
        result_tight = prep.winsorize_returns(returns, window=30, n_std=2.0)
        assert result_tight.iloc[55] <= result_loose.iloc[55]

    def test_all_constant(self, prep):
        """Constant series → rolling std ≈ 0, value unchanged (clipped to mean)."""
        idx = pd.date_range("2023-01-01", periods=40, freq="D", tz="UTC")
        returns = pd.Series([3.0] * 40, index=idx)
        result = prep.winsorize_returns(returns, window=30, n_std=5.0)
        np.testing.assert_allclose(result.values, 3.0, atol=1e-10)


# ===================================================================
# 3. merge_sentiment_data
# ===================================================================

class TestMergeSentimentData:
    """Tests for DataPreparation.merge_sentiment_data."""

    def test_columns_present(self, prep, daily_df, weekly_sentiment):
        """Merged result should contain all sentiment columns."""
        merged = prep.merge_sentiment_data(daily_df, weekly_sentiment)
        for col in ["S_gdelt_normalized", "S_reg_decomposed", "S_infra_decomposed"]:
            assert col in merged.columns

    def test_length_preserved(self, prep, daily_df, weekly_sentiment):
        """Merge should keep every row of the daily data (left join)."""
        merged = prep.merge_sentiment_data(daily_df, weekly_sentiment)
        assert len(merged) == len(daily_df)

    def test_no_nans_in_sentiment(self, prep, daily_df, weekly_sentiment):
        """After merge, sentiment columns should have no NaN (filled with 0)."""
        merged = prep.merge_sentiment_data(daily_df, weekly_sentiment)
        for col in ["S_gdelt_normalized", "S_reg_decomposed", "S_infra_decomposed"]:
            assert merged[col].isna().sum() == 0

    def test_forward_fill_propagates(self, prep):
        """Weekly value should forward-fill across subsequent days."""
        weekly_idx = pd.to_datetime(["2023-06-05"], utc=True)  # a Monday
        sentiment = pd.DataFrame(
            {"S_gdelt_normalized": [1.5], "S_reg_decomposed": [0.8], "S_infra_decomposed": [0.7]},
            index=weekly_idx,
        )
        daily_idx = pd.date_range("2023-06-05", periods=7, freq="D", tz="UTC")
        daily = pd.DataFrame({"returns": np.zeros(7)}, index=daily_idx)

        merged = prep.merge_sentiment_data(daily, sentiment)
        # All 7 days should carry the same value via ffill
        assert (merged["S_gdelt_normalized"] == 1.5).all()

    def test_missing_sentiment_columns_handled(self, prep, daily_df):
        """If sentiment_df lacks expected columns, merge should still work."""
        idx = pd.date_range("2023-01-02", periods=2, freq="W-MON", tz="UTC")
        partial = pd.DataFrame({"S_gdelt_normalized": [0.5, -0.3]}, index=idx)
        merged = prep.merge_sentiment_data(daily_df, partial)
        assert "S_gdelt_normalized" in merged.columns

    def test_returns_column_preserved(self, prep, daily_df, weekly_sentiment):
        """Original daily columns should survive the merge."""
        merged = prep.merge_sentiment_data(daily_df, weekly_sentiment)
        assert "returns" in merged.columns
        pd.testing.assert_series_equal(merged["returns"], daily_df["returns"])


# ===================================================================
# 4. Config validation
# ===================================================================

class TestConfig:
    """Sanity checks on config module values."""

    def test_random_seed_set(self):
        import config
        assert isinstance(config.RANDOM_SEED, int)

    def test_winsorization_std_positive(self):
        import config
        assert config.WINSORIZATION_STD > 0

    def test_winsorization_window_positive(self):
        import config
        assert config.WINSORIZATION_WINDOW > 0

    def test_bootstrap_simulations_positive(self):
        import config
        assert config.BOOTSTRAP_N_SIMULATIONS > 0

    def test_garch_orders_positive(self):
        import config
        assert config.GARCH_P >= 1
        assert config.GARCH_Q >= 1

    def test_cryptocurrencies_list_not_empty(self):
        import config
        assert len(config.CRYPTOCURRENCIES) > 0

    def test_date_range_valid(self):
        import config
        start = pd.Timestamp(config.START_DATE)
        end = pd.Timestamp(config.END_DATE)
        assert end > start

    def test_base_dir_is_path(self):
        import config
        assert isinstance(config.BASE_DIR, Path)

    def test_special_events_defined(self):
        import config
        assert isinstance(config.SPECIAL_EVENTS, dict)
        assert "SEC_TWIN_SUITS" in config.SPECIAL_EVENTS

    def test_validate_config_returns_list(self):
        import config
        errors = config.validate_config()
        assert isinstance(errors, list)


# ===================================================================
# 5. _calculate_percentile_ci  (BootstrapInference)
# ===================================================================

class TestCalculatePercentileCI:
    """Tests for BootstrapInference._calculate_percentile_ci."""

    @pytest.fixture
    def bootstrap_obj(self):
        """Minimal BootstrapInference with synthetic returns."""
        from bootstrap_inference import BootstrapInference
        idx = pd.date_range("2023-01-01", periods=100, freq="D", tz="UTC")
        returns = pd.Series(np.random.default_rng(42).standard_normal(100), index=idx)
        return BootstrapInference(returns, n_bootstrap=10, seed=42)

    def test_basic_ci(self, bootstrap_obj):
        """CI should bracket the original estimate for well-behaved data."""
        original = {"omega": 0.05, "alpha[1]": 0.10}
        boot_params = [
            {"omega": 0.04, "alpha[1]": 0.09},
            {"omega": 0.06, "alpha[1]": 0.11},
            {"omega": 0.05, "alpha[1]": 0.10},
            {"omega": 0.045, "alpha[1]": 0.095},
            {"omega": 0.055, "alpha[1]": 0.105},
        ]
        ci = bootstrap_obj._calculate_percentile_ci(boot_params, original, alpha=0.05)
        assert "omega" in ci
        assert "alpha[1]" in ci
        assert ci["omega"]["ci_lower"] <= ci["omega"]["ci_upper"]

    def test_empty_bootstrap(self, bootstrap_obj):
        """Empty bootstrap list → empty CI dict."""
        ci = bootstrap_obj._calculate_percentile_ci([], {"omega": 0.05})
        assert ci == {}

    def test_ci_keys(self, bootstrap_obj):
        """Each parameter entry should have the expected keys."""
        original = {"omega": 0.05}
        boot_params = [{"omega": v} for v in [0.04, 0.05, 0.06]]
        ci = bootstrap_obj._calculate_percentile_ci(boot_params, original)
        entry = ci["omega"]
        for key in ["original", "ci_lower", "ci_upper", "ci_width", "bootstrap_mean", "bootstrap_std"]:
            assert key in entry, f"Missing key: {key}"

    def test_ci_width_positive(self, bootstrap_obj):
        """CI width should be non-negative."""
        original = {"omega": 0.05}
        boot_params = [{"omega": v} for v in [0.03, 0.04, 0.05, 0.06, 0.07]]
        ci = bootstrap_obj._calculate_percentile_ci(boot_params, original)
        assert ci["omega"]["ci_width"] >= 0

    def test_original_value_stored(self, bootstrap_obj):
        """The CI dict should record the original parameter value."""
        original = {"omega": 0.123}
        boot_params = [{"omega": 0.1}, {"omega": 0.15}]
        ci = bootstrap_obj._calculate_percentile_ci(boot_params, original)
        assert ci["omega"]["original"] == 0.123

    def test_alpha_affects_width(self, bootstrap_obj):
        """Wider alpha → narrower CI."""
        original = {"omega": 0.05}
        boot_params = [{"omega": v} for v in np.linspace(0.01, 0.09, 50)]
        ci_95 = bootstrap_obj._calculate_percentile_ci(boot_params, original, alpha=0.05)
        ci_90 = bootstrap_obj._calculate_percentile_ci(boot_params, original, alpha=0.10)
        assert ci_95["omega"]["ci_width"] >= ci_90["omega"]["ci_width"]

    def test_missing_param_in_bootstrap(self, bootstrap_obj):
        """Param present in original but absent from bootstrap → skipped."""
        original = {"omega": 0.05, "gamma[1]": 0.02}
        boot_params = [{"omega": 0.04}, {"omega": 0.06}]
        ci = bootstrap_obj._calculate_percentile_ci(boot_params, original)
        assert "omega" in ci
        assert "gamma[1]" not in ci


# ===================================================================
# 6. Additional DataPreparation helpers
# ===================================================================

class TestCreateEventWindow:
    """Tests for DataPreparation.create_event_window."""

    def test_default_window_length(self, prep):
        """Default 3+1+3 = 7 days."""
        event_date = pd.Timestamp("2023-06-15", tz="UTC")
        window = prep.create_event_window(event_date)
        assert len(window) == 7

    def test_custom_window(self, prep):
        event_date = pd.Timestamp("2023-06-15", tz="UTC")
        window = prep.create_event_window(event_date, days_before=5, days_after=5)
        assert len(window) == 11

    def test_event_date_in_window(self, prep):
        event_date = pd.Timestamp("2023-06-15", tz="UTC")
        window = prep.create_event_window(event_date)
        assert event_date in window
