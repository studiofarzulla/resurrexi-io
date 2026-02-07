"""Tests for polygraphs/ops/math.py — _tologits, probs, likelihood, marginal.

These functions require torch tensors. All tests are skipped if torch is not installed.
"""

import math
import numpy as np
import pytest

torch = pytest.importorskip("torch")

import importlib.util
import sys
from pathlib import Path

# Import math.py directly to avoid polygraphs.__init__ which requires dgl
_math_path = Path(__file__).resolve().parent.parent / "polygraphs-consciousness" / "polygraphs" / "ops" / "math.py"
_spec = importlib.util.spec_from_file_location("polygraphs_ops_math", _math_path)
_math_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_math_mod)

_tologits = _math_mod._tologits
probs = _math_mod.probs
likelihood = _math_mod.likelihood
marginal = _math_mod.marginal
Evidence = _math_mod.Evidence


# ── _tologits ────────────────────────────────────────────────────────────────


class TestToLogits:
    def test_half_probability_gives_zero(self):
        p = torch.tensor([0.5])
        result = _tologits(p)
        assert torch.allclose(result, torch.tensor([0.0]), atol=1e-6)

    def test_known_value_073(self):
        """logit(0.73) ≈ log(0.73/0.27) ≈ 0.9946"""
        p = torch.tensor([0.73])
        result = _tologits(p)
        expected = torch.log(torch.tensor([0.73])) - torch.log1p(torch.tensor([-0.73]))
        assert torch.allclose(result, expected, atol=1e-5)

    def test_inverse_of_sigmoid(self):
        """_tologits should be the inverse of sigmoid."""
        p = torch.tensor([0.1, 0.3, 0.5, 0.7, 0.9])
        logits = _tologits(p)
        recovered = torch.sigmoid(logits)
        assert torch.allclose(recovered, p, atol=1e-5)

    def test_low_probability(self):
        p = torch.tensor([0.01])
        result = _tologits(p)
        assert result.item() < -4.0  # logit(0.01) ≈ -4.595

    def test_high_probability(self):
        p = torch.tensor([0.99])
        result = _tologits(p)
        assert result.item() > 4.0  # logit(0.99) ≈ 4.595

    def test_batch_input(self):
        p = torch.tensor([0.2, 0.5, 0.8])
        result = _tologits(p)
        assert result.shape == (3,)

    def test_extreme_values_clamped(self):
        """Values at 0 and 1 should be clamped and not produce inf."""
        p = torch.tensor([0.0, 1.0])
        result = _tologits(p)
        assert torch.all(torch.isfinite(result))


# ── probs ────────────────────────────────────────────────────────────────────


class TestProbs:
    def test_fair_coin_single_trial(self):
        """P(k=1 | p=0.5, n=1) should be 0.5."""
        logits = torch.tensor([0.0])  # p=0.5
        values = torch.tensor([1.0])
        trials = torch.tensor([1.0])
        result = probs(logits, values, trials)
        assert torch.allclose(result, torch.tensor([0.5]), atol=1e-4)

    def test_fair_coin_zero_successes(self):
        """P(k=0 | p=0.5, n=1) should be 0.5."""
        logits = torch.tensor([0.0])
        values = torch.tensor([0.0])
        trials = torch.tensor([1.0])
        result = probs(logits, values, trials)
        assert torch.allclose(result, torch.tensor([0.5]), atol=1e-4)

    def test_probabilities_non_negative(self):
        logits = torch.tensor([0.0, 1.0, -1.0])
        values = torch.tensor([1.0, 2.0, 0.0])
        trials = torch.tensor([3.0, 3.0, 3.0])
        result = probs(logits, values, trials)
        assert torch.all(result >= 0.0)

    def test_binomial_sum_to_one(self):
        """For n=2 trials, P(k=0)+P(k=1)+P(k=2) should sum to 1."""
        logits = torch.tensor([0.5])
        trials = torch.tensor([2.0])
        total = sum(
            probs(logits, torch.tensor([float(k)]), trials).item()
            for k in range(3)
        )
        assert abs(total - 1.0) < 1e-4


# ── likelihood ───────────────────────────────────────────────────────────────


class TestLikelihood:
    def test_hypothesis_true_returns_clamped(self):
        evidence = Evidence(
            logits=torch.tensor([0.0]),
            values=torch.tensor([1.0]),
            trials=torch.tensor([2.0]),
        )
        result = likelihood(evidence, hypothesis=True)
        assert result.item() > 0.0 and result.item() < 1.0

    def test_hypothesis_false_complement(self):
        """likelihood(E|H) and likelihood(E|¬H) should not be equal in general."""
        evidence = Evidence(
            logits=torch.tensor([1.0]),
            values=torch.tensor([2.0]),
            trials=torch.tensor([3.0]),
        )
        lh_true = likelihood(evidence, hypothesis=True)
        lh_false = likelihood(evidence, hypothesis=False)
        assert not torch.allclose(lh_true, lh_false)

    def test_output_in_unit_interval(self):
        evidence = Evidence(
            logits=torch.tensor([0.5, -0.5]),
            values=torch.tensor([1.0, 0.0]),
            trials=torch.tensor([2.0, 2.0]),
        )
        result = likelihood(evidence)
        assert torch.all(result > 0.0)
        assert torch.all(result < 1.0)


# ── marginal ─────────────────────────────────────────────────────────────────


class TestMarginal:
    def test_marginal_is_weighted_sum(self):
        """P(E) = P(H)*P(E|H) + P(¬H)*P(E|¬H)."""
        prior = torch.tensor([0.6])
        evidence = Evidence(
            logits=torch.tensor([0.5]),
            values=torch.tensor([1.0]),
            trials=torch.tensor([2.0]),
        )
        marg = marginal(prior, evidence)
        lh_true = likelihood(evidence, hypothesis=True)
        lh_false = likelihood(evidence, hypothesis=False)
        expected = prior * lh_true + (1.0 - prior) * lh_false
        # marginal clamps, so compare within tolerance
        assert torch.allclose(marg, expected.clamp(min=1e-7, max=1-1e-7), atol=1e-4)

    def test_marginal_in_unit_interval(self):
        prior = torch.tensor([0.3, 0.5, 0.9])
        evidence = Evidence(
            logits=torch.tensor([0.0, 1.0, -1.0]),
            values=torch.tensor([1.0, 2.0, 0.0]),
            trials=torch.tensor([2.0, 3.0, 2.0]),
        )
        result = marginal(prior, evidence)
        assert torch.all(result > 0.0)
        assert torch.all(result < 1.0)

    def test_uniform_prior_symmetry(self):
        """With prior=0.5, marginal should equal average of likelihoods."""
        prior = torch.tensor([0.5])
        evidence = Evidence(
            logits=torch.tensor([0.0]),
            values=torch.tensor([1.0]),
            trials=torch.tensor([2.0]),
        )
        marg = marginal(prior, evidence)
        lh_t = likelihood(evidence, hypothesis=True)
        lh_f = likelihood(evidence, hypothesis=False)
        expected = 0.5 * lh_t + 0.5 * lh_f
        assert torch.allclose(marg, expected.clamp(min=1e-7, max=1-1e-7), atol=1e-4)
