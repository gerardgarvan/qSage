---
phase: 04-product-conversion
plan: 03
subsystem: product-conversion
tags: [mprodmake, qfactor, zqfactor, qs2jaccombo, findprod, MProduct, QFactorResult]
dependency_graph:
  requires: [04-01, 04-02]
  provides: [CONV-05, CONV-06, CONV-07-stub, CONV-10, CONV-11]
  affects: [qseries/_conversion.py, qseries/__init__.py, tests/test_conversion.py, qseries/_series.py]
tech_stack:
  added: [cyclotomic_polynomial, euler_phi, divisors from sage.all, itertools.product]
  patterns: [greedy-cancellation, cyclotomic-trial-division, exhaustive-search]
key_files:
  created: []
  modified:
    - qseries/_conversion.py
    - qseries/_series.py
    - qseries/__init__.py
    - tests/test_conversion.py
decisions:
  - "qfactor accepts (num_poly, den_poly) tuple to avoid Sage fraction field auto-simplification"
  - "qfactor algorithm: cyclotomic trial-division greedy from largest k to smallest"
  - "mprodmake uses input series precision (not T argument) as working precision"
  - "zqfactor: documented best-effort stub returning None with UserWarning; full impl deferred Phase 5"
  - "QSeries.__pow__ extended to support negative integer exponents via series inversion"
metrics:
  duration: "45 min"
  completed: "2026-09-17"
  tasks: 2
  files_modified: 4
requirements: [CONV-05, CONV-06, CONV-10, CONV-11]
---

# Phase 4 Plan 3: mprodmake, qfactor, zqfactor, qs2jaccombo, findprod Summary

**One-liner:** Greedy (1+q^n) product identification, cyclotomic-based rational function factoring, and exhaustive q-product search complete the Phase 4 product-conversion toolkit.

## What Was Built

All 5 remaining product-conversion functions implemented in `qseries/_conversion.py`:

- **mprodmake** (CONV-05): greedy cancellation algorithm identifying (1+q^n) factors; working precision uses input series prec (not T argument) to detect the full range of exponents.
- **qfactor** (CONV-06): factors rational functions in QQ[q] into (1-q^k) terms using cyclotomic trial-division. Accepts `(num_poly, den_poly)` tuple to bypass Sage fraction field auto-simplification.
- **zqfactor** (CONV-07): documented best-effort stub returning None with UserWarning; bivariate factorization deferred to Phase 5.
- **qs2jaccombo** (CONV-10): converts list of QSeries terms to JacProduct objects by delegating to jacprodmake per term.
- **findprod** (CONV-11): exhaustive search over coefficient tuples; calls checkprod(combo, M, Q) to test each linear combination.

**Supporting change:** `QSeries.__pow__` now supports negative integer exponents via series inversion (required for etaq(q,4,T)**(-1) in mprodmake test).

**Exports:** MProduct, QFactorResult added to `__init__.py` and `__all__`.

## Test Results

All 14 tests in `tests/test_conversion.py` pass, 0 skipped.
Full suite: 103 passed, 4 pre-existing failures in test_building_blocks.py (unrelated to this plan).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] QSeries.__pow__ rejected negative exponents**
- Found during: Task 1 (test_mprodmake needs etaq**(-1))
- Issue: `__pow__` raised TypeError for n < 0
- Fix: added negative-exponent branch using series.__invert__() then iterative multiplication
- Files modified: qseries/_series.py
- Commit: c9c53dc

**2. [Rule 1 - Bug] qfactor fraction field auto-simplification**
- Found during: Task 1 (test_qfactor_t8 returned empty numerator exponents)
- Issue: Sage's fraction field auto-simplifies num/den, cancelling common cyclotomic factors before qfactor can reconstruct (1-q^k) terms
- Fix: qfactor accepts `(num_poly, den_poly)` tuple; test updated to pass polynomials directly instead of a fraction field element
- Files modified: qseries/_conversion.py, tests/test_conversion.py
- Commit: c9c53dc

**3. [Rule 1 - Bug] mprodmake used T argument instead of series precision**
- Found during: Task 1 (last exponent q^17 was missing from result)
- Issue: series.add_bigoh(T=17) truncated away q^17 term; greedy loop couldn't see it
- Fix: use input series prec as working_prec; limit recorded exponents to k <= T
- Files modified: qseries/_conversion.py
- Commit: c9c53dc

## Known Stubs

- `zqfactor`: documented stub, returns None + UserWarning. Full bivariate factorization planned for Phase 5. Test verifies no crash.

## Self-Check: PASSED

- qseries/_conversion.py: exists and contains all 10 functions
- qseries/__init__.py: exports MProduct, QFactorResult, all 10 new function names
- tests/test_conversion.py: 14 tests, 0 skipped
- Commits: c9c53dc present in git log
