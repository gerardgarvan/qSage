# qseries/_conversion.py
#
# Licensing note:
# This file is a clean reimplementation derived solely from the documentation of
# Frank Garvan's Maple qseries package v1.3 (https://qseries.org/fgarvan/qmaple/qseries/)
# and the accompanying tutorial (qseriesdoc.pdf). No Maple source code was consulted
# or translated. All mathematical algorithms are derived from the documented function
# specifications and examples. The qseries package is copyright Frank Garvan; this
# Python reimplementation is an independent work for research use in SageMath environments.

"""Product-conversion functions for qseries-sage (Phase 4).

Implements CONV-02 through CONV-11: etamake, qetamake, jacprodmake, jac2prod,
jac2series, mprodmake, qfactor, zqfactor, qs2jaccombo, findprod.

All 10 names are exported so that import lines in Plans 04-02 and 04-03 never
raise ImportError. Functions not yet implemented raise NotImplementedError.
"""

from sage.all import QQ
from collections import defaultdict

from math import isqrt

from qseries._series import QSeries
from qseries._symbolic import EtaProduct, EProduct, QProduct, JacProduct, PochProduct
from qseries._building_blocks import etaq
from qseries._prodmake import prodmake


# ---------------------------------------------------------------------------
# CONV-02: etamake
# ---------------------------------------------------------------------------

def etamake(f, q, T):
    """Greedy eta-product identification (CONV-02).

    Given a QSeries f, returns an EtaProduct c * q^r * prod_k eta(k*tau)^{e_k}
    such that to_series(T) matches f to O(q^T).

    Algorithm (D-04):
      1. Strip fractional q-shift r_input and leading constant c.
      2. Greedy loop: find lowest non-unit coefficient c_k at q^k;
         multiply residual by etaq(q,k,T)^(c_k) to cancel; record eta(k*tau)^(-c_k).
      3. EtaProduct.r = r_input - sum(k * e_k / 24) over recorded factors.

    Oracle (D-05):
      etamake(theta3(q,100), q, 100) -> eta(2tau)^5 / (eta(4tau)^2 * eta(tau)^2)
      etamake(theta4(q,100), q, 100) -> eta(tau)^2 / eta(2tau)
      etamake(theta2(q,100), q, 100) -> 2 * eta(4tau)^2 / eta(2tau)  (r=0)
    """
    r_input = QQ(f.r)

    # Step 1: strip leading constant so residual has constant term 1
    c = QQ(f.series[0])
    if c == 0:
        raise ValueError("etamake: leading coefficient is zero; cannot normalize")

    R = f.series.parent()
    residual_series = (f.series / c).add_bigoh(T)
    residual = QSeries(residual_series, T=T)  # r=0

    factors = []  # list of (level, exponent) pairs

    # Step 2: greedy cancellation loop
    for _ in range(T - 1):
        # Find lowest k >= 1 where coefficient != 0
        k = None
        for n in range(1, T):
            coeff = QQ(residual.series[n])
            if coeff != 0:
                k = n
                c_k = coeff
                break
        if k is None:
            break  # residual == 1 + O(q^T): done

        c_k_q = QQ(c_k)
        if c_k_q.denominator() != 1:
            raise ValueError(
                f"etamake: non-integer coefficient {c_k} at q^{k}; "
                "series is not an exact eta-product to this precision"
            )
        c_k_int = int(c_k_q)

        # Multiply residual by etaq(q,k,T)^(c_k_int) to cancel +c_k q^k term.
        # etaq = 1 - q^k + ..., so (etaq)^(c_k_int) contributes -c_k_int * q^k,
        # cancelling the positive c_k_int coefficient.
        eta_k = etaq(q, k, T)
        if c_k_int >= 0:
            multiplier = eta_k ** c_k_int
        else:
            # Negative exponent: multiply by etaq^(c_k_int) = 1/(etaq^|c_k_int|)
            # Use series inversion
            abs_exp = -c_k_int
            inv_series = (eta_k.series ** abs_exp).__invert__().add_bigoh(T)
            multiplier = QSeries(inv_series, T=T)

        residual = residual * multiplier
        # Record eta(k*tau)^(-c_k_int) in the EtaProduct
        factors.append((k, -c_k_int))

    # Step 3: compute EtaProduct.r
    # eta(k*tau) = q^(k/24) * prod_{n>=1}(1-q^{kn}), so accumulated q-shift
    # from the recorded factors (k, e_k) is sum(k * e_k / 24).
    eta_shift = sum(QQ(k) * QQ(e) / QQ(24) for k, e in factors)
    r_out = r_input - eta_shift

    # Merge duplicate levels
    merged = defaultdict(lambda: QQ(0))
    for k, e in factors:
        merged[k] += QQ(e)
    factors_merged = [(k, int(merged[k])) for k in sorted(merged) if merged[k] != 0]

    return EtaProduct(constant=c, r=r_out, factors=factors_merged)


