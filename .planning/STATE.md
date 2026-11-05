---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_plan: 3
status: Executing Phase 04
stopped_at: Phase 5 complete
last_updated: "2026-11-05T20:44:10.000Z"
progress:
  total_phases: 7
  completed_phases: 5
  total_plans: 16
  completed_plans: 16
---

# State: qseries-sage

**Docs:** `.planning/PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `REFERENCE.md` (verified Maple signatures/oracles — read before planning any phase).

## Position

Phase 1 complete (2026-09-16). Phase 2 complete. Phase 3 plan 01 complete. Progress 2/7.

Current Plan: 3
Last session: 2026-11-05T20:44:10.000Z
Stopped At: Phase 5 complete; next: plan Phase 6

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

- Phase 5: all exact relation finders live in `_relations.py` and share `_kernel_search` (monomials via `IntegerVectors`, `matrix(QQ, rows).left_kernel()`, polynomials in `X1..Xk`).
- Phase 5: N = rows + C + topshift with C = 21 (findhom/findnonhom) and C = 20 (combo variants); confirmed by tutorial term counts 25, 31, 61 and `findnonhomcombo` 42 / `matrix is , 37, x, 42`.
- Phase 5: q-shifts aligned in `_coefficient_rows` (shifts must differ by integers; common fractional part dropped); coefficients read from the minimum valuation so negative leading powers work.
- Phase 5: `etamake` imported lazily (only for etaoption='yes'); `topshift > -20` enforced.
- Phase 5: `findhomcombo`/`findnonhomcombo` return every combination with non-zero f coefficient; when f is itself a monomial the trivial combination is returned too (doc page allows several).
- Phase 5: `findcong` implication filter (A2 | A, B = B2 mod A2, M | M2) reproduces the oracle as written.
- Phase 2 fixes (2026-11-05): `(-1)**(n % 2)` for exact signs in `theta4`/`tripleprod` (`(-1)**n` with n < 0 is a float -> RDF series); `aqprod` starts at `parent(q).one()`; `theta` gets bivariate z coercion; tests: `QQ('1/4')`, tripleprod q^0 coefficient is `1 - z`.

- Phase 2 follow-up (2026-11-05): `etaq` starts from `1 + O(q^T)` so partial products stay truncated (etaq(q,1,1001): ~100 s -> under a second); `theta2(q^k)` sets r = k/4 via `_theta2_shift` (warns and uses 1/4 if the argument is not a power of the generator).

## Pending

- Package name `qseries` vs `qseries_sage` (before Phase 7).
- Merge Phase 6 into Phase 5: resolved - kept separate (05-CONTEXT D-01).


## Risks

- `prodmake` (recurrence, no linear algebra) is the highest-risk item.
- Oracle discipline: expected values from Maple docs only.
- Sage 9.5 may lack `nth_root` on Laurent series (needed for rational `JAC` exponents); upgrade via conda-forge if hit.
