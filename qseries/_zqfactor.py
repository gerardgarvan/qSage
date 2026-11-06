# qseries/_zqfactor.py
#
# Licensing note:
# Clean reimplementation derived solely from the documentation of Frank Garvan's Maple qseries
# package v1.3 (https://qseries.org/fgarvan/qmaple/qseries/functions/zqfactor.html).
# No Maple source code was consulted or translated.
#
# zqfactor(F, z, q, N) tries to write a (z,q)-series F as a product of terms
# (1 - a z^i q^j) with integer a.  Like Maple's version it is best-effort: it can fail to
# find a product even when one exists, and then warns and returns None.
#
# Algorithm (a two-variable form of Andrews' algorithm used by prodmake):
#   1. Pull out the lowest power of q (and F.r).
#   2. Factor the q^0 coefficient c0(z) over ZZ into binomials (1 - a z^i) and cyclotomic
#      polynomials Phi_n(z) = prod_{d|n} (1 - z^d)^mu(n/d), choosing each binomial's
#      orientation, (1 - a z^d) or (1 - a z^-d), so that the left-over monomial is simplest.
#   3. Divide every q^j coefficient by c0 (exactly), giving G = 1 + O(q).
#   4. For j = 1, 2, ...: the q^j coefficient of G is -sum_i e_ij z^i, so the factors at q^j are
#      (1 - z^i q^j)^(e_ij); divide them out and continue.
#   5. Rewrite (1 - x)^(-1) (1 - x^2) as (1 + x), as Maple prints it.

from itertools import product as _cartesian
import warnings

from sage.all import (
    QQ, ZZ, LaurentPolynomialRing, PolynomialRing, factor, moebius, divisors, binomial,
    infinity,
)
from qseries._series import QSeries


class ZQProduct:
    """
    Result of zqfactor: constant * z^zpow * q^qpow * prod (1 - a z^i q^j)^e.

    factors: list of (a, i, j, e) with integer a, i, j and non-zero integer e, ordered by j
             ascending and then i descending (the order Maple prints them in).
    """

    def __init__(self, factors, constant=1, zpow=0, qpow=0):
        self.factors = list(factors)
        self.constant = QQ(constant)
        self.zpow = int(zpow)
        self.qpow = QQ(qpow)

    # -- display ---------------------------------------------------------------------------
    @staticmethod
    def _monomial(a, i, j):
        num, den = [], []
        if abs(a) != 1:
            num.append(str(abs(a)))
        if i > 0:
            num.append("z" if i == 1 else "z^%d" % i)
        if j > 0:
            num.append("q" if j == 1 else "q^%d" % j)
        if i < 0:
            den.append("z" if i == -1 else "z^%d" % (-i))
        top = "*".join(num) if num else "1"
        return top + ("/" + "*".join(den) if den else "")

    def __repr__(self):
        parts = []
        if self.constant != 1:
            parts.append(str(self.constant))
        if self.zpow:
            parts.append("z" if self.zpow == 1 else "z^(%d)" % self.zpow)
        if self.qpow:
            parts.append("q" if self.qpow == 1 else "q^(%s)" % self.qpow)
        for a, i, j, e in self.factors:
            sign = "-" if a > 0 else "+"
            f = "(1 %s %s)" % (sign, self._monomial(a, i, j))
            parts.append(f if e == 1 else "%s^%d" % (f, e))
        return " * ".join(parts) if parts else "1"

    def __eq__(self, other):
        return (isinstance(other, ZQProduct) and self.factors == other.factors
                and self.constant == other.constant and self.zpow == other.zpow
                and self.qpow == other.qpow)

    __hash__ = None

    # -- expansion -------------------------------------------------------------------------
    def to_series(self, T, z=None):
        """Expand to O(q^T) in LaurentSeriesRing(LaurentPolynomialRing(QQ, z), 'q').

        The q^qpow prefactor is kept as the QSeries shift r when it is not an integer.
        """
        from sage.all import LaurentSeriesRing
        Lz = z.parent() if z is not None else LaurentPolynomialRing(QQ, 'z')
        zz = Lz.gen()
        S = LaurentSeriesRing(Lz, 'q', default_prec=T)
        q = S.gen()
        val = S(self.constant * zz**self.zpow).add_bigoh(T)
        for a, i, j, e in self.factors:
            fac = S(1 - a * zz**i * q**j).add_bigoh(T)
            if e < 0:
                fac = fac.__invert__()
            for _ in range(abs(e)):
                val = (val * fac).add_bigoh(T)
        r = self.qpow
        if r in ZZ:
            return QSeries((val * q**int(r)).add_bigoh(T + int(r)), T=T + int(r))
        return QSeries(val, T=T, r=r)


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------

