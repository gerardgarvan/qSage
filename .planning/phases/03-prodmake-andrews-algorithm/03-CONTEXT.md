# Phase 3: prodmake (Andrews' Algorithm) - Context

**Gathered:** 2026-09-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 3 delivers one function: `prodmake(f, q, T)`.

It implements Andrews' divisor-sum recurrence to recover the infinite-product exponent sequence
from a truncated q-series, returning a `QProduct`. It also fills in the `checkprod` stub that
was deliberately left as `NotImplementedError` in Phase 2.

No other conversion functions (`etamake`, `qetamake`, `jacprodmake`, etc.) belong here — those
are Phase 4, and they build on `prodmake`.

</domain>

<decisions>
## Implementation Decisions

### Normalization & Leading-Term Contract

- **D-01:** The Andrews recurrence requires the series to start with constant term 1.
  How `prodmake` handles a leading coefficient ≠ 1 is **Claude's discretion** — read the
  `prodmake` CONV-01 doc page first and match Maple's behavior exactly (either raise or
  normalize internally). Do not invent behavior; derive it from the doc page.

- **D-02:** When the input `QSeries` has a fractional q-power prefix `r ≠ 0` (e.g., `theta2`
  with `r = 1/4`), behavior is also **Claude's discretion** — but CONV-01 success criterion 3
  explicitly requires that `prodmake` on a series with a fractional q-power prefix returns the
  correct rational prefactor alongside the integer exponent list. The planner must implement
  this. `QProduct` already has a `r` field in `_symbolic.py` for this purpose.

### Recurrence & Stopping Rule

- **D-03:** How many exponents to compute (e.g., all n from 1 to T−1, or only nonzero ones)
  is **Claude's discretion** — choose whatever makes `QProduct.to_series(T)` round-trip
  cleanest and matches Maple's output format.

- **D-04:** Degenerate input (series that equals 1 + O(q^T) with all higher coefficients zero)
  behavior is **Claude's discretion** — but the result must be mathematically correct.

- **D-05:** Exponent type (Python `int` vs Sage `Integer`) is **Claude's discretion** — choose
  what causes fewest surprises when exponents are later used in Sage ring arithmetic in Phase 4.

- **D-06:** **Integer exponents only** in Phase 3. The Andrews recurrence on a proper q-series
  produces integer exponents. Rational exponents (needed for `jacprodmake` in Phase 4) are
  explicitly deferred to Phase 4.

### checkprod Integration

- **D-07:** Fill the `checkprod` stub from Phase 2 in this phase. The stub currently raises
  `NotImplementedError("checkprod requires prodmake, available after Phase 3")`.

- **D-08:** `checkprod` must accept **both** a `QSeries` (Maple's calling convention — calls
  `prodmake` internally) and a `QProduct` (direct exponent inspection, avoids recomputation).
  Use `isinstance` dispatch.

- **D-09:** The "nice product" criterion for `checkprod` is **Claude's discretion** — the
  planner MUST fetch the `checkprod` doc page (UTIL-06 [?]) before implementing. The criterion
  is unknown from discussion alone; do not guess it.

### Module Location

- **D-10:** Implement `prodmake` in a new file `qseries/_prodmake.py`. Import and re-export
  from `__init__.py`. Do not add it to `_building_blocks.py` or `_utilities.py`.

### Claude's Discretion (Summary)

- Leading-coefficient normalization strategy (raise vs divide internally) — derive from doc page
- Fractional-prefix handling internals (how `r` is stripped, recurrence run, and `r` restored)
- Stopping rule (n range stored in QProduct.exponents)
- Degenerate-input handling (all-zero series)
- Exponent type (int vs Sage Integer)
- "Nice product" criterion in checkprod — derive from doc page

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Garvan qseries Documentation

- `https://qseries.org/fgarvan/qmaple/qseries/` — function index; links to individual doc pages
- `https://qseries.org/fgarvan/qmaple/qseries/qseriesdoc.pdf` — tutorial; §3.1 contains the
  Rogers–Ramanujan example (success criterion 2 for CONV-01); §3 contains other prodmake examples
- **prodmake doc page** (linked from function index) — MUST read for: normalization contract,
  recurrence formula, what happens with leading coefficient ≠ 1, exact return format
