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
from collections import defaultdict, namedtuple
from dataclasses import dataclass, field
from typing import List

from math import isqrt

from qseries._series import QSeries
from qseries._symbolic import EtaProduct, EProduct, QProduct, JacProduct, PochProduct
from qseries._building_blocks import etaq
from qseries._prodmake import prodmake


# ---------------------------------------------------------------------------
# Return types for mprodmake and qfactor (Plan 04-03)
# ---------------------------------------------------------------------------

@dataclass
class MProduct:
    """Return type of mprodmake: product of (1+q^n) factors.

    exponents: list of n values where (1+q^n) appears (multiplicity tracked).
    """
    exponents: List[int] = field(default_factory=list)

    def __repr__(self):
        parts = []
        for n in sorted(self.exponents):
            parts.append("(1+q)" if n == 1 else f"(1+q^{n})")
        return " * ".join(parts) if parts else "1"

    def to_series(self, T):
        from sage.all import LaurentSeriesRing, QQ as _QQ
        R = LaurentSeriesRing(_QQ, 'q')
        q = R.gen()
        result = R(1).add_bigoh(T)
        for n in self.exponents:
            result = (result * (1 + q**n)).add_bigoh(T)
        return QSeries(result, T=T)


QFactorResult = namedtuple('QFactorResult', ['numerator', 'denominator', 'r'])


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
    # JAC(a,P) = (q^a;q^P)(q^(P-a);q^P)(q^P;q^P), a != 0, contributes its exponent at residues
    # a, P-a AND P; JAC(P/2,P) = (q^(P/2);q^P)^2 (q^P;q^P) contributes 2e at P/2 and e at P;
    # JAC(0,P) = (q^P;q^P) contributes at residue P only. So: take JAC(a,P)^(e_a) for each
    # symmetric pair, JAC(P/2,P)^(e_(P/2)/2), and put whatever exponent is left at residue P
    # into JAC(0,P). A pair with e_a != e_(P-a) is not a product of theta functions.
    import warnings
    e_period = _QQ(exponents.get(P, 0))   # exponent at the "zero" residue (multiples of P)
    factors = []
    for a in range(1, P // 2 + 1):
        paired = P - a
        e_a = _QQ(exponents.get(a, 0))
        e_pa = _QQ(exponents.get(paired, 0))
        if a == paired:
            if e_a != 0:
                factors.append((a, P, e_a / 2))
                e_period -= e_a / 2
        elif e_a != 0 or e_pa != 0:
            if e_a != e_pa:
                warnings.warn(
                    "jacprodmake: exponents at residues %d and %d (mod %d) differ (%s vs %s); "
                    "the series is not a product of theta functions. Returning None."
                    % (a, paired, P, e_a, e_pa))
                return None
            factors.append((a, P, e_a))
            e_period -= e_a
    if e_period != 0:
        factors.insert(0, (0, P, e_period))

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
    # Combine equal factors, as Maple prints (q^10;q^10)^3 rather than repeating it.
    merged = {}
    for a, b, e in factors:
        merged[(a, b)] = merged.get((a, b), 0) + e
    return PochProduct(factors=[(a, b, e) for (a, b), e in merged.items() if e != 0])


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

        if a_q == 0:
            # Maple convention: JAC(0,b,infinity) = (q^b;q^b)_inf (the theta series would vanish).
            eta_b = etaq(q_sym, int(b_q), T)
            eta_s = eta_b.series if isinstance(eta_b, QSeries) else R(eta_b)
            e_int0 = int(e_q) if e_q.denominator() == 1 else None
            if e_int0 is None:
                raise ValueError(f"jac2series: non-integer exponent {e_q} not supported")
            result_series = (result_series * eta_s.add_bigoh(T) ** e_int0).add_bigoh(T)
            continue

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
    """Greedy (1+q^n) product identification (CONV-05).

    Oracle: mprodmake(etaq(q,2,18)^2/etaq(q,4,18)/etaq(q,1,18), q, 17)
         -> MProduct([1,3,5,7,9,11,13,15,17])

    Algorithm: same greedy structure as etamake but multiply residual by (1+q^k)^(-c_k)
    to cancel the +c_k*q^k leading coefficient.
    """
    from sage.all import LaurentSeriesRing, QQ as _QQ

    c = _QQ(f.series[0])
    if c == 0:
        raise ValueError("mprodmake: leading coefficient is zero")

    R = f.series.parent()
    # Use the input series precision as working precision (may be > T)
    work_prec = int(f.series.prec())
    residual_series = (f.series / c).add_bigoh(work_prec)
    residual = QSeries(residual_series, T=work_prec)

    exponents = []
    for _ in range(work_prec - 1):
        k = None
        prec = int(residual.series.prec())
        for n in range(1, prec):
            try:
                coeff = _QQ(residual.series[n])
            except (IndexError, ValueError):
                break
            if coeff != 0:
                k = n
                c_k = coeff
                break
        if k is None:
            break

        c_k_q = _QQ(c_k)
        if c_k_q.denominator() != 1:
            raise ValueError(f"mprodmake: non-integer coefficient {c_k} at q^{k}")
        c_k_int = int(c_k_q)

        # To cancel +c_k*q^k in residual, multiply by (1+q^k)^(-c_k_int).
        # (1+q^k)^(-1) has -q^k + q^{2k} - ..., so it subtracts c_k*q^k.
        # Record: output product includes (1+q^k)^(c_k_int).
        q_gen = R.gen()
        factor_series = (1 + q_gen**k).add_bigoh(work_prec)
        if c_k_int >= 0:
            mult_series = factor_series.__invert__().add_bigoh(work_prec) ** c_k_int
        else:
            mult_series = (factor_series ** (-c_k_int)).add_bigoh(work_prec)
        new_res = (residual.series * mult_series).add_bigoh(work_prec)
        residual = QSeries(new_res, T=work_prec)

        # Record: the product has (1+q^k)^(c_k_int), only if k <= T
        if k <= T:
            for _ in range(abs(c_k_int)):
                exponents.append(k)

    return MProduct(exponents=exponents)


# ---------------------------------------------------------------------------
# CONV-06: qfactor (Plan 04-03)
# ---------------------------------------------------------------------------

def qfactor(f, T=None):
    """Factor polynomial/rational function in QQ[q] into (1-q^k) terms (CONV-06, D-06/D-07).

    Oracle: qfactor(q^6*(1-q^9)*(1-q^10)*(1-q^11)*(1-q^16)/((1-q)*(1-q^2)*(1-q^3)*(1-q^4)))
         -> QFactorResult(numerator=QProduct({9:1,10:1,11:1,16:1}),
                          denominator=QProduct({1:1,2:1,3:1,4:1}),
                          r=6)
    f must be in PolynomialRing(QQ,'q') or its fraction field.

    Algorithm: factor numerator and denominator polynomials using Sage, identify
    each irreducible factor as a cyclotomic polynomial Phi_d, then reconstruct
    (1-q^k) = prod_{d|k} Phi_d by greedy grouping of cyclotomic indices.
    """
    from sage.all import QQ as _QQ, PolynomialRing, cyclotomic_polynomial, divisors

    # Handle input: tuple (num, den), fraction field element, or polynomial
    if isinstance(f, tuple):
        num_poly, den_poly = f
    else:
        try:
            num_poly = f.numerator()
            den_poly = f.denominator()
        except AttributeError:
            num_poly = f
            den_poly = f.parent()(1)

    Rq = num_poly.parent()
    q = Rq.gen()

    # Build cyclotomic polynomial lookup: Phi_d(q) -> d
    # We'll identify factors by matching against cyclotomic_polynomial(d, 'q')
    def identify_cyclotomic(factor):
        """Return d if factor == Phi_d(q) (possibly negated), else None."""
        deg = factor.degree()
        from sage.all import euler_phi as ephi
        for d in range(1, 4 * deg + 4):
            if ephi(d) == deg:
                cp = Rq(cyclotomic_polynomial(d, var='q'))
                if cp == factor or cp == -factor:
                    return d
        return None

    def poly_to_cyclotomic_multiset(poly):
        """Factor poly, return (q_power, {d: count}) of cyclotomic factors."""
        if poly == Rq(1) or poly.degree() == 0:
            return _QQ(0), {}
        factorization = poly.factor()
        q_power = _QQ(0)
        cyc_counts = {}  # d -> total count
        for factor, exp in factorization:
            if factor == q:
                q_power += _QQ(exp)
            elif factor == Rq(-1) or factor.degree() == 0:
                pass  # scalar unit
            else:
                d = identify_cyclotomic(factor)
                if d is not None:
                    cyc_counts[d] = cyc_counts.get(d, 0) + exp
        return q_power, cyc_counts

    def cyclotomic_multiset_to_qproduct(cyc_counts):
        """Greedily reconstruct (1-q^k) factors from cyclotomic multiset.
        (1-q^k) uses exactly one Phi_d for each d|k.
        Returns exponents dict {k: count}.
        """
        remaining = dict(cyc_counts)
        exponents = {}
        # Try k from largest to smallest (greedy)
        max_d = max(remaining.keys()) if remaining else 0
        for k in range(max_d, 0, -1):
            divs = divisors(k)
            # Check if all divisors d|k are present in remaining with count >= 1
            while all(remaining.get(d, 0) >= 1 for d in divs):
                for d in divs:
                    remaining[d] -= 1
                exponents[k] = exponents.get(k, 0) + 1
        return exponents

    num_r, num_cyc = poly_to_cyclotomic_multiset(num_poly)
    den_r, den_cyc = poly_to_cyclotomic_multiset(den_poly)

    num_exp = cyclotomic_multiset_to_qproduct(num_cyc)
    den_exp = cyclotomic_multiset_to_qproduct(den_cyc)
    total_r = num_r - den_r

    return QFactorResult(
        numerator=QProduct(exponents=num_exp),
        denominator=QProduct(exponents=den_exp),
        r=total_r
    )


# ---------------------------------------------------------------------------
# CONV-07: zqfactor (Plan 04-03)
# ---------------------------------------------------------------------------

# zqfactor (CONV-07) is implemented in qseries/_zqfactor.py (Phase 7).
from qseries._zqfactor import zqfactor, ZQProduct  # noqa: F401

# ---------------------------------------------------------------------------
# CONV-10: qs2jaccombo (Plan 04-03)
# ---------------------------------------------------------------------------

def qs2jaccombo(f, q, T, P=None):
    """Convert each term in f to a JacProduct via jacprodmake (CONV-10).

    f: a list of QSeries (one per additive term), or a single QSeries.
    Returns: list of JacProduct objects (one per term).
    If any term cannot be converted, raises ValueError.
    """
    if isinstance(f, list):
        terms = f
    else:
        terms = [f]

    result = []
    for term in terms:
        if P is not None:
            jp = jacprodmake(term, q, T, base=P)
        else:
            jp = jacprodmake(term, q, T)
        result.append(jp)
    return result


# ---------------------------------------------------------------------------
# CONV-11: findprod (Plan 04-03)
# ---------------------------------------------------------------------------

def findprod(FL, T, M, Q):
    """Exhaustive search for linear combinations of FL that form nice q-products (CONV-11).

    FL: list of QSeries
    T: max |coefficient| in combinations (search range -T..T per series)
    M: max |exponent| in product — passed directly to checkprod(combo, M, Q)
    Q: highest power of q to consider (truncation for comparison)
    Returns: list of coefficient_lists for each found combination.

    Oracle: findprod([etaq(q,1,T)], 1, 3, 20) -> at least [[1]] or [[-1]]
    """
    from qseries._utilities import checkprod
    from itertools import product as itertools_product
    from sage.all import QQ as _QQ

    found = []
    n = len(FL)
    R = FL[0].series.parent()
    coeff_range = range(-T, T + 1)
    for coeffs in itertools_product(coeff_range, repeat=n):
        if all(c == 0 for c in coeffs):
            continue
        # Build linear combination
        combo_series = R(0).add_bigoh(Q)
        for i, c in enumerate(coeffs):
            if c == 0:
                continue
            term = FL[i]
            scaled = (_QQ(c) * term.series).add_bigoh(Q)
            combo_series = (combo_series + scaled).add_bigoh(Q)
        if combo_series.is_zero():
            continue
        val = combo_series.valuation()
        if val is None or val < 0:
            continue
        leading = _QQ(combo_series[val])
        if leading == 0:
            continue
        # checkprod requires constant term = 1 and r = 0
        # Normalize: divide by leading coefficient and shift by valuation
        q_gen = R.gen()
        normed = (combo_series / leading / q_gen**val).add_bigoh(Q - val)
        combo = QSeries(normed, T=Q)
        try:
            check_result = checkprod(combo, M, Q)
            if check_result is not False:
                found.append(list(coeffs))
        except Exception:
            pass  # skip edge cases
    return found
