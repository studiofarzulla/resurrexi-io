---
title: "gjr-garch-x: GJR-GARCH with Exogenous Variance Regressors"
category: "Open Source Software"
date: "December 2025"
github: "https://github.com/studiofarzulla/gjr-garch-x"
description: "Pure Python implementation of GJR-GARCH models supporting exogenous variables in the conditional variance equation—a feature missing from standard econometrics packages."
tags: ["Python", "Econometrics", "GARCH", "Volatility", "PyPI"]
---

## Overview

**Published on PyPI:** [`pip install gjr-garch-x`](https://pypi.org/project/gjr-garch-x/)

A standalone implementation of Glosten-Jagannathan-Runkle (1993) GARCH models with proper support for exogenous regressors in the variance equation. Standard packages like Python's `arch` don't natively support this—gjr-garch-x fills that gap.

## Why This Exists

Event studies and sentiment analysis require testing whether specific variables (regulatory announcements, sentiment indicators, regime dummies) affect conditional volatility. The standard GARCH-X specification in most packages only allows exogenous regressors in the **mean** equation, not the **variance** equation.

This package implements the full GJR-GARCH-X specification:

```
σ²_t = ω + α·ε²_{t-1} + γ·ε²_{t-1}·I(ε_{t-1}<0) + β·σ²_{t-1} + Σδⱼ·x_{j,t}
```

Where `x_{j,t}` are exogenous variables with estimated coefficients `δⱼ`.

## Features

- **Student-t innovations:** Captures fat tails in financial returns
- **GJR leverage effect:** Asymmetric response to positive/negative shocks
- **Robust standard errors:** Numerical Hessian with proper inference
- **Stationarity constraints:** Enforced during optimization
- **Pandas integration:** Works directly with Series/DataFrame
- **No `arch` dependency:** Standalone implementation

## Research Application

Developed for the [Market Reaction Asymmetry](https://doi.org/10.2139/ssrn.5788082) paper (under review at Digital Finance), which found infrastructure disruptions cause 3.2× greater volatility impact than regulatory events in cryptocurrency markets.

## Technical Details

- **Estimation:** Quasi-Maximum Likelihood (QML)
- **Optimizer:** SLSQP with constraint handling
- **Standard Errors:** Numerical Hessian inversion
- **Distribution:** Student-t with estimated degrees of freedom

## Citation

```bibtex
@software{farzulla2025gjrgarchx,
  author = {Farzulla, Murad},
  title = {gjr-garch-x: GJR-GARCH Models with Exogenous Variance Regressors},
  year = {2025},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.17988193},
  url = {https://github.com/studiofarzulla/gjr-garch-x}
}
```

## Status

**Published:** PyPI v0.1.0 (December 2025)

**DOI:** [10.5281/zenodo.17988193](https://doi.org/10.5281/zenodo.17988193)
