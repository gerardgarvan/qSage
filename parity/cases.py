"""
parity/cases.py -- the Maple-parity test battery (single source of truth).

Each Case gives the same computation in Maple (run by parity/make_maple.py -> qseries_battery.mpl)
and in Python (run by parity/compare.py), plus a `kind` that tells compare.py how to normalise and
compare the two results. Random cases use a fixed seed, so the battery is reproducible.
"""
import random
from dataclasses import dataclass, field

SEED = 20261106


@dataclass
class Case:
    id: str
    kind: str          # coeffs | eta | qeta | prod | jac | qfactor | mprod | rels | combo | lincombo |
                       # poly | cong | maxind | bool | number | zq | review
    maple: str         # Maple expression whose value is written to the results file
    py: str            # Python code; the value of its last expression is compared
    maple_setup: str = ""   # Maple statements run first (inside the same try block)
    opts: dict = field(default_factory=dict)   # k (number of X vars), p (prime), sl (names), vars


# Maple helpers loaded at the top of the battery (mirrored in compare.py's Python namespace).
MAPLE_PRELUDE = r"""
S := proc(f, T) convert(series(f, q, T), polynom) end proc:
CL := proc(f, a, b) local g, i; g := expand(f); [seq(coeff(g, q, i), i = a .. b)] end proc:
POCH := proc(a, b, T) local k; mul(1 - q^(a + b*k), k = 0 .. floor((T - 1 - a)/b)) end proc:
JS := proc(a, b, T) if a = 0 then POCH(b, b, T) else POCH(a, b, T)*POCH(b - a, b, T)*POCH(b, b, T) end if end proc:
E4S := proc(T) local n; 1 + 240*add(numtheory[sigma][3](n)*q^n, n = 1 .. T - 1) end proc:
E6S := proc(T) local n; 1 - 504*add(numtheory[sigma][5](n)*q^n, n = 1 .. T - 1) end proc:
UE := proc(k, p, T) local m, n; add(add(numtheory[jacobi](m, p)*n^(k - 1)*q^(m*n), n = 1 .. floor(T/m)), m = 1 .. T) end proc:
"""


def _etaprod_maple(fs, T):
    return "*".join("etaq(q,%d,%d)^(%d)" % (k, T, e) for k, e in fs)


def _etaprod_py(fs, T):
    return "*".join("etaq(q,%d,%d)**(%d)" % (k, T, e) for k, e in fs)


