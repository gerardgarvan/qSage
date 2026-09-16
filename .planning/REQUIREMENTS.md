# Requirements: qseries-sage

**Defined:** 2026-09-16
**Core Value:** A researcher who knows the Maple qseries package can do the same work in a free, scriptable, HiPerGator-installable environment, with results that agree with Maple's on the reference examples.

## v1 Requirements

### Foundation

- [ ] **FOUND-01**: Package provides a `QSeries` wrapper around Sage's `PowerSeriesRing`/`LaurentSeriesRing` over `QQ`, with an explicit truncation order `T` stored per-instance and propagated through arithmetic as `min(T1, T2)`.
- [ ] **FOUND-02**: Package provides `EtaProduct` and `JacProduct` Python classes that print in Maple-style notation (`eta(k*tau)^e * q^r`, `JAC(a,b,infinity)`) and expose a `.to_series(T)` method returning a `QSeries`.
- [ ] **FOUND-03**: Degree/lowest-degree/coefficient conventions (`qdegree`, `lqdegree`, `lqdegree0`) match Maple's behavior on Laurent polynomials in q, verified against documented examples.

### Building Blocks

- [ ] **BUILD-01**: `aqprod(a, q, T)` — q-Pochhammer product `(a; q)_∞` truncated to order T, matching Maple's argument order and return type.
- [ ] **BUILD-02**: `qbin(q, n, k)` — Gaussian binomial coefficient, argument order matching qseries 1.3.
- [ ] **BUILD-03**: `etaq(q, T)` — Euler's eta q-series `q^(1/24) prod(1-q^n)`.
- [ ] **BUILD-04**: `jacprod(a, b, q, T)` — Jacobi product, convention cited to Maple doc page.
- [ ] **BUILD-05**: `theta(q, T)` — Jacobi theta function θ₁, convention matching Maple doc page.
- [ ] **BUILD-06**: `theta2(q, T)` — Jacobi theta function θ₂.
- [ ] **BUILD-07**: `theta3(q, T)` — Jacobi theta function θ₃.
- [ ] **BUILD-08**: `theta4(q, T)` — Jacobi theta function θ₄.
- [ ] **BUILD-09**: `tripleprod(a, q, T)` — Jacobi triple product identity.
- [ ] **BUILD-10**: `quinprod(a, q, T)` — quintuple product identity.
- [ ] **BUILD-11**: `winquist(q, T)` — Winquist's identity.

### Series Utilities

- [ ] **UTIL-01**: `sift(f, r, m)` — extract every m-th coefficient starting at r.
- [ ] **UTIL-02**: `qdegree(f)` — degree of series f (highest non-zero coefficient index).
- [ ] **UTIL-03**: `lqdegree(f)` — lowest-degree (valuation) of series f.
- [ ] **UTIL-04**: `lqdegree0(f)` — variant of lqdegree matching Maple's behavior for the zero series.
- [ ] **UTIL-05**: `checkmult(f, g, T)` — verify f and g agree as truncated series to order T.
- [ ] **UTIL-06**: `checkprod(f, exponents, T)` — verify a series matches a product with given exponents.
- [ ] **UTIL-07**: `packageversion()` — returns version string for qseries-sage package.
- [ ] **UTIL-08**: `changes()` — returns changelog string matching the Maple package's changes function.

### Product Conversion

- [ ] **CONV-01**: `prodmake(f, q, T)` — Andrews' algorithm: recover exponent list of the infinite product representation of f, returning an `EtaProduct`-like structured result.
- [ ] **CONV-02**: `etamake(f, q, T)` — identify eta-product form of f; returns `EtaProduct`.
- [ ] **CONV-03**: `qetamake(f, q, T)` — variant of etamake including a q-power prefactor.
- [ ] **CONV-04**: `jacprodmake(f, q, T)` — identify Jacobi product form; returns `JacProduct`.
- [ ] **CONV-05**: `mprodmake(f, q, T)` — multi-parameter product recovery.
- [ ] **CONV-06**: `qfactor(f, q)` — factor out the leading q-power from f; returns (power, remaining series).
- [ ] **CONV-07**: `zqfactor(f, q)` — variant of qfactor for Laurent series with possibly negative valuation.
- [ ] **CONV-08**: `jac2prod(j, q, T)` — expand a `JacProduct` into a product of `aqprod` factors as a series.
- [ ] **CONV-09**: `jac2series(j, q, T)` — expand a `JacProduct` directly to a truncated series.
- [ ] **CONV-10**: `qs2jaccombo(f, q, T)` — decompose a series as a linear combination of Jacobi products.
- [ ] **CONV-11**: `findprod(f, q, T)` — search for a matching product form for f.

### Relation Finding

