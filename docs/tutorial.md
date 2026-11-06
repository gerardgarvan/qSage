# qseries-sage tutorial

Worked examples following F. G. Garvan, *A q-product tutorial for a q-series MAPLE package* (Seminaire Lotharingien de Combinatoire 42, 1999; arXiv:math/9812092), run with qseries-sage. Outputs are produced by `docs/make_tutorial.py`; where the tutorial or a Garvan doc page gives Maple's answer it is shown as **Maple** for comparison.

## Setup

Every example below starts from a Laurent series ring in `q` over the rationals. Series are `QSeries` objects: a Sage series plus its truncation order `T` and a rational shift `r` (the series is `q^r * series`). `head(f)` prints just the first terms.

```python
from sage.all import QQ, LaurentSeriesRing, LaurentPolynomialRing, PolynomialRing, kronecker, sigma
from qseries import *

R = LaurentSeriesRing(QQ, 'q', default_prec=1010)
q = R.gen()

def head(f, n=15):
    """First n terms of a QSeries (for display); the q^r prefactor is shown when r != 0."""
    s = f.series
    s = s.add_bigoh(s.valuation() + n) if s != 0 else s
    return "q^(%s) * (%s)" % (f.r, s) if f.r else s
```

## 1. Basic functions

*Source: Tutorial section 2.*

Finite q-products: `aqprod(a, q, n)` = (a;q)_n and the Gaussian polynomial `qbin(q, m, n)`.

```python
aqprod(q, q, 5)
```

Output:

```
1 - q - q^2 + q^5 + q^6 + q^7 - q^8 - q^9 - q^10 + q^13 + q^14 - q^15
```

```python
qbin(q, 2, 4)
```

Output:

```
1 + q + 2*q^2 + q^3 + q^4 + O(q^1010)
```

`etaq(q, k, T)` is the eta product prod_{n>=1} (1 - q^{kn}) to O(q^T), without the q^(k/24) factor.

```python
head(etaq(q, 1, 100), 20)
```

Output:

```
1 - q - q^2 + q^5 + q^7 - q^12 - q^15 + O(q^20)
```

**Maple:** Euler's pentagonal number theorem: 1 - q - q^2 + q^5 + q^7 - q^12 - q^15 + ...

Theta functions. `theta2` carries the `q^(1/4)` prefactor in its shift `r`.

```python
head(theta3(q, 100)), head(theta4(q, 100)), head(theta2(q, 100))
```

Output:

```
(1 + 2*q + 2*q^4 + 2*q^9 + O(q^15), 1 - 2*q + 2*q^4 - 2*q^9 + O(q^15), 'q^(1/4) * (2 + 2*q^2 + 2*q^6 + 2*q^12 + O(q^15))')
```

Jacobi's triple product: `tripleprod(q, q^3, T)` is Euler's pentagonal series again (tutorial section 6.1).

```python
(tripleprod(q, q**3, 10).series - etaq(q, 1, 100).series).add_bigoh(100) == 0
```

Output:

```
False
```

**Maple:** true

## 2. prodmake: Andrews' algorithm

*Source: Tutorial section 3.1.*

The left side of the first Rogers-Ramanujan identity, summed to n = 8 (accurate to well past q^40):

```python
x = sum(q**(n*n) / aqprod(q, q, n).series for n in range(9))
x = QSeries(x.add_bigoh(50), T=50)
head(x, 20)
```

Output:

```
1 + q + q^2 + q^3 + 2*q^4 + 2*q^5 + 3*q^6 + 3*q^7 + 4*q^8 + 5*q^9 + 6*q^10 + 7*q^11 + 9*q^12 + 10*q^13 + 12*q^14 + 14*q^15 + 17*q^16 + 19*q^17 + 23*q^18 + 26*q^19 + O(q^20)
```

`prodmake` recovers the infinite product. The exponents are -1 exactly at n = 1, 4 (mod 5): the Rogers-Ramanujan identity.

```python
p = prodmake(x, q, 40)
sorted(n for n, e in p.exponents.items() if e != 0) == [n for n in range(1, 40) if n % 5 in (1, 4)]
```

Output:

```
True
```

**Maple:** 1 / ((1-q)(1-q^4)(1-q^6)(1-q^9)...), i.e. exponents at n = +-1 (mod 5)

```python
p
```

Output:

```
(1-q)^-1 * (1-q^4)^-1 * (1-q^6)^-1 * (1-q^9)^-1 * (1-q^11)^-1 * (1-q^14)^-1 * (1-q^16)^-1 * (1-q^19)^-1 * (1-q^21)^-1 * (1-q^24)^-1 * (1-q^26)^-1 * (1-q^29)^-1 * (1-q^31)^-1 * (1-q^34)^-1 * (1-q^36)^-1 * (1-q^39)^-1
```

The same series as a theta-function product (tutorial section 3.4):

```python
jacprodmake(x, q, 40)
```

Output:

```
JAC(1,5,infinity)^-1
```

**Maple:** JAC(0,5,infinity) / JAC(1,5,infinity)

## 3. Eta-products

*Source: Tutorial section 3.2; etamake and qetamake doc pages.*

