"""Tests for consciousness_belief_sim.py — ConsciousnessBeliefNetwork and create_networks."""

import numpy as np
import networkx as nx
import pytest

from consciousness_belief_sim import ConsciousnessBeliefNetwork, create_networks


# ── ConsciousnessBeliefNetwork: initialization ──────────────────────────────


class TestConsciousnessBeliefNetworkInit:
    def test_init_sets_correct_node_count(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        assert net.n_agents == 5

    def test_init_beliefs_within_default_range(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        assert np.all(net.beliefs >= 0.3)
        assert np.all(net.beliefs <= 0.7)

    def test_init_beliefs_custom_range(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph, initial_belief_range=(0.1, 0.2))
        assert np.all(net.beliefs >= 0.1)
        assert np.all(net.beliefs <= 0.2)

    def test_init_history_has_one_entry(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        assert len(net.history) == 1

    def test_init_stores_graph(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        assert net.graph is small_complete_graph


# ── Belief bounds ────────────────────────────────────────────────────────────


class TestBeliefBounds:
    def test_beliefs_stay_in_unit_interval_after_update(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        for _ in range(50):
            net.update_beliefs()
        assert np.all(net.beliefs >= 0.0)
        assert np.all(net.beliefs <= 1.0)

    def test_extreme_evidence_clipped(self, small_cycle_graph):
        """Even with extreme evidence, beliefs stay in [0, 1]."""
        net = ConsciousnessBeliefNetwork(small_cycle_graph)
        for _ in range(100):
            net.update_beliefs(alpha=0.1, beta=0.1, gamma=0.8, evidence=5.0)
        assert np.all(net.beliefs >= 0.0)
        assert np.all(net.beliefs <= 1.0)

    def test_negative_evidence_clipped(self, small_cycle_graph):
        net = ConsciousnessBeliefNetwork(small_cycle_graph)
        for _ in range(100):
            net.update_beliefs(alpha=0.1, beta=0.1, gamma=0.8, evidence=-5.0)
        assert np.all(net.beliefs >= 0.0)
        assert np.all(net.beliefs <= 1.0)


# ── get_statistics ───────────────────────────────────────────────────────────


class TestGetStatistics:
    def test_returns_required_keys(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        stats = net.get_statistics()
        for key in ['mean', 'std', 'min', 'max', 'median']:
            assert key in stats

    def test_values_are_floats(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        stats = net.get_statistics()
        for v in stats.values():
            assert isinstance(v, float)

    def test_mean_between_min_and_max(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        stats = net.get_statistics()
        assert stats['min'] <= stats['mean'] <= stats['max']

    def test_std_non_negative(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        stats = net.get_statistics()
        assert stats['std'] >= 0.0


# ── create_networks ──────────────────────────────────────────────────────────


class TestCreateNetworks:
    def test_returns_dict(self):
        nets = create_networks(n=10)
        assert isinstance(nets, dict)

    def test_has_expected_keys(self):
        nets = create_networks(n=10)
        assert set(nets.keys()) == {'complete', 'cycle', 'facebook'}

    def test_values_are_graphs(self):
        nets = create_networks(n=10)
        for g in nets.values():
            assert isinstance(g, nx.Graph)

    def test_node_counts(self):
        nets = create_networks(n=15)
        for g in nets.values():
            assert g.number_of_nodes() == 15

    def test_complete_graph_edge_count(self):
        nets = create_networks(n=10)
        assert nets['complete'].number_of_edges() == 10 * 9 // 2


# ── Simulation / convergence ─────────────────────────────────────────────────


class TestSimulation:
    def test_simulate_returns_step_count(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        steps = net.simulate(n_steps=500, convergence_threshold=0.001, verbose=False)
        assert isinstance(steps, int)

    def test_simulate_converges_on_complete_graph(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        steps = net.simulate(n_steps=1000, convergence_threshold=0.001, verbose=False)
        assert steps < 1000, "Complete graph should converge quickly"

    def test_beliefs_close_after_convergence(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        net.simulate(n_steps=1000, convergence_threshold=0.0001, verbose=False)
        assert np.std(net.beliefs) < 0.01, "Beliefs should be very close after convergence on complete graph"

    def test_history_grows(self, small_complete_graph):
        net = ConsciousnessBeliefNetwork(small_complete_graph)
        steps = net.simulate(n_steps=500, convergence_threshold=0.001, verbose=False)
        # history starts with 1, each step adds 1
        assert len(net.history) == steps + 2  # initial + steps + 1 (0-indexed convergence)

    def test_isolated_node_unchanged(self, isolated_node_graph):
        """Isolated node (node 2) should keep its belief roughly constant (only evidence shifts it)."""
        net = ConsciousnessBeliefNetwork(isolated_node_graph)
        initial_belief_2 = net.beliefs[2]
        # With zero total evidence, isolated node belief is b_new = alpha*b + beta*b + gamma*0 = (alpha+beta)*b
        net.update_beliefs(evidence=0.0)
        expected = np.clip(0.6 * initial_belief_2 + 0.3 * initial_belief_2, 0, 1)
        np.testing.assert_allclose(net.beliefs[2], expected, atol=1e-10)
