# Patch list for the other .planning files (apply by hand)

## ROADMAP.md
- Phase 1 requirements → FOUND-01..05. Criterion 2 → "each FOUND-03 class prints in Maple notation and `.to_series(T)` round-trips"; add criterion "`QSeries` represents `q^(1/4)*(2+2q^2+…)` and a series Laurent in `z`".
- Phase 2 criterion 1: `aqprod(1 - q, q, 10)` is not a valid call. Replace with: `aqprod(q, q, 4)` equals `(1-q)(1-q^2)(1-q^3)(1-q^4)`; `tripleprod(q, q^3, 10)` equals Euler's pentagonal series (tutorial §6.1).
- Phase 2 criterion 3: `sift(f, 0, 3)` → `sift(etaq(q,1,500), q, 5, 0, 499)` equals the `E0` series printed in tutorial §6.2.
- Phase 3 criterion 1: keep; criterion 2 is redundant with 1 (etaq is `aqprod(q,q,∞)`); replace with the Rogers–Ramanujan example: `prodmake(x, q, 40)` gives exponents −1 at n ≡ ±1 mod 5 (tutorial §3.1).
- Phase 4 criteria: `jac2series(j, q, 20)` → `jac2series(j, 20)`; `qfactor(f, q)`/`zqfactor(f, q)` → `qfactor(t8, 20)` reproduces tutorial §3.2; add `etamake` on `theta3(q,100)` → `eta(2τ)^5/(eta(4τ)^2 eta(τ)^2)`.
- Phase 5: "9 exact relation finders" → 8. Criteria 1, 2, 4, 5 use invented signatures; replace with `findhom([θ3(q),θ4(q),θ3(q²),θ4(q²)], q, 2, 0)` → two relations; `findhomcombo(UE, [B1,B2], q, 3, 0, 'yes')` → `X1²X2 + 40X1X2² + 335X2³`; `findpoly(x, y, q, 3, 1, 60)` → `(X+6)³Y − 27(X+2)²`; `findcong(P, 1000)` → the four triples.
- Phase 6 criteria: fix signatures once the modp doc pages are read.
- Consider merging Phase 6 into Phase 5: the mod-p variants are the same code with the coefficient ring parameterised (`QQ` → `GF(p)`). A separate phase costs a full CONTEXT/PLAN/SUMMARY cycle for three thin wrappers.

## ARCHITECTURE.md
- "Product-recovery path": remove the coefficient matrix / `right_kernel` / Möbius steps. `prodmake` is the recurrence in CONV-01, nothing more. `etamake` is the greedy eta-multiplication loop; `jacprodmake` is `prodmake` + periodicity search. Only the `find*` family uses `right_kernel`.
- Series layer must be parameterised over the base ring (FOUND-01) and carry a rational shift (FOUND-02).
- `_symbolic.py` holds five classes, not two (FOUND-03).
- `qfactor` input is a polynomial/rational function in `QQ[q]`, not a `QSeries`; note the `factor()` step.

## PITFALLS.md
- #3: "partial fractions at roots of unity" is not how Andrews' algorithm works; replace with the recurrence. Phase reference "Phase 4" → Phase 3.
- #3/#11: fractional q-powers are not an edge case — `theta2` and every `etamake` output has one. Move to a Phase 1 pitfall tied to FOUND-02.
- Add: bivariate functions (`theta`, `tripleprod`, `quinprod`, `winquist`, `zqfactor`) — a `QQ`-only series ring cannot hold them.
- Add: `quinprod` overloads its 3rd argument (`int` | `'prodid'` | `'seriesid'`).
- Add: relation finders return polynomials in `X[i]`, and `findhom` has no `T` argument — the truncation is whatever the input series carry.

## STACK.md
- `q_binomial` row: Maple is `qbin(q, m, n)` = `[n; m]_q`, Sage is `q_binomial(n, m, q)`. Wrapper must swap and reorder.
- `qexp_eta` row: correct as-is (no `q^(1/24)`), matches `etaq(q, 1, T)`.

## 01-CONTEXT.md
- D-03: `LaurentSeriesRing(QQ,'q')` alone is insufficient — see FOUND-01/02. Rewrite as "LaurentSeriesRing over a pluggable base ring, plus rational exponent shift".
- D-09/D-10: `lqdegree0` is documented as the **monomial** variant of `lqdegree`, not a zero-safe alias. The options presented in the discussion log were all built on the wrong premise. Re-decide after reading the two doc pages; the zero-series behaviour is a separate, smaller question.
- Add the `X1..Xk` polynomial return convention (FOUND-04) as a decision, since it affects every relation finder.
