---
phase: "02"
plan: "04"
subsystem: building-blocks
tags: [gap-closure, tests, requirements]
dependency_graph:
  requires: [02-01, 02-02, 02-03]
  provides: [active-BUILD-tests]
  affects: [REQUIREMENTS.md]
tech_stack:
  added: []
  patterns: []
key_files:
  modified:
    - tests/test_building_blocks.py
    - .planning/REQUIREMENTS.md
decisions: []
metrics:
  duration: "5 min"
  completed: "2026-09-16"
  tasks_completed: 2
  files_modified: 2
---

# Phase 02 Plan 04: Gap Closure — Unskip BUILD-01..08 Tests Summary

**One-liner:** Removed 17 stale `@pytest.mark.skip` decorators from BUILD-01..08 test functions and marked all 11 BUILD requirements as complete in REQUIREMENTS.md.

## What Was Done

Both tasks executed cleanly with no deviations.

### Task 1: Remove @pytest.mark.skip from BUILD-01..08 test functions

Deleted the `@pytest.mark.skip(reason="stub: implement after _building_blocks.py")` decorator line from all 17 BUILD-01..08 test functions in `tests/test_building_blocks.py`:

- BUILD-01: `test_aqprod_basic`, `test_aqprod_zero_n`, `test_aqprod_tutorial_canonical`
- BUILD-02: `test_qbin_33_66`, `test_qbin_boundary`, `test_qbin_out_of_range`
- BUILD-03: `test_etaq_k1`, `test_etaq_k2`
- BUILD-04: `test_jacprod_basic`
- BUILD-05: `test_theta_z_minus1`, `test_theta_bivariate_type`
- BUILD-06: `test_theta2_shift`, `test_theta2_coefficients`
- BUILD-07: `test_theta3_coefficients`, `test_theta3_coefficients_T100`, `test_theta3_theta4_product_identity`
- BUILD-08: `test_theta4_coefficients`

No test logic, assertions, imports, or comments were changed. BUILD-09..11 tests were left unchanged (they had no skip decorators).

Verified: `grep pytest.mark.skip tests/test_building_blocks.py` returns 0 matches.

### Task 2: Mark BUILD-01..11 as complete in REQUIREMENTS.md

Changed all 11 `- [ ] **BUILD-XX**` lines to `- [x] **BUILD-XX**` in the Building Blocks section of `.planning/REQUIREMENTS.md`.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. The tests now actively call the implementations in `qseries/_building_blocks.py`. The `test_theta_bivariate_type` test may fail if the bivariate coercion fix is incomplete; if so, it will be visible as a failure (not a skip) and addressed in 02-05 per the plan's instructions.

## Self-Check: PASSED

- `tests/test_building_blocks.py` modified: confirmed (23 lines deleted — 17 decorator lines + blank lines)
- `.planning/REQUIREMENTS.md` modified: confirmed (11 `[ ]` → `[x]` changes)
- Commit `0105432`: feat(02-04): remove 17 @pytest.mark.skip decorators from BUILD-01..08 tests
- Commit `e21f093`: chore(02-04): mark BUILD-01..11 as complete in REQUIREMENTS.md
