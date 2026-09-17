# Phase 1: Foundation - Context

**Gathered:** 2026-09-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the legal basis to proceed and the core data layer:
1. Licensing decision documented.
2. `QSeries` wrapper — explicit truncation order `T`, pluggable base ring `R`, rational q-power shift `r`.
3. Five symbolic output types: `QProduct`, `EtaProduct`, `EProduct`, `JacProduct`, `PochProduct` — each printable in Maple-style notation with `.to_series(T)` method.
4. Degree functions: `qdegree`, `lqdegree`, `lqdegree0` (semantics verified against their doc pages).

No public q-series functions are implemented here — that is Phase 2.

</domain>

<decisions>
## Implementation Decisions

### Licensing

- **D-01:** Proceed immediately as a **clean reimplementation from docs only**. No Maple source is translated or consulted during coding. All implementation derives from the qseries documentation and qseriesdoc.pdf tutorial.
- **D-02:** Record the licensing decision in a **block comment at the top of `_series.py`**. No separate LICENSING.md. The comment must cite the Garvan docs URL and state that the approach is clean reimplementation, not translation.

### QSeries Wrapper

- **D-03:** `QSeries` wraps **`LaurentSeriesRing(R, 'q')`** with a pluggable base ring `R` (default `QQ`; `GF(p)` for mod-p functions; a polynomial ring in `z` for bivariate functions). It also carries a rational exponent shift `r` so that `q^r * (Laurent series)` is representable — required for `theta2` (`r=1/4`) and all `etamake` outputs. Never `PowerSeriesRing`.
- **D-04:** The underlying Sage series is exposed as **`self.series`** (a `.series` attribute). Internal modules access it directly for raw Sage operations, then rewrap the result. No delegation boilerplate.
- **D-05:** Arithmetic on two `QSeries` instances propagates truncation order as `min(T1, T2)`. Arithmetic operators (`__add__`, `__mul__`, etc.) must enforce this.

### EtaProduct / JacProduct repr

- **D-06:** **Suppress trivial parts** in `EtaProduct.__repr__`:
  - Exponent `e=1` → omit the `^1` suffix (print `eta(k*tau)`, not `eta(k*tau)^1`).
  - q-power prefix `r=0` → omit the `q^0` entirely.
- **D-07:** Multi-factor EtaProducts are joined with **` * `** (space-star-space): e.g., `eta(tau)^24 * eta(2*tau)^-24`.
- **D-08:** `JacProduct.__repr__` uses the `JAC(a,b,infinity)` format from the project spec, with analogous suppression of trivial exponents.

### Degree Functions

- **D-09:** `qdegree(f)` raises **`ValueError`** for the zero series (degree undefined). Same for `lqdegree(f)`.
- **D-10:** `lqdegree0` is documented as the **q-monomial variant** of `lqdegree` (not merely a zero-safe alias). The planner **must** read the `lqdegree0` doc page before implementing — the exact semantics differ from `lqdegree` in a way the discussion did not capture. Zero-series behaviour is a secondary question to resolve from the doc page.

### Relation Finder Return Convention

- **D-11:** All relation-finding functions (`findhom`, `findhomcombo`, `findlincombo`, `findpoly`, etc.) return Sage **polynomial objects** in variables `X1, X2, ...` from `PolynomialRing(QQ, ['X1','X2',...])` — not bare coefficient vectors. This matches Maple's `X[i]` global variable convention and is required for tutorial examples to print correctly.

### Arithmetic Shift Propagation

- **D-12:** Arithmetic shift rules on `QSeries`:
  - `*`: r_out = r1 + r2
  - `/`: r_out = r1 − r2
  - `+`/`−`: if r1 == r2, keep it; if r1 − r2 is an integer k, multiply the leading series by q^k and use the smaller r; if r1 − r2 is not an integer, raise `ValueError` (Maple would return a symbolic sum — out of scope for v1).
- **D-13:** `T` after any QSeries operation is `result.prec()` (Sage's actual precision after the operation), not `min(T1, T2)`. The two agree when no relative-precision loss occurs, but division can reduce it. Tests should assert `qs.T == qs.series.prec()`.

### JacProduct Representation

- **D-14:** `JacProduct` carries `constant` and `r` fields (same as `EtaProduct`). `to_series` handles `a == 0` as `JAC(0,b,∞) = (q^b;q^b)_∞` only (single Pochhammer, not three factors). Rational exponent `e` is expanded via `jac.nth_root(den) ** num`.

### Degree Function Domain

- **D-15:** `lqdegree` and `lqdegree0` v1 domain: `QSeries` and the symbolic classes (`EtaProduct`, `JacProduct`, etc. — any object with a `.r` attribute). Symbolic sums of JAC terms (e.g. `c1*JAC(...) + c2*JAC(...)`) are out of scope for v1. This is a documented divergence from the Maple doc-page examples which show `lqdegree` on such sums.

### Claude's Discretion

- Exact internal field names on `EtaProduct` and `JacProduct` dataclasses (beyond `__repr__` and `.to_series()`).
- Whether `QSeries.__repr__` delegates to Sage's repr or custom-formats the series.
- Exact wording of the licensing comment in `_series.py`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Garvan qseries Documentation

- `https://qseries.org/fgarvan/qmaple/qseries/` — function index and per-function doc pages; primary oracle for signatures and expected outputs.
- `https://qseries.org/fgarvan/qmaple/qseries/qseriesdoc.pdf` — tutorial document; expected values for test cases come from here.

### Project Planning Docs

- `.planning/REQUIREMENTS.md` — FOUND-01 through FOUND-05 define the acceptance criteria for this phase.
- `.planning/research/ARCHITECTURE.md` — module structure, data flow diagrams, interface decisions already researched.
- `.planning/research/STACK.md` — Sage primitives to wrap, what NOT to use.

No local ADRs yet — all decisions are captured in this CONTEXT.md.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- None — codebase is empty. This is the first code written.

### Established Patterns

- None yet. Patterns established in Phase 1 will carry forward:
  - `LaurentSeriesRing(R, 'q')` with pluggable `R` as the standard series ring.
  - `QSeries(series, T, shift=r)` as the wrapper convention.
  - `.series` attribute for accessing raw Sage series in internal modules.

### Integration Points

- `__init__.py` will import `QSeries`, all five symbolic classes, and the degree functions when they exist.
- Phase 2 (`_building_blocks.py`) will import `QSeries` from `_series.py` and symbolic classes from `_symbolic.py`.
- Phase 5 (`_relations.py`) will import `PolynomialRing` and the `X1..Xk` return convention established here.

</code_context>

<specifics>
## Specific Ideas

- No specific visual references or "I want it like X" moments — decisions are driven by Maple documentation fidelity.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-09-16*
