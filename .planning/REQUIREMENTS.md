# Requirements: qseries-sage

**Defined:** 2026-09-16 · **Revised:** 2026-09-16 (signatures corrected against Garvan's tutorial and doc pages)
**Core Value:** A researcher who knows the Maple qseries package can do the same work in a free, scriptable, HiPerGator-installable environment, with results that agree with Maple's on the reference examples.

Signature legend: **[V]** verified against qseriesdoc.pdf / doc pages · **[?]** taken from the function-index one-liner only — planner MUST read the doc page before writing the plan.

## v1 Requirements

### Foundation

- [ ] **FOUND-01**: `QSeries` wraps `LaurentSeriesRing(R, 'q')` with explicit truncation order `T` stored per instance and propagated as `min(T1, T2)`. `R` is `QQ` by default, `GF(p)` for mod-p functions, and `LaurentPolynomialRing(QQ, 'z')` (or a two-variable equivalent) for the functions that are Laurent in a second variable: `theta`, `tripleprod`, `quinprod`, `winquist`, `zqfactor`.
- [ ] **FOUND-02**: `QSeries` carries a rational exponent shift `r` so that `q^r * (Laurent series in q)` is representable. Needed because Maple returns fractional q-powers from `theta2` (`q^(1/4)`), `etamake` (`q^(-5/24)` etc.), and any user expression like `q^(1/3)*etaq(...)`.
- [ ] **FOUND-03**: Output classes, each printable in Maple's notation and convertible back via `.to_series(T)`:
  `QProduct` — `∏(1-q^n)^e_n` (return type of `prodmake`);
  `EtaProduct` — `c * q^r * ∏ eta(k*tau)^e_k` (return type of `etamake`);
  `EProduct` — `∏ _E(q^k)^e_k` (return type of `qetamake`);
  `JacProduct` — `∏ JAC(a,b,∞)^e` with **rational** `e` allowed (tutorial shows a square root);
  `PochProduct` — `∏ (q^a;q^b)_∞^e` (return type of `jac2prod`).
- [ ] **FOUND-04**: Relation finders return polynomials in Sage variables `X1..Xk` (or `X, Y` for `findpoly`) in a `PolynomialRing(QQ)`, mirroring Maple's global `X[i]`; not bare coefficient vectors.
- [ ] **FOUND-05**: `qdegree`, `lqdegree`, `lqdegree0` behave as their doc pages specify. `lqdegree0` is the **q-monomial** variant per the function index (not a zero-safe alias) — verify on the doc page before implementing.

### Building Blocks

- [ ] **BUILD-01** [V]: `aqprod(a, q, n)` — finite rising q-factorial `(a;q)_n = (1-a)(1-aq)…(1-aq^(n-1))`. `a` may be any Laurent monomial/series in q (tutorial uses `aqprod(-q,q,n)`). Doc page marked UPDATED in 1.3 — check whether `n = infinity` is accepted.
- [ ] **BUILD-02** [V]: `qbin(q, m, n)` — Gaussian polynomial `[n; m]_q`; returns 0 unless `0 ≤ m ≤ n`. Note argument order: lower index `m` second.
- [ ] **BUILD-03** [V]: `etaq(q, k, T)` — `∏_{n≥1}(1-q^{kn})` to `O(q^T)`. No `q^(1/24)` factor.
- [ ] **BUILD-04** [V]: `jacprod(a, b, q, T)` — `(q^a;q^b)_∞ (q^{b-a};q^b)_∞` to `O(q^T)`. (Note: `JAC(a,b,∞)` additionally includes `(q^b;q^b)_∞`; the two are different objects.)
- [ ] **BUILD-05** [V]: `theta(z, q, T)` — `Σ_{i=-T}^{T} z^i q^{i²}`. Bivariate.
- [ ] **BUILD-06** [V]: `theta2(q, T)` — `Σ q^{(n+1/2)²}` = `q^(1/4)·(2 + 2q² + 2q⁶ + …)`. Fractional shift.
- [ ] **BUILD-07** [V]: `theta3(q, T)` — `Σ q^{n²}`.
- [ ] **BUILD-08** [V]: `theta4(q, T)` — `Σ (-1)^n q^{n²}`.
- [ ] **BUILD-09** [V]: `tripleprod(z, q, T)` — `Σ (-1)^n z^n q^{n(n-1)/2}` truncated; Laurent in `z`. `tripleprod(q, q^3, 10)` must reproduce Euler's pentagonal series.
- [ ] **BUILD-10** [V]: `quinprod(z, q, T)` — if `T` is an integer, q-expansion of the quintuple-product series; if `T == 'prodid'` / `'seriesid'`, return the identity itself (product form / series form) as a displayable equation object.
- [ ] **BUILD-11** [V]: `winquist(a, b, q, T)` — right side of Winquist's identity; Laurent in `a`, `b`.

### Series Utilities

- [ ] **UTIL-01** [V]: `sift(s, q, n, k, T)` — from `s = Σ a_i q^i + O(q^T)` return `Σ a_{ni+k} q^i + O(q^{T/n})`.
- [ ] **UTIL-02** [V]: `qdegree(f)` — degree in q (`qdegree(P)` with one argument in the install example; check whether `(f, q)` is also accepted).
- [ ] **UTIL-03** [?]: `lqdegree(f, …)` — lowest degree in q of a q-polynomial.
- [ ] **UTIL-04** [?]: `lqdegree0(f, …)` — lowest degree in q of a q-monomial.
- [ ] **UTIL-05** [?]: `checkmult(f, …)` — test whether the coefficients `a(n)` are multiplicative (`a(mn) = a(m)a(n)` for coprime `m, n`).
- [ ] **UTIL-06** [?]: `checkprod(f, …)` — test whether a q-series is a "nice" product (bounded exponents from `prodmake`).
- [ ] **UTIL-07** [V]: `packageversion()` — version string.
- [ ] **UTIL-08** [V]: `changes()` — prints recent changes; content is this package's own changelog, not Maple's.

### Product Conversion

- [ ] **CONV-01** [V]: `prodmake(f, q, T)` — Andrews' algorithm via the recurrence `n·b_n = Σ_{j=1}^{n} b_{n-j} Σ_{d|j} d·a_d`, solved for `a_n` (divisor-sum inversion). No linear algebra. Requires `f = 1 + O(q)` after normalising the leading term; returns `QProduct` with exponents for `n < T`.
- [ ] **CONV-02** [V]: `etamake(f, q, T)` — greedy: at each step `f = c·q^r(1 + c_k q^k + …)`, multiply by `etaq(q,k,T)^(-c_k)`; return `EtaProduct` with constant, rational `q^r`, and `eta(kτ)` exponents. Must reproduce `theta2 = 2·eta(4τ)²/eta(2τ)` (via `q^(1/4)` shift), `theta3 = eta(2τ)^5/(eta(4τ)²eta(τ)²)`, `theta4 = eta(τ)²/eta(2τ)`.
- [ ] **CONV-03** [V]: `qetamake(f, q, T)` — same search, output in `_E(q^k)` form with no fractional q-power (e.g. `_E(q²)²/_E(q)` for the triangular-number series).
- [ ] **CONV-04** [V]: `jacprodmake(f, q, T [, base])` — run `prodmake`, detect periodicity in the exponent sequence, return `JacProduct`. 4th argument forces a period. Leading coefficient need not be 1 (v1.1 change). Rational exponents possible.
- [ ] **CONV-05** [?]: `mprodmake(f, q, T)` — write `f` as `(1+q^{n1})(1+q^{n2})…`.
- [ ] **CONV-06** [V]: `qfactor(f [, T])` — `f` is a **polynomial or rational function** in q (not a truncated series): factor over `QQ[q]`, then use `prodmake` on the cyclotomic part to express as a finite q-product; `T` bounds exponents, default `4d+3`. Must reproduce `qfactor(t8,20) = (1-q^9)(1-q^10)(1-q^11)(1-q^16) q^6 / ((1-q)(1-q^2)(1-q^3)(1-q^4))`.
- [ ] **CONV-07** [?]: `zqfactor(f, z, q, T)` — bivariate analogue of `qfactor` for `(z,q)`-series.
- [ ] **CONV-08** [V]: `jac2prod(jacexpr)` — `JacProduct` → `PochProduct` (`JAC(a,b,∞)` ↦ `(q^a;q^b)_∞(q^{b-a};q^b)_∞(q^b;q^b)_∞`; `JAC(0,b,∞)` ↦ `(q^b;q^b)_∞`).
- [ ] **CONV-09** [V]: `jac2series(jacexpr, T)` — replace each `JAC` factor by its theta-series (`theta(-q^{(b-2a)/2}, q^{b/2})`) truncated to `T`; return the product of series.
- [ ] **CONV-10** [?]: `qs2jaccombo(f, q, T, …)` — express a sum of q-series as a sum of `jacprod`s.
- [ ] **CONV-11** [?]: `findprod(…)` — "products that are a linear combination of q-series". Signature and semantics unknown; read doc page.

### Relation Finding

Return values are Sage polynomials in `X1..Xk` (FOUND-04). Tests compare the relation **span**, not order.

- [ ] **REL-01** [V]: `findhom(L, q, n, topshift)` — set of homogeneous degree-`n` relations among the series in `L`; truncation comes from the series themselves, `topshift` trims rows to suppress spurious relations. Must find no linear and two quadratic relations among `theta3(q), theta4(q), theta3(q²), theta4(q²)`.
- [ ] **REL-02** [V]: `findhomcombo(f, L, q, n, topshift, etaoption)` — express `f` as a homogeneous degree-`n` polynomial in `L`; if `etaoption == 'yes'` also return each monomial as an `EtaProduct`. Must reproduce `U_{5,6} = X1²X2 + 40 X1X2² + 335 X2³`.
- [ ] **REL-03** [?]: `findhommodp(L, q, p, n, topshift)` — `findhom` over `GF(p)`. Confirm argument position of `p`.
- [ ] **REL-04** [?]: `findhomcombomodp(f, L, q, p, n, topshift)` — mod-p `findhomcombo`.
- [ ] **REL-05** [V]: `findnonhom(L, q, n, topshift)` — same syntax as `findhom`, total degree `≤ n`.
- [ ] **REL-06** [V]: `findnonhomcombo(f, L, q, n, topshift, etaoption)` — same syntax as `findhomcombo`. Must reproduce Watson's mod-7 modular equation from the tutorial.
- [ ] **REL-07** [?]: `findlincombo(f, L, …)` — express `f` as a linear combination of `L`. Read doc page for the full argument list (a `SYMS` list and `etaoption` are believed to be present).
- [ ] **REL-08** [?]: `findlincombomodp(f, L, …, p, …)` — mod-p `findlincombo`.
- [ ] **REL-09** [?]: `findmaxind(L, …)` — maximal linearly independent sublist of `L`.
- [ ] **REL-10** [V]: `findpoly(x, y, q, deg1, deg2 [, check])` — polynomial relation `P(X,Y) = 0` between **two** series with degree bounds; if `check` given, verify to `O(q^check)`. Must reproduce `(X+6)³Y − 27(X+2)²`.
- [ ] **REL-11** [V]: `findcong(f, T [, …])` — Ramanujan-type congruences `a(An+B) ≡ 0 (mod M)` for a **single** series; returns a set of `[B, A, M]` triples. `findcong(1/etaq(q,1,1001), 1000)` must return `{[4,5,5],[5,7,7],[6,11,11],[24,25,25]}`. Check doc page for the optional 3rd argument.

### Packaging

- [ ] **PKG-01**: Installable with `sage -pip install .`; `from qseries import *` exports all 41 functions plus the FOUND-03 classes.
- [ ] **PKG-02**: Every public function has ≥1 pytest test (`sage -python -m pytest`) whose expected value is traceable to a Maple doc page or the tutorial, never to this package's own output.

## v2 Requirements

- **DEPLOY-01**: Confirmed on UF HiPerGator's Sage, no root.
- **DEPLOY-02**: Sage-kernel Jupyter tutorial mirroring the Maple tutorial's sections.
- **DEPLOY-03**: CI running the test suite.
- **EXT-01**: Related packages (ETA, thetaids, ramarobinsids) as later milestones.

## Out of Scope

| Feature | Reason |
|---|---|
| Maple-syntax compatibility layer / worksheet importer | Different project |
| Identity proving (valence formula) | thetaids, not qseries |
| Cython / parallelism | Not a v1 goal |
| Pure-SymPy fallback | No exact series ring or exact nullspace |
| Non-prime moduli in mod-p functions | `GF(p)` requires prime `p` |

## Traceability

| Requirement | Phase | Status |
|---|---|---|
| FOUND-01 … FOUND-05 | Phase 1: Foundation | Pending |
| BUILD-01 … BUILD-11, UTIL-01 … UTIL-08 | Phase 2: Building Blocks & Utilities | Pending |
| CONV-01 | Phase 3: prodmake | Pending |
| CONV-02 … CONV-11 | Phase 4: Product Conversion | Pending |
| REL-01, 02, 05, 06, 07, 09, 10, 11 | Phase 5: Relation Finding (Exact) | Pending |
| REL-03, 04, 08 | Phase 6: Relation Finding (Mod-p) | Pending |
| PKG-01, PKG-02 | Phase 7: Packaging & Test Suite | Pending |
