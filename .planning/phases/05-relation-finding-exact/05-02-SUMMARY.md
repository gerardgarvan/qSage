---
phase: 05-relation-finding-exact
plan: 02
status: complete
completed: 2026-11-05
requirements: [REL-01, REL-02, REL-05, REL-06, REL-07]
files_modified: [qseries/_relations.py, tests/test_relations.py]
---

# 05-02 Summary: findhom, findhomcombo, findnonhom, findnonhomcombo, findlincombo

All five share `_kernel_search`: monomials from `IntegerVectors`, an (#rows x N) coefficient
matrix, `matrix(QQ, rows).left_kernel()`, mapped to polynomials in `X1..Xk` over QQ.
Combo variants put `f` as the last row and return `{P : f = P(L)}`.

## Oracles reproduced (tutorial, arXiv math/9812092)

| Check | Result |
|---|---|
| §4.1 `findhom(theta family, q, 1, 0)` | `set()`, prints `# of terms , 25` |
| §4.1 degree 2 | 2 relations spanning `X1²+X2²−2X3²`, `X1X2−X4²`; `# of terms , 31` |
| §4.2 `findhomcombo(UE(q,6,5,50), [B1,B2], q, 3, 0, yes)` | exactly `{X1²X2 + 40X1X2² + 335X2³}`, `# of terms , 25` |
| §4.3 3 series, deg ≤ 3, topshift 20 | `# of terms , 61` |
| §4.4 `findnonhomcombo(T², [T, ξ], q, 7, −15)` | Watson's mod-7 relation returned; `# of terms , 42`, `matrix is , 37, x, 42` |
| `findlincombo(12f1+13f2, ...)` | `{12X1 + 13X2}`; non-combination prints `%NOT A LINEAR COMBO.%` |

C = 21 (findhom/findnonhom) and C = 20 (combo) confirmed by all five printed-term data points.

## Deviations

- **Test oracle fixes.** The plan's `UE = etaq^6/etaq(q,5)` (weight 5/2) was not the tutorial's
  series. The test now implements the tutorial's `UE(q,k,p,trunk)` procedure (Legendre symbol
  sum). Added the §4.4 Watson test and the §4.3 `# of terms , 61` test.
- **q-shift handling.** `_coefficient_rows` aligns rational shifts (they must differ by
  integers; the common fractional factor is dropped) and reads coefficients from the
  smallest valuation, so series with `r ≠ 0` or negative leading powers are handled. Plain
  `.series[j]` indexing would have silently ignored `r`.
- **Precision check.** Besides `QSeries.T >= N`, each monomial's actual Sage precision is
  checked against the coefficient window, raising `ValueError` on a shortfall.
- **§4.4 dual result.** `T²` is itself a monomial (`X1²`), so the result is
  `{watson_poly, X1²}`; the doc page allows several combinations when the monomials are
  dependent. Test asserts the Watson polynomial is present and nothing else but `X1²`.
