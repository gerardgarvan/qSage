# Roadmap: qseries-sage

**Project:** qseries-sage
**Milestone:** v1.0 — full 41-function port of Garvan's Maple qseries package
**Granularity:** Standard (7 phases)
**Requirements:** 30 v1 requirements (FOUND-01 through PKG-02)
**Coverage:** 30/30 ✓
**Last updated:** 2026-09-16

---

## Phases

- [x] **Phase 1: Foundation** — License resolution, QSeries wrapper, symbolic output types, degree conventions (completed 2026-09-16)
- [ ] **Phase 2: Building Blocks & Utilities** — All 11 q-product/theta functions and all 8 series utilities
- [ ] **Phase 3: prodmake (Andrews' Algorithm)** — Standalone implementation of the core product-recovery algorithm
- [ ] **Phase 4: Product Conversion** — Remaining 10 product conversion functions built on prodmake
- [ ] **Phase 5: Relation Finding (Exact)** — 8 exact relation finders over QQ
- [ ] **Phase 6: Relation Finding (Mod-p)** — 3 GF(p) relation finders
- [ ] **Phase 7: Packaging & Test Suite** — pyproject.toml, install validation, full pytest coverage

---

## Phase Details

### Phase 1: Foundation

**Goal:** The project has a legal basis to proceed and a working data layer — QSeries wrapper with explicit truncation, pluggable base ring, rational q-power shift, all five symbolic output types, and correct degree conventions.
**Depends on:** Nothing (first phase)
**Requirements:** FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05
**Success Criteria** (what must be TRUE):
  1. `QSeries(ring_element, T=20)` stores the truncation order and arithmetic on two QSeries instances propagates `min(T1, T2)` without user intervention.
  2. Each FOUND-03 class (`QProduct`, `EtaProduct`, `EProduct`, `JacProduct`, `PochProduct`) prints in Maple notation and `.to_series(T)` round-trips back to a `QSeries`.
  3. `QSeries` can represent `q^(1/4) * (2 + 2*q^2 + ...)` (fractional shift, needed for `theta2`) and a series Laurent in a second variable `z` (needed for `theta`, `tripleprod`, `quinprod`, `winquist`, `zqfactor`).
  4. `qdegree`, `lqdegree`, and `lqdegree0` return values matching the Maple documentation examples; `lqdegree0` behaviour verified against its doc page (it is the q-monomial variant, not a zero-safe alias).
  5. A block comment at the top of `_series.py` documents the clean-reimplementation licensing decision and cites the Garvan docs URL.
**Plans:** 3/3 plans complete
Plans:
- [x] 01-01-PLAN.md — Package scaffold + QSeries wrapper (_series.py): FOUND-01, FOUND-02
- [x] 01-02-PLAN.md — Five symbolic output classes (_symbolic.py): FOUND-03, FOUND-04
- [x] 01-03-PLAN.md — Degree functions + __init__.py + pytest scaffold: FOUND-05

### Phase 2: Building Blocks & Utilities

**Goal:** All 11 q-product/theta functions and all 8 series utilities are implemented, individually tested against Maple documentation examples, and importable from the package.
**Depends on:** Phase 1
**Requirements:** BUILD-01, BUILD-02, BUILD-03, BUILD-04, BUILD-05, BUILD-06, BUILD-07, BUILD-08, BUILD-09, BUILD-10, BUILD-11, UTIL-01, UTIL-02, UTIL-03, UTIL-04, UTIL-05, UTIL-06, UTIL-07, UTIL-08
**Success Criteria** (what must be TRUE):
  1. `aqprod(q, q, 4)` equals `(1-q)(1-q^2)(1-q^3)(1-q^4)`; `tripleprod(q, q^3, 10)` equals Euler's pentagonal series (tutorial §6.1).
  2. `theta3(q, 20)` and `theta4(q, 20)` produce series whose product matches the known identity to order 20.
  3. `sift(etaq(q, 1, 500), q, 5, 0, 499)` equals the `E0` series printed in tutorial §6.2.
  4. `packageversion()` and `changes()` return non-empty strings; `checkmult` and `checkprod` each pass on a known matching pair and raise/return False on a mismatch.
**Plans:** 2/4 plans executed
Plans:
- [x] 02-00-PLAN.md — Test scaffolding + _building_blocks.py skeleton: BUILD-01..11, UTIL-01, UTIL-05..08
- [x] 02-01-PLAN.md — Core building blocks: aqprod, qbin, etaq, jacprod, theta, theta2, theta3, theta4: BUILD-01..08
- [ ] 02-02-PLAN.md — Bivariate building blocks: tripleprod, quinprod, winquist: BUILD-09..11
- [x] 02-03-PLAN.md — Series utilities + __init__.py exports: sift, checkmult, checkprod, packageversion, changes: UTIL-01..08

### Phase 3: prodmake (Andrews' Algorithm)

**Goal:** `prodmake` correctly identifies the exponent list of the infinite product representation of a given truncated q-series, handling fractional q-power prefactors, and is verified against multiple Maple documentation examples.
**Depends on:** Phase 2
**Requirements:** CONV-01
**Success Criteria** (what must be TRUE):
  1. `prodmake(aqprod(q, q, 30), q, 30)` returns an exponent structure that, when re-expanded via `aqprod`, matches the original series to order 30.
  2. `prodmake(x, q, 40)` on the Rogers–Ramanujan series gives exponents −1 at n ≡ ±1 mod 5 (tutorial §3.1).
  3. `prodmake` on a series with a fractional q-power prefix returns the correct rational prefactor alongside the integer exponent list.
**Plans:** TBD

### Phase 4: Product Conversion

**Goal:** All 10 remaining product-conversion functions are implemented and correctly identify or expand product forms for the Maple documentation's reference examples.
**Depends on:** Phase 3
**Requirements:** CONV-02, CONV-03, CONV-04, CONV-05, CONV-06, CONV-07, CONV-08, CONV-09, CONV-10, CONV-11
**Success Criteria** (what must be TRUE):
  1. `etamake(theta3(q, 100), q, 100)` returns `eta(2*tau)^5 / (eta(4*tau)^2 * eta(tau)^2)` matching the Maple documentation example.
  2. `jac2series(j, 20)` on a known `JacProduct` returns a series matching the Maple documentation example.
  3. `qfactor(t8, 20)` reproduces the tutorial §3.2 result: `(1-q^9)(1-q^10)(1-q^11)(1-q^16) * q^6 / ((1-q)(1-q^2)(1-q^3)(1-q^4))`.
  4. `findprod(f, q, 30)` successfully identifies the product form for at least one Maple tutorial example series.
**Plans:** TBD

### Phase 5: Relation Finding (Exact)

**Goal:** All 8 exact relation-finding functions operate correctly over QQ — returning relations that are verifiable to high truncation order — matching the Maple documentation examples up to basis reordering.
**Depends on:** Phase 4
**Requirements:** REL-01, REL-02, REL-05, REL-06, REL-07, REL-09, REL-10, REL-11
**Success Criteria** (what must be TRUE):
  1. `findhom([theta3(q), theta4(q), theta3(q^2), theta4(q^2)], q, 2, 0)` returns no linear and exactly two quadratic relations.
  2. `findhomcombo(UE, [B1, B2], q, 3, 0, 'yes')` returns `X1^2*X2 + 40*X1*X2^2 + 335*X2^3` (tutorial §5 example).
  3. `findmaxind(f_list, q, T)` returns a maximal independent subset whose size matches the Maple documentation example.
  4. `findpoly(x, y, q, 3, 1, 60)` recovers `(X+6)^3*Y - 27*(X+2)^2` (tutorial §4 example).
  5. `findcong(P, 1000)` returns the set `{[4,5,5], [5,7,7], [6,11,11], [24,25,25]}` (tutorial §7 example).
**Plans:** TBD

### Phase 6: Relation Finding (Mod-p)

**Goal:** The three mod-p relation finders operate correctly over GF(p), assert prime p, and return results matching Maple's documented mod-p examples.
**Depends on:** Phase 5
**Requirements:** REL-03, REL-04, REL-08
**Success Criteria** (what must be TRUE):
  1. `findhommodp(f_list, q, p, 2, 0)` returns homogeneous degree-2 relations over GF(p) consistent with Maple's documented result (signatures to be verified against mod-p doc pages).
  2. `findlincombomodp(f, f_list, q, p, ...)` returns a GF(p) linear combination that evaluates to zero mod p (signatures to be verified against doc pages).
  3. Passing a non-prime `p` to any mod-p function raises a `ValueError` before any computation.
**Plans:** TBD

### Phase 7: Packaging & Test Suite

**Goal:** The package installs cleanly with `sage -pip install .`, all 41 public functions plus `EtaProduct`/`JacProduct` are importable, and every function has at least one pytest test with an expected value from Maple documentation.
**Depends on:** Phase 6
**Requirements:** PKG-01, PKG-02
**Success Criteria** (what must be TRUE):
  1. `sage -pip install --user .` in a clean directory completes without errors and `python -c "from qseries import *; print(packageversion())"` prints the version string.
  2. `sage -python -m pytest` runs to completion with zero failures and covers all 41 public functions (one test per function minimum).
  3. Every test's expected value is annotated with a reference to a specific Maple documentation page or function, not derived from the package's own output.
**Plans:** TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 3/3 | Complete   | 2026-09-16 |
| 2. Building Blocks & Utilities | 2/4 | In Progress|  |
| 3. prodmake (Andrews' Algorithm) | 0/? | Not started | - |
| 4. Product Conversion | 0/? | Not started | - |
| 5. Relation Finding (Exact) | 0/? | Not started | - |
| 6. Relation Finding (Mod-p) | 0/? | Not started | - |
| 7. Packaging & Test Suite | 0/? | Not started | - |

---

## Coverage Map

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Pending |
| FOUND-02 | Phase 1 | Pending |
| FOUND-03 | Phase 1 | Pending |
| FOUND-04 | Phase 1 | Pending |
| FOUND-05 | Phase 1 | Pending |
| BUILD-01 | Phase 2 | Pending |
| BUILD-02 | Phase 2 | Pending |
| BUILD-03 | Phase 2 | Pending |
| BUILD-04 | Phase 2 | Pending |
| BUILD-05 | Phase 2 | Pending |
| BUILD-06 | Phase 2 | Pending |
| BUILD-07 | Phase 2 | Pending |
| BUILD-08 | Phase 2 | Pending |
| BUILD-09 | Phase 2 | Pending |
| BUILD-10 | Phase 2 | Pending |
| BUILD-11 | Phase 2 | Pending |
| UTIL-01 | Phase 2 | Pending |
| UTIL-02 | Phase 2 | Pending |
| UTIL-03 | Phase 2 | Pending |
| UTIL-04 | Phase 2 | Pending |
| UTIL-05 | Phase 2 | Pending |
| UTIL-06 | Phase 2 | Pending |
| UTIL-07 | Phase 2 | Pending |
| UTIL-08 | Phase 2 | Pending |
| CONV-01 | Phase 3 | Pending |
| CONV-02 | Phase 4 | Pending |
| CONV-03 | Phase 4 | Pending |
| CONV-04 | Phase 4 | Pending |
| CONV-05 | Phase 4 | Pending |
| CONV-06 | Phase 4 | Pending |
| CONV-07 | Phase 4 | Pending |
| CONV-08 | Phase 4 | Pending |
| CONV-09 | Phase 4 | Pending |
| CONV-10 | Phase 4 | Pending |
| CONV-11 | Phase 4 | Pending |
| REL-01 | Phase 5 | Pending |
| REL-02 | Phase 5 | Pending |
| REL-03 | Phase 6 | Pending |
| REL-04 | Phase 6 | Pending |
| REL-05 | Phase 5 | Pending |
| REL-06 | Phase 5 | Pending |
| REL-07 | Phase 5 | Pending |
| REL-08 | Phase 6 | Pending |
| REL-09 | Phase 5 | Pending |
| REL-10 | Phase 5 | Pending |
| REL-11 | Phase 5 | Pending |
| PKG-01 | Phase 7 | Pending |
| PKG-02 | Phase 7 | Pending |
