"""
docs/make_tutorial.py -- build docs/tutorial.md by running every example with the installed code.

Usage (repo root):   sage -python docs/make_tutorial.py
Writes docs/tutorial.md. Each example's printed output and final value are captured, so the
document always shows what this version of qseries-sage actually returns. Examples follow the
sections of F. G. Garvan, "A q-product tutorial for a q-series MAPLE package" (arXiv:math/9812092);
where the tutorial or a doc page states Maple's answer, it is quoted for comparison.
Exit status is 1 if any example raises, so this can also run in CI.
"""
import ast, contextlib, io, os, sys, time, traceback

sys.path.insert(0, os.getcwd())
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tutorial.md")
MAXLEN = 1500

SETUP = '''
from sage.all import QQ, LaurentSeriesRing, LaurentPolynomialRing, PolynomialRing, kronecker, sigma
from qseries import *

R = LaurentSeriesRing(QQ, 'q', default_prec=1010)
q = R.gen()

def head(f, n=15):
    """First n terms of a QSeries (for display); the q^r prefactor is shown when r != 0."""
    s = f.series
    s = s.add_bigoh(s.valuation() + n) if s != 0 else s
    return "q^(%s) * (%s)" % (f.r, s) if f.r else s
'''

SECTIONS = [
    ("Setup", None, [
        ("Every example below starts from a Laurent series ring in `q` over the rationals. Series are "
         "`QSeries` objects: a Sage series plus its truncation order `T` and a rational shift `r` "
         "(the series is `q^r * series`). `head(f)` prints just the first terms.",
         SETUP, None),
    ]),

    ("1. Basic functions", "Tutorial section 2", [
        ("Finite q-products: `aqprod(a, q, n)` = (a;q)_n and the Gaussian polynomial `qbin(q, m, n)`.",
         "aqprod(q, q, 5)", None),
        (None, "qbin(q, 2, 4)", None),
        ("`etaq(q, k, T)` is the eta product prod_{n>=1} (1 - q^{kn}) to O(q^T), without the q^(k/24) factor.",
         "head(etaq(q, 1, 100), 20)", "Euler's pentagonal number theorem: 1 - q - q^2 + q^5 + q^7 - q^12 - q^15 + ..."),
        ("Theta functions. `theta2` carries the `q^(1/4)` prefactor in its shift `r`.",
         "head(theta3(q, 100)), head(theta4(q, 100)), head(theta2(q, 100))", None),
        ("Jacobi's triple product: `tripleprod(q, q^3, T)` is Euler's pentagonal series again (tutorial section 6.1).",
         "(tripleprod(q, q**3, 10).series - etaq(q, 1, 100).series).add_bigoh(100) == 0", "true"),
    ]),

    ("2. prodmake: Andrews' algorithm", "Tutorial section 3.1", [
        ("The left side of the first Rogers-Ramanujan identity, summed to n = 8 (accurate to well past q^40):",
         "x = sum(q**(n*n) / aqprod(q, q, n).series for n in range(9))\n"
         "x = QSeries(x.add_bigoh(50), T=50)\n"
         "head(x, 20)", None),
        ("`prodmake` recovers the infinite product. The exponents are -1 exactly at n = 1, 4 (mod 5): "
         "the Rogers-Ramanujan identity.",
         "p = prodmake(x, q, 40)\n"
         "sorted(n for n, e in p.exponents.items() if e != 0) == [n for n in range(1, 40) if n % 5 in (1, 4)]",
         "1 / ((1-q)(1-q^4)(1-q^6)(1-q^9)...), i.e. exponents at n = +-1 (mod 5)"),
        (None, "p", None),
        ("The same series as a theta-function product (tutorial section 3.4):",
         "jacprodmake(x, q, 40)", "JAC(0,5,infinity) / JAC(1,5,infinity)"),
    ]),

    ("3. Eta-products", "Tutorial section 3.2; etamake and qetamake doc pages", [
        (None, "etamake(theta3(q, 100), q, 100)", "eta(2 tau)^5 / (eta(tau)^2 eta(4 tau)^2)"),
        (None, "etamake(theta4(q, 100), q, 100)", "eta(tau)^2 / eta(2 tau)"),
        (None, "etamake(theta2(q, 100), q, 100)", "2 eta(4 tau)^2 / eta(2 tau)"),
        ("The triangular-number series sum q^(n(n+1)/2) in `_E(q^m) = (q^m;q^m)_inf` form:",
         "qetamake(etaq(q, 2, 30)**2 / etaq(q, 1, 30), q, 30)", "_E(q^2)^2 / _E(q)"),
    ]),

    ("4. Finite products and other product forms", "Tutorial section 3.3; qfactor, mprodmake doc pages", [
        ("`qfactor` factors a rational function into (1 - q^i) terms. Pass numerator and denominator "
         "separately so Sage does not cancel them first.",
         "P = PolynomialRing(QQ, 'q'); t = P.gen()\n"
         "num = t**6 * (1 - t**9) * (1 - t**10) * (1 - t**11) * (1 - t**16)\n"
         "den = (1 - t) * (1 - t**2) * (1 - t**3) * (1 - t**4)\n"
         "qfactor((num, den), 20)",
         "q^6 (1-q^9)(1-q^10)(1-q^11)(1-q^16) / ((1-q)(1-q^2)(1-q^3)(1-q^4))"),
        ("`mprodmake` writes a series as a product (1 + q^n1)(1 + q^n2)...:",
         "EP = etaq(q, 2, 18)**2 * etaq(q, 4, 18)**(-1) * etaq(q, 1, 18)**(-1)\n"
         "mprodmake(EP, q, 17)", "(1+q)(1+q^3)(1+q^5)...(1+q^17)"),
        ("`zqfactor` does the same for series in two variables z and q (zqfactor doc page). "
         "The example is Jacobi's triple product in disguise:",
         "Lz = LaurentPolynomialRing(QQ, 'z'); z = Lz.gen()\n"
         "Rz = LaurentSeriesRing(Lz, 'q'); qz = Rz.gen()\n"
         "g = tripleprod(-z**2 * qz**3, qz**4, 20) - tripleprod(-z**2 * qz, qz**4, 20) / z\n"
         "zqfactor(g, z, qz, 10)",
         "(1-1/z)(1-zq)(1-q)(1-q/z)(1-zq^2)(1-q^2)(1-q^2/z)(1-zq^3)(1-q^3)"),
    ]),

    ("5. Relations between q-series", "Tutorial section 4", [
        ("`findhom` finds homogeneous polynomial relations of a given degree (section 4.1). "
         "There are no linear relations among these four theta functions, and two quadratic ones:",
         "L = [theta3(q, 100), theta4(q, 100), theta3(q**2, 100), theta4(q**2, 100)]\n"
         "findhom(L, q, 1, 0), findhom(L, q, 2, 0)",
         "{} and {X1^2 + X2^2 - 2 X3^2, X1 X2 - X4^2}"),
        ("`findhomcombo` writes one series as a polynomial in others (section 4.2): the Eisenstein "
         "series U_{5,6} in terms of two eta-quotients.",
         "def UE(q, k, p, trunk):\n"
         "    x = sum(kronecker(m, p) * n**(k - 1) * q**(m * n)\n"
         "            for m in range(1, trunk + 1) for n in range(1, trunk // m + 1))\n"
         "    return QSeries(q.parent()(x).add_bigoh(trunk + 1), T=trunk + 1)\n"
         "B1 = etaq(q, 1, 50)**5 / etaq(q, 5, 50)\n"
         "B2 = QSeries(q * etaq(q, 5, 50).series**5 / etaq(q, 1, 50).series, 50)\n"
         "findhomcombo(UE(q, 6, 5, 50), [B1, B2], q, 3, 0)",
         "X1^2 X2 + 40 X1 X2^2 + 335 X2^3"),
        ("`findnonhomcombo` allows all degrees up to n (section 4.4): Watson's modular equation for 7, "
         "with xi = eta(49 tau)/eta(tau) and T = (eta(7 tau)/eta(tau))^4. (T^2 itself is one of the "
         "monomials, so the trivial answer X1^2 is returned as well.)",
         "E1 = etaq(q, 1, 100).series\n"
         "xi = QSeries(q**2 * etaq(q, 49, 100).series / E1, 100)\n"
         "T7 = QSeries(q * etaq(q, 7, 100).series**4 / E1**4, 100)\n"
         "findnonhomcombo(T7**2, [T7, xi], q, 7, -15)",
         "(35 xi^2 + 49 xi^3 + 7 xi) T + 343 xi^7 + 343 xi^6 + 147 xi^5 + 49 xi^4 + 21 xi^3 + 7 xi^2 + xi"),
        ("`findpoly` finds a polynomial relation between two series (section 4.5), here the Borweins' "
         "cubic theta functions:",
         "x = theta2(q, 100)**2 / theta2(q**3, 40)**2 + theta3(q, 100)**2 / theta3(q**3, 40)**2\n"
         "a = theta3(q, 100) * theta3(q**3, 40) + theta2(q, 100) * theta2(q**3, 40)\n"
         "c = QSeries(3 * etaq(q, 3, 100).series**3 / etaq(q, 1, 100).series, 100, r=QQ('1/3'))\n"
         "y = c**3 / a**3\n"
         "rels = findpoly(x, y, q, 3, 1, 60)\n"
         "X, Y = next(iter(rels)).parent().gens()\n"
         "rels, [rel / rel.lc() == (X + 6)**3 * Y - 27 * (X + 2)**2 for rel in rels]",
         "(X + 6)^3 Y - 27 (X + 2)^2"),
    ]),

    ("6. Sifting and dissections", "Tutorial section 6.2; sift doc page", [
        ("`sift` keeps the terms whose exponent is in a fixed class mod n: the 5-dissection component "
         "E0 of Euler's product.",
         "E0 = sift(etaq(q, 1, 500), q, 5, 0, 499)\n"
         "head(E0, 12)", None),
        (None, "jacprodmake(E0, q, 50)", None),
    ]),

    ("7. Congruences", "Tutorial section 7; findcong doc page", [
        ("`findcong` searches for congruences a(An + B) = 0 (mod M) in the coefficients. For the "
         "partition function it finds Ramanujan's congruences (returned as (B, A, M)):",
         "Pn = QSeries(etaq(q, 1, 1001).series.__invert__(), 1001)\n"
         "sorted(findcong(Pn, 1000))",
         "[4, 5, 5], [5, 7, 7], [6, 11, 11] and [24, 25, 25]"),
        ("`checkmult` tests multiplicativity: Ramanujan's tau function, from Delta = q (q;q)_inf^24.",
         "checkmult(q * etaq(q, 1, 60)**24, 59)", "1 (multiplicative)"),
    ]),

    ("8. Relations mod p", "findlincombomodp doc page", [
        ("The mod-p variants work over GF(p). The doc-page example writes a sifted series mod 13 in "
         "terms of six eta/Eisenstein products:",
         "E4 = QSeries(R(1 + 240 * sum(sigma(n, 3) * q**n for n in range(1, 300))).add_bigoh(300), 300)\n"
         "E6 = QSeries(R(1 - 504 * sum(sigma(n, 5) * q**n for n in range(1, 300))).add_bigoh(300), 300)\n"
         "ETA1 = etaq(q, 1, 300)\n"
         "F1 = sift(E4**16 * E6 * QSeries(ETA1.series.__invert__(), 300), q, 13, 6, 299)\n"
         "BB13 = [ETA1**11 * E6 * E4**(3 * j + 1) for j in range(6)]\n"
         "findlincombomodp(F1, BB13, None, 13, q, -8)",
         "-6 _ETA1^11 _E6 _E4   (i.e. -6 X1 mod 13), with 'nx = , 6' and '# of terms , 19'"),
        ("E4 = 1 (mod 5) because 240 is divisible by 5, so `findhommodp` finds a relation that does "
         "not exist over the rationals:",
         "one = QSeries(R(1).add_bigoh(300), 300)\n"
         "findhommodp([E4, E6, one], 5, q, 1, 0), findhom([E4, E6, one], q, 1, 0)", None),
    ]),
]


