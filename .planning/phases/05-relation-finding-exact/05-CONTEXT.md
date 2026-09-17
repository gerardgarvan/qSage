# Phase 5: Relation Finding (Exact) - Context

**Gathered:** 2026-09-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement all 11 relation-finding functions (8 exact QQ variants + 3 mod-p GF(p) variants,
merged from former Phase 6) in a single phase. Functions take lists of QSeries and return
polynomial relations as Sage polynomial objects in PolynomialRing(QQ, ['X1','X2',...]) or
PolynomialRing(GF(p), [...]) for the mod-p variants.

**Phase 6 merged into Phase 5.** The mod-p variants (findhommodp, findlincombomodp,
findlincombomodp — REL-03/04/08) are the same matrix algorithm with GF(p) as the coefficient
ring. Implementing both together eliminates a separate phase and avoids duplicated scaffold.
ROADMAP.md and REQUIREMENTS.md should be updated to reflect this merge.

Functions in scope:
- findhom, findhomcombo, findnonhom, findnonhomcombo (homogeneous/non-hom relation finding)
- findlincombo, findmaxind (linear combination / independence)
- findpoly (two-series polynomial relation)
- findcong (Ramanujan-type congruence hunting)
- findhommodp, findlincombomodp (mod-p variants — merged from former Phase 6)

</domain>

<decisions>
## Implementation Decisions

### Phase Scope (Merge Decision)
- **D-01:** Phase 6 is **merged into Phase 5**. All 11 relation-finding functions are implemented
  here. The mod-p variants share the same matrix/nullspace code path with GF(p) substituted for
  QQ. ROADMAP.md and REQUIREMENTS.md must be updated (Phase 6 removed, REL-03/04/08 folded into
  Phase 5 requirements).

### Matrix/Nullspace Algorithm
- **D-02:** The core algorithm for findhom/findnonhom/findlincombo and their mod-p variants:
  1. Build a Macaulay-style coefficient matrix — **rows = evaluated series, columns = monomials**
     of the appropriate degree in X1..Xk (or all degrees ≤ n for non-hom variants).
  2. Compute the **right nullspace** using `matrix(QQ, rows).right_kernel()` (or
     `matrix(GF(p), rows).right_kernel()` for mod-p variants).
  3. Each nullspace basis vector gives one relation polynomial in PolynomialRing(QQ, ['X1',...]).
- **D-03:** When the nullspace is trivial (no relations found), return **empty list `[]`**.
  Consistent with the list-of-polynomials return type; callers iterate without None-checking.

### topshift Semantics
- **D-04:** `topshift` trims the **top `topshift` rows** from the coefficient matrix before
  nullspace computation. Rows correspond to q-power coefficients q^0, q^1, q^2, .... Trimming
  top rows suppresses spurious relations caused by leading-term truncation artefacts.
  The tutorial §5 example uses `topshift=0`. Researcher must find a Garvan example with
  topshift > 0 to validate the trim direction precisely.

### Unknown Argument Signatures (REL-07, REL-09, REL-11)
- **D-05:** `findlincombo`, `findmaxind`, and `findcong` are marked `[?]` in REQUIREMENTS.md.
  The **gsd-phase-researcher must fetch the Garvan qseries doc pages** for these three functions
  to extract full argument lists and any optional parameters before planning can begin.
  Doc pages are at Garvan's qseries documentation site (researcher knows the URL pattern from
  prior phases — e.g. same site as findhom, findhomcombo).
- **D-06:** `findcong`'s optional 3rd argument is unknown — researcher resolves from the doc page.

### findcong Algorithm
- **D-07:** `findcong(f, T)` uses a **sift-and-check** approach:
  - Outer loop over candidate triples `(A, B, M)` where M is prime
  - For each triple: call `sift(f, q, A, B, T)` to extract the subsequence `a(An+B)`
  - Check if ALL extracted coefficients are 0 mod M
  - Collect passing triples into a set of `[B, A, M]` lists (note order from oracle)
  - Oracle: `findcong(1/etaq(q,1,1001), 1000)` → `{[4,5,5],[5,7,7],[6,11,11],[24,25,25]}`
