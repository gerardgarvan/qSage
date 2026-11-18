#!/usr/bin/env python
"""
b4_selfsimilar.py -- test Du & Tang's Conjecture 12 on 4-regular partitions with qSage.

Reference: J. Q. D. Du and D. Tang, "Congruence properties modulo powers of 2 for
4-regular partitions", Electron. J. Combin. 31(3) (2024), #P3.32, Conjecture 12.

Notation
    b4(n) = number of 4-regular partitions of n,   sum b4(n) q^n = f_4 / f_1,
    f_k   = prod_{m>=1} (1 - q^(k m))  =  etaq(q, k, T).

Self-similar form tested, for a prime p >= 5 and level alpha >= 1:

    sum_n b4( p^(2^alpha - 1) n + (p^(2^alpha) - 1)/8 ) q^n
        ==  c * sum_n b4(n) q^(p n)      (mod 2^e)

    alpha = 1:  b4(p n + (p^2-1)/8).  The largest e that works defines k_p
                (and c mod 2^k_p is c_p).
    alpha >= 2: Conjecture 12 predicts the congruence holds with e = k_p + alpha - 1.
                (alpha = 2 is b4(p^3 n + (p^4-1)/8); for p = 5, 7, 11 these are
                 the authors' congruences (36)-(38).)

For each (p, alpha) the script reports the largest e consistent with the
coefficients computed.  This is numerical evidence only: more coefficients can
lower an observed exponent, never raise it.

Run
    sage -python b4_selfsimilar.py                    # defaults, about 1-2 minutes
    sage -python b4_selfsimilar.py --tmax 45000       # more alpha = 2 cases, slower
    sage -python b4_selfsimilar.py --primes 5 7 11 --findcong 400
(with the pip/passagemath install, use `python` instead of `sage -python`)

Cost: etaq(q, 1, T) grows roughly like T^2 (about 40 s at T = 20000 on a
typical machine), so --tmax is the knob that controls run time.  alpha = 3 needs
millions of coefficients and is out of reach of this script.
"""
import argparse
import csv
import time

from sage.all import LaurentSeriesRing, QQ
from qseries import etaq, sift, findcong, packageversion

CAP = 60  # exponent reported when every computed difference is exactly zero


def v2(x):
    """2-adic valuation of an integer; CAP if x == 0."""
    x = int(x)
    if x == 0:
        return CAP
    return (x & -x).bit_length() - 1


def signed_residue(c, e):
    """Representative of c mod 2^e in (-2^(e-1), 2^(e-1)]."""
    m = 1 << e
    r = c % m
    return r - m if r > m // 2 else r


def level_data(B, q, T, p, alpha):
    """
    Coefficients a(n) = b4(A n + d), A = p^(2^alpha - 1), d = (p^(2^alpha) - 1)/8,
    for all n with A n + d < T, extracted with qSage's sift.
    """
    A = p ** (2 ** alpha - 1)
    d = (p ** (2 ** alpha) - 1) // 8
    k, shift = d % A, d // A              # sift wants 0 <= k < A; then drop `shift` terms
    S = sift(B, q, A, k, T)               # sum_i b4(A i + k) q^i
    nterms = S.T - shift
    a = [int(S.series[n + shift]) for n in range(max(nterms, 0))]
    return A, d, a


