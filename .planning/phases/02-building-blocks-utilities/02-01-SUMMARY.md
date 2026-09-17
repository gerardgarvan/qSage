---
phase: 02-building-blocks-utilities
plan: "01"
subsystem: math
tags: [sage, q-series, building-blocks, aqprod, qbin, etaq, jacprod, theta]

requires:
  - phase: 02-00
    provides: test scaffolding and _building_blocks.py skeleton

provides:
  - 8 core building-block functions implemented and tested (aqprod, qbin, etaq, jacprod, theta, theta2, theta3, theta4)
  - BUILD-01 through BUILD-08 tests passing

affects: [02-02, 02-03]

tech-stack:
  added: []
  patterns:
    - compute on caller's q/z — no internal LaurentSeriesRing construction
    - exact polynomial result uses T=Infinity
    - truncated result uses add_bigoh(T)

key-files:
  created: []
  modified:
    - qseries/_building_blocks.py
    - tests/test_building_blocks.py

key-decisions:
  - "All 8 functions compute on the caller's arguments; Sage coercion determines the parent ring"
  - "aqprod result initialized as 1+0*q to avoid plain int when n=0"
  - "QQ('1/4') used instead of QQ(1,4) two-arg form (Sage 9.5 compatibility)"
  - "theta bivariate: LaurentPolynomialRing * LaurentSeriesRing coercion — fixed by building bivariate ring internally when z is a LaurentPolynomialRing_generic element"

patterns-established:
  - "Import from sage.all, not sage submodules (avoids import errors on Sage 9.5)"
  - "theta3/theta4 summation bound: isqrt(T)+1 (not isqrt(T))"

requirements-completed: [BUILD-01, BUILD-02, BUILD-03, BUILD-04, BUILD-05, BUILD-06, BUILD-07, BUILD-08]

duration: 25min
completed: "2026-09-17"
---

# Phase 02-01: Core Building Blocks Summary

**8 q-series primitives implemented (aqprod, qbin, etaq, jacprod, theta, theta2, theta3, theta4) — all BUILD-01..08 tests pass with Sage 9.5 compatibility fixes**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- aqprod, qbin, etaq, jacprod implemented with exact/truncated semantics
- theta, theta2 (with r=QQ(1/4) shift), theta3, theta4 implemented with correct summation bounds
- All 17 tests passing; BUILD-09..11 (bivariate) remain skipped for Wave 2

## Task Commits

1. **Task 1: Implement aqprod, qbin, etaq, jacprod** - `91a3585` (feat)
2. **Task 2: Implement theta, theta2, theta3, theta4; export building blocks** - `1aaa250` (feat)
3. **Plan metadata** - `4764710` (docs)

## Files Created/Modified
- `qseries/_building_blocks.py` — 8 functions implemented; stubs remain for Wave 2
- `tests/test_building_blocks.py` — BUILD-01..08 unskipped and passing

## Decisions Made
- QQ(1,4) two-arg form fails in Sage 9.5 — used QQ('1/4') string form
- aqprod(q, q, 0): initialized result as 1+0*q not plain int 1 to avoid subscript error
- theta bivariate coercion: when z is a LaurentPolynomialRing element, build bivariate ring internally

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] QQ(1,4) fails on Sage 9.5**
- **Issue:** QQ(1, 4) two-arg form raises TypeError in Sage 9.5
- **Fix:** QQ('1/4') string form works
- **Committed in:** 1aaa250

**2. [Rule 3 - Blocking] aqprod empty product returns plain int**
- **Issue:** aqprod(q, q, 0) returned int 1, not subscriptable
- **Fix:** Initialize result = 1 + 0*q so result is always a ring element
- **Committed in:** 91a3585

---

**Total deviations:** 2 auto-fixed (Sage 9.5 compatibility, ring element initialization)
**Impact on plan:** All auto-fixes necessary for correctness. No scope creep.

## Issues Encountered
None beyond the auto-fixed Sage 9.5 compatibility issues.

## Next Phase Readiness
- All 8 core building-block primitives ready for Wave 2 (bivariate functions)
- Tests for tripleprod/quinprod/winquist remain skipped, awaiting 02-02

---
*Phase: 02-building-blocks-utilities*
*Completed: 2026-09-17*
