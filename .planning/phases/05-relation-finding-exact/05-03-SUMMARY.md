---
phase: 05-relation-finding-exact
plan: 03
status: complete
completed: 2026-11-05
requirements: [REL-09, REL-10, REL-11]
files_modified: [qseries/_relations.py, qseries/__init__.py, tests/test_relations.py]
---

# 05-03 Summary: findmaxind, findpoly, findcong + package exports

## Results

- `findmaxind([f1, f2, f1+f2], 0)` → `[[f1, f2], [1, 2]]`; a dependent middle element is
  skipped (`[1, 2, 4]`). Greedy incremental `matrix(QQ, rows).rank()`.
- `findpoly(x, y, q, 3, 1, 60)` (tutorial §4.5, Borwein cubic theta functions) returns one
  relation proportional to `(X+6)³Y − 27(X+2)²`, verified to O(q^60).
  `x = θ2(q)²/θ2(q³)² + θ3(q)²/θ3(q³)²`, `y = c³/a³` (θ3 version confirmed; θ4 gives none).
- `findcong(1/etaq(q,1,1001), 1000)` == `{(4,5,5), (5,7,7), (6,11,11), (24,25,25)}`.
  The `_suppress_implied` direction in the stub (`A2 | A`, `B ≡ B2 mod A2`, `M | M2`)
  reproduced the oracle as written, so no inversion was needed. `XSET={5}` drops `(4,5,5)`.
- `__init__.py` imports and adds all 8 names to `__all__`.

Test file: 15 tests, all passing (≈1:45, dominated by building `etaq(q,1,1001)`).

## Deviations

- `findpoly(..., check)`: N stays `rows + 21`; the check re-reads coefficients up to
  `q^(check-1)` and confirms every kernel vector vanishes (raises `ValueError` otherwise),
  instead of inflating N to `check + 1`.
- Plan's findpoly test used eta-quotients for x, y that are not the tutorial's; replaced with
  the tutorial §4.5 construction.

## Issues found in earlier phases (not fixed here)

1. **`theta2(q**k, T)` keeps `r = 1/4`** for every k; the shift should be `k/4`. The findpoly
   test works around it with `theta2_q3`. Needs a Phase 2 fix (theta2 can't see k from a
   substituted series; likely needs an explicit argument or detecting `q^k`).
2. **`etaq` is slow at large T**: it multiplies exact polynomials and truncates only at the
   end; `etaq(q, 1, 1001)` takes ~100 s. Truncating with `add_bigoh(T)` inside the loop would
   fix it.

## Not verified here

Run in a passagemath/Sage 10.x environment with a local copy of `_series.py` and the four
building blocks used by the tests. The full repository suite (`sage -python -m pytest`) on
Sage 9.5 in WSL still needs to be run.