def _to_laurent(c, Lz):
    """Coerce a coefficient into the Laurent polynomial ring Lz (denominators must be monomials)."""
    try:
        return Lz(c)
    except (TypeError, ValueError):
        pass
    num, den = Lz(c.numerator()), Lz(c.denominator())
    dd = den.dict()
    if len(dd) != 1:
        raise ValueError("coefficient %s is not a Laurent polynomial in z" % c)
    return num * den**(-1)


def _split(c, P):
    """Laurent polynomial c = z^s * p(z) with p(0) != 0; returns (p in P, s)."""
    d = c.dict()
    s = min(d)
    return P({k - s: v for k, v in d.items()}), s


def _exact_div(c, c0, Lz, P):
    """c / c0 as a Laurent polynomial, or None if the division is not exact."""
    if c == 0:
        return Lz(0)
    p1, s1 = _split(c, P)
    p0, s0 = _split(c0, P)
    quo, rem = p1.quo_rem(p0)
    if rem != 0:
        return None
    zz = Lz.gen()
    return Lz(quo) * zz**(s1 - s0)


def _cyclotomic_index(f):
    """n if f == Phi_n(z) (as a primitive integer polynomial), else 0."""
    try:
        n = f.is_cyclotomic(certificate=True)
        return int(n) if n else 0
    except TypeError:                           # older Sage without certificate=
        from sage.all import cyclotomic_polynomial, euler_phi
        d = f.degree()
        if f.leading_coefficient() != 1:
            return 0
        for n in range(2, 6 * d * d + 7):      # euler_phi(n) >= sqrt(n/2) bounds n
            if euler_phi(n) == d and f == f.parent()(cyclotomic_polynomial(n)):
                return n
        return 0


