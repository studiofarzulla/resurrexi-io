"""
Verify that all main modules import successfully and expose expected symbols.
"""

import pytest


def test_import_config():
    """Config module loads and exposes key settings."""
    import config
    assert hasattr(config, "RANDOM_SEED")
    assert hasattr(config, "DATA_DIR")
    assert hasattr(config, "CRYPTOCURRENCIES")
    assert hasattr(config, "validate_config")


def test_import_data_preparation():
    """data_preparation exposes the DataPreparation class."""
    import data_preparation
    assert hasattr(data_preparation, "DataPreparation")
    assert callable(data_preparation.DataPreparation)
    # Check convenience functions
    assert hasattr(data_preparation, "load_and_prepare_single_crypto")
    assert hasattr(data_preparation, "load_and_prepare_all_cryptos")


def test_import_garch_models():
    """garch_models module imports without error."""
    import garch_models
    assert hasattr(garch_models, "GARCHModels")


def test_import_event_impact_analysis():
    """event_impact_analysis module imports without error."""
    import event_impact_analysis
    assert hasattr(event_impact_analysis, "__file__")


@pytest.mark.slow
def test_import_bootstrap_inference():
    """bootstrap_inference exposes BootstrapInference class."""
    import bootstrap_inference
    assert hasattr(bootstrap_inference, "BootstrapInference")
    assert hasattr(bootstrap_inference, "run_bootstrap_analysis")


@pytest.mark.slow
def test_import_bootstrap_inference_optimized():
    """bootstrap_inference_optimized imports without error."""
    import bootstrap_inference_optimized
    assert bootstrap_inference_optimized is not None