# ---------------------------------------------------------------------------
# CONV-03: qetamake
# ---------------------------------------------------------------------------

def qetamake(f, q, T):
    """Greedy _E-product identification (CONV-03).

    Returns an EProduct with exponents dict {k: e_k} such that
    to_series(T) matches f to O(q^T).

    Requires f.r == 0 (no fractional q-shift). Same greedy algorithm as etamake
    but factors are _E(q^k) = prod_{n>=1}(1-q^{kn}) (no q^(k/24) shift tracked).

    Oracle: qetamake(triangular_series, q, 30) -> EProduct({1:-1, 2:2})
    """
    if QQ(f.r) != 0:
        raise ValueError(
            f"qetamake requires r=0 (no fractional q-shift), got r={f.r}"
        )

    c = QQ(f.series[0])
    if c == 0:
        raise ValueError("qetamake: leading coefficient is zero")
    if c != 1:
        # qetamake strips constant silently (consistent with etamake)
        residual_series = (f.series / c).add_bigoh(T)
    else:
        residual_series = f.series.add_bigoh(T)
    residual = QSeries(residual_series, T=T)

    factors = []

    for _ in range(T - 1):
        k = None
        for n in range(1, T):
            coeff = QQ(residual.series[n])
            if coeff != 0:
                k = n
                c_k = coeff
                break
        if k is None:
            break

        c_k_q = QQ(c_k)
        if c_k_q.denominator() != 1:
            raise ValueError(
                f"qetamake: non-integer coefficient {c_k} at q^{k}"
            )
        c_k_int = int(c_k_q)

        eta_k = etaq(q, k, T)
        if c_k_int >= 0:
            multiplier = eta_k ** c_k_int
        else:
            abs_exp = -c_k_int
            inv_series = (eta_k.series ** abs_exp).__invert__().add_bigoh(T)
            multiplier = QSeries(inv_series, T=T)

        residual = residual * multiplier
        factors.append((k, -c_k_int))

    merged = defaultdict(lambda: QQ(0))
    for k, e in factors:
        merged[k] += QQ(e)
    exponents = {k: int(merged[k]) for k in sorted(merged) if merged[k] != 0}
    return EProduct(exponents=exponents)


# ---------------------------------------------------------------------------
# CONV-04: jacprodmake (Plan 04-02)
# ---------------------------------------------------------------------------

