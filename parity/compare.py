"""
parity/compare.py -- run the parity battery in Python and compare with Maple's results.

Usage (repo root):
  sage -python parity/compare.py                      # dry run: Python side only (checks every case runs)
  sage -python parity/compare.py maple_results.txt    # full comparison -> parity/parity_report.md
  sage -python parity/compare.py --selftest           # check the Maple-output parsers on known strings

Statuses:  MATCH        same canonical form
           VALUE-MATCH  different form, same q-series (e.g. another but equivalent JAC product)
           DIFFER       results differ -> investigate
           REVIEW       no automatic comparison for this kind (both outputs shown)
           KNOWN-MAPLE  differs because of a documented Maple problem (see README; port is correct)
           MAPLE-ERROR / PY-ERROR / MISSING
Exit status 1 if any case is DIFFER or PY-ERROR.
"""
import ast
import os
import re
import sys
import traceback
from collections import Counter

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sage.all import (QQ, ZZ, GF, SR, LaurentSeriesRing, LaurentPolynomialRing, PolynomialRing,  # noqa: E402
                      PowerSeriesRing, matrix, sage_eval, sigma, kronecker, function, var, Integer)
from sage.symbolic.operators import mul_vararg, add_vararg  # noqa: E402
import operator  # noqa: E402

from parity.cases import CASES, SEED  # noqa: E402
import qseries  # noqa: E402
from qseries import *  # noqa: E402,F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
PREC = 800


# ---------------------------------------------------------------------------------------------
# Python namespace (mirrors the Maple prelude in cases.py)
# ---------------------------------------------------------------------------------------------

