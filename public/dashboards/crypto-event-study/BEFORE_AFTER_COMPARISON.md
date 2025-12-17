# Before/After Comparison - Dashboard Data Fix

## Individual Cryptocurrency Effects

### Before (WRONG - showing ~0.1% effects with 0.001pp differences)
```
BTC: Infrastructure -0.084%, Regulatory -0.083%, Diff: -0.001pp
ETH: Infrastructure  0.613%, Regulatory  0.612%, Diff:  0.001pp
XRP: Infrastructure -0.189%, Regulatory -0.191%, Diff:  0.002pp
BNB: Infrastructure  0.947%, Regulatory  0.943%, Diff:  0.004pp
LTC: Infrastructure -0.027%, Regulatory -0.030%, Diff:  0.003pp
ADA: Infrastructure  2.165%, Regulatory  2.168%, Diff: -0.003pp
```
**Problem:** Values way too small, many negative, differences microscopic

### After (CORRECT - TARCH-X coefficients from paper)
```
BTC: Infrastructure  1.191%, Regulatory  0.32%, Diff:  0.871pp  (3.7× larger)
ETH: Infrastructure  2.531%, Regulatory  0.55%, Diff:  1.981pp  (5.1× larger)
XRP: Infrastructure  2.386%, Regulatory  1.47%, Diff:  0.916pp  (1.7× larger)
BNB: Infrastructure  2.913%, Regulatory  0.16%, Diff:  2.753pp  (9.4× larger)
LTC: Infrastructure  2.920%, Regulatory  0.05%, Diff:  2.870pp (58.0× larger)
ADA: Infrastructure  3.371%, Regulatory  0.00%, Diff:  3.371pp  (∞× larger)
```
**Fixed:** All positive, realistic magnitudes, clear infrastructure dominance

---

## Key Metrics Section

### Before (4 metrics, 1 wrong)
```
┌─────────────────────────┐  ┌─────────────────────────┐
│ Heterogeneity Spread    │  │ Statistical Significance│
│      2.18pp             │  │      p < 0.001          │
└─────────────────────────┘  └─────────────────────────┘

┌─────────────────────────┐  ┌─────────────────────────┐
│ Effect Size             │  │ FDR Significant         │
│      d = 2.75           │  │      5/6  ❌ WRONG      │
└─────────────────────────┘  └─────────────────────────┘
```

### After (6 metrics, all correct, headline added)
```
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│ Infrastructure vs Reg   │  │ Statistical Significance│  │ Effect Size             │
│    5.7× multiplier ⭐   │  │      p = 0.0008         │  │      d = 2.753          │
└─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘

┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│ FDR Significant         │  │ Heterogeneity Spread    │  │ TARCH-X Wins AIC        │
│    ETH only ✓           │  │      2.18pp             │  │    5/6 (83%)            │
└─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘
```

---

## Advanced Statistics (NEW ADDITION)

### Before
*Nothing - these were completely missing*

### After
**Three new sections added:**

#### 1. Advanced Statistical Tests
- Independent t-test: t = 4.768, p = 0.0008***
- Mann-Whitney U: U = 34.0, p = 0.0043**
- Cohen's d: d = 2.753 (huge effect)
- Inverse-var weighted Z: Z = 3.64, p = 0.0003***
- Bayes Factors: BF > 10 for 4/6 cryptos

#### 2. Network Analysis
- ETH eigenvector centrality: 0.89 (most central)
- BTC eigenvector centrality: 0.71
- Network density: 0.667

#### 3. Regime-Switching Model
- Sensitivity amplification: 5× during crisis
- F-statistic: F = 45.23, p < 0.001***
- Placebo test: 1,000 random dates validation

---

## Impact Summary

### What was wrong
1. **Data values 10-100× too small** (showing 0.001pp differences instead of 0.871-3.371pp)
2. **Many negative values** (BTC, XRP, LTC showed negative effects - impossible for TARCH-X coefficients)
3. **Missing headline finding** (5.7× multiplier not displayed)
4. **FDR claim backwards** (said 5/6 significant, actually only ETH survives)
5. **Missing advanced stats** (no Bayes Factors, network analysis, regime-switching)

### What's fixed
1. ✓ All values match paper exactly
2. ✓ 5.7× multiplier prominently displayed
3. ✓ FDR corrected (ETH only)
4. ✓ TARCH-X model performance added (83% AIC wins)
5. ✓ Mann-Whitney U test added (p = 0.0043)
6. ✓ Bayes Factors added (4/6 with strong evidence)
7. ✓ Network analysis added (ETH centrality > BTC)
8. ✓ Regime-switching results added (5× crisis amplification)

### Files affected
- `dashboard.html` - Full fixes + advanced stats
- `dashboard-lite.html` - Data fixes only
- `dashboard-specialty.html` - Data fixes only

---

**Bottom line:** Dashboard now accurately represents the paper's findings. The old version was essentially showing noise (differences of 0.001-0.004pp) instead of the massive infrastructure effects (0.871-3.371pp) that the paper actually discovered.
