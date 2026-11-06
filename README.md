# qseries-sage

A Python/SageMath port of Frank Garvan's Maple **qseries** package (version 1.3): q-products,
theta functions, product conversion (Andrews' algorithm, eta-products, Jacobi products) and
the search for polynomial relations and congruences between q-series — without Maple.

This is a clean reimplementation written from Garvan's public documentation and tutorial only;
no Maple source code was consulted. The qseries package and its documentation are by
Frank Garvan: <https://qseries.org/fgarvan/qmaple/qseries/>.

## Requirements

- SageMath (tested with Ubuntu's SageMath 9.5 on Python 3.10, and Sage 10.x / passagemath)
- Run Python through Sage: `sage -python`, `sage -pip`

## Install

```bash
cd qSage
sage -pip install --user .
sage -python -c "from qseries import *; print(packageversion())"   # 1.3.0
```

The distribution is called `qseries-sage`; the import name is `qseries`.

## Example

```python
from sage.all import LaurentSeriesRing, QQ
from qseries import etaq, theta3, theta4, prodmake, findhom, findcong, QSeries

R = LaurentSeriesRing(QQ, 'q', default_prec=110)
q = R.gen()

# Quadratic relations among theta functions (Garvan tutorial, section 4.1)
findhom([theta3(q, 100), theta4(q, 100), theta3(q**2, 100), theta4(q**2, 100)], q, 2, 0)
# -> {X1^2 + X2^2 - 2*X3^2, X1*X2 - X4^2}

# Ramanujan's partition congruences
P = QSeries(etaq(q, 1, 1001).series.__invert__(), 1001)
findcong(P, 1000)
# -> {(4, 5, 5), (5, 7, 7), (6, 11, 11), (24, 25, 25)}
```

Series are `QSeries` objects: a Sage Laurent series with an explicit truncation order `T`
and a rational q-power shift `r` (so `theta2` can carry its `q^(1/4)` factor).

## Functions (41)

| Group | Functions |
|---|---|
| Building blocks | `aqprod`, `qbin`, `etaq`, `jacprod`, `theta`, `theta2`, `theta3`, `theta4`, `tripleprod`, `quinprod`, `winquist` |
| Utilities | `sift`, `qdegree`, `lqdegree`, `lqdegree0`, `checkmult`, `checkprod`, `packageversion`, `changes` |
| Product conversion | `prodmake`, `etamake`, `qetamake`, `jacprodmake`, `jac2prod`, `jac2series`, `mprodmake`, `qfactor`, `zqfactor`, `qs2jaccombo`, `findprod` |
| Relations (exact) | `findhom`, `findhomcombo`, `findnonhom`, `findnonhomcombo`, `findlincombo`, `findmaxind`, `findpoly`, `findcong` |
| Relations (mod p) | `findhommodp`, `findhomcombomodp`, `findlincombomodp` |

Output types: `QSeries`, `QProduct`, `EtaProduct`, `EProduct`, `JacProduct`, `PochProduct`,
`MProduct`, `QFactorResult`, `ZQProduct`.

### Differences from the Maple package

- Relations are returned as Sage polynomials in `X1..Xk` (or `X, Y` for `findpoly`) instead of
  Maple's global `X[i]`; the `SL` name lists of `findlincombo*` are accepted but not used.
- `findcong` returns a set of `(B, A, M)` tuples.
- `zqfactor` returns a `ZQProduct` of factors `(1 - a z^i q^j)^e`. Like Maple's version it is
  best-effort: when it cannot find such a product it warns and returns `None`.

## Tests

```bash
sage -python -m pytest -q
```

Expected values in the tests come from Garvan's documentation and tutorial, or from stated
mathematical identities — never from this package's own output.
