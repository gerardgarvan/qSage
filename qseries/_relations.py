# qseries/_relations.py
# Clean reimplementation of Garvan's qseries Maple package relation-finding functions.
# Reference: https://qseries.org/fgarvan/qmaple/qseries/
# All oracles taken from Garvan's tutorial (qseriesdoc.pdf) and function doc pages.
# No Maple source code was used.
#
# Phase 5 (exact, over QQ): findhom, findhomcombo, findnonhom, findnonhomcombo,
# findlincombo, findmaxind, findpoly, findcong.
# Phase 6 (mod p, over GF(p)): findhommodp, findhomcombomodp, findlincombomodp.

from sage.all import (
    matrix, QQ, GF, ZZ, IntegerVectors, PolynomialRing, is_prime, infinity
)
from math import isqrt, gcd
from functools import reduce
from qseries._series import QSeries


# ---------------------------------------------------------------------------
# Internal helpers (not exported)
# ---------------------------------------------------------------------------

def _compute_N(num_rows, topshift, is_combo):
    """
    Number of q-coefficients used per row (D-04): N = num_rows + C + topshift,
    with C = 21 for findhom/findnonhom and C = 20 for the *combo variants.
    Checked against the tutorial's printed '# of terms': findhom 4 rows -> 25,
    10 rows -> 31; findhomcombo 5 rows -> 25; findnonhom 20 rows, topshift 20 -> 61;
    findnonhomcombo 37 rows, topshift -15 -> 42.
    """
    C = 20 if is_combo else 21
    return num_rows + C + topshift


def _parse_optional_args(args):
    """
    Dispatch trailing optional arguments by type (D-05):
    integer -> topshift, 'yes'/'no' -> etaoption.  Returns (topshift, etaoption).
    """
    topshift = 0
    etaoption = 'no'
    for a in args:
        if isinstance(a, str):
            if a not in ('yes', 'no'):
                raise ValueError(f"etaoption must be 'yes' or 'no', got {a!r}")
            etaoption = a
        elif not isinstance(a, bool) and a in ZZ:
            topshift = int(a)
        else:
            raise TypeError(f"Unrecognised optional argument {a!r} (expected int topshift "
                            "or 'yes'/'no' etaoption)")
    if topshift <= -20:
        raise ValueError(f"topshift must be greater than -20, got {topshift}")
    return topshift, etaoption


def _eval_monomial(exponents, series_list):
    """
    Evaluate a monomial prod series_list[i] ** exponents[i].
    Returns (laurent_series, r) where r is the total rational q-shift
    (sum of exponents[i] * series_list[i].r).  The degree-0 monomial is (1, 0).
    """
    parent = series_list[0].series.parent()
    val = parent.one()
    r = QQ(0)
    for s, e in zip(series_list, exponents):
        if e != 0:
            val = val * s.series ** e
            r += e * s.r
    return val, r


def _validate_series_lengths(L, N, label='L'):
    """Raise ValueError if any series in L has fewer than N terms (D-04)."""
    for i, s in enumerate(L):
        if s.T < N:
            raise ValueError(
                f"Series {label}[{i}] has precision {s.T} but N={N} "
                f"terms required; recompute with T >= {N}"
            )


def _coefficient_rows(row_items, N):
    """
    Turn a list of (laurent_series, r) pairs into an N-column list of QQ rows.

    Shifts are aligned first: every r must differ from the smallest r by an integer
    (e.g. theta2-based monomials of the same degree share q^(n/4)); the common
    fractional factor is dropped, as it does not affect linear relations.
    Coefficients are then read from q^v to q^(v+N-1), where v is the smallest
    valuation among the rows, so series with negative leading powers are handled.
    """
    r_min = min(r for _, r in row_items)
    aligned = []
    for s, r in row_items:
        d = r - r_min
        if d not in ZZ:
            raise ValueError(
                f"Series have incommensurable q-shifts (q^{r} vs q^{r_min}); "
                "a polynomial relation cannot mix them."
            )
        if d != 0:
            s = s * s.parent().gen() ** int(d)
        aligned.append(s)
    nonzero = [s for s in aligned if s != 0]
    v = min(s.valuation() for s in nonzero) if nonzero else 0
    rows = []
    for i, s in enumerate(aligned):
        p = s.prec()
        if p != infinity and p < v + N:
            raise ValueError(
                f"Row {i} is only known to O(q^{p}) but coefficients q^{v}..q^{v + N - 1} "
                f"(N={N}) are required; recompute the input series with higher T"
            )
        rows.append([QQ(s[v + j]) for j in range(N)])
    return rows


