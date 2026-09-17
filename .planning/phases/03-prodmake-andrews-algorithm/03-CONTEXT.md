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
are Phase 4, and they build on `prodmake`. Fractional q-power prefix handling belongs in Phase 4
(etamake), not here.

</domain>

<decisions>
## Implementation Decisions

### The Algorithm — State It Explicitly

The algorithm is two nested loops over exact arithmetic. Do NOT leave it to the planner to
rediscover from a vague description.

Given `f = Σ_{n≥0} b_n q^n` with `b_0 = 1`, find exponents `a_n` such that
`f = ∏_{n≥1} (1 − q^n)^(−a_n)`.

**Step 1 — compute auxiliary sequence `c_n`:**

```
c_n = n·b_n − Σ_{k=1}^{n−1} b_{n−k} · c_k      for n = 1, 2, …, T−1
```

**Step 2 — recover exponents `a_n`:**

```
a_n = (c_n − Σ_{d | n, d < n} d · a_d) / n      for n = 1, 2, …, T−1
```

These two recurrences run in order n = 1, 2, … using only previously computed values.
No linear algebra. Arithmetic is exact over `QQ` throughout (Sage's rational field).
`divisors(n)` from `sage.all` gives the divisors of n; filter `d < n` in the inner sum.

The exponents `a_n` come out as rational numbers from the division by n; for a proper q-series
with integer coefficients they will be integers. Store them as Sage rationals (the division
produces them naturally) — integer-valued rationals are fine.

- **D-01:** `prodmake` **requires `r == 0` and `b_0 == 1`; raise `ValueError` otherwise.**
  Maple's `prodmake` takes a plain q-series starting at 1. If `f.r != 0` (fractional prefix)
  or the constant term is not 1, raise immediately. Do not strip-and-restore; do not silently
  normalize. The doc page decides if there is any exception to this — but the default is raise.
  Fractional-prefix handling belongs in `etamake` (Phase 4), which calls `prodmake` after
  stripping the prefix.

- **D-02:** Exponents for `n = 1, …, T−1` are computed and stored in `QProduct.exponents`.
  Zero exponents MAY be omitted (matching how `QProduct.__repr__` already works) or stored;
  Claude's discretion — choose whichever makes `to_series(T)` round-trip cleanest.

- **D-03:** For the degenerate input `f = 1 + O(q^T)` (all coefficients zero past 0), the
  recurrence correctly produces all `a_n = 0`. Return `QProduct(exponents={})`, representing
  the empty product (= 1). This is mathematically correct and should not raise.

### checkprod — Use the Phase 2 Research Result

The `checkprod` signature was **already resolved** in Phase 2 research (02-RESEARCH.md,
"Resolved Unknowns"). Do NOT send the planner back to the doc page.

- **D-04:** `checkprod(f, M, Q)` — takes a q-series `f`, upper bound `M`, and base `Q`.
  Returns `[c, n]` (the "nice product" representation). This is the exact signature from
  the Maple doc page, already verified in Phase 2 research.

- **D-05:** `checkprod` calls `prodmake` internally on `f`. It does NOT accept a `QProduct`
  directly — there is no Maple counterpart for that path and it was an invention. `checkprod`
  fills the stub in `_utilities.py` using the resolved signature; the planner reads
  `.planning/phases/02-building-blocks-utilities/02-RESEARCH.md` for the resolved details.

- **D-06:** Fill the stub: replace the `raise NotImplementedError(...)` body in `_utilities.py`
  with the real implementation. The function signature in `_utilities.py` must be updated to
  match `checkprod(f, M, Q)` (the stub currently has `checkprod(f)` from Phase 2).

### Module Location

- **D-07:** Implement `prodmake` in a new file `qseries/_prodmake.py`. Import and re-export
  from `__init__.py`. Do not add it to `_building_blocks.py` or `_utilities.py`.

### Claude's Discretion

- Whether zero exponents are stored or omitted in `QProduct.exponents`.
- Exact type of stored exponents (Sage rational vs integer — whichever the recurrence produces
  naturally without extra conversion).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Garvan qseries Documentation

- `https://qseries.org/fgarvan/qmaple/qseries/` — function index; links to individual doc pages
- `https://qseries.org/fgarvan/qmaple/qseries/qseriesdoc.pdf` — tutorial §3.1: Rogers–Ramanujan
  example with full expected exponent table; §3 contains other `prodmake` examples
- **prodmake doc page** (linked from function index) — MUST read for: exact recurrence formula
  confirmation, what Maple does with leading coefficient ≠ 1, return format

### Project Planning Docs

- `.planning/REQUIREMENTS.md` — CONV-01 (prodmake) and UTIL-06 (checkprod) define acceptance criteria
- `.planning/phases/02-building-blocks-utilities/02-RESEARCH.md` — "Resolved Unknowns" section:
  `checkprod(f, M, Q)` returning `[c, n]` already verified; planner reads this, not the doc page again
- `.planning/phases/01-foundation/01-CONTEXT.md` — QSeries API (shift rules, T propagation)
- `.planning/phases/02-building-blocks-utilities/02-CONTEXT.md` — D-08/D-09: checkprod stub
  location and export

### Existing Code (read before planning)

- `qseries/_symbolic.py` — `QProduct`: `exponents` dict, `__repr__`, `to_series(T)`
- `qseries/_series.py` — `QSeries`: `.series`, `.T`, `.r`, `.R`
- `qseries/_utilities.py` — `checkprod` stub to be replaced
- `qseries/__init__.py` — current exports; extend with `prodmake`
- `qseries/_building_blocks.py` — `etaq`, `aqprod` for test inputs

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `QProduct` (`_symbolic.py`) — exact return type; `exponents` dict maps `n → e_n`;
  `to_series(T)` already round-trippable; `__repr__` suppresses zero exponents.
- `QSeries` (`_series.py`) — input type; `.series` is raw Sage `LaurentSeries`; `.r` is
  rational shift; `.T` is truncation order.
- `aqprod`, `etaq` (`_building_blocks.py`) — for constructing test inputs.
- `sage.all.divisors(n)` — returns divisors of n; use directly in the recurrence inner sum.

### Established Patterns

- New module per functional group: `_prodmake.py` follows `_building_blocks.py` / `_utilities.py`.
- Explicit `T` parameter — `prodmake(f, q, T)` matches Maple's argument order.
- `from sage.all import QQ, ZZ, divisors` — `sage.all` imports only.
- Tests in `tests/test_prodmake.py`; expected values from Maple docs only, never from running
  the code being tested.

### Integration Points

- `__init__.py`: add `prodmake` to `__all__`; `checkprod` already exported (stub needs update).
- Phase 4 calls `prodmake` internally — must be importable as
  `from qseries._prodmake import prodmake`.
- `checkprod` in `_utilities.py` imports `prodmake` from `_prodmake`; no circular import
  (utilities → prodmake, not the reverse).

</code_context>

<specifics>
## Test Oracles — Concrete Expected Values

Tests that only check "exponent −1 at n ≡ ±1 mod 5" will pass on a wrong implementation that
gets n ≡ 0, ±2 wrong. Every test must check the full exponent dict, not a subset.

### Oracle 1 — Identity round-trip via etaq

```python
f = etaq(q, 1, 20)   # = prod_{n>=1}(1-q^n) to O(q^20)
p = prodmake(f, q, 20)
# Expected: QProduct(exponents={1: -1})  — i.e., a_1 = -1, all others 0
# because etaq(q,1,T) = (1-q^1)^1 * (1-q^2)^1 * ... from prodmake's perspective
# WAIT: etaq = prod(1-q^n), so prodmake should give a_n = 1 for all n, not -1.
# The sign depends on the product convention: f = prod(1-q^n)^(-a_n) means
# if f = prod(1-q^n)^1 then a_n = -1 for all n up to T-1.
# Planner: verify this sign convention against the doc page before writing the test.
```

**Simpler oracle:** `prodmake(1 + q + q^2 + ... (geometric), q, T)` where the exact expected
exponents are known by hand. Use `prodmake(aqprod(q, q, 20), q, 20)` and re-expand:
`QProduct.to_series(20)` must equal `aqprod(q, q, 20)` to `O(q^20)`. This is a round-trip
test, not a fixed-value test — but it's meaningful because `QProduct.to_series` is independent
of `prodmake`.

### Oracle 2 — Rogers–Ramanujan (tutorial §3.1)

The Rogers–Ramanujan series is `R(q) = sum_{n>=0} q^{n^2} / (q;q)_n` (or the G-series form
shown in the tutorial). `prodmake(R, q, T)` must return a `QProduct` where:

- `a_n = 1` for n ≡ ±1 (mod 5) — i.e., n = 1, 4, 6, 9, 11, 14, ...
- `a_n = 0` for all other n

**The test must assert the full `exponents` dict up to T−1**, not just check a few values.
Pull the exact expected dict from tutorial §3.1 — do not compute it from the code.

### Oracle 3 — A series with known product form from the tutorial

Pick any other `prodmake` example from §3 of the tutorial where Maple prints the full
`QProduct`. Use that as a third fixed-value test. Planner: read §3 and pick one with a
short, checkable exponent list (e.g., fewer than 10 nonzero terms up to order 20).

</specifics>

<deferred>
## Deferred Ideas

- Fractional q-power prefix handling in `prodmake` — belongs in `etamake` (Phase 4). CONV-01
  success criterion 3 is moved to Phase 4; it does not apply to `prodmake` directly.
- Rational exponents in `QProduct.exponents` — deferred to Phase 4 (jacprodmake).

</deferred>

---

*Phase: 03-prodmake-andrews-algorithm*
*Context gathered: 2026-09-16*
