# Phase 5: Relation Finding - Context

**Gathered:** 2026-09-17 · **Revised:** 2026-09-17 (topshift, matrix orientation, findcong bounds, optional-argument overloading corrected against the tutorial and the `findnonhomcombo` doc page)
**Status:** Ready for planning

<domain>
## Phase Boundary

All 11 relation-finding functions, exact and mod-p, in one phase (former Phase 6 merged here — ROADMAP.md and REQUIREMENTS.md updated accordingly):

- `findhom`, `findhomcombo`, `findnonhom`, `findnonhomcombo`
- `findlincombo`, `findmaxind`
- `findpoly`
- `findcong`
- `findhommodp`, `findhomcombomodp`, `findlincombomodp`

Inputs are `QSeries`; relations are returned as Sage polynomials in `X1..Xk` (or `X, Y` for `findpoly`) over `QQ`, or over `GF(p)` for the mod-p variants.

</domain>

<decisions>
## Implementation Decisions

### D-01 — Scope
Phase 6 merged into Phase 5. Mod-p variants reuse the exact code path with `GF(p)` as the coefficient ring; a non-prime `p` raises `ValueError` before any computation.

### D-02 — Matrix construction (Maple's description, tutorial §4.1)
1. Generate the monomials: degree exactly `n` in `X1..Xk` for `findhom`/`findhomcombo`; all degrees `≤ n` for `findnonhom`/`findnonhomcombo`; degree 1 for `findlincombo`. For the `*combo` variants, `f` is an extra row.
2. Evaluate each monomial on the series in `L` and take the first `N` q-coefficients as a **row**: matrix `M` is `(#rows) × N`.
3. Relations = `M.left_kernel()` (Maple: "kernel of the transpose"). Each kernel vector's entries are the coefficients of the corresponding monomials; the `*combo` variants solve for `f` as a combination of the others (the `f` row's coefficient normalised to 1).
4. Map each kernel vector to a polynomial in `PolynomialRing(QQ, ['X1',…,'Xk'])`.
5. Print `# of terms , N` and, for the combo variants, `matrix is , rows, x, N`, matching Maple's console output (these are the only observable diagnostics and the tests can assert them).

### D-03 — Empty result
No relations → return an empty set/list. The `*combo` functions always return a collection: the doc page says more than one combination may come back when `L` is linearly dependent.

### D-04 — `topshift` (corrected)
`topshift` **adds** equations. The number of q-coefficients used is
`N = (#rows) + C + topshift`, where the printed `# of terms` in the tutorial fixes `C`: `findhom` 4 rows → 25, 10 rows → 31; `findhomcombo` 5 rows → 25; `findnonhomcombo` 4 rows → 24. So `C = 20` for the combo variants and apparently `21` for `findhom`; the planner sets `C` per function from these four data points. Doc page: `topshift - integer greater than -20`, so negative values are legal. If a series in `L` carries fewer than `N` terms, raise `ValueError` naming the shortfall — do not silently use fewer. Default `topshift = 0`.

### D-05 — Optional-argument overloading (from the doc page)
Maple accepts `findnonhomcombo(f,L,q,n,topshift,etaoption)`, `(f,L,q,n,topshift)`, `(f,L,q,n,etaoption)`, `(f,L,q,n)`; trailing arguments are distinguished by type (`int` → `topshift`, string `'yes'`/`'no'` → `etaoption`). Implement the same dispatch for `findhom`, `findhomcombo`, `findnonhom`, `findnonhomcombo` (and the mod-p forms once their pages are read). `etaoption` values are the strings `'yes'`/`'no'`; with `'yes'`, each monomial in the result is additionally shown as an `EtaProduct` via `etamake` (match the tutorial §4.2 printout).

### D-06 — Still-unverified signatures
`findlincombo`, `findlincombomodp`, `findmaxind`, `findhommodp`, `findhomcombomodp`, and the optional 3rd argument of `findcong` are `[?]`. The researcher reads each doc page before Plan 05-03 is written. Believed shapes: `findlincombo(f, L, SYMS, q, topshift, etaoption)`, `findhommodp(L, q, p, n, topshift)` — confirm the position of `p`.