def _factor_q0(c0, Lz):
    """
    Factor the q^0 coefficient c0(z) into constant * z^k * prod (1 - a z^i)^e.
    Returns (constant, k, [(a, i, e), ...]) or None if a factor is not of that shape.
    """
    PZ = PolynomialRing(ZZ, 'z')
    PQ = PolynomialRing(QQ, 'z')
    p, s = _split(c0, PQ)
    den = p.denominator() if hasattr(p, 'denominator') else 1
    pz = PZ(p * den)
    fac = factor(pz)
    unit = QQ(fac.unit()) / den
    zk = s
    fixed = []          # (a, i, e) with fixed orientation
    binomials = []      # (u, v, d, e): u z^d + v, multiplicity e
    for f, e in fac:
        if f.degree() == 0:
            unit *= QQ(f) ** e
            continue
        terms = f.dict()
        if len(terms) == 2 and 0 in terms:
            d = max(terms)
            binomials.append((QQ(terms[d]), QQ(terms[0]), d, e))
            continue
        cyc = _cyclotomic_index(f)
        if cyc and cyc > 1:
            n = cyc
            for d in divisors(n):
                mu = moebius(n // d)
                if mu:
                    fixed.append((1, d, mu * e))
            continue
        return None

    best = None
    for choice in _cartesian((0, 1), repeat=len(binomials)):
        const, zexp, facs, ok = unit, zk, list(fixed), True
        for (u, v, d, e), orient in zip(binomials, choice):
            if orient == 0:                     # v * (1 - a z^d), a = -u/v
                a = -u / v
                const *= v ** e
                facs.append((a, d, e))
            else:                               # u z^d * (1 - a z^-d), a = -v/u
                a = -v / u
                const *= u ** e
                zexp += d * e
                facs.append((a, -d, e))
            if a not in ZZ:
                ok = False
                break
        if not ok:
            continue
        key = (abs(zexp), abs(const - 1), sum(1 for x in choice if x))
        if best is None or key < best[0]:
            best = (key, const, zexp, facs)
        if len(binomials) > 16:                 # avoid 2^k blow-up: take first valid choice
            break
    if best is None:
        return None
    _, const, zexp, facs = best
    return const, zexp, [(ZZ(a), int(i), int(e)) for a, i, e in facs]


def _mul_factor(G, i, j, k, zz):
    """In place: G <- G * (1 - z^i q^j)^k, truncated to len(G)."""
    J = len(G)
    zi = zz**i
    for _ in range(abs(k)):
        if k > 0:      # multiply by (1 - x): G[n] -= x G[n-j], n descending
            for n in range(J - 1, j - 1, -1):
                if G[n - j] != 0:
                    G[n] -= zi * G[n - j]
        else:          # multiply by 1/(1 - x): G[n] += x G[n-j], n ascending
            for n in range(j, J):
                if G[n - j] != 0:
                    G[n] += zi * G[n - j]


def _assemble(q0_factors, exps):
    """Step 5 on a copy of exps: (1 - x)^(-k) (1 - x^2)^k -> (1 + x)^k; sorted factor list."""
    exps = dict(exps)
    plus = {}
    for (i, jj) in sorted(exps, key=lambda t: (t[1], -t[0])):
        e = exps.get((i, jj), 0)
        e2 = exps.get((2 * i, 2 * jj), 0)
        if e < 0 and e2 > 0:
            k = min(-e, e2)
            exps[(i, jj)] += k
            exps[(2 * i, 2 * jj)] -= k
            plus[(i, jj)] = plus.get((i, jj), 0) + k
    factors = [(a, i, 0, e) for a, i, e in q0_factors if e != 0]
    factors += [(1, i, jj, e) for (i, jj), e in exps.items() if e]
    factors += [(-1, i, jj, k) for (i, jj), k in plus.items()]
    factors.sort(key=lambda t: (t[2], -t[1], -t[0]))
    return factors


def _fail(msg):
    warnings.warn("zqfactor: " + msg + "; returning None")
    return None


# ---------------------------------------------------------------------------------------------
# public
# ---------------------------------------------------------------------------------------------

def zqfactor(F, z, q=None, N=1000):
    """
    Try to write the (z,q)-series F as a product of terms (1 - a z^i q^j), a an integer.

    zqfactor(F, z, q)
    zqfactor(F, z, q, N)

    F: QSeries whose coefficients are (Laurent) polynomials in z.
    z: the z variable (generator of a LaurentPolynomialRing).
    q: accepted for Maple interface fidelity (the q-variable is F's series generator).
    N: maximum number of terms (factors) to return, default 1000; at most N - 1 factors are
       returned, which reproduces the doc-page example (N = 10 gives nine factors).

    Returns a ZQProduct, or None with a UserWarning when no product of that shape is found
    (Maple's version is also documented as best-effort).  CONV-07.
    """
    if not isinstance(F, QSeries):
        raise TypeError("zqfactor expects a QSeries, got %s" % type(F).__name__)
    N = int(N)
    s = F.series
    if s == 0:
        return _fail("F is zero")
    zname = str(z) if z is not None else 'z'
    Lz = LaurentPolynomialRing(QQ, zname)
    zz = Lz.gen()
    PQ = PolynomialRing(QQ, zname)

    v = s.valuation()
    prec = s.prec()
    last = (prec - 1) if prec != infinity else s.degree()
    J = int(last - v + 1)
    try:
        C = [_to_laurent(s[v + j], Lz) for j in range(J)]
    except ValueError as exc:
        return _fail(str(exc))

    # Step 2: the q^0 coefficient
    q0 = _factor_q0(C[0], Lz)
    if q0 is None:
        return _fail("the q^0 coefficient %s does not factor into terms (1 - a z^i)" % C[0])
    const, zexp, q0_factors = q0

    # Step 3: divide out c0
    G = []
    for c in C:
        d = _exact_div(c, C[0], Lz, PQ)
        if d is None:
            return _fail("a q-coefficient is not divisible by the q^0 coefficient %s" % C[0])
        G.append(d)

    # Step 4: read off exponents e_ij order by order in q.  Work in stages: after each stage
    # build the final factor list; it is final once every returned factor at q^j has had
    # q^(2j) examined (needed by the (1 + x) rewrite in step 5) or the data is exhausted.
    exps = {}                                   # (i, j) -> e
    j_done = 0
    j_stop = min(J, max(2, 2 * N + 1))
    while True:
        for j in range(j_done + 1, j_stop):
            cj = G[j]
            if cj == 0:
                continue
            for i, b in sorted(cj.dict().items(), key=lambda t: -t[0]):
                e = -b
                if e not in ZZ:
                    return _fail("non-integer exponent %s at z^%d q^%d" % (e, i, j))
                e = int(e)
                exps[(i, j)] = exps.get((i, j), 0) + e
                _mul_factor(G, i, j, -e, zz)
        j_done = j_stop - 1
        factors = _assemble(q0_factors, exps)[:max(N - 1, 0)]
        jmax = max((f[2] for f in factors), default=0)
        if j_stop >= J or 2 * jmax < j_stop:
            break
        j_stop = min(J, 2 * jmax + 1)
    return ZQProduct(factors, constant=const, zpow=zexp, qpow=QQ(F.r) + v)