- **D-08:** The search bounds for `(A, B, M)` — specifically what A ranges over and which primes M
  to try — must be extracted by the researcher from the Garvan doc page and the oracle example
  (A goes up to at least 24 from the oracle; exact upper bound rule needed).

### Return Type (Locked from Phase 1, D-11)
- **D-09:** All relation finders return **`PolynomialRing(QQ, ['X1','X2',...])` objects** (or
  `PolynomialRing(GF(p), [...])` for mod-p). NOT bare coefficient vectors. Matches Maple's `X[i]`
  convention and makes tutorial examples print correctly. This was decided in Phase 1 D-11 and
  is non-negotiable.

### Claude's Discretion
- Exact monomial ordering within the coefficient matrix (grlex vs lex) — choose to match
  Maple's output ordering on the tutorial examples.
- Whether findhomcombo and findnonhomcombo with `etaoption='yes'` call etamake on each
  monomial internally or return a parallel list — match Maple tutorial §5 output format.
- Implementation file structure: single `_relation.py` or split — planner's call.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Garvan Doc Pages (researcher must fetch)
- Garvan qseries documentation site — findhom, findhomcombo, findnonhom, findnonhomcombo doc pages
- Garvan qseries documentation site — findlincombo doc page (full argument list unknown — REL-07)
- Garvan qseries documentation site — findmaxind doc page (full argument list unknown — REL-09)
- Garvan qseries documentation site — findcong doc page (full argument list + 3rd arg unknown — REL-11)
- Garvan qseries documentation site — findhommodp, findlincombomodp doc pages (merged from Phase 6)

### Tutorial
- qseriesdoc.pdf §4 — findpoly example: recovers `(X+6)^3*Y - 27*(X+2)^2`
- qseriesdoc.pdf §5 — findhomcombo example: `U_{5,6} = X1^2*X2 + 40*X1*X2^2 + 335*X2^3`
- qseriesdoc.pdf §7 — findcong example: `{[4,5,5],[5,7,7],[6,11,11],[24,25,25]}`

### Project Planning Files
- `.planning/REQUIREMENTS.md` — REL-01 through REL-11 (acceptance criteria)
- `.planning/STATE.md` — Decisions and environment notes
- `.planning/phases/01-foundation/01-CONTEXT.md` — D-11: polynomial return type (non-negotiable)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `qseries/_utilities.py:sift` — Required by findcong's sift-and-check loop; already implemented
- `qseries/_conversion.py:etamake` — Required by findhomcombo/findnonhomcombo `etaoption='yes'` path
- `qseries/_series.py:QSeries` — All inputs are QSeries; access `.series` for raw Sage series coefficients

### Established Patterns
- All imports from `sage.all` only (no direct sage submodule imports)
- `QQ('1/4')` not `QQ(1,4)` for rational construction (Sage 9.5 compat — see STATE.md)
- Return type wrapping: internal modules use raw Sage objects, public API wraps in QSeries or
  the appropriate symbolic class
- `PolynomialRing(QQ, ['X1','X2',...])` for polynomial relations — established in Phase 1

### Integration Points
- `qseries/__init__.py` — all 11 new functions added to `__all__` and imported from `_relation.py`
- `tests/test_relation.py` — new test file, mirroring pattern from `tests/test_conversion.py`
- `qseries/_utilities.py` — `sift` called internally by findcong

</code_context>

<specifics>
## Specific Ideas

- The matrix/nullspace approach uses `matrix(QQ, rows).right_kernel()` — the standard Sage
  exact rational nullspace, not floating-point approximation.
- For mod-p: same matrix code, `GF(p)` substituted for `QQ`. Passing non-prime `p` raises
  `ValueError` before any computation (from Phase 6 requirement REL-03/04/08).
- findcong oracle: `findcong(1/etaq(q,1,1001), 1000)` → `{[4,5,5],[5,7,7],[6,11,11],[24,25,25]}`
  — note the series is `1/etaq(q,1,1001)` (Euler's generating function for partitions), T=1000.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-relation-finding-exact*
*Context gathered: 2026-09-17*