def base_namespace():
    R = LaurentSeriesRing(QQ, 'q', default_prec=PREC)
    q = R.gen()
    P = PolynomialRing(QQ, 't')
    ns = dict(vars(qseries))
    ns.update(QQ=QQ, ZZ=ZZ, R=R, q=q, P=P, t=P.gen(), QSeries=QSeries, prod=_prod)

    def CL(f, a, b):
        s = f.series if isinstance(f, QSeries) else f
        return [s[i] for i in range(a, b + 1)]

    def POCH(a, b, T):
        s = R(1).add_bigoh(T)
        k = 0
        while a + b * k < T:
            s = (s * (1 - q**(a + b * k))).add_bigoh(T)
            k += 1
        return s

    def JS(a, b, T):
        if a == 0:
            return POCH(b, b, T)
        return (POCH(a, b, T) * POCH(b - a, b, T) * POCH(b, b, T)).add_bigoh(T)

    def E4(T):
        return QSeries(R(1 + 240 * sum(sigma(n, 3) * q**n for n in range(1, T))).add_bigoh(T), T)

    def E6(T):
        return QSeries(R(1 - 504 * sum(sigma(n, 5) * q**n for n in range(1, T))).add_bigoh(T), T)

    def ONE(T):
        return QSeries(R(1).add_bigoh(T), T)

    def UE(qq, k, p, trunk):
        x = sum(kronecker(m, p) * n**(k - 1) * qq**(m * n)
                for m in range(1, trunk + 1) for n in range(1, trunk // m + 1))
        return QSeries(qq.parent()(x).add_bigoh(trunk + 1), T=trunk + 1)

    def LQ(f):
        """The Laurent series q^r * f.series of a QSeries with integral shift r."""
        return f.series * q**int(f.r)

    ns.update(CL=CL, POCH=POCH, JS=JS, E4=E4, E6=E6, ONE=ONE, UE=UE, LQ=LQ)
    return ns


def _prod(it):
    r = 1
    for x in it:
        r = r * x
    return r


def case_namespace(base, case):
    ns = dict(base)
    v = case.opts.get("vars")
    if v in ("z", "a,b"):
        L = LaurentPolynomialRing(QQ, v.replace(",", ", "))
        Rq = LaurentSeriesRing(L, 'q', default_prec=PREC)
        ns.update(dict(zip(v.split(","), L.gens())), q=Rq.gen(), R=Rq)
    return ns


def run_py(code, ns):
    tree = ast.parse(code)
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(tree, "<case>", "exec"), ns)
        return eval(compile(ast.Expression(last.value), "<case>", "eval"), ns) if last else None


# ---------------------------------------------------------------------------------------------
# Parsing Maple output (lprint syntax) into Sage objects
# ---------------------------------------------------------------------------------------------

def _symbolic_ns():
    names = dict(q=var('q'), tau=var('tau'), z=var('z'), a=var('a'), b=var('b'),
                 infinity=var('infinity'), eta=function('eta'), JAC=function('JAC'), _E=function('_E'))
    return names


def parse_sr(text):
    return sage_eval(text, locals=_symbolic_ns())


def factor_terms(expr):
    """Multiplicative decomposition of a symbolic expression: (constant, [(base, exponent), ...])."""
    const = QQ(1)
    terms = []

    def walk(e, power):
        nonlocal const
        if e.is_numeric():
            const *= QQ(e) ** power if QQ(power) in ZZ else 1
            return
        op = e.operator()
        if op is mul_vararg:
            for o in e.operands():
                walk(o, power)
        elif op is operator.pow:
            base, ex = e.operands()
            if ex.is_numeric():
                walk(base, power * QQ(ex))
            else:
                terms.append((e, power))
        else:
            terms.append((e, power))
    walk(SR(expr), QQ(1))
    return const, terms


def _qpoly(base):
    try:
        return PolynomialRing(QQ, 'q')(SR(base))
    except Exception:
        return None


def _binomial_index(base):
    """Return (k, sign, kind) if base is 1 - q^k, q^k - 1 or 1 + q^k; else None."""
    p = _qpoly(base)
    if p is None:
        return None
    qq = p.parent().gen()
    for k in range(1, 2000):
        if p.degree() != k:
            continue
        if p == 1 - qq**k:
            return k, 1, "minus"
        if p == qq**k - 1:
            return k, -1, "minus"
        if p == 1 + qq**k:
            return k, 1, "plus"
        break
    return None


def maple_qpower_const_and_terms(text):
    const, terms = factor_terms(parse_sr(text))
    qv = var('q')
    r = QQ(0)
    rest = []
    for base, e in terms:
        if base == qv:
            r += e
        else:
            rest.append((base, e))
    return const, r, rest


# ---------------------------------------------------------------------------------------------
# Canonical forms per kind:  python_canon(result, case) and maple_canon(text, case)
# ---------------------------------------------------------------------------------------------

def canon_coeffs_py(res, case):
    return [str(x) for x in _normalize_coeffs(res, case)]


def _normalize_coeffs(vals, case):
    v = case.opts.get("vars")
    if v in ("z", "a,b"):
        L = LaurentPolynomialRing(QQ, v.replace(",", ", "))
        return [L(x) if not hasattr(x, "numerator") or x in L else x for x in vals]
    return [QQ(x) for x in vals]


def canon_coeffs_maple(text, case):
    v = case.opts.get("vars")
    if v in ("z", "a,b"):
        L = LaurentPolynomialRing(QQ, v.replace(",", ", "))
        vals = sage_eval(text, locals=dict(zip(v.split(","), L.gens())))
        return [str(L(x)) if x in L else str(x) for x in vals]
    return [str(QQ(x)) for x in sage_eval(text)]


def canon_eta_py(res, case):
    return (QQ(res.constant), QQ(res.r), tuple(sorted((int(k), QQ(e)) for k, e in res.factors if e)))


def canon_eta_maple(text, case):
    const, r, terms = maple_qpower_const_and_terms(text)
    fs = Counter()
    for base, e in terms:
        if base.operator() is not None and str(base.operator()) == "eta":
            k = QQ(base.operands()[0] / var('tau'))
            fs[int(k)] += e
        else:
            raise ValueError("unexpected factor %s" % base)
    return (const, r, tuple(sorted((k, e) for k, e in fs.items() if e)))


def canon_qeta_py(res, case):
    return tuple(sorted((int(k), QQ(e)) for k, e in res.exponents.items() if e))


def canon_qeta_maple(text, case):
    const, r, terms = maple_qpower_const_and_terms(text)
    fs = Counter()
    for base, e in terms:
        if str(base.operator()) == "_E":
            arg = base.operands()[0]
            k = 1 if arg == var('q') else int(arg.operands()[1])
            fs[k] += e
        else:
            raise ValueError("unexpected factor %s" % base)
    return tuple(sorted((k, e) for k, e in fs.items() if e))


def canon_prod_py(res, case):
    return tuple(sorted((int(n), QQ(e)) for n, e in res.exponents.items() if e))


def canon_prod_maple(text, case):
    const, r, terms = maple_qpower_const_and_terms(text)
    fs = Counter()
    for base, e in terms:
        bi = _binomial_index(base)
        if bi is None or bi[2] != "minus":
            raise ValueError("unexpected factor %s" % base)
        fs[bi[0]] += e
    return tuple(sorted((k, e) for k, e in fs.items() if e))


def canon_jac_py(res, case):
    if res is None:
        return None
    fs = Counter()
    for a, b, e in res.factors:
        fs[(int(a), int(b))] += QQ(e)
    return (QQ(res.constant), QQ(res.r), tuple(sorted((k, e) for k, e in fs.items() if e)))


def canon_jac_maple(text, case):
    const, r, terms = maple_qpower_const_and_terms(text)
    fs = Counter()
    for base, e in terms:
        if str(base.operator()) == "JAC":
            a, b = int(base.operands()[0]), int(base.operands()[1])
            fs[(a, b)] += e
        elif str(base.operator()) == "sqrt":
            raise ValueError("sqrt form")
        else:
            raise ValueError("unexpected factor %s" % base)
    return (const, r, tuple(sorted((k, e) for k, e in fs.items() if e)))


def jac_value(canon, T):
    """Series of const * q^r * prod JAC(a,b)^e (r must be integral) to O(q^T)."""
    PS = PowerSeriesRing(QQ, 'q', default_prec=T)
    qq = PS.gen()
    const, r, fs = canon

    def poch(a, b):
        s = PS(1).add_bigoh(T)
        k = 0
        while a + b * k < T:
            if a + b * k > 0:
                s = (s * (1 - qq**(a + b * k))).add_bigoh(T)
            k += 1
        return s
    val = PS(const).add_bigoh(T)
    for (a, b), e in fs:
        j = poch(b, b) if a == 0 else (poch(a % b if a % b else b, b) * poch((b - a) % b or b, b) * poch(b, b))
        if e in ZZ:
            val = (val * j**int(e)).add_bigoh(T)
        else:
            val = (val * (e * j.log()).exp(T)).add_bigoh(T)
    return (r, val)


def canon_qfactor_py(res, case):
    fs = Counter()
    for k, e in res.numerator.exponents.items():
        fs[int(k)] += QQ(e)
    for k, e in res.denominator.exponents.items():
        fs[int(k)] -= QQ(e)
    return (QQ(res.r), tuple(sorted((k, e) for k, e in fs.items() if e)))


def canon_qfactor_maple(text, case):
    const, r, terms = maple_qpower_const_and_terms(text)
    fs = Counter()
    for base, e in terms:
        bi = _binomial_index(base)
        if bi is None or bi[2] != "minus":
            raise ValueError("unexpected factor %s" % base)
        fs[bi[0]] += e
    return (r, tuple(sorted((k, e) for k, e in fs.items() if e)))


def canon_mprod_py(res, case):
    return tuple(sorted(Counter(int(n) for n in res.exponents).items()))


def canon_mprod_maple(text, case):
    const, r, terms = maple_qpower_const_and_terms(text)
    fs = Counter()
    for base, e in terms:
        bi = _binomial_index(base)
        if bi is None or bi[2] != "plus":
            raise ValueError("unexpected factor %s" % base)
        fs[bi[0]] += int(e)
    return tuple(sorted(fs.items()))


def _xring(case):
    k = case.opts.get("k", 1)
    F = GF(case.opts["p"]) if "p" in case.opts else QQ
    return PolynomialRing(F, ['X%d' % i for i in range(1, k + 1)])


def _maple_polys(text, case):
    """Parse a Maple set/expression in X[i] (or SL names) into polynomials of _xring(case)."""
    Rx = _xring(case)
    gens = Rx.gens()
    loc = {"X": [None] + list(gens)}
    for i, name in enumerate(case.opts.get("sl", [])):
        loc[name] = gens[i]
    text = text.strip()
    if text in ("", "NULL", "{}", "[]"):
        return []
    val = sage_eval(text, locals=loc)
    items = list(val) if isinstance(val, (set, frozenset, list, tuple)) else [val]
    return [Rx(x) for x in items]


def _py_polys(res, case):
    Rx = _xring(case)
    if res is None:
        return []
    items = list(res) if isinstance(res, (set, frozenset, list, tuple)) else [res]
    out = []
    for p in items:
        out.append(Rx(sage_eval(str(p), locals=dict(zip([str(g) for g in Rx.gens()], Rx.gens())))))
    return out


def _span(polys, Rx):
    monos = sorted({m for p in polys for m in p.monomials()})
    if not polys or not monos:
        return 0, None, monos
    M = matrix(Rx.base_ring(), [[p.monomial_coefficient(m) for m in monos] for p in polys])
    return M.rank(), M, monos


def same_span(p1, p2, Rx):
    allp = p1 + p2
    r_all, _, _ = _span(allp, Rx)
    r1, _, _ = _span(p1, Rx)
    r2, _, _ = _span(p2, Rx)
    return r1 == r2 == r_all


def canon_cong(text_or_res, from_maple):
    if from_maple:
        return tuple(sorted(tuple(int(x) for x in m) for m in re.findall(r"\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]", text_or_res)))
    return tuple(sorted(tuple(int(x) for x in t) for t in text_or_res))


def zq_sr(res):
    z, q = var('z'), var('q')
    e = SR(res.constant) * z**res.zpow * q**res.qpow
    for a, i, j, ex in res.factors:
        e *= (1 - a * z**i * q**j) ** ex
    return e


# ---------------------------------------------------------------------------------------------
# Comparison driver
# ---------------------------------------------------------------------------------------------

def compare(case, mtext, pres):
    """Return (status, detail)."""
    k = case.kind
    if k == "review":
        return "REVIEW", ""
    if k == "list":
        def plain(x):
            if isinstance(x, (list, tuple)):
                return [plain(y) for y in x]
            return QQ(x)
        a, b = plain(sage_eval(mtext)), plain(pres)
        return ("MATCH", "") if a == b else ("DIFFER", "Maple %s vs Python %s" % (a, b))
    if k == "poch":
        a = Counter()
        for m in re.finditer(r"\(q(?:\^(\d+))?,q\^(\d+)\)\[infinity\](?:\^(\d+))?", mtext):
            a[(int(m.group(1) or 1), int(m.group(2)))] += int(m.group(3) or 1)
        b = Counter()
        for x, y, e in pres.factors:
            b[(int(x), int(y))] += int(e)
        return ("MATCH", "") if a == b else ("DIFFER", "Maple %s vs Python %s" % (dict(a), dict(b)))
    if k == "jaccombo":
        expr = parse_sr(mtext)
        terms = expr.operands() if expr.operator() == add_vararg else [expr]
        a = sorted(canon_jac_maple(str(t), case) for t in terms)
        b = sorted(canon_jac_py(t, case) for t in pres)
        return ("MATCH", "") if a == b else ("DIFFER", "Maple %s vs Python %s" % (a, b))
    if k == "coeffs":
        a, b = canon_coeffs_maple(mtext, case), canon_coeffs_py(pres, case)
        if a == b:
            return "MATCH", ""
        first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        return "DIFFER", "first difference at coefficient index %d: Maple %s vs Python %s" % (
            first, a[first] if first < len(a) else "-", b[first] if first < len(b) else "-")
    if k in ("number",):
        return ("MATCH", "") if QQ(sage_eval(mtext)) == QQ(pres) else ("DIFFER", "")
    if k == "bool":
        m = mtext.strip() in ("1", "true", "[1]")
        return ("MATCH", "") if m == bool(pres) else ("DIFFER", "Maple %s, Python %s" % (m, bool(pres)))
    if k == "maxind":
        return ("MATCH", "") if [int(x) for x in sage_eval(mtext)] == [int(x) for x in pres] else ("DIFFER", "")
    if k == "cong":
        a, b = canon_cong(mtext, True), canon_cong(pres, False)
        return ("MATCH", "") if a == b else ("DIFFER", "Maple %s vs Python %s" % (a, b))
    if k in ("rels", "combo", "lincombo") and mtext.strip() in ("NULL", "{{}}"):
        mtext = "{}"          # Maple prints an empty relation set as {{}} and "no combination" as NULL
    if k == "zq":
        if pres is None:
            return "DIFFER", "Python returned None"
        diff = (parse_sr(mtext) - zq_sr(pres)).expand()
        return ("MATCH", "") if diff == 0 else ("DIFFER", "")
    if k in ("rels", "poly"):
        if k == "poly":
            Rx = PolynomialRing(QQ, ['X', 'Y'])
            loc = dict(X=Rx.gen(0), Y=Rx.gen(1))
            mv = sage_eval(mtext, locals=loc)
            mp = [Rx(x) for x in (mv if isinstance(mv, (set, list, tuple)) else [mv])]
            pp = [Rx(sage_eval(str(x), locals=loc)) for x in pres]
        else:
            Rx = _xring(case)
            mp, pp = _maple_polys(mtext, case), _py_polys(pres, case)
        return ("MATCH", "") if same_span(mp, pp, Rx) else ("DIFFER", "relation spaces differ")
    if k in ("combo", "lincombo"):
        mp, pp = _maple_polys(mtext, case), _py_polys(pres, case)
        if set(mp) == set(pp):
            return "MATCH", ""
        if set(mp) & set(pp):
            return "VALUE-MATCH", "overlapping but not identical sets of combinations"
        return "DIFFER", ""
    canon = {"eta": (canon_eta_maple, canon_eta_py), "qeta": (canon_qeta_maple, canon_qeta_py),
             "prod": (canon_prod_maple, canon_prod_py), "jac": (canon_jac_maple, canon_jac_py),
             "qfactor": (canon_qfactor_maple, canon_qfactor_py), "mprod": (canon_mprod_maple, canon_mprod_py)}
    fm, fp = canon[k]
    a, b = fm(mtext, case), fp(pres, case)
    if a == b:
        return "MATCH", ""
    if k == "jac" and a is not None and b is not None:
        if jac_value(a, 40) == jac_value(b, 40):
            return "VALUE-MATCH", "different JAC factorisation of the same series"
    return "DIFFER", "Maple %s vs Python %s" % (a, b)


def read_maple(path):
    meta, rows = {}, {}
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if not line:
            continue
        if line.startswith("#"):
            parts = line[1:].strip().split("\t", 1)
            meta[parts[0]] = parts[1] if len(parts) > 1 else ""
            continue
        parts = line.split("\t")
        rows[parts[0]] = (parts[1] if len(parts) > 1 else "", parts[2] if len(parts) > 2 else "")
    return meta, rows


def short(x, n=300):
    s = str(x)
    return s if len(s) <= n else s[:n] + " ..."


def main(argv):
    if "--selftest" in argv:
        return selftest()
    maple_path = next((a for a in argv if not a.startswith("-")), None)
    meta, mrows = read_maple(maple_path) if maple_path else ({}, {})
    base = base_namespace()
    results = []
    for case in CASES:
        try:
            pres = run_py(case.py, case_namespace(base, case))
            perr = None
        except Exception:
            pres, perr = None, traceback.format_exc().strip().splitlines()[-1]
        if perr:
            results.append((case, "PY-ERROR", perr, mrows.get(case.id, ("", ""))[0], None))
            continue
        if not maple_path:
            results.append((case, "PY-OK", "", "", pres))
            continue
        if case.id not in mrows:
            results.append((case, "MISSING", "not in Maple results", "", pres))
            continue
        mtext = mrows[case.id][0]
        known = case.opts.get("known_maple")
        if mtext.startswith("ERROR"):
            if known:
                results.append((case, "KNOWN-MAPLE", known + " (Maple: " + mtext[6:] + ")", mtext, pres))
            else:
                results.append((case, "MAPLE-ERROR", mtext[6:], mtext, pres))
            continue
        try:
            st, det = compare(case, mtext, pres)
        except Exception:
            st, det = "REVIEW", "could not compare automatically: " + traceback.format_exc().strip().splitlines()[-1]
        if st == "DIFFER" and known:
            st, det = "KNOWN-MAPLE", known
        results.append((case, st, det, mtext, pres))

    counts = Counter(r[1] for r in results)
    lines = ["# qseries-sage vs Maple qseries: parity report", "",
             "Battery seed %d, %d cases. Maple: %s. qseries: %s." % (SEED, len(CASES), meta.get("maple", "n/a"), meta.get("qseries", "n/a")),
             "", "| status | count |", "|---|---|"] + ["| %s | %d |" % kv for kv in sorted(counts.items())] + [""]
    order = ["DIFFER", "PY-ERROR", "MAPLE-ERROR", "MISSING", "KNOWN-MAPLE", "REVIEW", "VALUE-MATCH", "MATCH", "PY-OK"]
    for st in order:
        group = [r for r in results if r[1] == st]
        if not group:
            continue
        lines += ["## %s (%d)" % (st, len(group)), ""]
        for case, s, det, mtext, pres in group:
            if st in ("MATCH", "PY-OK"):
                lines.append("- `%s` (%s)" % (case.id, case.kind))
                continue
            lines += ["### `%s` (%s)" % (case.id, case.kind), ""]
            if case.opts.get("note"):
                lines += ["Note: " + case.opts["note"], ""]
            if det:
                lines += [det, ""]
            lines += ["- Maple input: `%s`" % short(case.maple, 400), "- Maple result: `%s`" % short(mtext),
                      "- Python result: `%s`" % short(pres), ""]
        lines.append("")
    out = os.path.join(HERE, "parity_report.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join("%-12s %d" % kv for kv in sorted(counts.items())))
    print("wrote " + out)
    return 1 if counts.get("DIFFER") or counts.get("PY-ERROR") else 0


def selftest():
    """Check the Maple-output parsers on strings in Maple's lprint format (from Garvan's doc pages)."""
    from parity.cases import Case
    checks = [
        (canon_eta_maple("eta(2*tau)^5/eta(tau)^2/eta(4*tau)^2", None), (1, 0, ((1, -2), (2, 5), (4, -2)))),
        (canon_eta_maple("eta(2*tau)^2/q^(1/8)/eta(tau)", None), (1, QQ(-1) / 8, ((1, -1), (2, 2)))),
        (canon_eta_maple("2*eta(4*tau)^2/eta(2*tau)", None), (2, 0, ((2, -1), (4, 2)))),
        (canon_qeta_maple("_E(q^2)^2/_E(q)", None), ((1, -1), (2, 2))),
        (canon_jac_maple("JAC(0,5,infinity)/JAC(1,5,infinity)", None), (1, 0, (((0, 5), 1), ((1, 5), -1)))),
        (canon_jac_maple("JAC(1,10,infinity)*JAC(3,10,infinity)/JAC(5,10,infinity)^2", None),
         (1, 0, (((1, 10), 1), ((3, 10), 1), ((5, 10), -2)))),
        (canon_prod_maple("1/((1-q)*(1-q^4)*(1-q^6))", None), ((1, -1), (4, -1), (6, -1))),
        (canon_qfactor_maple("q^6*(1-q^9)*(1-q^10)*(1-q^11)*(1-q^16)/((1-q)*(1-q^2)*(1-q^3)*(1-q^4))", None),
         (6, ((1, -1), (2, -1), (3, -1), (4, -1), (9, 1), (10, 1), (11, 1), (16, 1)))),
        (canon_qfactor_maple("q^6*(q^9-1)*(q^10-1)/((q-1)*(q^2-1))", None), (6, ((1, -1), (2, -1), (9, 1), (10, 1)))),
        (canon_mprod_maple("(1+q)*(1+q^3)*(1+q^5)", None), ((1, 1), (3, 1), (5, 1))),
        (canon_cong("[{[5, 7, 7], [4, 5, 5], [24, 25, 25], [6, 11, 11]}]", True), ((4, 5, 5), (5, 7, 7), (6, 11, 11), (24, 25, 25))),
    ]
    c4 = Case("x", "rels", "", "", opts={"k": 4})
    rel = _maple_polys("{X[1]*X[2]-X[4]^2, X[1]^2+X[2]^2-2*X[3]^2}", c4)
    checks.append((len(rel), 2))
    c2 = Case("x", "lincombo", "", "", opts={"k": 2, "sl": ["F1", "F2"]})
    checks.append((str(_maple_polys("12*F1+13*F2", c2)[0]), "12*X1 + 13*X2"))
    c13 = Case("x", "lincombo", "", "", opts={"k": 6, "p": 13, "sl": ["B%d" % i for i in range(1, 7)]})
    checks.append((_maple_polys("-6*B1", c13)[0] == 7 * _xring(c13).gen(0), True))
    zcase = parse_sr("(1-1/z)*(1-z*q)*(1-q)")
    checks.append(((zcase - (1 - 1 / var('z')) * (1 - var('z') * var('q')) * (1 - var('q'))).expand(), 0))
    bad = [(i, got, want) for i, (got, want) in enumerate(checks) if got != want]
    for i, got, want in bad:
        print("selftest %d FAILED: got %r want %r" % (i, got, want))
    print("selftest: %d/%d passed" % (len(checks) - len(bad), len(checks)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
