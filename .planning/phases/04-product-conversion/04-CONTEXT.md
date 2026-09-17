# Phase 4: Product Conversion - Context

**Gathered:** 2026-09-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 4 delivers 10 product-conversion functions (CONV-02 through CONV-11) that identify or
expand product forms of q-series. All build on `prodmake` (Phase 3) and the symbolic output
types already implemented (`EtaProduct`, `EProduct`, `JacProduct`, `PochProduct`, `QProduct`).

Functions in scope:
- **eta-family:** `etamake`, `qetamake`
- **jac-family:** `jacprodmake`, `jac2prod`, `jac2series`, `qs2jaccombo`
- **misc/misc:** `mprodmake`, `qfactor`, `zqfactor`, `findprod`

No relation-finding functions (Phase 5/6) belong here.

</domain>

<decisions>
## Implementation Decisions

### Module Layout

- **D-01:** All 10 functions go into a single new file `qseries/_conversion.py`, following the
  pattern of `_building_blocks.py` and `_prodmake.py`. One new file, minimal `__init__.py` wiring.

- **D-02:** Split into **~3 plans** by subgroup:
  - Plan 04-01: `etamake` + `qetamake`
  - Plan 04-02: jac-family (`jacprodmake`, `jac2prod`, `jac2series`)
  - Plan 04-03: misc/unknowns (`mprodmake`, `qfactor`, `zqfactor`, `qs2jaccombo`, `findprod`)
    — `findprod` may move to Phase 5 if researcher confirms it requires relation-finding (see D-09)

  This matches the prior phases' pattern of 2-3 focused plans and lets the executor parallelize
  within each plan.

### Unknown Signatures (CONV-05, CONV-10, CONV-11)

- **D-03:** `mprodmake` (CONV-05), `qs2jaccombo` (CONV-10), and `findprod` (CONV-11) have
  unknown signatures (marked [?] in REQUIREMENTS.md). The **researcher reads the Garvan doc pages**
  for each and fully resolves the signature before the planner writes Plan 04-03. Do not stub
  without attempting to resolve from the doc page. If the doc page is genuinely ambiguous,
  researcher flags with specific questions; planner should not guess.

### etamake Greedy Algorithm

- **D-04:** `etamake(f, q, T)` uses a greedy loop:
  1. Strip the fractional q-power prefix `q^r_input` (record as `r_input`) and scalar constant
     `c` (record separately). The returned `r` is computed at the end (see step 5).
  2. At each step find the lowest-degree non-unit coefficient `c_k` (at `q^k`) in the residual.
  3. **Sign:** multiply the residual by `etaq(q, k, T)^(c_k)` (positive exponent) to cancel the
     `+c_k q^k` term — dividing out the factor. Record `eta(k*tau)^(-c_k)` (negative exponent)
     in the `EtaProduct` factors list.
     - Check: `theta4 = 1 - 2q + ...` → `c_1 = -2`, multiply residual by `etaq(q,1,T)^(-2)`,
       record `eta(tau)^2`. ✓
  4. **Termination:** the loop always terminates in ≤ T−1 steps because each iteration
     eliminates the leading non-unit term, raising the lowest non-unit degree by at least 1.
     Stop when the residual equals `1 + O(q^T)`. **Do not raise `ValueError`**; a series that
     isn't a clean eta product simply returns a long product (matching Maple's behaviour).
  5. **Eta q-shift correction:** each `eta(k*tau)` factor carries `q^(k/24)`, so the accumulated
     eta exponents shift the q-power. The returned `EtaProduct.r` is:
     ```
     r = r_input - sum(k * e_k / 24  for each recorded factor (k, e_k))
     ```
     where `e_k` is the exponent recorded in step 3 (i.e. `-c_k`).
     - Check: `theta2` has `r_input = 1/4`; factors `eta(4τ)^2, eta(2τ)^(-1)` contribute
       `(4*2 + 2*(-1))/24 = 6/24 = 1/4`; so `r = 1/4 - 1/4 = 0`... wait — the returned
       `EtaProduct` for `theta2` is `2·q^(-1/4)·eta(4τ)²/eta(2τ)`, meaning `r = -1/4`.
       Maple prints `q^(-1/4)` as part of the `EtaProduct`. The total shift from factors is
       `(4·2 + 2·(-1))/24 = 6/24 = 1/4`. So `r = r_input - 1/4 = 1/4 - 1/4 = 0`... this
       needs the researcher to verify against the exact Maple output. **Researcher must check
       the `etamake(theta2(q,T), q, T)` result on the doc page to confirm the sign convention
       for `EtaProduct.r` vs the q-shift stripped in step 1.**
     - The `theta2` test is mandatory precisely because `theta3` and `theta4` have zero net
       q-shift, so they would not expose a sign error in the r computation.