def _monomial(R, exponents):
    term = R.one()
    for g, e in zip(R.gens(), exponents):
        term *= g ** e
    return term


def _build_kernel_polys(kern, mono_exps, R):
    """Map the basis of a left kernel to a set of polynomials in R."""
    result = set()
    for vec in kern.basis():
        poly = R.zero()
        for coeff, exponents in zip(vec, mono_exps):
            if coeff != 0:
                poly += coeff * _monomial(R, exponents)
        if poly != R.zero():
            result.add(poly)
    return result


def _build_combo_polys(kern, mono_exps, R):
    """
    For the *combo variants the f row is the last row.  Each kernel vector with a
    non-zero f coefficient gives f = P(X1..Xk); return the set of such P.
    """
    result = set()
    for vec in kern.basis():
        f_coeff = vec[-1]
        if f_coeff == 0:
            continue
        poly = R.zero()
        for coeff, exponents in zip(vec[:-1], mono_exps):
            if coeff != 0:
                poly += (coeff / (-f_coeff)) * _monomial(R, exponents)
        result.add(poly)
    return result


def _xring(k, F=QQ):
    return PolynomialRing(F, ['X%d' % (i + 1) for i in range(k)])


def _check_prime(p):
    """Mod-p functions: p must be a prime integer; checked before any computation."""
    if isinstance(p, bool) or p not in ZZ or not is_prime(ZZ(p)):
        raise ValueError(f"p must be a prime, got {p!r}")
    return GF(ZZ(p))


def _to_field(rows, F):
    """Reduce QQ coefficient rows into the field F (identity for QQ)."""
    if F is QQ:
        return rows
    try:
        return [[F(c) for c in row] for row in rows]
    except ZeroDivisionError:
        raise ValueError(
            f"A coefficient has a denominator divisible by {F.characteristic()}; "
            "the series cannot be reduced mod p"
        )


def _gcd_list(vals):
    """GCD of a list of integers, initialised to 0 (gcd(0,x)=x)."""
    return reduce(gcd, (abs(int(v)) for v in vals), 0)


def _suppress_implied(triples):
    """
    Remove (B, A, M) if an already-accepted (B2, A2, M2) implies it, i.e.
    A2 | A, B = B2 (mod A2) and M | M2  (D-07).  Input must be sorted by A.
    """
    accepted = []
    for B, A, M in triples:
        implied = False
        for B2, A2, M2 in accepted:
            if A % A2 == 0 and B % A2 == B2 % A2 and M2 % M == 0:
                implied = True
                break
        if not implied:
            accepted.append((B, A, M))
    return accepted


def _print_etaoption(result, L, q):
    """etaoption='yes': print each relation and, best-effort, each monomial as an eta-product."""
    try:
        from qseries._conversion import etamake
    except Exception:
        etamake = None
    T = min(s.T for s in L)
    for poly in result:
        print(poly)
        if etamake is None:
            continue
        for mono, coeff in poly.dict().items():
            exps = list(mono) if hasattr(mono, '__iter__') else [mono]
            val, r = _eval_monomial(exps, L)
            try:
                ep = etamake(QSeries(val, T, r=r), q, T)
                print(f"    {coeff} * {ep}")
            except Exception:
                pass


def _kernel_search(f, L, q, mono_exps, args, is_combo, F=QQ):
    """
    Shared body of findhom / findnonhom / findhomcombo / findnonhomcombo / findlincombo
    and the mod-p variants (F = GF(p)).
    """
    topshift, etaoption = _parse_optional_args(args)
    k = len(L)
    if k == 0:
        raise ValueError("L must contain at least one series")
    num_rows = len(mono_exps) + (1 if is_combo else 0)
    N = _compute_N(num_rows, topshift, is_combo)
    _validate_series_lengths(L, N)
    if is_combo and f.T < N:
        raise ValueError(f"Series f has precision {f.T} but N={N} terms required")
    print(f"# of terms , {N}")
    if is_combo:
        print(f"matrix is , {num_rows}, x, {N}")

    items = [_eval_monomial(e, L) for e in mono_exps]
    if is_combo:
        items.append((f.series, f.r))
    M = matrix(F, _to_field(_coefficient_rows(items, N), F))
    kern = M.left_kernel()
    R = _xring(k, F)
    if is_combo:
        result = _build_combo_polys(kern, mono_exps, R)
    else:
        result = _build_kernel_polys(kern, mono_exps, R)
    if etaoption == 'yes':
        _print_etaoption(result, L, q)
    return result