def jacprodmake(f, q, T, base=None):
    """Jacobi product identification (CONV-04, D-08).

    Given a QSeries f, identifies it as a JacProduct by detecting the period of
    the exponent sequence returned by prodmake.

    Oracle: jacprodmake(tripleprod(q,q^5,10), q, 10) -> JAC(1,5,inf)
    Mandatory: jacprodmake(sqrt(JAC(7,14)/JAC(0,14)), q, 40) -> factor (7,14,1/2)
    base: if given, search only divisors of base for the period P.
    """
    from sage.all import QQ as _QQ, divisors as sage_divisors

    r_input = _QQ(f.r)
    if r_input != 0:
        raise ValueError(
            f"jacprodmake: input has fractional q-shift r={r_input}; strip it first"
        )

    # Strip leading constant
    c = _QQ(f.series[0])
    if c == 0:
        raise ValueError("jacprodmake: leading coefficient is zero")
    normalized_series = (f.series / c).add_bigoh(T)
    f_norm = QSeries(normalized_series, T=T)

    # Call prodmake to get exponent dict {n: e_n}
    qprod = prodmake(f_norm, q, T)
    exponents = qprod.exponents  # {n: e_n} nonzero only

    if not exponents:
        return JacProduct(constant=c, r=r_input, factors=[])

    # Find smallest period P
    if base is not None:
        candidates = sorted(sage_divisors(int(base)))
    else:
        max_n = max(exponents.keys())
        candidates = range(1, max_n + 1)

    def _residue(n, P):
        """Residue of n mod P in range [1, P] (so multiples of P map to P, not 0)."""
        r = n % P
        return r if r != 0 else P

    P = None
    for candidate in candidates:
        if all(exponents.get(n, 0) == exponents.get(_residue(n, candidate), 0)
               for n in range(1, T)):
            P = candidate
            break
    if P is None:
        P = max(exponents.keys())

    # Build JacProduct factors from residue classes mod P.
    #
    # JAC(a,P) contributes prodmake exponents e at residues a, P-a, and P(=0 mod P).
    # JAC(0,P) contributes exponent e at residue P only.
    #
    # Algorithm:
    #   1. Get e at residue P.
    #   2. Scan pairs (a, P-a) for a in 1..floor(P/2).
    #      If e_a == e_{P-a} == e_P (and e_P != 0): JAC(a,P)^e_P; mark residue P accounted.
    #      If a == P/2: JAC(P/2,P)^(e_{P/2}/2) — the D-08 mandatory half-exponent case.
    #      Otherwise: record individual residues (non-standard case).
    #   3. If residue P still unaccounted: add JAC(0,P) factor.

    e_period = _QQ(exponents.get(P, 0))   # exponent at the "zero" residue (multiples of P)
    factors = []
    period_accounted = False

    seen = set()
    for a in range(1, P):
        if a in seen:
            continue
        paired = P - a
        seen.add(a)
        seen.add(paired)
        e_a = _QQ(exponents.get(a, 0))
        e_pa = _QQ(exponents.get(paired, 0))

        if a == paired:
            # P even, a == P/2: D-08 mandatory case — half exponent
            if e_a != 0:
                factors.append((a, P, e_a / 2))
        elif e_a != 0 or e_pa != 0:
            if e_a == e_pa == e_period and e_period != 0:
                # Standard JAC(a,P)^e pattern: residues a, P-a, P all equal
                factors.append((a, P, e_a))
                period_accounted = True
            elif e_a == e_pa and e_a != 0:
                # Paired but different from e_period: non-standard
                factors.append((a, P, e_a))
            else:
                # Unequal: record individually
                if e_a != 0:
                    factors.append((a, P, e_a))
                if e_pa != 0:
                    factors.append((paired, P, e_pa))

    # Add JAC(0,P) only if residue-P exponent not yet accounted for
    if not period_accounted and e_period != 0:
        factors.append((0, P, e_period))

    return JacProduct(constant=c, r=r_input, factors=factors)


# ---------------------------------------------------------------------------
# CONV-08: jac2prod (Plan 04-02)
# ---------------------------------------------------------------------------

def jac2prod(jacexpr):
    """Convert JacProduct to PochProduct (CONV-08).

    JAC(a,b,inf) with a!=0 -> (q^a;q^b)_inf * (q^{b-a};q^b)_inf * (q^b;q^b)_inf
    JAC(0,b,inf)            -> (q^b;q^b)_inf only

    Oracle: jac2prod(JAC(1,5,inf)) -> (q;q^5)*(q^4;q^5)*(q^5;q^5)
    Oracle: jac2prod(JAC(0,10,inf)) -> (q^10;q^10)
    """
    factors = []
    for a, b, e in jacexpr.factors:
        e_int = int(QQ(e))
        if a == 0:
            factors.append((b, b, e_int))
        else:
            factors.append((a, b, e_int))
            factors.append((b - a, b, e_int))
            factors.append((b, b, e_int))
    return PochProduct(factors=factors)


# ---------------------------------------------------------------------------
# CONV-09: jac2series (Plan 04-02)
# ---------------------------------------------------------------------------