- **checkprod doc page** (UTIL-06 [?], linked from function index) — MUST read for: full
  argument signature, "nice product" criterion, return type, any optional arguments

### Project Planning Docs

- `.planning/REQUIREMENTS.md` — CONV-01 (prodmake) and UTIL-06 (checkprod) define acceptance
  criteria; CONV-01 success criteria 1–3 are the exact test oracle
- `.planning/phases/01-foundation/01-CONTEXT.md` — QSeries API decisions (D-03 through D-15)
  that prodmake must respect (shift rules, T propagation, etc.)
- `.planning/phases/02-building-blocks-utilities/02-CONTEXT.md` — D-08/D-09 established the
  checkprod stub and the expectation that Phase 3 fills it in

### Existing Code (read before planning)

- `qseries/_symbolic.py` — `QProduct` class (already built): its `exponents` dict, `__repr__`,
  and `to_series(T)` method define the return contract for `prodmake`
- `qseries/_series.py` — `QSeries` wrapper: `.series`, `.T`, `.r`, `.R` attributes
- `qseries/_utilities.py` — contains the `checkprod` stub at `NotImplementedError`; Phase 3
  replaces the body
- `qseries/__init__.py` — current exports; extend with `prodmake` (and update `checkprod`)
- `qseries/_building_blocks.py` — `etaq`, `aqprod` available for use in tests

No local ADRs — all decisions captured here and in prior phase CONTEXT.md files.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `QProduct` (`_symbolic.py`) — the exact return type; `exponents` dict maps `n → e_n`;
  `to_series(T)` already implemented and round-trippable; `__repr__` already suppresses zero exponents.
  `prodmake` constructs and returns a `QProduct` instance — no new class needed.
- `QSeries` (`_series.py`) — input type; `.series` gives the raw Sage `LaurentSeries`;
  `.r` gives the rational q-power shift; `.T` gives truncation order.
- `checkprod` stub (`_utilities.py`) — currently: `raise NotImplementedError(...)`. Phase 3
  replaces only the function body; the function signature may need updating after reading the doc page.
- `aqprod`, `etaq` (`_building_blocks.py`) — useful for constructing test inputs to `prodmake`.

### Established Patterns

- New module per functional group: `_prodmake.py` follows the pattern of `_building_blocks.py`,
  `_utilities.py`, `_symbolic.py`.
- Explicit `T` parameter everywhere — `prodmake(f, q, T)` matches Maple's argument order.
- `from sage.all import QQ, ZZ, divisors` etc. — use `sage.all` imports only.
- Tests in `tests/test_prodmake.py` (new file); expected values from Maple docs only.

### Integration Points

- `__init__.py`: add `prodmake` to `__all__`; `checkprod` is already exported (stub).
- Phase 4 (`_conversion.py`): `etamake` and `jacprodmake` call `prodmake` internally.
  Phase 3 must make `prodmake` importable as `from qseries._prodmake import prodmake`.
- `checkprod` in `_utilities.py` will import `prodmake` from `_prodmake.py` — avoid circular
  imports (utilities imports from prodmake, not the reverse).

</code_context>

<specifics>
## Specific Ideas

- **CONV-01 success criterion 2**: `prodmake` on the Rogers–Ramanujan series must give
  exponents −1 at n ≡ ±1 mod 5. This is the canonical tutorial §3.1 example and MUST be
  a test case with the expected value taken from the Maple doc page, not from running the code.
- **CONV-01 success criterion 1**: `prodmake(aqprod(q, q, 30), q, 30)` must round-trip —
  re-expand via `aqprod` and match original to order 30.
- **CONV-01 success criterion 3**: fractional q-power prefix (e.g., `r = 1/4`) must round-trip
  through `prodmake` → `QProduct.to_series()`.

</specifics>

<deferred>
## Deferred Ideas

- Rational exponents in `QProduct.exponents` — deferred to Phase 4 (jacprodmake needs them;
  prodmake on a proper q-series produces integer exponents only).
- `checkprod` with a bound parameter (if doc page reveals one) — implement per doc page, not ahead of it.

</deferred>

---

*Phase: 03-prodmake-andrews-algorithm*
*Context gathered: 2026-09-16*
