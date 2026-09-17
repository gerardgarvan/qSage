---
phase: "03-prodmake-andrews-algorithm"
plan: "01"
subsystem: "product-conversion"
tags: ["prodmake", "andrews-algorithm", "checkprod", "qproduct"]
dependency_graph:
  requires: []
  provides: ["prodmake", "checkprod-impl"]
  affects: ["Phase 4 etamake/qetamake/jacprodmake"]
tech_stack:
  added: ["sage.all.divisors"]
  patterns: ["Andrews divisor-sum recurrence", "QProduct sign convention e_n=-a_n"]
key_files:
  created:
    - "qseries/_prodmake.py"
    - "tests/test_prodmake.py"
  modified:
    - "qseries/_utilities.py"
    - "qseries/__init__.py"
    - "tests/test_utilities.py"
decisions:
  - "QProduct exponents store e_n = -a_n (Maple a_n from f=prod(1-q^n)^(-a_n))"
  - "Rogers-Ramanujan G-series has exponents -1 (reciprocal product), not +1"
  - "q argument to prodmake unused in recurrence; None is acceptable from checkprod"
  - "Pre-existing test_building_blocks failures (5) are out of scope"
metrics:
  duration: "25 min"
  completed: "2026-09-16"
  tasks: 2
  files: 5
requirements_satisfied: ["CONV-01"]
---

# Phase 03 Plan 01: prodmake (Andrews' Algorithm) Summary

**One-liner:** Andrews' two-step divisor-sum recurrence recovering QProduct exponent sequence from truncated q-series, with checkprod stub replaced.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Implement prodmake in qseries/_prodmake.py | b97cb68 | qseries/_prodmake.py, tests/test_prodmake.py |
| 2 | Fill checkprod stub and wire prodmake into __init__.py | 88d4e98 | qseries/_utilities.py, qseries/__init__.py, tests/test_utilities.py |

## What Was Built

### prodmake(f, q, T)

Implements Andrews' divisor-sum recurrence from Garvan's tutorial §3:

**Step 1** — auxiliary sequence c_n:
```
c_n = n*b_n - sum_{k=1}^{n-1} b_{n-k} * c_k
```

**Step 2** — exponent recovery:
```
a_n = (c_n - sum_{d|n, d<n} d*a_d) / n
```

Returns `QProduct(exponents={n: -a_n for n where a_n != 0})`.

### checkprod(f, M, Q)

Replaced the Phase 2 `NotImplementedError` stub. Calls `prodmake(f, None, Q)`, checks all `|e_n| <= M`, returns `[1, exp_list]` or `False`.

### Exports

`prodmake` added to `qseries/__init__.py` and `__all__`.

## Sign Convention (Key Decision)

The plan's behavior block had an ambiguity in the Rogers-Ramanujan expected exponents. Resolved by testing:

- Maple: `f = prod(1-q^n)^(-a_n)` 
- QProduct: stores `e_n = -a_n`
- G(q) = `1/prod_{n≡±1 mod 5}(1-q^n)` — the **reciprocal** product
- Therefore `a_n = 1` for those n, and `e_n = -1`

The plan specified `{1:1, 4:1, ...}` but the correct values are `{1:-1, 4:-1, ...}`. Corrected in test oracle before writing the final test.

## Verification Results

All plan success criteria met:

1. `sage -python -m pytest tests/test_prodmake.py` — **8 passed, 0 failed**
2. Full suite (excluding pre-existing failures) — **70 passed, 0 failed**
3. Round-trip `prodmake(etaq(q,1,20), q, 20).to_series(20)` — **OK**
4. Rogers-Ramanujan exponents `{1:-1, 4:-1, 6:-1, 9:-1, 11:-1, 14:-1, 16:-1, 19:-1}` — **exact match**
5. `ValueError` for `r != 0` and constant term `!= 1` — **both pass**
6. `checkprod` no longer raises `NotImplementedError` — **confirmed**
7. `from qseries import prodmake` — **works**

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Rogers-Ramanujan expected exponent signs corrected**
- **Found during:** Task 1 GREEN phase
- **Issue:** Plan behavior block specified expected exponents `{1:1, 4:1, ...}` but G(q) is a reciprocal product, giving actual exponents `{1:-1, 4:-1, ...}`
- **Fix:** Corrected test oracle to `{1:-1, 4:-1, 6:-1, 9:-1, 11:-1, 14:-1, 16:-1, 19:-1}` with explanation in comment
- **Files modified:** tests/test_prodmake.py

**2. [Rule 1 - Bug] test_utilities.py::test_checkprod_raises updated for Phase 3**
- **Found during:** Task 2 full suite run
- **Issue:** Old test expected `NotImplementedError` from checkprod stub; now real implementation raises `AttributeError` when passed `None`
- **Fix:** Updated to accept `(AttributeError, TypeError, ValueError)` 
- **Files modified:** tests/test_utilities.py

**3. [Out of scope] Pre-existing failures in test_building_blocks.py**
- 5 pre-existing failures (`test_aqprod_zero_n`, `test_theta_bivariate_type`, `test_theta2_shift`, `test_theta2_coefficients`, `test_tripleprod_bivariate_type`) confirmed present before this plan's changes via `git stash` verification.
- Not fixed — out of scope per deviation rules. Logged here for tracking.

## Known Stubs

None — prodmake is fully implemented. checkprod stub is now fully replaced.

## Self-Check: PASSED

- `qseries/_prodmake.py` exists: FOUND
- `tests/test_prodmake.py` exists: FOUND
- Commit b97cb68 exists: FOUND
- Commit 88d4e98 exists: FOUND
- `from qseries import prodmake` works: CONFIRMED
- `from qseries import checkprod` returns real implementation: CONFIRMED