def observed_exponent(a, b4, p):
    """
    Largest e such that  a(n) == c * b4(n/p) [p | n],  a(n) == 0 [p does not divide n]
    (mod 2^e) for all computed n.  Since b4(0) = 1, c is forced to be a(0).
    Returns (e, c, e_zero, e_mult).
    """
    c = a[0]
    e_zero = min([v2(a[n]) for n in range(len(a)) if n % p] or [CAP])
    e_mult = min([v2(a[p * m] - c * b4[m]) for m in range(1, (len(a) - 1) // p + 1)] or [CAP])
    return min(e_zero, e_mult), c, e_zero, e_mult


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--primes", type=int, nargs="+",
                    default=[5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47],
                    help="primes p >= 5 to test")
    ap.add_argument("--alpha-max", type=int, default=2, help="highest level alpha to attempt (default 2)")
    ap.add_argument("--tmax", type=int, default=22000,
                    help="number of coefficients of f_4/f_1 to compute (default 22000)")
    ap.add_argument("--min-terms", type=int, default=12,
                    help="skip a (p, alpha) case with fewer than this many terms (default 12)")
    ap.add_argument("--findcong", type=int, default=0, metavar="T",
                    help="also run findcong on b4 up to q^T and list congruences modulo powers of 2")
    ap.add_argument("--csv", default="b4_selfsimilar_results.csv", help="output CSV file")
    args = ap.parse_args()

    for p in args.primes:
        if p < 5:
            ap.error("primes must be >= 5")

    T = args.tmax
    print(f"qseries-sage {packageversion()};  computing f_4/f_1 to O(q^{T}) ...", flush=True)
    R = LaurentSeriesRing(QQ, "q", default_prec=T)
    q = R.gen()
    t0 = time.time()
    B = etaq(q, 4, T) / etaq(q, 1, T)      # sum b4(n) q^n
    b4 = [int(B.series[n]) for n in range(T)]
    print(f"  done in {time.time() - t0:.1f} s;  b4(0..9) = {b4[:10]}\n", flush=True)

    rows = []
    kp = {}
    hdr = f"{'p':>3} {'p%24':>4} {'alpha':>5} {'progression':>22} {'terms':>6} {'observed e':>10} {'predicted e':>11} {'c mod 2^e':>10}  status"
    print(hdr)
    print("-" * len(hdr))
    for p in args.primes:
        for alpha in range(1, args.alpha_max + 1):
            A, d, a = level_data(B, q, T, p, alpha)
            prog = f"{A}n+{d}"
            if len(a) < args.min_terms:
                print(f"{p:>3} {p % 24:>4} {alpha:>5} {prog:>22} {len(a):>6} {'-':>10} {'-':>11} {'-':>10}  skipped (raise --tmax)")
                rows.append([p, p % 24, alpha, A, d, len(a), "", "", "", "skipped"])
                continue
            e, c, e_zero, e_mult = observed_exponent(a, b4, p)
            if alpha == 1:
                kp[p] = e
                predicted, status = "(defines k_p)", "k_p, c_p"
                pred_num = ""
            else:
                pred_num = kp[p] + alpha - 1 if p in kp else ""
                predicted = str(pred_num)
                if pred_num == "":
                    status = "no k_p"
                elif e >= pred_num:
                    status = "consistent" + ("" if e == pred_num else f" (holds to 2^{e} on these terms)")
                else:
                    status = "FAILS -- check!"
            e_show = f">={CAP}" if e >= CAP else str(e)
            c_show = signed_residue(c, e) if e < CAP else c
            print(f"{p:>3} {p % 24:>4} {alpha:>5} {prog:>22} {len(a):>6} {e_show:>10} {predicted:>11} {c_show:>10}  {status}")
            rows.append([p, p % 24, alpha, A, d, len(a), e, pred_num, c_show, status])

    with open(args.csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["p", "p_mod_24", "alpha", "A", "d", "terms", "observed_e", "predicted_e", "c_mod_2^e", "status"])
        w.writerows(rows)
    print(f"\nWrote {args.csv}")

    if args.findcong:
        Tc = min(args.findcong, T - 1)
        print(f"\nfindcong(f_4/f_1, {Tc}) -- congruences b4(A n + B) == 0 (mod M) with M a power of 2:")
        found = sorted((A_, B_, M_) for (B_, A_, M_) in findcong(B, Tc) if M_ % 2 == 0)
        if not found:
            print("  none found in this range")
        for A_, B_, M_ in found:
            print(f"  b4({A_}n + {B_}) == 0 (mod {M_})")


if __name__ == "__main__":
    main()
