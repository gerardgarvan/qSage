---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_plan: Not started
status: Ready to plan
stopped_at: Phase 5 context gathered
last_updated: "2026-09-17T14:54:40.592Z"
progress:
  total_phases: 7
  completed_phases: 4
  total_plans: 13
  completed_plans: 13
---

# State: qseries-sage

**Docs:** `.planning/PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `REFERENCE.md` (verified Maple signatures/oracles — read before planning any phase).

## Position

Phase 1 complete (2026-09-16). Phase 2 complete. Phase 3 plan 01 complete. Phase 4 complete. Progress 4/7.

Current Plan: Not started
Last session: 2026-09-17T14:54:40.587Z
Stopped At: Phase 5 context gathered

## Environment

Ubuntu WSL, apt SageMath 9.5, repo at `~/qSage`, tests via `sage -python -m pytest`. Import Sage names only from `sage.all`.

## Performance Metrics

| Phase | Plan | Duration | Tasks | Files |
|-------|------|----------|-------|-------|
| 02 | 00 | 15 min | 4 | 4 |
| 02 | 01 | 25 min | 2 | 4 |
| 03 | 01 | 25 min | 2 | 5 |
| Phase 04-product-conversion P01 | 25 min | 3 tasks | 3 files |
| Phase 04-product-conversion P02 | 45 min | 2 tasks | 3 files |
| Phase 04-product-conversion P03 | 45 min | 2 tasks | 4 files |

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
- `etamake` greedy: multiply residual by `etaq^(c_k)` to cancel `+c_k*q^k`; record `eta(k*tau)^(-c_k)`; `EtaProduct.r = r_input - sum(k*e_k/24)`.
- `theta2` etamake test: assert `constant==2` and numeric round-trip; `r` not gated per D-04/D-05 open question.
- `jacprodmake` period residue: use [1..P] convention (n%P==0 maps to P), not [0..P-1]; JAC(a,P) pattern detected when residues {a, P-a, P} all equal; period slot not double-counted.
- `jac2series` uses direct theta sum `sum_i (-1)^i q^{i*(b-2a)/2 + i^2*b/2}` (not bivariate theta call); cross-checked against Pochhammer expansion.
- `qfactor` accepts `(num_poly, den_poly)` tuple — Sage fraction field auto-simplifies, destroying factor structure; callers must pass unevaluated polynomials.
- `qfactor` algorithm: cyclotomic trial-division greedily identifies `(1-q^k)` factors from largest k to smallest.
- `mprodmake` uses input series precision (not T argument) as working precision; exponents recorded only for k <= T.
- `QSeries.__pow__` extended to support negative integer exponents via `series.__invert__()`.
- `zqfactor`: best-effort stub returning None + UserWarning; full bivariate factorization deferred to Phase 5 (CONV-07).

## Pending

- Package name `qseries` vs `qseries_sage` (before Phase 7).
- Merge Phase 6 into Phase 5 (same code, ring parameterised) — decide at Phase 5 planning.

## Risks

- `prodmake` (recurrence, no linear algebra) is the highest-risk item.
- Oracle discipline: expected values from Maple docs only.
- Sage 9.5 may lack `nth_root` on Laurent series (needed for rational `JAC` exponents); upgrade via conda-forge if hit.