- **D-05:** `etamake` returns an `EtaProduct` with the accumulated `constant`, `r`, and `factors`
  list. Must reproduce the Phase 4 success criterion:
  - `etamake(theta3(q,100), q, 100)` → `eta(2*tau)^5 / (eta(4*tau)^2 * eta(tau)^2)`
  - `etamake(theta2(q,100), q, 100)` → `2 * q^(-1/4) * eta(4*tau)^2 / eta(2*tau)` — mandatory
    test for the q-shift correction (theta3/theta4 both have zero net shift and would not catch
    an error here)
  - `etamake(theta4(q,100), q, 100)` → `eta(tau)^2 / eta(2*tau)`

### jacprodmake Algorithm

- **D-08:** `jacprodmake(f, q, T [, base])` method:
  1. Call `prodmake(f, q, T)` to get exponent sequence `{n: e_n}`.
  2. Find the smallest period `P` of the exponent sequence (i.e. smallest `P` such that
     `e_n = e_{n mod P}` for all `n`). The optional 4th argument `base` overrides `P` directly.
  3. For each residue class `a` in `0..P-1`:
     - `a == 0`: contributes `JAC(0, P, ∞)^(e_0)` (special case: single Pochhammer factor).
     - `a` and `P-a` (with `a < P-a`): if `e_a == e_{P-a}`, contributes `JAC(a, P, ∞)^(e_a)`.
       If `e_a ≠ e_{P-a}`, contributes fractional exponents — e.g. the sqrt case
       `JAC(a,P,∞)^(e_a/2) * JAC(P-a,P,∞)^(e_{P-a}/2)` (or equivalent rational exponents).
     - `a == P/2` (if `P` even): `e_{P/2}` forms its own class → `JAC(P/2, P, ∞)^(e_{P/2}/2)`.
  4. Return `JacProduct` with the accumulated factors. `JacProduct` already supports rational
     exponents (implemented in `_symbolic.py`).
  - **Mandatory test:** the tutorial's `sqrt(JAC(7,14,∞) / JAC(0,14,∞))` example exercises
    fractional exponents from unequal paired residue classes — researcher must locate and use
    this exact example.

### findprod — Phase Assignment

- **D-09:** `findprod` (CONV-11) is described as "products that are a linear combination of
  q-series". If the researcher confirms from the doc page that `findprod` requires the relation-
  finding machinery (linear algebra over a basis of products), **move `findprod` to Phase 5**
  rather than stubbing it in Phase 4. Researcher makes this determination and notes it in
  RESEARCH.md; planner adjusts plan grouping accordingly.

### qfactor Input and Return Type

- **D-06:** `qfactor(f [, T])` accepts `f` as a **Sage polynomial or rational function element**
  from `PolynomialRing(QQ, 'q')` or its fraction field. Callers construct `f` using Sage
  polynomial arithmetic (e.g. `R.<q> = QQ[]; t8 = (1-q^9)*.../(1-q)*...`). This is the most
  natural Sage representation for a polynomial/rational function, consistent with Sage's `factor()`.

- **D-07:** `qfactor` returns a **rich structured result** capturing the rational product form:
  `(numerator QProduct, denominator QProduct, q^r prefactor)`. This preserves the structure
  of results like `q^6 * (1-q^9)(1-q^10)(1-q^11)(1-q^16) / ((1-q)(1-q^2)(1-q^3)(1-q^4))`.
  Exact return type (namedtuple, dataclass, or plain tuple) is Claude's discretion — choose
  whichever makes `__repr__` and downstream use cleanest. Researcher should check what Maple
  returns for `qfactor(t8, 20)` to confirm the structure.

### Claude's Discretion

- Exact return type container for `qfactor` (namedtuple vs dataclass vs tuple).
- Whether `qs2jaccombo` and `findprod` are placed in Plan 04-02 or 04-03 once researcher
  resolves their signatures (may belong with jac-family if semantics are close).
- Handling of edge cases in `zqfactor` and `mprodmake` — researcher resolves from doc pages.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Garvan qseries Documentation

- `https://qseries.org/fgarvan/qmaple/qseries/` — function index with links to individual doc pages
- `https://qseries.org/fgarvan/qmaple/qseries/qseriesdoc.pdf` — tutorial:
  - §3.2: `qfactor(t8, 20)` reference result (numerator/denominator product form, q^6 shift)
  - §3.3/3.4: `jacprodmake`, `jac2prod`, `jac2series` examples
  - §3: `etamake` examples including theta3, theta4, theta2 expected results
