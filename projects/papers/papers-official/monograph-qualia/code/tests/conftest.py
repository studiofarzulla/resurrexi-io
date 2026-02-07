"""Shared fixtures for monograph-qualia tests."""

import sys
from pathlib import Path

import numpy as np
import networkx as nx
import pytest

# Add source directories to path so we can import modules
CODE_DIR = Path(__file__).resolve().parent.parent
COMP_MODEL_DIR = CODE_DIR / "computational-model"
COMP_MODEL_SRC_DIR = COMP_MODEL_DIR / "src"
POLYGRAPHS_DIR = CODE_DIR / "polygraphs-consciousness"

for p in [COMP_MODEL_DIR, COMP_MODEL_SRC_DIR, POLYGRAPHS_DIR]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


# --- NetworkX graph fixtures ---

@pytest.fixture
def small_complete_graph():
    """Complete graph with 5 nodes."""
    return nx.complete_graph(5)


@pytest.fixture
def small_cycle_graph():
    """Cycle graph with 5 nodes."""
    return nx.cycle_graph(5)


@pytest.fixture
def small_path_graph():
    """Path graph with 4 nodes."""
    return nx.path_graph(4)


@pytest.fixture
def isolated_node_graph():
    """Graph with one isolated node and a connected pair."""
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2])
    G.add_edge(0, 1)
    return G


# --- Numpy array fixtures ---

@pytest.fixture
def stable_activations():
    """Synthetic activations that are stable (low variance across time)."""
    rng = np.random.default_rng(42)
    base = rng.uniform(0.6, 0.8, size=(1, 8))
    noise = rng.normal(0, 0.01, size=(20, 8))
    return base + noise


@pytest.fixture
def unstable_activations():
    """Synthetic activations that are unstable (high variance across time)."""
    rng = np.random.default_rng(42)
    return rng.uniform(0.0, 1.0, size=(20, 8))


@pytest.fixture
def constant_activations():
    """Activations that are perfectly constant over time."""
    return np.ones((10, 5)) * 0.5