def build_cases():
    rnd = random.Random(SEED)
    C = []
    add = C.append

    # ---------------------------------------------------------------- building blocks (coefficients)
    add(Case("aqprod_1", "coeffs", "CL(aqprod(q,q,5),0,15)", "CL(aqprod(q,q,5),0,15)"))
    add(Case("aqprod_2", "coeffs", "CL(aqprod(q^2,q^3,4),0,25)", "CL(aqprod(q**2,q**3,4),0,25)"))
    add(Case("qbin_1", "coeffs", "CL(qbin(q,3,6),0,9)", "CL(qbin(q,3,6),0,9)"))
    add(Case("qbin_2", "coeffs", "CL(qbin(q,2,7),0,10)", "CL(qbin(q,2,7),0,10)"))
    add(Case("qbin_3", "coeffs", "CL(qbin(q,0,5),0,3)", "CL(qbin(q,0,5),0,3)"))
    for k in (1, 3, 7):
        add(Case("etaq_%d" % k, "coeffs", "CL(etaq(q,%d,60),0,59)" % k, "CL(etaq(q,%d,60),0,59)" % k))
    add(Case("theta3_1", "coeffs", "CL(theta3(q,50),0,49)", "CL(theta3(q,50),0,49)"))
    add(Case("theta4_1", "coeffs", "CL(theta4(q,50),0,49)", "CL(theta4(q,50),0,49)"))
    add(Case("theta2_1", "coeffs", "CL(expand(theta2(q,10)/q^(1/4)),0,29)", "CL(theta2(q,10),0,29)",
             opts={"note": "Maple theta2(q,T) sums finitely many terms; compare only q^0..q^29"}))
    add(Case("theta2_q3", "coeffs", "CL(expand(simplify(theta2(q^3,10)/q^(3/4))),0,40)", "CL(theta2(q**3,10),0,40)"))
    add(Case("theta_z", "coeffs", "CL(theta(z,q,4),0,16)", "CL(theta(z,q,4),0,16)", opts={"vars": "z"}))
    add(Case("tripleprod_z", "coeffs", "CL(tripleprod(z,q,6),0,10)", "CL(tripleprod(z,q,6),0,10)", opts={"vars": "z"}))
    add(Case("tripleprod_q", "coeffs", "CL(tripleprod(q,q^3,10),0,49)", "CL(tripleprod(q,q**3,10),0,49)"))
    add(Case("quinprod_z", "coeffs", "CL(quinprod(z,q,3),0,26)", "CL(quinprod(z,q,3),0,26)", opts={"vars": "z"}))
    add(Case("winquist_ab", "coeffs", "CL(convert(series(winquist(a,b,q,12),q,12),polynom),0,11)",
             "CL(winquist(a,b,q,12),0,11)", opts={"vars": "a,b"}))
    add(Case("winquist_doc", "coeffs",
             "CL(subs(a=1,b=1,normal(convert(series(winquist(a,b,q,30)/(1-a)/(1-b)/(1-a*b)/(1-a/b),q,30),polynom))),0,29)",
             "CL(etaq(q,1,40)**10,0,29)",
             opts={"note": "doc page: Winquist / ((1-a)(1-b)(1-ab)(1-a/b)) at a=b=1 equals (q;q)^10"}))
    for a, b in [(1, 5), (2, 7), (3, 8)]:
        add(Case("jacprod_%d_%d" % (a, b), "coeffs", "CL(S(jacprod(%d,%d,q,40),40),0,39)" % (a, b),
                 "CL(jacprod(%d,%d,q,40),0,39)" % (a, b)))
    add(Case("jac2series_doc1", "coeffs", "CL(q^4*jac2series(JAC(-4,5,infinity),20),0,15)",
             "CL(q**4*LQ(jac2series(JacProduct(factors=[(-4,5,1)]),20)),0,15)"))
    add(Case("jac2series_doc2", "coeffs", "CL(q*jac2series(JAC(6,5,infinity),20),0,18)",
             "CL(q*LQ(jac2series(JacProduct(factors=[(6,5,1)]),20)),0,18)"))
    add(Case("jac2series_doc3", "coeffs", "CL(jac2series(JAC(0,10,infinity),50),0,49)",
             "CL(jac2series(JacProduct(factors=[(0,10,1)]),50),0,49)"))
    add(Case("jac2series_ratio", "coeffs",
             "CL(S(jac2series(JAC(1,10,infinity)*JAC(3,10,infinity)/JAC(5,10,infinity)^2,40),40),0,39)",
             "CL(jac2series(JacProduct(factors=[(1,10,1),(3,10,1),(5,10,-2)]),40),0,39)"))
    add(Case("jac2prod_1", "review", "jac2prod(JAC(1,5,infinity))", "jac2prod(JacProduct(factors=[(1,5,1)]))"))
    add(Case("jac2prod_2", "review", "jac2prod(JAC(0,10,infinity)*JAC(2,10,infinity)^2)",
             "jac2prod(JacProduct(factors=[(0,10,1),(2,10,2)]))"))

    # ---------------------------------------------------------------- utilities
    add(Case("qdegree_1", "number", "qdegree(S(etaq(q,1,30),30))", "qdegree(etaq(q,1,30))"))
    add(Case("lqdegree_1", "number", "lqdegree(expand(q^3*S(etaq(q,1,30),30)))", "lqdegree(QSeries(q**3*etaq(q,1,30).series,33))"))
    for n, k in [(5, 0), (5, 4), (7, 5), (11, 6), (3, 1), (2, 1)]:
        add(Case("sift_P_%d_%d" % (n, k), "coeffs",
                 "CL(sift(S(1/etaq(q,1,400),400),q,%d,%d,399),0,19)" % (n, k),
                 "CL(sift(QSeries(etaq(q,1,400).series.__invert__(),400),q,%d,%d,399),0,19)" % (n, k)))
    add(Case("sift_E_5_0", "coeffs", "CL(sift(etaq(q,1,500),q,5,0,499),0,30)",
             "CL(sift(etaq(q,1,500),q,5,0,499),0,30)"))
    add(Case("checkmult_doc_S1", "bool",
             "checkmult(S(etaq(q,3,201)^3*etaq(q,5,201)^3*q+etaq(q,1,201)^3*etaq(q,15,201)^3*q^2,200),199)",
             "checkmult(QSeries(q*etaq(q,3,201).series**3*etaq(q,5,201).series**3+q**2*etaq(q,1,201).series**3*etaq(q,15,201).series**3,200),199)",
             opts={"note": "doc page: eta(3t)^3 eta(5t)^3 + eta(t)^3 eta(15t)^3 is multiplicative"}))
    add(Case("checkmult_doc_S3", "bool",
             "checkmult(S(q*etaq(q,3,201)^3*etaq(q,5,201)^3,200),199)",
             "checkmult(QSeries((q*etaq(q,3,201).series**3*etaq(q,5,201).series**3).add_bigoh(200),200),199)",
             opts={"note": "doc page: eta(3t)^3 eta(5t)^3 alone is not multiplicative"}))
    add(Case("checkmult_delta", "bool", "checkmult(S(q*etaq(q,1,100)^24,100),99)",
             "checkmult(QSeries((q*etaq(q,1,100).series**24).add_bigoh(100),100),99)"))

    # ---------------------------------------------------------------- product conversion
    add(Case("prodmake_tripleprod", "prod", "prodmake(tripleprod(q,q^5,30),q,50)",
             "prodmake(QSeries(tripleprod(q,q**5,30).series.add_bigoh(60),60),q,50)"))
    add(Case("prodmake_RR", "prod",
             "prodmake(S(add(q^(n^2)/aqprod(q,q,n),n=0..8),50),q,40)",
             "prodmake(QSeries(sum(q**(n*n)/aqprod(q,q,n).series for n in range(9)).add_bigoh(50),50),q,40)"))
    for i in range(10):
        ns = sorted(rnd.sample(range(1, 21), rnd.randint(2, 5)))
        es = [rnd.choice([-2, -1, 1, 2]) for _ in ns]
        mp = "*".join("(1-q^%d)^(%d)" % (n, e) for n, e in zip(ns, es))
        pp = "*".join("(1-q**%d)**(%d)" % (n, e) for n, e in zip(ns, es))
        add(Case("prodmake_rand_%d" % i, "prod", "prodmake(S(%s,40),q,40)" % mp,
                 "prodmake(QSeries(R(%s).add_bigoh(40),40),q,40)" % pp))

    for name in ("theta3", "theta4", "theta2"):
        add(Case("etamake_%s" % name, "eta", "etamake(%s(q,100),q,100)" % name, "etamake(%s(q,100),q,100)" % name))
    add(Case("etamake_triangular", "eta", "etamake(add(q^(n*(n+1)/2),n=0..20),q,20)",
             "etamake(QSeries(R(sum(q**(n*(n+1)//2) for n in range(21))).add_bigoh(200),200),q,20)"))
    levels = [1, 2, 3, 4, 5, 6, 8, 9, 12]
    for i in range(12):
        ks = sorted(rnd.sample(levels, rnd.randint(2, 3)))
        fs = [(k, rnd.choice([-3, -2, -1, 1, 2, 3])) for k in ks]
        add(Case("etamake_rand_%d" % i, "eta", "etamake(S(%s,60),q,50)" % _etaprod_maple(fs, 60),
                 "etamake(%s,q,50)" % _etaprod_py(fs, 60)))
        if i < 6:
            add(Case("qetamake_rand_%d" % i, "qeta", "qetamake(S(%s,60),q,50)" % _etaprod_maple(fs, 60),
                     "qetamake(%s,q,50)" % _etaprod_py(fs, 60)))
    add(Case("qetamake_triangular", "qeta", "qetamake(add(q^(n*(n+1)/2),n=0..20),q,20)",
             "qetamake(QSeries(R(sum(q**(n*(n+1)//2) for n in range(21))).add_bigoh(200),200),q,20)"))

    add(Case("jacprodmake_tripleprod", "jac", "jacprodmake(tripleprod(q,q^5,10),q,50)",
             "jacprodmake(QSeries(tripleprod(q,q**5,10).series.add_bigoh(60),60),q,50)"))
    add(Case("jacprodmake_RR", "jac", "jacprodmake(S(add(q^(n^2)/aqprod(q,q,n),n=0..8),50),q,40)",
             "jacprodmake(QSeries(sum(q**(n*n)/aqprod(q,q,n).series for n in range(9)).add_bigoh(50),50),q,40)"))
    add(Case("jacprodmake_E0", "jac", "jacprodmake(sift(etaq(q,1,500),q,5,0,499),q,50)",
             "jacprodmake(sift(etaq(q,1,500),q,5,0,499),q,50)"))
    add(Case("jacprodmake_theta3", "jac", "jacprodmake(theta3(q,100),q,60)", "jacprodmake(theta3(q,100),q,60)"))
    add(Case("jacprodmake_doc_XX", "jac",
             "jacprodmake(S((1-theta4(q,60)^2/theta4(q^5,12)^2)/4/q,60),q,50)",
             "jacprodmake(QSeries(((1-theta4(q,60).series**2/theta4(q**5,12).series**2)/4/q).add_bigoh(60),60),q,50)",
             opts={"note": "jac2series doc page: JAC(1,10) JAC(3,10) / JAC(5,10)^2"}))
    for i in range(8):
        b = rnd.choice([5, 7, 8, 10, 12])
        As = sorted(rnd.sample(range(1, b // 2 + 1), rnd.randint(1, 2)))
        fs = [(a, rnd.choice([-1, 1])) for a in As]
        if rnd.random() < 0.5:
            fs.append((0, rnd.choice([-1, 1])))
        mp = "*".join("JS(%d,%d,60)^(%d)" % (a, b, e) for a, e in fs)
        pp = "*".join("JS(%d,%d,60)**(%d)" % (a, b, e) for a, e in fs)
        add(Case("jacprodmake_rand_%d" % i, "jac", "jacprodmake(S(%s,60),q,50)" % mp,
                 "jacprodmake(QSeries((%s).add_bigoh(60),60),q,50)" % pp))

    add(Case("qfactor_t8", "qfactor",
             "qfactor(q^6*(1-q^9)*(1-q^10)*(1-q^11)*(1-q^16)/((1-q)*(1-q^2)*(1-q^3)*(1-q^4)),20)",
             "qfactor((t**6*(1-t**9)*(1-t**10)*(1-t**11)*(1-t**16), (1-t)*(1-t**2)*(1-t**3)*(1-t**4)), 20)"))
    for i in range(6):
        ks = rnd.sample(range(1, 13), rnd.randint(4, 7))
        nk, dk = sorted(ks[: len(ks) // 2]), sorted(ks[len(ks) // 2:])
        r0 = rnd.randint(0, 4)
        mnum = "q^%d*%s" % (r0, "*".join("(1-q^%d)" % k for k in nk))
        mden = "*".join("(1-q^%d)" % k for k in dk)
        pnum = "t**%d*%s" % (r0, "*".join("(1-t**%d)" % k for k in nk))
        pden = "*".join("(1-t**%d)" % k for k in dk)
        add(Case("qfactor_rand_%d" % i, "qfactor", "qfactor(expand(%s)/expand(%s),40)" % (mnum, mden),
                 "qfactor((P(%s), P(%s)), 40)" % (pnum, pden)))

    add(Case("mprodmake_doc", "mprod", "mprodmake(S(etaq(q,2,100)^2/etaq(q,4,100)/etaq(q,1,100),100),q,17)",
             "mprodmake(etaq(q,2,100)**2*etaq(q,4,100)**(-1)*etaq(q,1,100)**(-1),q,17)"))
    for i in range(4):
        ns = sorted(rnd.sample(range(1, 16), rnd.randint(3, 6)))
        mp = "*".join("(1+q^%d)" % n for n in ns)
        pp = "*".join("(1+q**%d)" % n for n in ns)
        add(Case("mprodmake_rand_%d" % i, "mprod", "mprodmake(S(%s,30),q,20)" % mp,
                 "mprodmake(QSeries(R(%s).add_bigoh(30),30),q,20)" % pp))

    add(Case("zqfactor_doc", "zq", "zqfactor(tripleprod(-z^2*q^3,q^4,20)-tripleprod(-z^2*q,q^4,20)/z,z,q,10)",
             "zqfactor(tripleprod(-z**2*q**3,q**4,20)-tripleprod(-z**2*q,q**4,20)/z,z,q,10)", opts={"vars": "z"}))
    add(Case("zqfactor_plus", "zq", "zqfactor(S(mul(1+z*q^n,n=1..12),13),z,q,12)",
             "zqfactor(QSeries(prod(1+z*q**n for n in range(1,13)).add_bigoh(13),13),z,q,12)", opts={"vars": "z"}))
    add(Case("findprod_1", "review", "findprod([etaq(q,1,30),etaq(q,2,30)],1,3,20)",
             "findprod([etaq(q,1,30),etaq(q,2,30)],1,3,20)"))
    add(Case("qs2jaccombo_1", "review", "qs2jaccombo(theta3(q,40)+theta4(q,40),q,40)",
             "qs2jaccombo([theta3(q,40),theta4(q,40)],q,40)"))
    add(Case("checkprod_1", "review", "checkprod(S(etaq(q,1,30),30),2,30)", "checkprod(etaq(q,1,30),2,30)"))

    # ---------------------------------------------------------------- relations over QQ
    TH = ("theta3(q,100),theta4(q,100),theta3(q^2,100),theta4(q^2,100)",
          "theta3(q,100),theta4(q,100),theta3(q**2,100),theta4(q**2,100)")
    for n in (1, 2, 3):
        add(Case("findhom_theta_%d" % n, "rels", "findhom([%s],q,%d,0)" % (TH[0], n),
                 "findhom([%s],q,%d,0)" % (TH[1], n), opts={"k": 4}))
    add(Case("findnonhom_theta", "rels",
             "findnonhom([theta3(q,100),theta4(q,100),theta3(q^4,100)],q,3,20)",
             "findnonhom([theta3(q,100),theta4(q,100),theta3(q**4,100)],q,3,20)", opts={"k": 3}))
    B12 = ("[etaq(q,1,60)^5/etaq(q,5,60),S(q*etaq(q,5,60)^5/etaq(q,1,60),60)]",
           "[etaq(q,1,60)**5/etaq(q,5,60),QSeries(q*etaq(q,5,60).series**5/etaq(q,1,60).series,60)]")
    add(Case("findhomcombo_doc", "combo", "findhomcombo(S(UE(6,5,60),60),%s,q,3,0,no)" % B12[0],
             "findhomcombo(UE(q,6,5,60),%s,q,3,0,'no')" % B12[1], opts={"k": 2}))
    add(Case("findhomcombo_doc2", "combo",
             "findhomcombo(S(q*etaq(q,5,60)^5/etaq(q,1,60),60),%s,q,1,0,no)" % B12[0],
             "findhomcombo(QSeries(q*etaq(q,5,60).series**5/etaq(q,1,60).series,60),%s,q,1,0,'no')" % B12[1], opts={"k": 2}))
    add(Case("findnonhomcombo_watson", "combo",
             "findnonhomcombo(S(q^2*etaq(q,7,100)^8/etaq(q,1,100)^8,100),[S(q*etaq(q,7,100)^4/etaq(q,1,100)^4,100),S(q^2*etaq(q,49,100)/etaq(q,1,100),100)],q,7,-15)",
             "findnonhomcombo(QSeries(q**2*etaq(q,7,100).series**8/etaq(q,1,100).series**8,100),[QSeries(q*etaq(q,7,100).series**4/etaq(q,1,100).series**4,100),QSeries(q**2*etaq(q,49,100).series/etaq(q,1,100).series,100)],q,7,-15)",
             opts={"k": 2}))
    add(Case("findlincombo_doc", "lincombo", "findlincombo(12*(1+q+q^3)+13*(1+q-q^3-q^5-q^7),[1+q+q^3,1+q-q^3-q^5-q^7],[F1,F2],q,0)",
             "findlincombo(QSeries(R(12*(1+q+q**3)+13*(1+q-q**3-q**5-q**7)).add_bigoh(40),40),[QSeries(R(1+q+q**3).add_bigoh(40),40),QSeries(R(1+q-q**3-q**5-q**7).add_bigoh(40),40)],['F1','F2'],q,0)",
             opts={"k": 2, "sl": ["F1", "F2"]}))
    add(Case("findlincombo_doc_none", "lincombo",
             "findlincombo(12*(1+q+q^3)+13*(1+q-q^3-q^5-q^7),[1+q+q^3,1+q-q^3-q^5-q^7+q],[F1,F2],q,0)",
             "findlincombo(QSeries(R(12*(1+q+q**3)+13*(1+q-q**3-q**5-q**7)).add_bigoh(40),40),[QSeries(R(1+q+q**3).add_bigoh(40),40),QSeries(R(1+q-q**3-q**5-q**7+q).add_bigoh(40),40)],['F1','F2'],q,0)",
             opts={"k": 2, "sl": ["F1", "F2"]}))
    for i in range(5):
        basis = []
        for _ in range(3):
            ks = sorted(rnd.sample([1, 2, 3, 4, 6], 2))
            basis.append([(k, rnd.choice([-2, -1, 1, 2])) for k in ks])
        cs = [rnd.randint(-5, 5) or 1 for _ in basis]
        mL = ",".join("S(%s,60)" % _etaprod_maple(fs, 60) for fs in basis)
        pL = ",".join(_etaprod_py(fs, 60) for fs in basis)
        mf = "+".join("(%d)*S(%s,60)" % (c, _etaprod_maple(fs, 60)) for c, fs in zip(cs, basis))
        pf = "+".join("(%d)*(%s)" % (c, _etaprod_py(fs, 60)) for c, fs in zip(cs, basis))
        add(Case("findlincombo_rand_%d" % i, "lincombo", "findlincombo(expand(%s),[%s],[F1,F2,F3],q,0)" % (mf, mL),
                 "findlincombo(%s,[%s],['F1','F2','F3'],q,0)" % (pf, pL), opts={"k": 3, "sl": ["F1", "F2", "F3"]}))
    add(Case("findmaxind_1", "maxind",
             "findmaxind([theta3(q,60),theta4(q,60),expand(theta3(q,60)+theta4(q,60)),theta3(q^2,60)],0)[2]",
             "findmaxind([theta3(q,60),theta4(q,60),QSeries(theta3(q,60).series+theta4(q,60).series,60),theta3(q**2,60)],0)[1]"))
    add(Case("findpoly_cubic", "poly",
             "findpoly(S(radsimp(theta2(q,100)^2/theta2(q^3,40)^2)+theta3(q,100)^2/theta3(q^3,40)^2,100),"
             "S(radsimp(27*q*etaq(q,3,100)^9/etaq(q,1,100)^3/(theta3(q,100)*theta3(q^3,40)+radsimp(theta2(q,100)*theta2(q^3,40)))^3),100),q,3,1,60)",
             "findpoly(theta2(q,100)**2/theta2(q**3,40)**2+theta3(q,100)**2/theta3(q**3,40)**2,"
             "QSeries(3*etaq(q,3,100).series**3/etaq(q,1,100).series,100,r=QQ('1/3'))**3/(theta3(q,100)*theta3(q**3,40)+theta2(q,100)*theta2(q**3,40))**3,q,3,1,60)",
             opts={"vars": "X,Y"}))

    # ---------------------------------------------------------------- congruences
    for name, mexpr, pexpr in [
        ("partitions", "S(1/etaq(q,1,601),601)", "QSeries(etaq(q,1,601).series.__invert__(),601)"),
        ("distinct", "S(etaq(q,2,601)/etaq(q,1,601),601)", "QSeries(etaq(q,2,601).series/etaq(q,1,601).series,601)"),
        ("overpartitions", "S(etaq(q,2,601)/etaq(q,1,601)^2,601)", "QSeries(etaq(q,2,601).series/etaq(q,1,601).series**2,601)"),
        ("bipartitions", "S(1/etaq(q,1,601)^2,601)", "QSeries(etaq(q,1,601).series**(-2),601)"),
        ("composite_gcd", "add(q^n,n=0..600)+add(5*q^(3*n+2),n=0..199)",
         "QSeries(R(sum(q**n for n in range(601))+sum(5*q**(3*n+2) for n in range(200))).add_bigoh(601),601)"),
    ]:
        add(Case("findcong_" + name, "cong", "[findcong(%s,600)]" % mexpr, "findcong(%s,600)" % pexpr))

    # ---------------------------------------------------------------- mod p
    add(Case("findlincombomodp_doc", "lincombo",
             "findlincombomodp(sift(S(E4S(300)^16*E6S(300)/etaq(q,1,300),300),q,13,6,299),"
             "[seq(S(etaq(q,1,300)^11*E6S(300)*E4S(300)^(3*j+1),300),j=0..5)],[B1,B2,B3,B4,B5,B6],13,q,-8)",
             "findlincombomodp(sift(QSeries((E4(300)**16*E6(300)).series/etaq(q,1,300).series,300),q,13,6,299),"
             "[etaq(q,1,300)**11*E6(300)*E4(300)**(3*j+1) for j in range(6)],['B%d'%i for i in range(1,7)],13,q,-8)",
             opts={"k": 6, "p": 13, "sl": ["B1", "B2", "B3", "B4", "B5", "B6"]}))
    add(Case("findhommodp_e4_5", "rels", "findhommodp([E4S(100),E6S(100),1],5,q,1,0)",
             "findhommodp([E4(100),E6(100),ONE(100)],5,q,1,0)", opts={"k": 3, "p": 5}))
    add(Case("findhommodp_e6_7", "rels", "findhommodp([E4S(100),E6S(100),1],7,q,1,0)",
             "findhommodp([E4(100),E6(100),ONE(100)],7,q,1,0)", opts={"k": 3, "p": 7}))
    add(Case("findhommodp_deg2_5", "rels", "findhommodp([E4S(100),E6S(100)],5,q,2,0)",
             "findhommodp([E4(100),E6(100)],5,q,2,0)", opts={"k": 2, "p": 5}))
    add(Case("findhomcombomodp_1", "combo", "findhomcombomodp(E6S(100),[E4S(100),E6S(100)],5,q,2,0,no)",
             "findhomcombomodp(E6(100),[E4(100),E6(100)],5,q,2,0,'no')", opts={"k": 2, "p": 5}))
    return C


CASES = build_cases()
