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
    result = 1
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
    result = 1
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
    from sage.all import Infinity
    result = sum(z**i * q**(i * i) for i in range(-T, T + 1))
    return QSeries(result, T=Infinity)


def theta2(q, T):
    """Jacobi theta2 = sum_{n=-T}^{T} q^{(n+1/2)^2}, stored as q^{1/4} * (integer-power poly).

    T is the index bound (sum i=-T..T). Returns exact Laurent polynomial (T=Infinity).
    QSeries.r = QQ(1, 4). Coefficients: 2 at each exponent n^2+n.
    Oracle: Garvan theta2 doc page; Phase 2 RESEARCH.md Pattern 4.
    """
    from sage.all import Infinity, QQ
    # Integer exponent part: (n+1/2)^2 = n^2 + n + 1/4, factoring out q^{1/4}
    result = sum(q**(i * i + i) for i in range(-T, T + 1))
    return QSeries(result, T=Infinity, r=QQ(1, 4))


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
    result = sum((-1)**n * q**(n * n) for n in range(-bound, bound + 1))
    return QSeries(result, T=Infinity)


def tripleprod(z, q, T):
    """Jacobi triple product sum_{n=-inf}^{inf} (-1)^n z^n q^{n(n-1)/2} to O(q^T).

    Stub: not yet implemented.
    Oracle: Garvan tripleprod doc page.
    """
    raise NotImplementedError("tripleprod: not yet implemented")


def quinprod(z, q, T):
    """Watson quintuple product to O(q^T) or as identity string.

    3-arg signature: quinprod(z, q, T). The 4-arg header on the doc page is a typo;
    all examples use the 3-arg form.
    Stub: not yet implemented.
    Oracle: Garvan quinprod doc page.
    """
    raise NotImplementedError("quinprod: not yet implemented")


def winquist(a, b, q, T):
    """Winquist's identity 8-factor product to O(q^T).

    Stub: not yet implemented.
    Oracle: Garvan winquist doc page.
    """
    raise NotImplementedError("winquist: not yet implemented")
