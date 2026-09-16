# Phase 1: Foundation - Context

**Gathered:** 2026-09-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the legal basis to proceed and the core data layer:
1. Licensing decision documented.
2. `QSeries` wrapper class with explicit truncation order `T` and `min(T1,T2)` propagation.
3. `EtaProduct` and `JacProduct` display types — printable in Maple-style notation, `.to_series(T)` method.
4. Degree functions: `qdegree`, `lqdegree`, `lqdegree0`.

No public q-series functions are implemented here — that is Phase 2.

</domain>

<decisions>
## Implementation Decisions

### Licensing

- **D-01:** Proceed immediately as a **clean reimplementation from docs only**. No Maple source is translated or consulted during coding. All implementation derives from the qseries documentation and qseriesdoc.pdf tutorial.
- **D-02:** Record the licensing decision in a **block comment at the top of `_series.py`**. No separate LICENSING.md. The comment must cite the Garvan docs URL and state that the approach is clean reimplementation, not translation.

### QSeries Wrapper

- **D-03:** `QSeries` always wraps **`LaurentSeriesRing(QQ, 'q')`** — never `PowerSeriesRing`. Laurent subsumes power series and handles negative-degree terms needed by `lqdegree`.
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
- **D-10:** `lqdegree0(f)` is a **safe variant** that returns `0` for the zero series instead of raising. Used inside relation finders where a zero intermediate result is valid.

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

- `.planning/REQUIREMENTS.md` — FOUND-01, FOUND-02, FOUND-03 define the acceptance criteria for this phase.
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
  - `LaurentSeriesRing(QQ, 'q')` as the standard series ring.
  - `.series` attribute convention for accessing raw Sage series.

### Integration Points

- `__init__.py` will import `QSeries`, `EtaProduct`, `JacProduct`, and the three degree functions when they exist.
- Phase 2 (`_building_blocks.py`) will import `QSeries` from `_series.py` and `EtaProduct`/`JacProduct` from `_symbolic.py`.

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