def run(code, ns):
    """Exec all statements; return (stdout, repr of the final expression or None, seconds)."""
    tree = ast.parse(code)
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    buf = io.StringIO()
    t0 = time.time()
    with contextlib.redirect_stdout(buf):
        exec(compile(tree, "<example>", "exec"), ns)
        value = eval(compile(ast.Expression(last.value), "<example>", "eval"), ns) if last else None
    out = buf.getvalue()
    return out, (None if last is None else repr(value)), time.time() - t0


def clip(s):
    return s if len(s) <= MAXLEN else s[:MAXLEN] + " ... [truncated]"


def main():
    ns = {}
    md = ["# qseries-sage tutorial", "",
          "Worked examples following F. G. Garvan, *A q-product tutorial for a q-series MAPLE package* "
          "(Seminaire Lotharingien de Combinatoire 42, 1999; arXiv:math/9812092), run with qseries-sage. "
          "Outputs are produced by `docs/make_tutorial.py`; where the tutorial or a Garvan doc page "
          "gives Maple's answer it is shown as **Maple** for comparison.", ""]
    failures = 0
    for title, source, examples in SECTIONS:
        md += ["## " + title, ""]
        if source:
            md += ["*Source: %s.*" % source, ""]
        for text, code, maple in examples:
            if text:
                md += [text, ""]
            md += ["```python", code.strip("\n"), "```", ""]
            try:
                out, val, secs = run(code, ns)
                shown = "\n".join(x for x in [out.rstrip("\n"), val] if x)
                if shown:
                    md += ["Output:", "", "```", clip(shown), "```", ""]
                status = "ok   %5.1fs" % secs
            except Exception:
                failures += 1
                exc = sys.exc_info()[1]
                err = "".join(traceback.format_exception_only(type(exc), exc)).strip()
                md += ["**This example raised an error in this version:**", "", "```", clip(err), "```", ""]
                status = "FAIL"
                print("--- failing example:\n" + code + "\n" + traceback.format_exc())
            if maple:
                md += ["**Maple:** " + maple, ""]
            print("%s  %s" % (status, (code.strip().splitlines() or [""])[-1][:70]))
    open(OUT, "w", encoding="utf-8").write("\n".join(md))
    print("\nwrote %s (%d example(s) failed)" % (OUT, failures))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