```python
etamake(theta3(q, 100), q, 100)
```

Output:

```
eta(tau)^-2 * eta(2*tau)^5 * eta(4*tau)^-2
```

**Maple:** eta(2 tau)^5 / (eta(tau)^2 eta(4 tau)^2)

```python
etamake(theta4(q, 100), q, 100)
```

Output:

```
eta(tau)^2 * eta(2*tau)^-1
```

**Maple:** eta(tau)^2 / eta(2 tau)

```python
etamake(theta2(q, 100), q, 100)
```

Output:

```
2 * eta(2*tau)^-1 * eta(4*tau)^2
```

**Maple:** 2 eta(4 tau)^2 / eta(2 tau)

The triangular-number series sum q^(n(n+1)/2) in `_E(q^m) = (q^m;q^m)_inf` form:

```python
qetamake(etaq(q, 2, 30)**2 / etaq(q, 1, 30), q, 30)
```

Output:

```
_E(q)^-1 * _E(q^2)^2
```

**Maple:** _E(q^2)^2 / _E(q)

## 4. Finite products and other product forms

*Source: Tutorial section 3.3; qfactor, mprodmake doc pages.*

`qfactor` factors a rational function into (1 - q^i) terms. Pass numerator and denominator separately so Sage does not cancel them first.

```python
P = PolynomialRing(QQ, 'q'); t = P.gen()
num = t**6 * (1 - t**9) * (1 - t**10) * (1 - t**11) * (1 - t**16)
den = (1 - t) * (1 - t**2) * (1 - t**3) * (1 - t**4)
qfactor((num, den), 20)
```

Output:

```
QFactorResult(numerator=(1-q^9) * (1-q^10) * (1-q^11) * (1-q^16), denominator=(1-q) * (1-q^2) * (1-q^3) * (1-q^4), r=6)
```

**Maple:** q^6 (1-q^9)(1-q^10)(1-q^11)(1-q^16) / ((1-q)(1-q^2)(1-q^3)(1-q^4))

`mprodmake` writes a series as a product (1 + q^n1)(1 + q^n2)...:

```python
EP = etaq(q, 2, 18)**2 * etaq(q, 4, 18)**(-1) * etaq(q, 1, 18)**(-1)
mprodmake(EP, q, 17)
```

Output:

```
(1+q) * (1+q^3) * (1+q^5) * (1+q^7) * (1+q^9) * (1+q^11) * (1+q^13) * (1+q^15) * (1+q^17)
```

**Maple:** (1+q)(1+q^3)(1+q^5)...(1+q^17)

`zqfactor` does the same for series in two variables z and q (zqfactor doc page). The example is Jacobi's triple product in disguise:

```python
Lz = LaurentPolynomialRing(QQ, 'z'); z = Lz.gen()
Rz = LaurentSeriesRing(Lz, 'q'); qz = Rz.gen()
g = tripleprod(-z**2 * qz**3, qz**4, 20) - tripleprod(-z**2 * qz, qz**4, 20) / z
zqfactor(g, z, qz, 10)
```

Output:

```
(1 - 1/z) * (1 - z*q) * (1 - q) * (1 - q/z) * (1 - z*q^2) * (1 - q^2) * (1 - q^2/z) * (1 - z*q^3) * (1 - q^3)
```

**Maple:** (1-1/z)(1-zq)(1-q)(1-q/z)(1-zq^2)(1-q^2)(1-q^2/z)(1-zq^3)(1-q^3)

## 5. Relations between q-series

*Source: Tutorial section 4.*

`findhom` finds homogeneous polynomial relations of a given degree (section 4.1). There are no linear relations among these four theta functions, and two quadratic ones:

```python
L = [theta3(q, 100), theta4(q, 100), theta3(q**2, 100), theta4(q**2, 100)]
findhom(L, q, 1, 0), findhom(L, q, 2, 0)
```

Output:

```
# of terms , 25
# of terms , 31
(set(), {X1*X2 - X4^2, X1^2 + X2^2 - 2*X3^2})
```

**Maple:** {} and {X1^2 + X2^2 - 2 X3^2, X1 X2 - X4^2}

`findhomcombo` writes one series as a polynomial in others (section 4.2): the Eisenstein series U_{5,6} in terms of two eta-quotients.

```python
def UE(q, k, p, trunk):
    x = sum(kronecker(m, p) * n**(k - 1) * q**(m * n)
            for m in range(1, trunk + 1) for n in range(1, trunk // m + 1))
    return QSeries(q.parent()(x).add_bigoh(trunk + 1), T=trunk + 1)
B1 = etaq(q, 1, 50)**5 / etaq(q, 5, 50)
B2 = QSeries(q * etaq(q, 5, 50).series**5 / etaq(q, 1, 50).series, 50)
findhomcombo(UE(q, 6, 5, 50), [B1, B2], q, 3, 0)
```

Output:

```
# of terms , 25
matrix is , 5, x, 25
{X1^2*X2 + 40*X1*X2^2 + 335*X2^3}
```

**Maple:** X1^2 X2 + 40 X1 X2^2 + 335 X2^3

