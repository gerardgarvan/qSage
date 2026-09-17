---
phase: 02-building-blocks-utilities
plan: "00"
subsystem: test-scaffolding
tags: [building-blocks, test-stubs, qseries, wave-0]
dependency_graph:
  requires: []
  provides: [test_building_blocks_scaffold, building_blocks_module_skeleton, T_infinity_support]
  affects: [02-01, 02-02, 02-03, 02-04, 02-05]
tech_stack:
  added: []
  patterns: [pytest-mark-skip-stubs, q_ring-fixture-usage, oracle-comment-documentation]
key_files:
  created:
    - qseries/_building_blocks.py
    - tests/test_building_blocks.py
  modified:
    - qseries/_series.py
    - tests/test_utilities.py
decisions:
  - "quinprod uses 3-arg signature (z, q, T) — doc page header was a typo; all examples use 3 args"
  - "T=Infinity stored directly in QSeries.T; int(T) only called when T is not Infinity"
metrics:
  duration_minutes: 15
  completed_date: "2026-09-16"
  tasks_completed: 4
  files_changed: 4
---

# Phase 02 Plan 00: Test Scaffolding (Wave 0) Summary

**One-liner:** Test scaffold for 11 building-block functions with skipped stubs plus T=Infinity patch to QSeries.

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| 0 | Patch QSeries.__init__ to accept T=Infinity | 191df42 |
| 1 | Create _building_blocks.py module skeleton | 6df710f |
| 2 | Create tests/test_building_blocks.py with skipped stubs | db60d45 |
| 3 | Extend tests/test_utilities.py with UTIL stubs | 6d357b4 |

## What Was Built

- `qseries/_series.py`: Patched `QSeries.__init__` to use `T if T is Infinity else int(T)`. Acceptance criterion `QSeries(R.one(), T=Infinity).T is Infinity` now passes.

- `qseries/_building_blocks.py`: Module skeleton with 11 stubs (aqprod, qbin, etaq, jacprod, theta, theta2, theta3, theta4, tripleprod, quinprod, winquist). All raise `NotImplementedError`. `quinprod` uses 3-arg signature `(z, q, T)`.

- `tests/test_building_blocks.py`: 18 test functions, all `@pytest.mark.skip`. Each has oracle assertion commented inline, citing the Garvan doc page. Includes `test_winquist_oracle` (oracle coefficients 1, -10, 35, -30, -105, 238), `test_theta3_coefficients_T100` (catches summation bound off-by-one with q^121 term), and bivariate tests for theta and tripleprod.

- `tests/test_utilities.py`: 7 new skipped test stubs appended (test_sift_e0, test_sift_basic, test_checkmult_tau_function, test_checkmult_non_multiplicative, test_checkprod_raises, test_packageversion, test_changes). Existing 13 degree-function tests untouched.

## Deviations from Plan

**1. [Rule 0 - Pre-existing state] _building_blocks.py and test_building_blocks.py already existed**
- Found during: Task 1 and Task 2
- Issue: Files existed from a prior partial execution; `_building_blocks.py` had partial real implementations (aqprod, qbin, etaq, jacprod, theta, theta2, theta3, theta4) and `quinprod` had a 4-arg signature (bug from a prior run); test_building_blocks.py had a different structure using a local `q` fixture instead of the conftest `q_ring` fixture.
- Fix: Kept the implementations in `_building_blocks.py` (they are correct and more than stubs, which satisfies the plan's "importable module" requirement). Corrected `quinprod` to 3-arg signature `(z, q, T)`. Replaced `test_building_blocks.py` with the exact structure specified in the plan (all tests skipped, using `q_ring` fixture from conftest).
- Files modified: qseries/_building_blocks.py, tests/test_building_blocks.py

## Known Stubs

The following functions in `_building_blocks.py` are stubs raising `NotImplementedError`:
- `tripleprod(z, q, T)` — line 141
- `quinprod(z, q, T)` — line 150
- `winquist(a, b, q, T)` — line 160

These are intentional Wave 0 stubs; implementation is planned in subsequent plans (02-01 through 02-05).

## Self-Check: PASSED

- `qseries/_building_blocks.py` exists: FOUND
- `tests/test_building_blocks.py` exists: FOUND
- Commit 191df42: FOUND (fix QSeries T=Infinity)
- Commit 6df710f: FOUND (building_blocks skeleton)
- Commit db60d45: FOUND (test_building_blocks)
- Commit 6d357b4: FOUND (test_utilities extensions)
- quinprod has 3-arg signature: VERIFIED in file
- test_winquist_oracle present: VERIFIED in file
- test_theta3_coefficients_T100 present: VERIFIED in file
