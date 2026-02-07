"""Tests for src/metrics.py — NarrativeStabilityMetrics, AttractorBasinMetrics, TemporalPersistenceMetrics.

All tests use numpy arrays only — NO torch dependency.
"""

import numpy as np
import pytest
from scipy.stats import pearsonr, spearmanr

# metrics.py imports torch and sklearn at top level; we patch around that.
# We import the classes after ensuring sys.path is set up via conftest.
import importlib
import sys
from unittest import mock


def _import_metrics():
    """Import metrics module with torch and model mocked out so it loads without torch."""
    # Mock torch and model at module level so metrics.py can import
    fake_torch = mock.MagicMock()
    fake_model = mock.MagicMock()
    with mock.patch.dict(sys.modules, {"torch": fake_torch, "torch.nn.functional": mock.MagicMock(), "model": fake_model}):
        # Also need sklearn
        import metrics as m
        importlib.reload(m)  # reload to pick up mocks
        return m


metrics = _import_metrics()
NarrativeStabilityMetrics = metrics.NarrativeStabilityMetrics
AttractorBasinMetrics = metrics.AttractorBasinMetrics
TemporalPersistenceMetrics = metrics.TemporalPersistenceMetrics


# ── NarrativeStabilityMetrics ────────────────────────────────────────────────


class TestNarrativeStabilityMetrics:
    def test_returns_required_keys(self, stable_activations):
        result = NarrativeStabilityMetrics.compute_stability_score(stable_activations)
        for key in ['mean_activation', 'variance', 'stability_score', 'overall_stability']:
            assert key in result

    def test_stable_activations_high_stability(self, stable_activations):
        result = NarrativeStabilityMetrics.compute_stability_score(stable_activations)
        assert result['overall_stability'] > 0.9

    def test_unstable_activations_lower_stability(self, unstable_activations):
        result = NarrativeStabilityMetrics.compute_stability_score(unstable_activations)
        assert result['overall_stability'] < 0.95

    def test_constant_activations_perfect_stability(self, constant_activations):
        result = NarrativeStabilityMetrics.compute_stability_score(constant_activations)
        np.testing.assert_allclose(result['overall_stability'], 1.0)

    def test_variance_non_negative(self, stable_activations):
        result = NarrativeStabilityMetrics.compute_stability_score(stable_activations)
        assert np.all(result['variance'] >= 0.0)

    def test_stability_score_bounded(self, unstable_activations):
        result = NarrativeStabilityMetrics.compute_stability_score(unstable_activations)
        assert np.all(result['stability_score'] > 0.0)
        assert np.all(result['stability_score'] <= 1.0)

    def test_mean_activation_shape(self, stable_activations):
        result = NarrativeStabilityMetrics.compute_stability_score(stable_activations)
        assert result['mean_activation'].shape == (stable_activations.shape[1],)

    def test_stability_trend_length(self, stable_activations):
        trend = NarrativeStabilityMetrics.compute_stability_trend(stable_activations, window_size=5)
        expected_len = stable_activations.shape[0] - 5 + 1
        assert len(trend) == expected_len

    def test_stability_trend_values_bounded(self, stable_activations):
        trend = NarrativeStabilityMetrics.compute_stability_trend(stable_activations, window_size=3)
        assert np.all(trend > 0.0)
        assert np.all(trend <= 1.0)


# ── AttractorBasinMetrics ────────────────────────────────────────────────────


class TestAttractorBasinMetrics:
    def test_identical_arrays_perfect_resistance(self):
        arr = np.array([0.5, 0.6, 0.7, 0.8, 0.9])
        result = AttractorBasinMetrics.compute_perturbation_resistance(arr, arr)
        np.testing.assert_allclose(result['pearson_correlation'], 1.0, atol=1e-10)
        np.testing.assert_allclose(result['cosine_similarity'], 1.0, atol=1e-10)
        np.testing.assert_allclose(result['mean_absolute_difference'], 0.0, atol=1e-10)

    def test_different_arrays_lower_resistance(self):
        pre = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        post = np.array([0.9, 0.8, 0.7, 0.6, 0.5])
        result = AttractorBasinMetrics.compute_perturbation_resistance(pre, post)
        assert result['pearson_correlation'] < 0.0  # negatively correlated

    def test_resistance_score_is_average(self):
        pre = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        post = np.array([0.15, 0.35, 0.55, 0.75, 0.95])
        result = AttractorBasinMetrics.compute_perturbation_resistance(pre, post)
        expected = (result['pearson_correlation'] + result['spearman_correlation'] + result['cosine_similarity']) / 3
        np.testing.assert_allclose(result['resistance_score'], expected, atol=1e-10)

    def test_basin_depth_decreasing_distances(self):
        distances = [1.0, 0.8, 0.6, 0.4, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005]
        result = AttractorBasinMetrics.compute_basin_depth(distances)
        assert result['convergence_magnitude'] > 0
        assert result['convergence_rate'] > 0
        assert result['final_stability'] > 0.8

    def test_basin_depth_flat_distances(self):
        distances = [0.5] * 20
        result = AttractorBasinMetrics.compute_basin_depth(distances)
        np.testing.assert_allclose(result['convergence_magnitude'], 0.0, atol=1e-10)


# ── TemporalPersistenceMetrics ───────────────────────────────────────────────


class TestTemporalPersistenceMetrics:
    def test_identical_arrays_strong_persistence(self):
        arr = np.array([0.5, 0.6, 0.7, 0.8, 0.9])
        result = TemporalPersistenceMetrics.compute_persistence_score(arr, arr)
        assert result['interpretation'] == 'strong'
        np.testing.assert_allclose(result['mean_relative_change'], 0.0, atol=1e-6)

    def test_slightly_decayed_still_strong(self):
        pre = np.array([0.5, 0.6, 0.7, 0.8, 0.9])
        post = pre * 0.95
        result = TemporalPersistenceMetrics.compute_persistence_score(pre, post)
        assert result['persistence_score'] > 0.7

    def test_completely_different_weak_persistence(self):
        rng = np.random.default_rng(123)
        pre = rng.uniform(0.1, 0.9, size=20)
        post = rng.uniform(0.1, 0.9, size=20)
        result = TemporalPersistenceMetrics.compute_persistence_score(pre, post)
        assert result['persistence_score'] < 0.7

    def test_returns_required_keys(self):
        pre = np.array([0.5, 0.6, 0.7])
        post = np.array([0.5, 0.6, 0.7])
        result = TemporalPersistenceMetrics.compute_persistence_score(pre, post)
        for key in ['pearson_correlation', 'spearman_correlation', 'mean_relative_change',
                     'persistence_score', 'interpretation']:
            assert key in result

    def test_activation_decay_decreasing(self):
        rng = np.random.default_rng(42)
        # Simulate exponential decay over 20 timesteps, 5 concepts
        t = np.arange(20).reshape(-1, 1)
        activations = 1.0 * np.exp(-0.1 * t) + rng.normal(0, 0.001, size=(20, 5))
        activations = np.clip(activations, 0.001, None)
        result = TemporalPersistenceMetrics.compute_activation_decay(activations)
        assert result['decay_rate'] > 0
        assert result['retention_ratio'] < 1.0
