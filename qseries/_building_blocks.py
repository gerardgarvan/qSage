# qseries/_building_blocks.py
#
# Licensing note:
# This file is a clean reimplementation derived solely from the documentation of
# Frank Garvan's Maple qseries package v1.3 (https://qseries.org/fgarvan/qmaple/qseries/)
# and the accompanying tutorial (qseriesdoc.pdf). No Maple source code was consulted
# or translated. All mathematical algorithms are derived from the documented function
# specifications and examples. The qseries package is copyright Frank Garvan; this
# Python reimplementation is an independent work for research use in SageMath environments.

from qseries._series import QSeries


def aqprod(a, q, n):
    """Finite q-Pochhammer symbol (a;q)_n = prod_{i=0}^{n-1}(1 - a*q^i).

    Returns exact polynomial (T=Infinity). n=0 returns 1.
    Negative n not supported in v1.0.
    Oracle: Garvan aqprod doc page.
    """
    from sage.all import Infinity
    if n < 0:
        raise NotImplementedError("aqprod: negative n not yet supported")
    from sage.all import parent
    result = parent(q).one()
    for i in range(n):
        result = result * (1 - a * q**i)
    return QSeries(result, T=Infinity)


def qbin(q, m, n):
    """Gaussian binomial (q-binomial coefficient). Returns 0 if not 0<=m<=n.

    Maple: qbin(q, m, n); wraps sage.all.q_binomial(n, m, q).
    Returns exact polynomial (T=Infinity).
    Oracle: Garvan qbin doc page.
    """
    from sage.all import q_binomial, Infinity
    if not (0 <= m <= n):
        return QSeries(0 * q, T=Infinity)
    raw = q_binomial(n, m, q)
    return QSeries(raw, T=Infinity)