def _hom_monomials(n, k):
    return [list(e) for e in IntegerVectors(n, k)]


def _nonhom_monomials(n, k):
    exps = []
    for d in range(n + 1):
        exps.extend(list(e) for e in IntegerVectors(d, k))
    return exps


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def findhom(L, q, n, *args):
    """
    Set of homogeneous degree-n polynomial relations among the series in L.

    findhom(L, q, n)
    findhom(L, q, n, topshift)
    findhom(L, q, n, etaoption)
    findhom(L, q, n, topshift, etaoption)

    Returns a set of polynomials in X1..Xk over QQ (empty set if none).  REL-01.
    """
    return _kernel_search(None, L, q, _hom_monomials(n, len(L)), args, is_combo=False)


def findhomcombo(f, L, q, n, *args):
    """
    Express f as a homogeneous degree-n polynomial in the series of L.

    findhomcombo(f, L, q, n [, topshift] [, etaoption])

    Returns a set of polynomials P with f = P(L) (empty if f is not such a
    combination; more than one if L is dependent).  REL-02.
    """
    return _kernel_search(f, L, q, _hom_monomials(n, len(L)), args, is_combo=True)


def findnonhom(L, q, n, *args):
    """
    Set of polynomial relations of total degree <= n among the series in L.

    findnonhom(L, q, n [, topshift] [, etaoption])   REL-05.
    """
    return _kernel_search(None, L, q, _nonhom_monomials(n, len(L)), args, is_combo=False)


def findnonhomcombo(f, L, q, n, *args):
    """
    Express f as a polynomial of total degree <= n in the series of L.

    findnonhomcombo(f, L, q, n [, topshift] [, etaoption])   REL-06.
    """
    return _kernel_search(f, L, q, _nonhom_monomials(n, len(L)), args, is_combo=True)


def findlincombo(f, L, SL, q, topshift=0):
    """
    Express f as a linear combination of the series in L.

    SL (list of symbolic names) is accepted for interface fidelity; the result is
    always a set of degree-1 polynomials in X1..Xk over QQ (D-09).  Prints
    '%NOT A LINEAR COMBO.%' and returns an empty set if there is none.  REL-07.
    """
    result = _kernel_search(f, L, q, _hom_monomials(1, len(L)), (topshift,), is_combo=True)
    if not result:
        print("%NOT A LINEAR COMBO.%")
    return result


# ---------------------------------------------------------------------------
# Mod-p variants (Phase 6)
# ---------------------------------------------------------------------------

def findhommodp(L, p, q, n, *args):
    """
    Set of homogeneous degree-n polynomial relations mod p among the series in L.

    findhommodp(L, p, q, n)
    findhommodp(L, p, q, n, topshift)

    Mod-p version of findhom: same monomials and N = rows + 21 + topshift, but the kernel
    is computed over GF(p).  Returns polynomials in X1..Xk over GF(p).  REL-03.
    Raises ValueError if p is not prime (before any computation).
    """
    F = _check_prime(p)
    return _kernel_search(None, L, q, _hom_monomials(n, len(L)), args, is_combo=False, F=F)


def findhomcombomodp(f, L, p, q, n, *args):
    """
    Express f mod p as a homogeneous degree-n polynomial in the series of L.

    findhomcombomodp(f, L, p, q, n [, topshift] [, etaoption])   (doc-page calling sequence)

    Mod-p version of findhomcombo (N = rows + 20 + topshift).  Returns a set of
    polynomials P over GF(p) with f = P(L) mod p.  REL-04.
    """
    F = _check_prime(p)
    return _kernel_search(f, L, q, _hom_monomials(n, len(L)), args, is_combo=True, F=F)


def findlincombomodp(f, L, SL, p, q, topshift=0):
    """
    Express f mod p as a linear combination of the series in L.

    findlincombomodp(f, L, SL, p, q, topshift)   (doc-page calling sequence)

    SL (names for display) is accepted for interface fidelity; the result is a set of
    degree-1 polynomials in X1..Xk over GF(p).  Prints 'nx = , k' like Maple, and
    '%NOT A LINEAR COMBO.%' with an empty set when there is none.  REL-08.
    """
    F = _check_prime(p)
    print(f"nx = , {len(L)}")
    result = _kernel_search(f, L, q, _hom_monomials(1, len(L)), (topshift,), is_combo=True, F=F)
    if not result:
        print("%NOT A LINEAR COMBO.%")
    return result


