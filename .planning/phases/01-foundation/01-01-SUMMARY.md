---
phase: 01-foundation
plan: 01
subsystem: series-core
tags: [qseries, QSeries, package-scaffold, TDD, LaurentSeriesRing]
dependency_graph:
  requires: []
  provides: [QSeries, pyproject.toml, qseries-package]
  affects: [all-subsequent-phases]
tech_stack:
  added: [setuptools>=68, pytest, LaurentSeriesRing]
  patterns: [QSeries-wrapper, pluggable-ring-R, rational-shift-r, T-from-prec]
key_files:
  created:
    - qseries/_series.py
    - qseries/__init__.py
    - pyproject.toml
    - tests/test_series.py
    - tests/conftest.py
  modified: []
decisions:
  - "LaurentSeriesRing (not PowerSeriesRing) as underlying Sage primitive — supports negative exponents and bivariate rings (D-03)"
  - "T = result.prec() after each operation, not hardcoded min(T1, T2) (D-13)"
  - "_align_shifts: integer shift diff allowed in add/sub; non-integer raises ValueError (D-12)"
  - "Clean reimplementation from docs only, block comment in _series.py cites Garvan URL (D-01, D-02)"
metrics:
  duration: "~15 minutes"
  completed: "2026-09-16"
  tasks: 2
  files: 5
---

# Phase 01 Plan 01: Package Scaffold and QSeries Wrapper Summary

**One-liner:** Package scaffold with QSeries wrapper using LaurentSeriesRing over pluggable ring R, explicit truncation T from Sage's actual precision, and rational shift r for fractional q-power support.

## What Was Built

### Task 1: Package Scaffold

- `pyproject.toml` — setuptools>=68 build backend, name=qseries-sage, version=1.3.0, requires-python>=3.10, dependencies=[] (SageMath is runtime not pip dep)
- `qseries/__init__.py` — stub importing QSeries, __version__="1.3.0", __all__=["QSeries"]

### Task 2: QSeries Wrapper (TDD)

- `qseries/_series.py` — QSeries class with:
  - Licensing block comment citing `https://qseries.org/fgarvan/qmaple/qseries/` (clean reimplementation, no Maple source consulted)
  - `__init__(series, T=20, r=None, R=None)`: stores `.series`, `.T`, `.r` (as QQ rational), `.R` (inferred from series parent's base ring)
  - `_wrap(result, r, R)`: wraps raw Sage LaurentSeries; T = int(result.prec())
  - `_align_shifts(other)`: integer-shift-diff add/sub; raises ValueError for non-integer diff
  - `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__neg__`, `__radd__`, `__rsub__`, `__rmul__`
  - `__repr__` showing q^(r) * series when r != 0
  - `__eq__` and `__hash__ = None`
- `tests/test_series.py` — 13 tests covering all behaviors listed in plan
- `tests/conftest.py` — sys.path insertion so qseries is importable without install

### QSeries.__init__ Signature

```python
def __init__(self, series, T=20, r=None, R=None):
```

- `series`: Sage LaurentSeries element
- `T`: int, truncation order; stored as `int(T)`
- `r`: rational shift (stored as `QQ(r)`); default 0
- `R`: coefficient ring; inferred from `series.parent().base_ring()` if not supplied

### Truncation Propagation

T after any operation is `int(result.prec())` where `result` is the raw Sage LaurentSeries. Sage naturally truncates to `min(T1, T2)` for addition and subtraction; for division it may reduce further. Tests assert `result.T == int(result.series.prec())`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `LaurentSeriesRing.O(N)` not available in Sage 9.5**
- **Found during:** Task 2 test runs
- **Issue:** Tests used `L.O(20)` (Sage's `PowerSeriesRing` syntax) but `LaurentSeriesRing` in Sage 9.5 has no `.O()` method
- **Fix:** Replaced all `X + L.O(N)` with `X.add_bigoh(N)` in `tests/test_series.py`
- **Files modified:** `tests/test_series.py`
- **Commit:** 7eb627f

**2. [Rule 2 - Missing] conftest.py needed for sys.path**
- **Found during:** Task 2 verification — `sage -c "from qseries import QSeries"` failed when not installed
- **Fix:** Added `tests/conftest.py` that inserts project root into sys.path
- **Files modified:** `tests/conftest.py` (new)
- **Commit:** 7eb627f

## Known Stubs

None — QSeries is fully implemented. `qseries/__init__.py` intentionally exports only QSeries at this stage; other exports added in Plan 03.

## Self-Check: PASSED
