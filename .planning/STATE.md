---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_plan: 2
status: Executing Phase 03
last_updated: "2026-09-17T03:20:00.000Z"
progress:
  total_phases: 7
  completed_phases: 2
  total_plans: 10
  completed_plans: 10
---

# State: qseries-sage

**Docs:** `.planning/PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `REFERENCE.md` (verified Maple signatures/oracles — read before planning any phase).

## Position

Phase 1 complete (2026-09-16). Phase 2 complete. Phase 3 plan 01 complete. Progress 2/7.

Current Plan: 2
Last session: 2026-09-17T03:20:00.000Z
Stopped At: Completed 03-01-PLAN.md

## Environment

Ubuntu WSL, apt SageMath 9.5, repo at `~/qSage`, tests via `sage -python -m pytest`. Import Sage names only from `sage.all`.

## Performance Metrics

| Phase | Plan | Duration | Tasks | Files |
|-------|------|----------|-------|-------|
| 02 | 00 | 15 min | 4 | 4 |
| 02 | 01 | 25 min | 2 | 4 |
| 03 | 01 | 25 min | 2 | 5 |

## Decisions (cumulative)

- Python on SageMath; full 41-function port; oracle = Maple docs + identity checks; explicit `T` everywhere.
- Licensing: clean reimplementation from docs, recorded in `_series.py` header. **Resolved.**
- `QSeries`: `LaurentSeriesRing(R,'q')`, pluggable `R`, rational shift `r`, `T = result.prec()`; must also accept `T = Infinity` for exact polynomials.
- Five symbolic classes (`QProduct`, `EtaProduct`, `EProduct`, `JacProduct`, `PochProduct`); trivial exponents suppressed; ` * ` join.
- `lqdegree`/`lqdegree0` v1.0 scope: `QSeries` and single symbolic objects, not symbolic sums.
- Relation finders return polynomials in `X1..Xk`.
- Building blocks compute on the caller's `z`, `q`; identity functions (`theta*`, `tripleprod`, `quinprod`, `winquist`) return exact Laurent polynomials with Maple's summation bounds; only `etaq`, `jacprod` truncate at `O(q^T)`.
- `quinprod(z, q, T)` — 3 args (doc-page header is a typo).
- `QSeries.T` accepts `Infinity` from `sage.all`; `int(T)` only called when T is a finite integer.
- `QQ(1, 4)` two-arg form fails in Sage 9.5; use `QQ('1/4')` or `1/QQ(4)` throughout.
- theta bivariate path: detect `LaurentPolynomialRing_generic` z parent, build `LaurentSeriesRing(Rz, 'q')` internally.
- theta3/theta4 summation bound: `isqrt(T)+1` (not `isqrt(T)`) to include n=8 for T=50, n=11 for T=100.
- `checkmult` skips pairs where m, n, or m*n is at/beyond series precision (avoids false negatives from truncation).
- `QSeries.__pow__` added for non-negative integer exponents via iterative multiplication.
- tau multiplicativity test: use `q * etaq(q,1,T)**24` (= Delta) so tau(n) sits at index n.
- `prodmake`: QProduct exponents store e_n = -a_n (Maple a_n from f=prod(1-q^n)^(-a_n)); G-series has exponents -1 (reciprocal product).
- `prodmake`: q argument unused in recurrence; None is acceptable when called from checkprod.

## Pending

- Package name `qseries` vs `qseries_sage` (before Phase 7).
- Merge Phase 6 into Phase 5 (same code, ring parameterised) — decide at Phase 5 planning.

## Risks

- `prodmake` (recurrence, no linear algebra) is the highest-risk item.
- Oracle discipline: expected values from Maple docs only.
- Sage 9.5 may lack `nth_root` on Laurent series (needed for rational `JAC` exponents); upgrade via conda-forge if hit.