`findnonhomcombo` allows all degrees up to n (section 4.4): Watson's modular equation for 7, with xi = eta(49 tau)/eta(tau) and T = (eta(7 tau)/eta(tau))^4. (T^2 itself is one of the monomials, so the trivial answer X1^2 is returned as well.)

```python
E1 = etaq(q, 1, 100).series
xi = QSeries(q**2 * etaq(q, 49, 100).series / E1, 100)
T7 = QSeries(q * etaq(q, 7, 100).series**4 / E1**4, 100)
findnonhomcombo(T7**2, [T7, xi], q, 7, -15)
```

Output:

```
# of terms , 42
matrix is , 37, x, 42
{343*X2^7 + 343*X2^6 + 147*X2^5 + 49*X1*X2^3 + 49*X2^4 + 35*X1*X2^2 + 21*X2^3 + 7*X1*X2 + 7*X2^2 + X2, X1^2}
```

**Maple:** (35 xi^2 + 49 xi^3 + 7 xi) T + 343 xi^7 + 343 xi^6 + 147 xi^5 + 49 xi^4 + 21 xi^3 + 7 xi^2 + xi

`findpoly` finds a polynomial relation between two series (section 4.5), here the Borweins' cubic theta functions:

```python
x = theta2(q, 100)**2 / theta2(q**3, 40)**2 + theta3(q, 100)**2 / theta3(q**3, 40)**2
a = theta3(q, 100) * theta3(q**3, 40) + theta2(q, 100) * theta2(q**3, 40)
c = QSeries(3 * etaq(q, 3, 100).series**3 / etaq(q, 1, 100).series, 100, r=QQ('1/3'))
y = c**3 / a**3
rels = findpoly(x, y, q, 3, 1, 60)
X, Y = next(iter(rels)).parent().gens()
rels, [rel / rel.lc() == (X + 6)**3 * Y - 27 * (X + 2)**2 for rel in rels]
```

Output:

```
# of terms , 29
CHECK: relation(s) verified to O(q^60)
({-1/108*X^3*Y - 1/6*X^2*Y + 1/4*X^2 - X*Y + X - 2*Y + 1}, [True])
```

**Maple:** (X + 6)^3 Y - 27 (X + 2)^2

## 6. Sifting and dissections

*Source: Tutorial section 6.2; sift doc page.*

`sift` keeps the terms whose exponent is in a fixed class mod n: the 5-dissection component E0 of Euler's product.

```python
E0 = sift(etaq(q, 1, 500), q, 5, 0, 499)
head(E0, 12)
```

Output:

```
1 + q - q^3 - q^7 - q^8 + O(q^12)
```

```python
jacprodmake(E0, q, 50)
```

Output:

```
JAC(1,5,infinity)^-1 * JAC(2,5,infinity)
```

## 7. Congruences

*Source: Tutorial section 7; findcong doc page.*

`findcong` searches for congruences a(An + B) = 0 (mod M) in the coefficients. For the partition function it finds Ramanujan's congruences (returned as (B, A, M)):

```python
Pn = QSeries(etaq(q, 1, 1001).series.__invert__(), 1001)
sorted(findcong(Pn, 1000))
```

Output:

```
[(4, 5, 5), (5, 7, 7), (6, 11, 11), (24, 25, 25)]
```

**Maple:** [4, 5, 5], [5, 7, 7], [6, 11, 11] and [24, 25, 25]

`checkmult` tests multiplicativity: Ramanujan's tau function, from Delta = q (q;q)_inf^24.

```python
checkmult(q * etaq(q, 1, 60)**24, 59)
```

Output:

```
True
```

**Maple:** 1 (multiplicative)

## 8. Relations mod p

*Source: findlincombomodp doc page.*

The mod-p variants work over GF(p). The doc-page example writes a sifted series mod 13 in terms of six eta/Eisenstein products:

```python
E4 = QSeries(R(1 + 240 * sum(sigma(n, 3) * q**n for n in range(1, 300))).add_bigoh(300), 300)
E6 = QSeries(R(1 - 504 * sum(sigma(n, 5) * q**n for n in range(1, 300))).add_bigoh(300), 300)
ETA1 = etaq(q, 1, 300)
F1 = sift(E4**16 * E6 * QSeries(ETA1.series.__invert__(), 300), q, 13, 6, 299)
BB13 = [ETA1**11 * E6 * E4**(3 * j + 1) for j in range(6)]
findlincombomodp(F1, BB13, None, 13, q, -8)
```

Output:

```
nx = , 6
# of terms , 19
matrix is , 7, x, 19
{-6*X1}
```

**Maple:** -6 _ETA1^11 _E6 _E4   (i.e. -6 X1 mod 13), with 'nx = , 6' and '# of terms , 19'

E4 = 1 (mod 5) because 240 is divisible by 5, so `findhommodp` finds a relation that does not exist over the rationals:

```python
one = QSeries(R(1).add_bigoh(300), 300)
findhommodp([E4, E6, one], 5, q, 1, 0), findhom([E4, E6, one], q, 1, 0)
```

Output:

```
# of terms , 24
# of terms , 24
({X1 - X3}, set())
```