### D-07 — `findcong` algorithm (corrected)
`findcong(f, T [, …])` returns a set of `[B, A, M]` with `a(An+B) ≡ 0 (mod M)`.
- For each `A` (bound from the doc page) and each `0 ≤ B < A`: `M = gcd(a(An+B) for An+B ≤ T)`; a candidate if `M > 1`.
- `M` is **not** restricted to primes — the oracle contains `[24,25,25]`, and `gcd` reproduces it (`p(24)=1575`, `p(49)=173525`, gcd 25).
- Suppress implied triples: skip `(B, A, M)` if an already-reported `(B', A', M')` has `A' | A`, `B ≡ B' (mod A')`, and `M | M'`. This is why the oracle has four entries and not `[9,10,5]`, `[4,10,5]`, ….
- Oracle: `findcong(1/etaq(q,1,1001), 1000) == {[4,5,5],[5,7,7],[6,11,11],[24,25,25]}`.
- Uses `sift` from `_utilities.py` for the subsequence extraction.

### D-08 — `findpoly(x, y, q, deg1, deg2 [, check])`
Monomials `X^i Y^j`, `i ≤ deg1`, `j ≤ deg2`; same left-kernel machinery; result in `PolynomialRing(QQ, ['X','Y'])`. If `check` is given, verify the relation to `O(q^check)` and print the check as Maple does. Oracle: tutorial §4.5 → `(X+6)^3·Y − 27·(X+2)^2`.

### D-09 — Return type (Phase 1 D-11, fixed)
Polynomials in `X1..Xk` / `X, Y`, never bare vectors. Tests compare the relation **span** (or, for `*combo`, the normalised polynomial), not ordering.

### Claude's Discretion
- Monomial ordering (choose the one that reproduces Maple's printed polynomials in §4.1–4.3).
- One module `_relations.py` vs. a split.
- Exact console-output formatting beyond the `# of terms` / `matrix is` lines.

</decisions>

<canonical_refs>
## Canonical References

- `https://qseries.org/fgarvan/qmaple/qseries/functions/` — doc pages for every function in scope; `findnonhomcombo.html` (already read: calling sequences, `topshift > -20`, global `X`, worked example with `N(q)/z^6` in terms of `x`).
- `qseriesdoc.pdf` §4.1 (`findhom` theta example, `# of terms` 25/31, two quadratic relations), §4.2 (`findhomcombo`, `U_{5,6} = X1²X2 + 40X1X2² + 335X2³`), §4.3–4.4 (`findnonhom`/`findnonhomcombo`, Watson's mod-7 equation), §4.5 (`findpoly`), §7 (`findcong`).
- `.planning/REQUIREMENTS.md` REL-01…REL-11; `.planning/REFERENCE.md` if present.
- `qseries/_utilities.py` (`sift`), `qseries/_conversion.py` (`etamake`), `qseries/_series.py` (`QSeries`, shift arithmetic).

</canonical_refs>

<code_context>
## Existing Code Insights

- The `findnonhomcombo` doc example builds `c = 3·q^(1/3)·etaq(q,3,100)³/etaq(q,1,100)` and then `x = c³/a³`: a `q^(1/3)` shift cubed to an integer, then divided. This is the first real exercise of the Phase 1 shift arithmetic (D-12) — include it as a test.
- Sage 9.5: construct rationals as `QQ('1/3')` / `QQ((1,3))`, not `QQ(1,3)`.
- Imports from `sage.all` only.

</code_context>

<specifics>
## Specific Ideas

- `findhom([theta3(q,100), theta4(q,100), theta3(q^2,100), theta4(q^2,100)], q, 1, 0)` → `{{}}` and `# of terms , 25`; degree 2 → two relations, `# of terms , 31`. Assert both the count and the span.
- `findhomcombo(f, [B1, B2], q, 3, 0, 'yes')` → `X1²X2 + 40X1X2² + 335X2³` with `f = UE(q,6,5,50)`, `B1 = etaq(q,1,50)^5/etaq(q,5,50)`, `B2 = q·etaq(q,5,50)^5/etaq(q,1,50)`.
- `findpoly(x, y, q, 3, 1, 60)` → `(X+6)³Y − 27(X+2)²`.
- `findcong(1/etaq(q,1,1001), 1000)` → the four triples above.

</specifics>

<deferred>
## Deferred Ideas

None.

</deferred>

---
*Phase: 05-relation-finding · Context revised 2026-09-17*