def findmaxind(XFL, T=0):
    """
    Return [P, NXFL]: a maximal linearly independent sublist P of XFL and the
    1-based positions NXFL of its members in XFL.  T acts as topshift for the
    independence check (N = len(XFL) + 21 + T coefficients).  REL-09.
    """
    if not XFL:
        return [[], []]
    k = len(XFL)
    N = k + 21 + T
    _validate_series_lengths(XFL, N, label='XFL')
    rows = _coefficient_rows([(s.series, s.r) for s in XFL], N)

    P, NXFL = [], []
    current_rows = []
    current_rank = 0
    for idx, (s, row) in enumerate(zip(XFL, rows)):
        test_rows = current_rows + [row]
        test_rank = matrix(QQ, test_rows).rank()
        if test_rank > current_rank:
            P.append(s)
            NXFL.append(idx + 1)
            current_rows = test_rows
            current_rank = test_rank
    return [P, NXFL]


def findpoly(x, y, q, deg1, deg2, check=None):
    """
    Find polynomial relations P(X, Y) = 0 with deg_X P <= deg1, deg_Y P <= deg2.

    If check is given, each relation is verified to O(q^check) and the result is
    printed; a relation that fails the check raises ValueError.
    Returns a set of polynomials in QQ[X, Y].  REL-10.
    """
    mono_exps = [(i, j) for j in range(deg2 + 1) for i in range(deg1 + 1)]
    num_rows = len(mono_exps)
    N = num_rows + 21
    _validate_series_lengths([x, y], N, label='[x, y]')
    print(f"# of terms , {N}")

    items = []
    for (i, j) in mono_exps:
        val = x.series.parent().one()
        if i > 0:
            val = val * x.series ** i
        if j > 0:
            val = val * y.series ** j
        items.append((val, i * x.r + j * y.r))
    rows = _coefficient_rows(items, N)
    kern = matrix(QQ, rows).left_kernel()
    R = PolynomialRing(QQ, ['X', 'Y'])
    result = _build_kernel_polys(kern, mono_exps, R)

    if check is not None:
        # Re-read coefficients up to q^(check-1) and confirm every relation vanishes there.
        v = _min_valuation(items)
        Nc = max(check - v, N)
        Mc = matrix(QQ, _coefficient_rows(items, Nc))
        for vec in kern.basis():
            if any(c != 0 for c in vec * Mc):
                raise ValueError(f"findpoly: a relation fails the check to O(q^{check})")
        print(f"CHECK: relation(s) verified to O(q^{check})")
    return result


def _min_valuation(items):
    r_min = min(r for _, r in items)
    vals = [s.valuation() + int(r - r_min) for s, r in items if s != 0]
    return min(vals) if vals else 0


def findcong(f, T, LM=None, XSET=None):
    """
    Find Ramanujan-type congruences a(An+B) = 0 (mod M) among the coefficients
    a(0..T) of f.  Returns a set of (B, A, M) tuples.

    findcong(f, T)            A runs over 2..floor(sqrt(T))
    findcong(f, T, LM)        A runs over 2..LM
    findcong(f, T, LM, XSET)  moduli in XSET are excluded

    M is the gcd of a(An+B) over An+B <= T (not restricted to primes); congruences
    implied by an earlier one (A2 | A, B = B2 mod A2, M | M2) are suppressed.
    REL-11.  Oracle: findcong(1/etaq(q,1,1001), 1000) == {(4,5,5),(5,7,7),(6,11,11),(24,25,25)}.
    """
    if f.r != 0:
        raise ValueError(f"findcong needs an integral q-series (r=0), got r={f.r}")
    if f.T <= T:
        raise ValueError(f"Series f has precision {f.T}; coefficients up to q^{T} require T > {T}")
    if LM is None:
        LM = isqrt(T)
    XSET = set(XSET) if XSET is not None else set()

    coeffs = [f.series[n] for n in range(T + 1)]
    for n, c in enumerate(coeffs):
        if c not in ZZ:
            raise ValueError(f"findcong needs integer coefficients; a({n}) = {c}")

    raw = []
    for A in range(2, LM + 1):
        for B in range(A):
            vals = [coeffs[A * n + B] for n in range((T - B) // A + 1)]
            M = _gcd_list(vals)
            if M > 1 and M not in XSET:
                raw.append((B, A, M))

    raw.sort(key=lambda t: (t[1], t[0]))
    return set(_suppress_implied(raw))
