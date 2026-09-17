# Phase 1 plan review — fixes to apply before /gsd:execute-phase 1

Severity: **BLOCKER** = execution or verification will fail · **BUG** = wrong result, tests as written may still pass · **NOTE** = fidelity/hygiene.

## Cross-cutting

- **BLOCKER — environment.** Every `<verify>` runs `cd C:/qSage && sage -python …` in a Windows shell. SageMath 10.x has no native Windows build; it runs under WSL (or Linux/macOS). Either run the whole phase inside WSL with the repo on the Linux side, or prefix commands with `wsl -e bash -lc '…'`. Confirm `sage --version` works from the shell GSD will use before executing anything.
- **BLOCKER — 01-01 Task 1.** `build-backend = "setuptools.backends.legacy:build"` does not exist. Use `build-backend = "setuptools.build_meta"`. As written `sage -pip install .` fails.
- **BUG — 01-02 (twice).** `from sage.functions.other import qexp_eta` — wrong module (`qexp_eta` is in `sage.modular.etaproducts`). The import sits inside `EProduct.to_series` and `EtaProduct.to_series`, so both raise `ImportError` on first call. It is never used; delete both lines. STACK.md has the same wrong path.
- **NOTE.** 01-02 is `wave: 1, depends_on: []` but imports `QSeries` from 01-01 and its tests cannot run until `_series.py` exists. Either `depends_on: [01-01]` or accept that its verify step is meaningless until wave 1 finishes.

## 01-01 — QSeries

- **BUG — shift `r` is lost in arithmetic.** `_binop` returns `QSeries(result, T=T)`, so `r` and `R` reset to defaults; the scalar branches (`self.series + other`) ignore `r` too. `r` is the whole reason FOUND-02 exists. Required semantics:
  - `*` : `r = r1 + r2`;  `/` : `r = r1 − r2`
  - `+`, `−` : if `r1 == r2`, keep it; if `r1 − r2` is an integer `k`, shift one operand by `q^k` and use the smaller `r`; otherwise raise `ValueError` (Maple would return a symbolic sum — out of scope here).
  - scalar `+ c`: only valid when `r == 0` (or renormalise as above).
  - `R` must also be carried through; today it is re-inferred from the result, which happens to work, but pass it explicitly.
- **BUG — `T` overstated.** Pre-truncating with `add_bigoh(T)` and then storing `T = min(T1, T2)` ignores that Sage's own precision after `*` or `/` on Laurent series with negative valuation is lower than `T` (relative-precision loss). Store `T = result.prec()` when it is finite, else `min(T1, T2)`. Tests should assert `qs.T == qs.series.prec()`.
- **NOTE.** `T=20` default contradicts PITFALLS #1 ("never rely on default 20"). Make `T` required, or default to `series.prec()` when finite.
- **NOTE.** `__eq__` compares `T`, so two mathematically equal series with different truncation are unequal, and defining `__eq__` without `__hash__` makes `QSeries` unhashable. Decide whether equality means "agree to `min(T)`" and add `__hash__ = None` deliberately or drop `__eq__`.
- **NOTE.** Task 1 verify uses bare `python` + `tomllib` (3.11+); use `sage -python` for consistency.

## 01-02 — symbolic classes

- **BUG — `EtaProduct.to_series` shift is wrong.** `eta(kτ) = q^(k/24) ∏(1−q^{kn})`. The object represents `c · q^r · ∏ eta(kτ)^{e_k}`, so the expanded series has shift `r + Σ k·e_k / 24`, not `r`. Check with the tutorial: `etamake(theta2/q^(1/4)) = 2·eta(4τ)²/(q^(1/4)·eta(2τ))` → `r = −1/4`, `Σ k e_k/24 = (8 − 2)/24 = 1/4`, total `0` ✓. The plan's version returns shift `−1/4` for a series that has none.
- **BUG — `JacProduct.to_series` with `a = 0`.** The 3-factor formula gives `(1 − q^0) = 0` and zeroes the whole series. `JAC(0,b,∞) = (q^b;q^b)_∞` only (tutorial §3.4). The Rogers–Ramanujan example uses `JAC(0,5,∞)`, so this breaks the first thing anyone will try.
- **BUG — rational exponents.** `jac ** QQ(1)/2` on a Sage Laurent series raises. Since `JacProduct` explicitly allows rational `e` (tutorial shows a square root), `to_series` must handle it: `jac.nth_root(den) ** num` (constant term 1 guarantees the root exists) or `exp(e * log(jac))`. Same applies to `EtaProduct` if fractional exponents are ever allowed there.
- **BUG — `JacProduct` has no `constant` or `r`.** `jacprodmake` handles leading coefficient ≠ 1 (v1.1 changelog), and the `lqdegree0` doc examples are `sqrt(q)·JAC(…)`, `JAC(…)/q^3`, `JAC(…)/q^(1/3)`. Give `JacProduct` the same `constant`/`r` fields as `EtaProduct`; 01-03's `lqdegree0(JacProduct)` returning `0` unconditionally is a consequence of this gap.
- **NOTE — Pochhammer notation.** Maple prints `(q, q^5)_∞` (comma), the tutorial shows `(q,q^5)_infinity`. The plan prints `(q;q^5)_infinity`. Pick one and record it; the `;` form is standard mathematics but is a divergence from the oracle output.
- **NOTE.** `for n in range(1, T // k + 2): if k*n >= T: break` works; simpler and clearer is `for n in range(1, (T − 1)//k + 1)`.

## 01-03 — degree functions

- **BUG — `qdegree` ignores `r`.** `lqdegree` returns `r + valuation` but `qdegree` returns the raw exponent. Both should include the shift, or neither.
- **BUG/NOTE — `s.dict()` on a `LaurentSeries`.** Sage's `LaurentSeries` exposes `.exponents()`, `.coefficients()`, `.valuation()`, `.degree()`; don't rely on `.dict()`. `qdegree` is just `f.r + s.degree()` after the zero check.
- **NOTE — scope divergence, record it.** The interface block correctly transcribes the doc pages: `lqdegree` and `lqdegree0` operate on *symbolic sums of JAC-monomials* (e.g. `(1/2)·JAC(1,2) + q·JAC(3,4) + JAC(1,5)/q^(11/2)` → `−11/2`). The plan implements them on `QSeries` and single objects with `.r`, so the documented example cannot be reproduced and Phase 1 success criterion 4 ("match the Maple doc examples") is not met as written. This is an acceptable v1 divergence *if* it is written into CONTEXT.md and the roadmap criterion is amended — but note that `qs2jaccombo` returns a sum of JAC terms, so a `JacSum` (list of `(coeff, r, JacProduct)`) will be needed by Phase 4 anyway, and `lqdegree` over it is trivial once it exists. Consider adding it now.
- **NOTE.** The `is_zero()` checks: confirm in Sage whether `(0 + O(q^T)).is_zero()` is `True` for Laurent series; if not, also treat "no non-zero known coefficient" as zero.

## Suggested CONTEXT.md amendments (D-12 … D-15)

- **D-12** Arithmetic on shifts: `*`/`/` add/subtract `r`; `+`/`−` require integer-comparable shifts.
- **D-13** `T` after an operation is Sage's resulting precision, never larger.
- **D-14** `JacProduct` carries `constant` and `r`; `to_series` handles `a = 0` and rational exponents.
- **D-15** `lqdegree`/`lqdegree0` v1 domain: `QSeries` and the symbolic classes (and `JacSum` if added); symbolic-expression input is out of scope.
