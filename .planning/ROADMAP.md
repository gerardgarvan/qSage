# Roadmap: qseries-sage

**Project:** qseries-sage
**Milestone:** v1.0 — full 41-function port of Garvan's Maple qseries package
**Granularity:** Standard (7 phases)
**Requirements:** 28 v1 requirements (FOUND-01 through PKG-02)
**Coverage:** 28/28 ✓
**Last updated:** 2026-09-16

---

## Phases

- [ ] **Phase 1: Foundation** — License resolution, QSeries wrapper, symbolic output types, degree conventions
- [ ] **Phase 2: Building Blocks & Utilities** — All 11 q-product/theta functions and all 8 series utilities
- [ ] **Phase 3: prodmake (Andrews' Algorithm)** — Standalone implementation of the core product-recovery algorithm
- [ ] **Phase 4: Product Conversion** — Remaining 10 product conversion functions built on prodmake
- [ ] **Phase 5: Relation Finding (Exact)** — 9 exact relation finders over QQ
- [ ] **Phase 6: Relation Finding (Mod-p)** — 3 GF(p) relation finders
- [ ] **Phase 7: Packaging & Test Suite** — pyproject.toml, install validation, full pytest coverage

---

## Phase Details

### Phase 1: Foundation

**Goal:** The project has a legal basis to proceed and a working data layer — QSeries wrapper with explicit truncation, printable EtaProduct/JacProduct types, and correct degree conventions.
**Depends on:** Nothing (first phase)
**Requirements:** FOUND-01, FOUND-02, FOUND-03
**Success Criteria** (what must be TRUE):
  1. `QSeries(ring_element, T=20)` stores the truncation order and arithmetic on two QSeries instances propagates `min(T1, T2)` without user intervention.
  2. `EtaProduct([...]).to_series(T)` returns a QSeries, and `str(EtaProduct([...]))` prints in Maple-style `eta(k*tau)^e * q^r` notation.
  3. `qdegree`, `lqdegree`, and `lqdegree0` return values matching the Maple documentation examples for both ordinary and Laurent polynomials in q.
  4. A written record (comment in `_series.py` or a `LICENSING.md`) documents the conclusion of the licensing check and the chosen porting method (translation vs. clean reimplementation from docs).
**Plans:** TBD

### Phase 2: Building Blocks & Utilities

**Goal:** All 11 q-product/theta functions and all 8 series utilities are implemented, individually tested against Maple documentation examples, and importable from the package.
**Depends on:** Phase 1
**Requirements:** BUILD-01, BUILD-02, BUILD-03, BUILD-04, BUILD-05, BUILD-06, BUILD-07, BUILD-08, BUILD-09, BUILD-10, BUILD-11, UTIL-01, UTIL-02, UTIL-03, UTIL-04, UTIL-05, UTIL-06, UTIL-07, UTIL-08
**Success Criteria** (what must be TRUE):
  1. `aqprod(1 - q, q, 10)` returns the correct truncated q-Pochhammer series matching the Maple documentation example.
  2. `theta3(q, 20)` and `theta4(q, 20)` produce series whose product matches the known identity (e.g., theta3*theta4 relation) to order 20.
  3. `sift(f, 0, 3)` on a known series extracts exactly the coefficients at positions 0, 3, 6, ... matching the Maple result.
  4. `packageversion()` and `changes()` return non-empty strings; `checkmult` and `checkprod` each pass on a known matching pair and raise/return False on a mismatch.
**Plans:** TBD

### Phase 3: prodmake (Andrews' Algorithm)

**Goal:** `prodmake` correctly identifies the exponent list of the infinite product representation of a given truncated q-series, handling fractional q-power prefactors, and is verified against multiple Maple documentation examples.
**Depends on:** Phase 2
**Requirements:** CONV-01
**Success Criteria** (what must be TRUE):
  1. `prodmake(aqprod(q, q, 30), q, 30)` returns an exponent structure that, when re-expanded via `aqprod`, matches the original series to order 30.
  2. `prodmake` applied to `etaq(q, 30)` recovers the correct single-factor eta exponent list matching the Maple documentation output.
  3. `prodmake` on a series with a fractional q-power prefix (e.g., a Ramanujan-style eta quotient) returns the correct rational prefactor alongside the integer exponent list.
**Plans:** TBD

### Phase 4: Product Conversion

**Goal:** All 10 remaining product-conversion functions are implemented and correctly identify or expand product forms for the Maple documentation's reference examples.
**Depends on:** Phase 3
**Requirements:** CONV-02, CONV-03, CONV-04, CONV-05, CONV-06, CONV-07, CONV-08, CONV-09, CONV-10, CONV-11
**Success Criteria** (what must be TRUE):
  1. `etamake(f, q, 30)` on a known eta-product series returns an `EtaProduct` whose `.to_series(30)` matches f to order 30.
  2. `jac2series(j, q, 20)` on a known `JacProduct` returns a series matching the Maple documentation example.
  3. `qfactor(f, q)` and `zqfactor(f, q)` return the correct (power, remaining) pair for a series with a leading q-power, matching Maple's output.
  4. `findprod(f, q, 30)` successfully identifies the product form for at least one Maple tutorial example series.
**Plans:** TBD

### Phase 5: Relation Finding (Exact)

**Goal:** All 9 exact relation-finding functions operate correctly over QQ — returning relations that are verifiable to high truncation order — matching the Maple documentation examples up to basis reordering.
**Depends on:** Phase 4
**Requirements:** REL-01, REL-02, REL-05, REL-06, REL-07, REL-09, REL-10, REL-11
**Success Criteria** (what must be TRUE):
  1. `findhom([f1, f2, f3], q, 40, 2)` returns a set of homogeneous degree-2 relations whose span matches Maple's result (checked by verifying each returned relation evaluates to the zero series to order 40).
  2. `findlincombo(f_list, q, 40)` on the Maple tutorial's canonical example returns a linear relation whose coefficients, when applied to the series, sum to zero to order 40.
  3. `findmaxind(f_list, q, 40)` returns a maximal independent subset whose size matches the Maple documentation example.
  4. `findpoly(f, g_list, q, 40, 3)` recovers the correct degree-3 polynomial in g_list that equals f, matching the Maple tutorial example.
  5. `findcong(f_list, q, 40, 5)` identifies at least one congruence documented in the Maple tutorial.
**Plans:** TBD

### Phase 6: Relation Finding (Mod-p)

**Goal:** The three mod-p relation finders operate correctly over GF(p), assert prime p, and return results matching Maple's documented mod-p examples.
**Depends on:** Phase 5
**Requirements:** REL-03, REL-04, REL-08
**Success Criteria** (what must be TRUE):
  1. `findhommodp([f1, f2, f3], q, 40, 2, 5)` returns homogeneous degree-2 relations over GF(5) whose span is consistent with Maple's documented result (relation set verified to order 40 mod 5).
  2. `findlincombomodp(f_list, q, 40, 7)` returns a GF(7) linear relation that evaluates to the zero series mod 7 to order 40.
  3. Passing a non-prime `p` to any mod-p function raises an assertion error or ValueError before any computation.
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
| 1. Foundation | 0/? | Not started | - |
| 2. Building Blocks & Utilities | 0/? | Not started | - |
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
