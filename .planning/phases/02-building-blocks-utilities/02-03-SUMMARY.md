---
phase: 02-building-blocks-utilities
plan: "03"
subsystem: utilities
tags: [sift, checkmult, checkprod, packageversion, changes, exports, phase2-complete]
dependency_graph:
  requires: ["02-02"]
  provides: [UTIL-01, UTIL-05, UTIL-06, UTIL-07, UTIL-08, package-exports]
  affects: [qseries/__init__.py, qseries/_utilities.py, qseries/_series.py]
tech_stack:
  added: []
  patterns:
    - "sift extracts residue class using s.series.parent() to preserve GF(p) coefficient ring"
    - "checkmult skips pairs at/beyond precision boundary (avoids false-negative from truncation)"
    - "QSeries.__pow__ added for integer exponentiation (required by checkmult tau test)"
key_files:
  created: []
  modified:
    - qseries/_utilities.py
    - qseries/_series.py
    - qseries/__init__.py
    - tests/test_utilities.py
decisions:
  - "checkmult skips (m,n) pairs where m, n, or m*n is at/beyond series precision to avoid false negatives from truncation"
  - "tau multiplicativity test uses shifted series (q * etaq^24) so tau(n) sits at index n"
  - "QSeries.__pow__ added as missing critical functionality (Rule 2); iterative multiplication over QQ rings"
  - "2 pre-existing test_building_blocks failures (tripleprod/quinprod bivariate) logged as deferred, out of 02-03 scope"
metrics:
  duration: "20 min"
  completed: "2026-09-17"
  tasks: 2
  files_modified: 4
---

# Phase 02 Plan 03: Utilities Completion Summary

**One-liner:** Five new utility functions (sift, checkmult, checkprod stub, packageversion, changes) added to `_utilities.py`; `__init__.py` extended to export all 19 Phase 2 names from the `qseries` package.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Implement sift, checkmult, checkprod, packageversion, changes | f684709 | qseries/_utilities.py, qseries/_series.py, tests/test_utilities.py |
| 2 | Extend __init__.py to export all Phase 2 names | b7278ec | qseries/__init__.py |

## Verification Results

- `sage -python -m pytest tests/test_utilities.py -q` — 24 passed, 0 failed
- `sage -python -m pytest tests/ -q` — 66 passed, 17 skipped, 2 pre-existing failures (out of scope)
- All 19 Phase 2 names importable from `qseries` package

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical Functionality] Added QSeries.__pow__**
- **Found during:** Task 1, when test_checkmult_tau_function called `etaq(q, 1, T) ** 24`
- **Issue:** QSeries had no `__pow__` method; `**` raised TypeError
- **Fix:** Added `__pow__` with iterative multiplication, non-negative integer exponents only
- **Files modified:** qseries/_series.py
- **Commit:** f684709

**2. [Rule 1 - Bug] Fixed checkmult precision guard**
- **Found during:** Task 1, when checkmult(tau, 30) returned False despite tau being multiplicative
- **Issue:** Original guard used 0 for out-of-precision coefficients, causing false inequality when m*n = prec (truncated to 0 instead of actual value)
- **Fix:** Skip pairs where any of m, n, m*n is at or beyond series precision
- **Files modified:** qseries/_utilities.py
- **Commit:** f684709

**3. [Rule 1 - Bug] Fixed tau multiplicativity test indexing**
- **Found during:** Task 1, when test_checkmult_tau_function failed even after precision fix
- **Issue:** `etaq(q,1,T)**24` has `tau(n+1)` at index n (0-indexed); checkmult needs `tau(n)` at index n
- **Fix:** Test now uses `q * etaq(q,1,T)**24` series (= Delta(q)), placing tau(n) at index n
- **Files modified:** tests/test_utilities.py
- **Commit:** f684709

### Deferred (Out of Scope)

Pre-existing failures from 02-02 plan: `test_tripleprod_bivariate_type` and `test_quinprod_series` fail due to bivariate ring coercion issues in `_building_blocks.py`. Logged to `deferred-items.md`. These tests were unskipped in 02-02; they are not caused by 02-03 changes.

## Known Stubs

- `checkprod(f, M, Q)` — raises `NotImplementedError` with message referencing prodmake. Intentional; Phase 3 will implement it. Exported per D-09 so callers get a clear error rather than ImportError.

## Self-Check: PASSED

- `qseries/_utilities.py` — exists, contains sift/checkmult/checkprod/packageversion/changes
- `qseries/__init__.py` — exports all 19 names
- `tests/test_utilities.py` — 24 tests all passing
- Commits f684709 and b7278ec exist in git log