def etaq(q, k, T):
    """Eta product prod_{n>=1}(1 - q^{kn}) to O(q^T). No q^{1/24} factor.

    Direct product on caller's q — does NOT use qexp_eta (sage.modular.etaproducts, banned).
    Oracle: Garvan etaq doc page.
    """
    from sage.all import parent as _parent
    # Start from 1 + O(q^T) so every partial product is truncated at O(q^T);
    # multiplying exact polynomials and truncating only at the end is very slow for large T.
    result = _parent(q).one().add_bigoh(T)
    for n in range(1, T // k + 1):
        result = result * (1 - q**(k * n))
    # Truncate at O(q^T): add_bigoh if result supports it, else wrap in series
    try:
        result = result.add_bigoh(T)
    except AttributeError:
        # result is exact 1 (empty product); coerce to series ring and truncate
        from sage.all import parent
        P = parent(q)
        result = P(result).add_bigoh(T)
    return QSeries(result, T=T)


def jacprod(a, b, q, T):
    """Jacobi product (q^a;q^b)_inf * (q^{b-a};q^b)_inf to O(q^T).

    a, b are positive integers with a < b.
    Oracle: Garvan jacprod doc page.
    """
    result = 1
    # Factor 1: (q^a; q^b)_inf -- product (1 - q^{a + b*i}) for i=0,1,...
    i = 0
    while a + b * i < T:
        result = result * (1 - q**(a + b * i))
        i += 1
    # Factor 2: (q^{b-a}; q^b)_inf -- product (1 - q^{(b-a) + b*j}) for j=0,1,...
    j = 0
    while (b - a) + b * j < T:
        result = result * (1 - q**((b - a) + b * j))
        j += 1
    try:
        result = result.add_bigoh(T)
    except AttributeError:
        from sage.all import parent
        result = parent(q)(result).add_bigoh(T)
    return QSeries(result, T=T)


def theta(z, q, T):
    """Jacobi theta function sum_{i=-T}^{T} z^i q^{i^2}. Exact Laurent polynomial.

    Computes on caller's z and q. Sage coercion picks the parent ring automatically.
    Works for scalar z (e.g. z=-1) and ring-variable z.
    Oracle: Garvan theta doc page; tutorial section 2.2.2.
    """
    from sage.all import Infinity, LaurentSeriesRing
    from sage.rings.polynomial.laurent_polynomial_ring import LaurentPolynomialRing_generic
    if hasattr(z, 'parent') and isinstance(z.parent(), LaurentPolynomialRing_generic):
        q = LaurentSeriesRing(z.parent(), 'q')(q)
    result = sum(z**i * q**(i * i) for i in range(-T, T + 1))
    return QSeries(result, T=Infinity)


def _theta2_shift(q):
    """Rational prefactor exponent for theta2 at q = g^k (g the series generator): k/4.

    theta2(q^k) = sum q^(k(n+1/2)^2) = q^(k/4) * sum q^(k(n^2+n)).
    Falls back to 1/4 with a warning if q is not a pure power of the generator.
    """
    from sage.all import QQ
    try:
        v = q.valuation()
        if v > 0 and q == q.parent().gen() ** v:
            return QQ(v) / 4
    except (AttributeError, TypeError, ValueError):
        pass
    import warnings
    warnings.warn("theta2: argument is not a power of the series generator; using q^(1/4) prefactor")
    return QQ(1) / 4


def theta2(q, T):
    """Jacobi theta2 = sum_{n=-T}^{T} q^{(n+1/2)^2}, stored as q^{1/4} * (integer-power poly).

    T is the index bound (sum i=-T..T). Returns exact Laurent polynomial (T=Infinity).
    QSeries.r = QQ(1, 4). Coefficients: 2 at each exponent n^2+n.
    Oracle: Garvan theta2 doc page; Phase 2 RESEARCH.md Pattern 4.
    """
    from sage.all import Infinity, QQ
    # Integer exponent part: (n+1/2)^2 = n^2 + n + 1/4, factoring out q^{1/4}
    result = sum(q**(i * i + i) for i in range(-T, T + 1))
    return QSeries(result, T=Infinity, r=_theta2_shift(q))


def theta3(q, T):
    """Jacobi theta3 = sum_{n: |n|<=isqrt(T)+1} q^{n^2}. Exact Laurent polynomial.

    Summation bound: include all n with |n| <= isqrt(T)+1.
    Coefficient of q^{n^2} is 2 for n!=0, 1 for n=0, 0 for non-squares.
    Oracle: Garvan theta3 doc page: theta3(q,50) up to 2q^64; theta3(q,100) up to 2q^121.
    """
    from sage.all import Infinity, isqrt
    bound = isqrt(T) + 1
    result = sum(q**(n * n) for n in range(-bound, bound + 1))
    return QSeries(result, T=Infinity)


def theta4(q, T):
    """Jacobi theta4 = sum_{n: |n|<=isqrt(T)+1} (-1)^n q^{n^2}. Exact Laurent polynomial.

    Same summation bound as theta3: include all n with |n| <= isqrt(T)+1.
    Coefficient of q^{k^2} is 2*(-1)^k for k!=0, 1 for k=0.
    Oracle: Garvan theta4 doc page: theta4(q,50) up to 2q^64.
    """
    from sage.all import Infinity, isqrt
    bound = isqrt(T) + 1
    result = sum((-1)**(n % 2) * q**(n * n) for n in range(-bound, bound + 1))
    return QSeries(result, T=Infinity)


def tripleprod(z, q, T):
    """Jacobi triple product: sum_{n=-N}^{N} (-1)^n z^n q^{n(n-1)/2}, exact.

    T is a summation index bound (not q-order). Returns exact Laurent polynomial.
    Handles bivariate z (LaurentPolynomialRing generator) via internal ring coercion.
    Oracle: tripleprod(q, q**3, 30) gives Euler pentagonal series (tutorial sec 6.1).
    Garvan doc page: https://qseries.org/fgarvan/qmaple/qseries/functions/tripleprod.html
    """
    from math import isqrt
    from sage.all import Infinity, LaurentSeriesRing
    from sage.rings.polynomial.laurent_polynomial_ring import LaurentPolynomialRing_generic
    # Bivariate coercion: when z is a LaurentPolynomialRing variable, q must be coerced
    # into LaurentSeriesRing(Rz, 'q') so that z**n * q**exp is well-typed.
    if hasattr(z, 'parent') and isinstance(z.parent(), LaurentPolynomialRing_generic):
        Rz = z.parent()
        Sq = LaurentSeriesRing(Rz, 'q')
        q = Sq(q)
    N = isqrt(2 * T) + 2
    result = sum((-1)**(n % 2) * z**n * q**(n * (n - 1) // 2) for n in range(-N, N + 1))
    return QSeries(result, T=Infinity)


def quinprod(z, q, T):
    """Watson quintuple product identity, series side or identity strings.

    quinprod(z, q, T) -- 3 arguments (doc-page 4-arg header is a typo; all examples use 3).

    T='prodid': return string showing the product form of the identity.
    T='seriesid': return string showing the series form of the identity.
    T=integer: return series sum_m [(-z)^{-3m} - (-z)^{3m+1}] q^{m(3m+1)/2}, exact.

    Correct identity (tutorial (6.9)):
      product: (-z;q)_inf * (-q/z;q)_inf * (z^2*q;q^2)_inf * (q/z^2;q^2)_inf * (q;q)_inf
      series:  sum_m [(-z)^{-3m} - (-z)^{3m+1}] q^{m(3m+1)/2}

    Oracle: Garvan quinprod doc page.
    """
    from sage.all import Infinity
    if isinstance(T, str):
        if T == 'prodid':
            return (
                "quinprod identity (product form): "
                "(-z;q)_inf * (-q/z;q)_inf * (z^2*q;q^2)_inf * (q/z^2;q^2)_inf * (q;q)_inf"
                " = sum_m [(-z)^{-3m} - (-z)^{3m+1}] * q^{m*(3m+1)/2}"
            )
        elif T == 'seriesid':
            return (
                "quinprod identity (series form): "
                "sum_{m=-inf}^{inf} [(-z)^{-3m} - (-z)^{3m+1}] * q^{m*(3m+1)/2}"
                " = (-z;q)_inf * (-q/z;q)_inf * (z^2*q;q^2)_inf * (q/z^2;q^2)_inf * (q;q)_inf"
            )
        else:
            raise ValueError(f"quinprod: T must be integer, 'prodid', or 'seriesid'; got {T!r}")
    # Integer T: series side, exact, computed on caller's z and q
    # Bivariate coercion: when z is a LaurentPolynomialRing variable, q must be coerced
    # into LaurentSeriesRing(Rz, 'q') so that (-z)**exp * q**pow is well-typed.
    from sage.all import LaurentSeriesRing
    from sage.rings.polynomial.laurent_polynomial_ring import LaurentPolynomialRing_generic
    if hasattr(z, 'parent') and isinstance(z.parent(), LaurentPolynomialRing_generic):
        Rz = z.parent()
        Sq = LaurentSeriesRing(Rz, 'q')
        q = Sq(q)
    terms = []
    for m in range(-T - 1, T + 2):
        exp = m * (3 * m + 1) // 2
        if exp < 0:
            continue
        q_pow = q**exp
        term = (-z)**(-3 * m) * q_pow - (-z)**(3 * m + 1) * q_pow
        terms.append(term)
    result = sum(terms) if terms else q * 0
    return QSeries(result, T=Infinity)


def _pochhammer_trunc(x, q, T):
    """Compute prod_{i=0}^{...}(1 - x * q^i) truncated so that x*q^i contributes up to order T.

    Returns the product as a Sage ring element (computed on caller's x and q).
    """
    result = 1
    # Build product; stop when the leading power of q^i exceeds T
    for i in range(T + 1):
        result = result * (1 - x * q**i)
    return result


def winquist(a, b, q, T):
    """Winquist's identity: 8-factor product identity, truncated to O(q^T).

    winquist(a, b, q, T) -- Garvan doc page:
      https://qseries.org/fgarvan/qmaple/qseries/functions/winquist.html

    The 8-factor product, matching Maple qseries 1.3 (checked against Maple 2026 output):
      (a;q)_inf * (q/a;q)_inf * (b;q)_inf * (q/b;q)_inf
      * (ab;q)_inf * (q/(ab);q)_inf * (a/b;q)_inf * (bq/a;q)_inf
      * (q;q)_inf^2
    Its q^0 coefficient is (1-a)(1-b)(1-ab)(1-a/b), so it vanishes at a=b=1; the doc-page
    identity divides by that factor first, after which a=b=1 gives (q;q)_inf^10.

    Oracle: Garvan winquist doc page.
    """
    from sage.all import Infinity

    def poch(x):
        """Truncated (x;q)_T = prod_{i=0}^{T-1}(1 - x*q^i)."""
        result = 1
        for i in range(T):
            result = result * (1 - x * q**i)
        return result

    def poch_inv(x):
        """Truncated (q/x;q)_T = prod_{i=0}^{T-1}(1 - q^{i+1}/x)."""
        result = 1
        for i in range(T):
            result = result * (1 - q**(i + 1) / x)
        return result

    # 8 Pochhammer factors + (q;q)^2
    f1 = poch(a)           # (a; q)_inf
    f2 = poch_inv(a)       # (q/a; q)_inf ~ prod(1 - q^{i+1}/a)
    f3 = poch(b)           # (b; q)_inf
    f4 = poch_inv(b)       # (q/b; q)_inf
    f5 = poch(a * b)       # (ab; q)_inf
    f6 = poch_inv(a * b)   # (q/(ab); q)_inf
    f7 = poch(a / b)       # (a/b; q)_inf
    f8 = poch_inv(a / b)   # (bq/a; q)_inf = poch_inv(a/b) since q/(a/b) = bq/a

    # (q;q)^2 = prod_{i=1}^{T}(1 - q^i)^2
    qq_factor = 1
    for i in range(1, T + 1):
        qq_factor = qq_factor * (1 - q**i)
    qq_sq = qq_factor * qq_factor

    result = f1 * f2 * f3 * f4 * f5 * f6 * f7 * f8 * qq_sq
    # Truncate at O(q^T)
    try:
        result = result.add_bigoh(T)
    except AttributeError:
        from sage.all import parent
        result = parent(q)(result).add_bigoh(T)
    return QSeries(result, T=T)
