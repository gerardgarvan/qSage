# Phase 2: Building Blocks & Utilities - Context

**Gathered:** 2026-09-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 delivers all 11 q-product/theta building-block functions and all 8 series utility functions,
each individually tested against Maple documentation examples and importable from the package.

- **Building blocks:** `aqprod`, `qbin`, `etaq`, `jacprod`, `theta`, `theta2`, `theta3`, `theta4`,
  `tripleprod`, `quinprod`, `winquist`
- **Utilities:** `sift`, `qdegree`*, `lqdegree`*, `lqdegree0`*, `checkmult`, `checkprod`,
  `packageversion`, `changes`

(*) `qdegree`, `lqdegree`, `lqdegree0` were completed in Phase 1 Plan 3 — do NOT reimplement.
Verify they export correctly and write tests; no new code needed.

No product-conversion or relation-finding functions belong here.

</domain>

<decisions>
## Implementation Decisions

### Sage Primitive Wrapping

- **D-01:** `etaq` and `qbin` **wrap Sage builtins** — `sage.functions.other.qexp_eta` for `etaq`,
  `sage.arith.misc.q_binomial` for `qbin`. We handle the argument-order difference (Maple's
  `(q, m, n)` vs Sage's `(n, k, q)`) in the wrapper. Return type is `QSeries`.
- **D-02:** All other building blocks (`aqprod`, `jacprod`, `theta`, `theta2`, `theta3`, `theta4`,
  `tripleprod`, `quinprod`, `winquist`) are **reimplemented from the documented math formulas**.
  No Sage modular or symbolic machinery used (consistent with clean-reimplementation principle
  and `sage.modular.etaproducts` being off-limits per CLAUDE.md).

### Bivariate z-Variable Interface

- **D-03:** `theta(z, q, T)`, `tripleprod(z, q, T)`, `winquist(a, b, q, T)` accept `z` (and `a`,
  `b`) as Sage symbolic variables that the **caller creates externally** (e.g.,
  `z = var('z'); theta(z, q, 20)`). This matches Maple's calling convention exactly.
- **D-04:** Bivariate functions return a `QSeries` with
  `R = LaurentPolynomialRing(QQ, 'z')` (or the two-variable analogue for `winquist`), consistent
  with Phase 1 FOUND-01. The `QSeries` wrapper's `T` and `r` propagate normally.

### quinprod Identity Modes

- **D-05:** `quinprod(z, q, T)` with `T == 'prodid'` or `T == 'seriesid'` returns a **plain
  formatted string** showing the quintuple product identity (e.g., `"LHS = RHS"` with symbolic
  product/series form). No new class required.
- **D-06:** When `T` is an integer, `quinprod` returns a `QSeries` (Laurent in z) as normal.

### checkmult / checkprod Semantics

- **D-07:** `checkmult(f)` returns **`bool`** — `True` if all tested coprime pairs `(m, n)` satisfy
  `a(mn) = a(m)*a(n)`, `False` otherwise. Planner must read the `checkmult` doc page to determine
  which coprime pairs are checked and the argument signature.
- **D-08:** `checkprod(f)` returns **`bool`** — `True` if `prodmake` on `f` gives a `QProduct` with
  bounded exponents (Maple's "nice product" criterion). However, `prodmake` is not built until Phase 3.
  **Phase 2 implementation:** stub `checkprod` with `raise NotImplementedError("checkprod requires prodmake, available after Phase 3")`. Phase 3 fills in the real implementation.
- **D-09:** `checkprod` IS exported in `__init__.py` in Phase 2 (with the stub), so the name is
  available. The stub makes the dependency explicit rather than hiding it.

### Module Structure

- **D-10:** Follow the architecture established in STATE.md:
  - `qseries/_building_blocks.py` — the 11 building-block functions
  - `qseries/_utilities.py` — already exists (degree functions); extend with `sift`, `checkmult`,
    `checkprod`, `packageversion`, `changes`
  - `__init__.py` — extend to export all new functions

### Claude's Discretion

- Exact iteration bounds for checking multiplicativity in `checkmult` (which coprime pairs to test,
  up to what bound) — derive from doc page.
- Internal variable naming in bivariate functions.
- Exact string format for `quinprod` identity modes — must be readable and correct.
- Whether `packageversion()` reads `__version__` from `__init__.py` or a separate constant.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Garvan qseries Documentation

- `https://qseries.org/fgarvan/qmaple/qseries/` — function index and per-function doc pages;
  primary oracle for signatures, argument order, and expected outputs.
- `https://qseries.org/fgarvan/qmaple/qseries/qseriesdoc.pdf` — tutorial; test expected values
  come from here (§6.1 for `tripleprod`, §6.2 for `sift`, etc.).

**Planner MUST fetch the individual doc pages for all [?]-marked functions before writing tasks:**
- `checkmult` — UTIL-05 [?]: full argument list and return value unknown
- `checkprod` — UTIL-06 [?]: full argument list and "nice product" criterion
- `lqdegree` / `lqdegree0` — UTIL-03/04 [?]: verify against doc page (already implemented; just confirm)
- `mprodmake` — out of scope for Phase 2 but note CONV-05 is [?]

### Project Planning Docs

- `.planning/REQUIREMENTS.md` — BUILD-01 through BUILD-11, UTIL-01 through UTIL-08 define
  acceptance criteria; [V] vs [?] labels are critical — planner must fetch [?] doc pages.
- `.planning/phases/01-foundation/01-CONTEXT.md` — Phase 1 decisions (QSeries API, shift rules,
  arithmetic conventions) that Phase 2 code must respect.

### Existing Code (read before planning)

- `qseries/_series.py` — QSeries wrapper API
- `qseries/_symbolic.py` — EtaProduct, JacProduct, etc.
- `qseries/_utilities.py` — already has qdegree/lqdegree/lqdegree0; extend, don't rewrite
- `qseries/__init__.py` — current exports; extend with Phase 2 functions

No local ADRs — all decisions captured here and in Phase 1 CONTEXT.md.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `QSeries` (`_series.py`) — the wrapper all building-block return values must use; `.series`,
  `.T`, `.r`, `.R` attributes; arithmetic operators propagate truncation correctly.
- `LaurentSeriesRing(R, 'q')` — the ring to use for all new q-series.
- `LaurentPolynomialRing(QQ, 'z')` — R for bivariate functions.
- `qdegree`, `lqdegree`, `lqdegree0` in `_utilities.py` — already correct; do not change.

### Established Patterns

- Return `QSeries(_wrap(...))` from every building-block function.
- Truncation parameter `T` passed explicitly; no global precision.
- `R = GF(p)` for mod-p variants (none in Phase 2, but pattern established).
- `sage.arith.misc.q_binomial(n, k, q)` — argument order (n, k, q); our `qbin(q, m, n)` must reorder.
- `sage.functions.other.qexp_eta(q, prec)` — returns a power series; wrap into `QSeries`.

### Integration Points

- `__init__.py`: add all 11 building-block functions and `sift`, `checkmult`, `checkprod`,
  `packageversion`, `changes` to `__all__`.
- Phase 3 (`_prodmake.py`) will call `etaq`, `aqprod` from this phase — those must be importable.
- Phase 4 (`_conversion.py`) will call `theta2`, `theta3`, `theta4`, `etaq`, `jacprod`.

</code_context>

<specifics>
## Specific Ideas

- `aqprod(-q, q, n)` is the tutorial's canonical example — test it first (BUILD-01 acceptance).
- `tripleprod(q, q^3, 10)` must reproduce Euler's pentagonal series — success criterion 1.
- `sift(etaq(q, 1, 500), q, 5, 0, 499)` must equal the E0 series from tutorial §6.2 — success criterion 3.
- `theta2` must carry `r = 1/4` (fractional shift) — test that `QSeries.r` equals `QQ(1, 4)`.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-building-blocks-utilities*
*Context gathered: 2026-09-16*