def jac2series(jacexpr, T):
    """Expand JacProduct to QSeries via theta substitution (CONV-09).

    JAC(a,b,inf) -> sum_{i} (-1)^i * q^{i*(b-2a)/2 + i^2*b/2}

    Oracle: jac2series(JAC(-4,5,inf), 20) = (1 - q - q^4 - q^7 - q^13 - q^18) * q^{-4}
    Reference: Garvan jac2series doc page.
    """
    from sage.all import LaurentSeriesRing, QQ as _QQ

    R = LaurentSeriesRing(_QQ, 'q')
    q_sym = R.gen()

    result_series = R(_QQ(jacexpr.constant)).add_bigoh(T)
    total_r = _QQ(jacexpr.r)

    for a, b, e in jacexpr.factors:
        a_q = _QQ(a)
        b_q = _QQ(b)
        e_q = _QQ(e)

        shift = (b_q - 2 * a_q) / 2   # exponent of q for z = -q^{(b-2a)/2}
        step = b_q / 2                 # exponent step for q^{b/2}

        N = isqrt(int(T)) + 2
        terms = {}
        for i in range(-N, N + 1):
            exp = _QQ(i) * shift + _QQ(i * i) * step
            coeff = (-1) ** i
            terms[exp] = terms.get(exp, _QQ(0)) + _QQ(coeff)

        # Remove zero terms
        terms = {exp: coeff for exp, coeff in terms.items() if coeff != 0}

        if not terms:
            continue

        min_exp = min(terms.keys())

        # Build as integer-indexed series with rational shift min_exp
        s = R(0).add_bigoh(T)
        for exp, coeff in terms.items():
            int_idx = exp - min_exp
            if int_idx.denominator() != 1:
                raise ValueError(
                    f"Non-integer index {int_idx} in jac2series; "
                    "rational shift not reducible to integer"
                )
            idx = int(int_idx)
            if idx < T:
                s = s + R(coeff) * q_sym ** idx
        s = s.add_bigoh(T)

        theta_qs = QSeries(s, T=T, r=min_exp)

        if e_q.denominator() != 1:
            raise ValueError(f"jac2series: non-integer exponent {e_q} not supported")
        e_int = int(e_q)
        if e_int >= 0:
            for _ in range(e_int):
                result_series = (result_series * theta_qs.series).add_bigoh(T)
                total_r += theta_qs.r
        else:
            for _ in range(-e_int):
                result_series = (result_series / theta_qs.series).add_bigoh(T)
                total_r -= theta_qs.r

    return QSeries(result_series, T=T, r=total_r)


# ---------------------------------------------------------------------------
# CONV-05: mprodmake (Plan 04-03)
# ---------------------------------------------------------------------------

def mprodmake(f, q, T):
    """Write f as a product of (1+q^n) factors (CONV-05). Implemented in Plan 04-03."""
    raise NotImplementedError("mprodmake: implemented in Plan 04-03")


# ---------------------------------------------------------------------------
# CONV-06: qfactor (Plan 04-03)
# ---------------------------------------------------------------------------

def qfactor(f, T=None):
    """Factor a polynomial/rational function in q (CONV-06). Implemented in Plan 04-03."""
    raise NotImplementedError("qfactor: implemented in Plan 04-03")


# ---------------------------------------------------------------------------
# CONV-07: zqfactor (Plan 04-03)
# ---------------------------------------------------------------------------

def zqfactor(F, z, q, N=1000):
    """Factor a bivariate (z,q)-series (CONV-07). Implemented in Plan 04-03."""
    raise NotImplementedError("zqfactor: implemented in Plan 04-03")


# ---------------------------------------------------------------------------
# CONV-10: qs2jaccombo (Plan 04-03)
# ---------------------------------------------------------------------------

def qs2jaccombo(f, q, T, P=None):
    """Convert each term in a sum to a JacProduct (CONV-10). Implemented in Plan 04-03."""
    raise NotImplementedError("qs2jaccombo: implemented in Plan 04-03")


# ---------------------------------------------------------------------------
# CONV-11: findprod (Plan 04-03)
# ---------------------------------------------------------------------------

def findprod(FL, T, M, Q):
    """Exhaustive search for q-products (CONV-11). Implemented in Plan 04-03."""
    raise NotImplementedError("findprod: implemented in Plan 04-03")
