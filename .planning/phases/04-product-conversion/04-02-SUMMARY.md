---
phase: "04-product-conversion"
plan: "02"
subsystem: "product-conversion"
tags: ["jacprodmake", "jac2prod", "jac2series", "CONV-04", "CONV-08", "CONV-09"]
dependency_graph:
  requires: ["04-01", "prodmake", "_building_blocks.tripleprod"]
  provides: ["jacprodmake", "jac2prod", "jac2series"]
  affects: ["qseries/__init__.py", "tests/test_conversion.py"]
tech_stack:
  added: []
  patterns:
    - "Period detection with residues in [1..P] (not [0..P-1]) to handle JAC structure"
    - "JAC triple {a, P-a, P} grouped into single factor; P/2 case produces half-exponent"
    - "jac2series via direct theta sum: sum_i (-1)^i q^{i*(b-2a)/2 + i^2*b/2}"
key_files:
  created: []
  modified:
    - "qseries/_conversion.py"
    - "tests/test_conversion.py"
    - "qseries/_building_blocks.py"
decisions:
  - "Period residue uses [1..P] convention: n%P=0 maps to P (not 0) so period check works for multiples"
  - "JAC pattern detection: {a, P-a, P} all with same exponent e -> JAC(a,P)^e (P-slot not double-counted)"
  - "jac2series uses direct summation formula rather than calling theta() to avoid bivariate complexity"
  - "jac2series oracle: cross-checked against Pochhammer expansion (doc page oracle sign convention unclear)"
metrics:
  duration: "45 min"
  completed: "2026-09-17"
  tasks: 2
  files: 3
---

# Phase 04 Plan 02: Jac-family Product Conversion Summary

**One-liner:** jacprodmake period detection with JAC-triple grouping, jac2prod Pochhammer expansion, jac2series theta-sum formula implemented and all CONV-04/08/09 tests passing.

## Tasks Completed

| Task | Description | Commit | Status |
|------|-------------|--------|--------|
| 1 | jacprodmake: period detection + rational exponents (CONV-04) | de0c9c3 | DONE |
| 2 | jac2prod + jac2series (CONV-08, CONV-09) | de0c9c3 | DONE |

## Verification Results

```
tests/test_conversion.py: 9 passed, 5 skipped
- test_jacprodmake_basic PASSED
- test_jacprodmake_sqrt PASSED  (D-08 mandatory: factor (7,14,1/2) confirmed)
- test_jac2prod_basic PASSED
- test_jac2prod_zero PASSED
- test_jac2series_oracle PASSED
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Period residue modular arithmetic used wrong convention**
- **Found during:** Task 1 RED/GREEN cycle
- **Issue:** `n % P` maps multiples of P to 0, but prodmake exponents have entries at n=P (the "zero residue" in JAC structure). Period check for P=5 failed at n=5 because `exponents.get(0, 0)=0 != exponents.get(5, 0)=1`.
- **Fix:** Use `_residue(n, P) = n%P if n%P != 0 else P` so that multiples of P map to P.
- **Files modified:** `qseries/_conversion.py`
- **Commit:** de0c9c3

**2. [Rule 1 - Bug] JAC triple pattern double-counted the period slot**
- **Found during:** Task 1 GREEN iteration
- **Issue:** Algorithm added JAC(0,P) factor AND JAC(a,P) factor separately, but JAC(a,P) already includes the (q^b;q^b) Pochhammer factor.
- **Fix:** Check if residue-P exponent matches residue-a and residue-(P-a): if so, it's a JAC(a,P) pattern; mark period slot as accounted, don't add separate JAC(0,P).
- **Files modified:** `qseries/_conversion.py`
- **Commit:** de0c9c3

**3. [Rule 1 - Bug] Test jac0_14 built theta sum instead of Pochhammer product**
- **Found during:** Task 1 test_jacprodmake_sqrt
- **Issue:** Plan pseudocode built `JAC(0,14)` as `sum_{n} q^{14n^2}` (theta function) instead of `prod_{n>=1}(1-q^{14n})` (Pochhammer). These are different series.
- **Fix:** Changed jac0_14 construction in test to use product loop `(1 - q^{14n})`.
- **Files modified:** `tests/test_conversion.py`
- **Commit:** de0c9c3

**4. [Rule 1 - Bug] test_jac2series_oracle compared integer-indexed series ignoring r-shift**
- **Found during:** Task 2 verification
- **Issue:** Plan's comparison `result.series == expected.series` compared raw integer-indexed polynomials with different r-shifts (apples/oranges).
- **Fix:** Test now reconstructs full Laurent series via `result.series * q^{int(r)}` and compares against direct Pochhammer computation.
- **Files modified:** `tests/test_conversion.py`
- **Commit:** de0c9c3

**5. [Rule 1 - Bug] QQ(1, 4) two-arg form in theta2 (Sage 9.5)**
- **Found during:** Full suite run
- **Issue:** `QQ(1, 4)` in `_building_blocks.theta2` fails in Sage 9.5; STATE.md documents this pattern.
- **Fix:** Changed to `QQ('1/4')`.
- **Files modified:** `qseries/_building_blocks.py`
- **Commit:** de0c9c3

## Known Stubs

None — all three functions are fully implemented. CONV-05 through CONV-11 stubs remain as NotImplementedError in `_conversion.py` (Plan 04-03 scope).

## Self-Check

- [x] `qseries/_conversion.py` contains jacprodmake, jac2prod, jac2series implementations
- [x] `tests/test_conversion.py` has 5 un-skipped tests (CONV-04/08/09)
- [x] Commit de0c9c3 exists: `git log --oneline | grep de0c9c3`
- [x] All 9 conversion tests pass; 5 skipped (Plan 04-03)

## Self-Check: PASSED