- [ ] **REL-01**: `findhom(f_list, q, T, d)` — find homogeneous polynomial relations of degree d among series in f_list over QQ.
- [ ] **REL-02**: `findhomcombo(f_list, q, T, d)` — find homogeneous relations and return explicit coefficient combinations.
- [ ] **REL-03**: `findhommodp(f_list, q, T, d, p)` — findhom over GF(p) for prime p.
- [ ] **REL-04**: `findhomcombomodp(f_list, q, T, d, p)` — findhomcombo over GF(p).
- [ ] **REL-05**: `findnonhom(f_list, q, T, d)` — find non-homogeneous polynomial relations of total degree ≤ d.
- [ ] **REL-06**: `findnonhomcombo(f_list, q, T, d)` — findnonhom with explicit combos.
- [ ] **REL-07**: `findlincombo(f_list, q, T)` — find linear (degree-1) relations among series.
- [ ] **REL-08**: `findlincombomodp(f_list, q, T, p)` — findlincombo over GF(p).
- [ ] **REL-09**: `findmaxind(f_list, q, T)` — find the maximum independent subset of a list of series.
- [ ] **REL-10**: `findpoly(f, g_list, q, T, d)` — find a polynomial of degree d in g_list that equals f.
- [ ] **REL-11**: `findcong(f_list, q, T, m)` — find congruences modulo m among the series.

### Packaging

- [ ] **PKG-01**: Package is installable with `sage -pip install .` (and plain `pip` inside a Sage venv); `from qseries import *` imports all 41 functions plus `EtaProduct` and `JacProduct`.
- [ ] **PKG-02**: Every public function has at least one `pytest` test with an expected value traceable to the Maple documentation (not self-computed), runnable via `sage -python -m pytest`.

## v2 Requirements

### Deployment & Documentation

- **DEPLOY-01**: Package confirmed working on UF HiPerGator (no root, Sage version pinned to HiPerGator's).
- **DEPLOY-02**: Sage-kernel Jupyter tutorial notebook mirroring the sections of the Maple qseries tutorial.
- **DEPLOY-03**: CI workflow (GitHub Actions or similar) running the test suite on each push.

### Extended Scope

- **EXT-01**: Related packages (ETA, thetaids, ramarobinsids) — subsequent milestones after v1.0 validation.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Maple-syntax compatibility layer | Explicitly excluded — different project; adds maintenance burden |
| Maple worksheet importer | Out of scope |
| Identity proving (valence formula) | Lives in thetaids, not qseries |
| Cython / parallelism | Performance not a v1 goal |
| Pure-SymPy fallback | No exact power-series ring in SymPy; rejected in Key Decisions |
| Non-prime moduli for mod-p functions | GF(p) requires prime p; ZZ/nZZ not well-defined for linear algebra |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1: Foundation | Pending |
| FOUND-02 | Phase 1: Foundation | Pending |
| FOUND-03 | Phase 1: Foundation | Pending |
| BUILD-01 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-02 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-03 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-04 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-05 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-06 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-07 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-08 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-09 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-10 | Phase 2: Building Blocks & Utilities | Pending |
| BUILD-11 | Phase 2: Building Blocks & Utilities | Pending |
| UTIL-01 | Phase 2: Building Blocks & Utilities | Pending |
| UTIL-02 | Phase 2: Building Blocks & Utilities | Pending |
| UTIL-03 | Phase 2: Building Blocks & Utilities | Pending |
| UTIL-04 | Phase 2: Building Blocks & Utilities | Pending |
| UTIL-05 | Phase 2: Building Blocks & Utilities | Pending |
| UTIL-06 | Phase 2: Building Blocks & Utilities | Pending |
| UTIL-07 | Phase 2: Building Blocks & Utilities | Pending |
| UTIL-08 | Phase 2: Building Blocks & Utilities | Pending |
| CONV-01 | Phase 3: prodmake (Andrews' Algorithm) | Pending |
| CONV-02 | Phase 4: Product Conversion | Pending |
| CONV-03 | Phase 4: Product Conversion | Pending |
| CONV-04 | Phase 4: Product Conversion | Pending |
| CONV-05 | Phase 4: Product Conversion | Pending |
| CONV-06 | Phase 4: Product Conversion | Pending |
| CONV-07 | Phase 4: Product Conversion | Pending |
| CONV-08 | Phase 4: Product Conversion | Pending |
| CONV-09 | Phase 4: Product Conversion | Pending |
| CONV-10 | Phase 4: Product Conversion | Pending |
| CONV-11 | Phase 4: Product Conversion | Pending |
| REL-01 | Phase 5: Relation Finding (Exact) | Pending |
| REL-02 | Phase 5: Relation Finding (Exact) | Pending |
| REL-03 | Phase 6: Relation Finding (Mod-p) | Pending |
| REL-04 | Phase 6: Relation Finding (Mod-p) | Pending |
| REL-05 | Phase 5: Relation Finding (Exact) | Pending |
| REL-06 | Phase 5: Relation Finding (Exact) | Pending |
| REL-07 | Phase 5: Relation Finding (Exact) | Pending |
| REL-08 | Phase 6: Relation Finding (Mod-p) | Pending |
| REL-09 | Phase 5: Relation Finding (Exact) | Pending |
| REL-10 | Phase 5: Relation Finding (Exact) | Pending |
| REL-11 | Phase 5: Relation Finding (Exact) | Pending |
| PKG-01 | Phase 7: Packaging & Test Suite | Pending |
| PKG-02 | Phase 7: Packaging & Test Suite | Pending |
