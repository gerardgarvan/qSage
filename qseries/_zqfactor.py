# qseries/_zqfactor.py
#
# zqfactor(F, z, q, N) writes a (z,q)-series F as a product of terms (1 + t q^j), where t is a
# monomial c z^i, and powers (1 - q^j)^e.  Like Maple's version it is best-effort.
#
# Algorithm (matches Maple qseries 1.3 output, checked with Maple 2026 in the parity battery):
#   1. Pull out the lowest power of q (an extension: Maple needs a non-zero q^0 term).
#   2. Divide by the q^0 coefficient c(z); c is kept, unfactored, as the constant.
#   3. Repeat until the series is 1 to O(q^(N+1)): let q^d be the lowest remaining power and
#      split its coefficient into terms t.  A plain integer t != -1 gives (1 - q^d)^(-t); any
#      other term gives (1 + t q^d).  Divide each factor out, truncating at q^N.
#   N is the q-order worked to (Maple: series(..., q, N+1)); an optional fifth argument caps
#   the number of steps (Maple's default 1000).

import warnings

from sage.all import QQ, ZZ, LaurentPolynomialRing, infinity
from qseries._series import QSeries


class ZQProduct:
    """
    Result of zqfactor: constant * z^zpow * q^qpow * prod (1 - a z^i q^j)^e.

    constant: the q^0 coefficient c(z) (a Laurent polynomial in z, or a rational number).
    factors: list of (a, i, j, e) with rational a, integers i, j and non-zero integer e, ordered
             by j ascending and then i descending.
    """

    def __init__(self, factors, constant=1, zpow=0, qpow=0):
        self.factors = list(factors)
        self.constant = constant
        self.zpow = int(zpow)
        self.qpow = QQ(qpow)

    # -- display ---------------------------------------------------------------------------
    @staticmethod
    def _monomial(a, i, j):
        num, den = [], []
        if abs(a) != 1:
            num.append(str(abs(a)) if QQ(a) in ZZ else "(%s)" % abs(a))
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
            c = str(self.constant)
            parts.append("(%s)" % c if ("+" in c or " - " in c) else c)
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
# public
# ---------------------------------------------------------------------------------------------

def _fail(msg):
    warnings.warn("zqfactor: " + msg + "; returning None")
    return None


def _div_one_plus(G, t, d, N):
    """In place: G <- G / (1 + t q^d), truncated at q^N."""
    for n in range(d, N + 1):
        if G[n - d] != 0:
            G[n] -= t * G[n - d]


def _mul_one_minus_pow(G, d, k, N):
    """In place: G <- G * (1 - q^d)^k, truncated at q^N."""
    for _ in range(abs(k)):
        if k > 0:
            for n in range(N, d - 1, -1):
                if G[n - d] != 0:
                    G[n] -= G[n - d]
        else:
            for n in range(d, N + 1):
                if G[n - d] != 0:
                    G[n] += G[n - d]


def zqfactor(F, z, q=None, N=1000, buglim=1000):
    """
    Try to write the (z,q)-series F as c(z) * prod (1 + t q^j) * prod (1 - q^j)^e.

    zqfactor(F, z, q, N)
    zqfactor(F, z, q, N, buglim)

    F: QSeries whose coefficients are (Laurent) polynomials in z.
    z: the z variable (generator of a LaurentPolynomialRing).
    q: accepted for Maple interface fidelity (the q-variable is F's series generator).
    N: work to O(q^(N+1)), so factors up to q^N are found (as in Maple).  N is lowered to
       the precision of F when F is known to fewer terms.
    buglim: maximum number of factor steps (Maple's optional fifth argument, default 1000).

    Each step reads the lowest non-zero q^d coefficient of what is left and, for each of its
    terms t, divides out (1 - q^d)^(-t) when t is an integer other than -1, else (1 + t q^d).
    The q^0 coefficient is returned unfactored as the constant, as Maple prints it.
    Returns a ZQProduct, or None with a UserWarning when a coefficient is not a Laurent
    polynomial in z.  CONV-07.
    """
    if not isinstance(F, QSeries):
        raise TypeError("zqfactor expects a QSeries, got %s" % type(F).__name__)
    s = F.series
    if s == 0:
        return _fail("F is zero")
    zname = str(z) if z is not None else 'z'
    Lz = LaurentPolynomialRing(QQ, zname)
    K = Lz.fraction_field()

    v = s.valuation()
    prec = s.prec()
    N = int(N)
    if prec != infinity:
        N = min(N, int(prec - v - 1))
    try:
        G = [K(s[v + j]) for j in range(N + 1)]
    except (TypeError, ValueError) as exc:
        return _fail(str(exc))

    c = G[0]
    if c != 1:
        G = [g / c for g in G]
    try:
        constant = Lz(c) if c.denominator() in QQ or len(Lz(c.denominator()).dict()) == 1 else c
    except (TypeError, ValueError):
        constant = c
    if constant in QQ:
        constant = QQ(constant)

    factors = []
    steps = 0
    while steps <= buglim:
        d = next((j for j in range(1, N + 1) if G[j] != 0), None)
        if d is None:
            break
        try:
            TT = Lz(G[d])
        except (TypeError, ValueError):
            num, den = G[d].numerator(), G[d].denominator()
            dd = Lz(den).dict()
            if len(dd) != 1:
                return _fail("the q^%d coefficient %s is not a Laurent polynomial in z" % (d, G[d]))
            TT = Lz(num) * Lz(den) ** (-1)
        for i, cf in sorted(TT.dict().items(), key=lambda t: -t[0]):
            cf = QQ(cf)
            steps += 1
            if i == 0 and cf in ZZ and cf != -1:
                factors.append((1, 0, d, int(-cf)))           # (1 - q^d)^(-t)
                _mul_one_minus_pow(G, d, int(cf), N)
            else:
                factors.append((-cf, int(i), d, 1))           # (1 + t q^d), t = cf z^i
                _div_one_plus(G, cf * K(Lz.gen()) ** i, d, N)
    factors.sort(key=lambda t: (t[2], -t[1], -t[0]))
    return ZQProduct(factors, constant=constant, zpow=0, qpow=QQ(F.r) + v)