- **Per-function doc pages** (linked from function index) — researcher MUST read for:
  - `etamake` — exact greedy algorithm, convergence behavior, leading coefficient handling
  - `qetamake` — how _E notation differs from eta, expected examples
  - `jacprodmake` — periodicity detection in exponent sequence, 4th arg (force period)
  - `jac2prod` — JAC→Poch conversion rules including JAC(0,b,∞) special case
  - `jac2series` — theta-series substitution formula
  - `mprodmake` — full signature and semantics (CONV-05, [?])
  - `qs2jaccombo` — full signature and semantics (CONV-10, [?])
  - `findprod` — full signature and semantics (CONV-11, [?])
  - `qfactor` — confirm input type, return format, what t8 is in the example
  - `zqfactor` — bivariate analogue, confirm (z,q) argument handling

### Project Planning Docs

- `.planning/REQUIREMENTS.md` — CONV-02 through CONV-11 define acceptance criteria
- `.planning/phases/03-prodmake-andrews-algorithm/03-CONTEXT.md` — prodmake API, QProduct
  exponent sign convention (e_n = -a_n), D-01 (requires r==0 and b_0==1)
- `.planning/phases/01-foundation/01-CONTEXT.md` — QSeries API (shift r, T propagation)
- `.planning/phases/02-building-blocks-utilities/02-CONTEXT.md` — etaq, jacprod, theta* APIs;
  bivariate z-variable interface pattern (D-03, D-04)

### Existing Code (read before planning)

- `qseries/_symbolic.py` — `EtaProduct`, `EProduct`, `JacProduct`, `PochProduct`, `QProduct`:
  dataclass fields, `__repr__`, `to_series(T)` — these are the return types for this phase
- `qseries/_prodmake.py` — `prodmake(f, q, T)` — called internally by `etamake`, `qetamake`,
  `jacprodmake`, `findprod`
- `qseries/_series.py` — `QSeries`: `.series`, `.T`, `.r`, `.R`
- `qseries/_building_blocks.py` — `etaq`, `jacprod`, `theta`, `theta2`, `theta3`, `theta4`
  for constructing test inputs and use inside etamake
- `qseries/__init__.py` — current exports; extend with all 10 new functions

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `EtaProduct` (`_symbolic.py`) — return type for `etamake`; `constant`, `r`, `factors` list of
  `(level, exponent)` pairs; `to_series(T)` already handles fractional q-shift accumulation.
- `EProduct` (`_symbolic.py`) — return type for `qetamake`; `exponents` dict of `k → e_k`.
- `JacProduct` (`_symbolic.py`) — return type for `jacprodmake`; supports rational exponents;
  `to_series(T)` handles `JAC(0,b,∞)` special case.
- `PochProduct` (`_symbolic.py`) — return type for `jac2prod`; `factors` list of `(a, b, e)`.
- `QProduct` (`_symbolic.py`) — used internally by `etamake`/`qetamake` via `prodmake`.
- `prodmake(f, q, T)` (`_prodmake.py`) — core dependency; requires `f.r == 0` and `b_0 == 1`.
- `etaq(q, k, T)` (`_building_blocks.py`) — used inside `etamake` greedy loop.
- `jacprod(a, b, q, T)` (`_building_blocks.py`) — building block for jac-family tests.
- `theta2`, `theta3`, `theta4` (`_building_blocks.py`) — primary test inputs for `etamake`.

### Established Patterns

- New module per functional group: `_conversion.py` follows `_building_blocks.py`, `_prodmake.py`.
- `from sage.all import QQ, ZZ, ...` — Sage imports only from `sage.all`.
- Explicit `T` parameter throughout; `T` propagates as `min(T1, T2)`.
- Tests in `tests/test_conversion.py`; expected values from Maple docs only.
- `raise ValueError(...)` for invalid inputs — no silent normalization.

### Integration Points

- `__init__.py`: add all 10 functions to `__all__`.
- `_conversion.py` imports `prodmake` from `qseries._prodmake` — no circular import (conversion
  → prodmake, not the reverse).
- `qfactor` uses `PolynomialRing(QQ, 'q')` or `QQ['q'].fraction_field()` for input handling —
  distinct from the `LaurentSeriesRing` used elsewhere; document clearly.

</code_context>

<specifics>
## Specific Ideas

- The `qfactor(t8, 20)` example (CONV-06 success criterion) is the highest-confidence oracle for
  Plan 04-03. Researcher must pull the exact expected result from tutorial §3.2 before the planner
  writes the test.
- `etamake` on `theta3(q, 100)` is the primary oracle for Plan 04-01 (success criterion 1).
- `jac2series(j, 20)` oracle (success criterion 2) must come from a specific Maple doc example
  for a known `JacProduct` `j` — researcher identifies which example.

</specifics>

<deferred>
## Deferred Ideas

- None raised during discussion.

</deferred>

---

*Phase: 04-product-conversion*
*Context gathered: 2026-09-16*
