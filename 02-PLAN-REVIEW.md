# Phase 2 plan review — fix before /gsd:execute-phase 2

Severity: **BLOCKER** (breaks the tutorial or won't run) · **BUG** (wrong result, plan's tests may still pass) · **NOTE**.

## The one design error that runs through all four plans

**BLOCKER — every building block ignores its `q` (and `z`) arguments.** Each function does `R = LaurentSeriesRing(QQ,'q'); qvar = R.gen()` and computes in *its own* `q`. The Maple package is used almost entirely by passing powers of q: the tutorial calls `theta3(q^5,100)`, `theta3(q^25,20)`, `theta(q^10,q^25,5)`, `tripleprod(q^n,q^33,10)`, `winquist(q^5,q^3,q^11,10)`, `quinprod(q,q^5,20)`, `etaq(q,49,100)`. Under the plans, `theta4(q**2, T)` silently returns `theta4(q, T)` — the plan's own `test_theta3_theta4_product_identity` would fail for this reason.

The try/except "scalar vs bivariate" branching in `theta` and `tripleprod`, the `int(a)==a` guard in `winquist`, and the hand-built `LaurentPolynomialRing(QQ,['a','b'])` inside `quinprod`/`winquist` are all workarounds for this. Replace them with one rule:

> **Compute with the objects the caller passed.** `z`, `a`, `b`, `q` are Sage elements (a Laurent-polynomial generator, a q-series ring generator, `q**5`, `-1`, …). Build the finite sum/product as arithmetic on them; Sage coercion picks the parent. Wrap the result in `QSeries`, taking `R` from the result's base ring. No ring construction inside the function, no type sniffing.

`theta(z, q, T)` becomes `sum(z**i * q**(i*i) for i in range(-T, T+1))` — three lines, correct for every tutorial call.

## Second cross-cutting problem: truncation semantics

**BUG — "T" is a summation bound for the identity functions, not a q-order.** From the doc pages and tutorial:
- `theta(z,q,T) = Σ_{i=-T}^{T} z^i q^{i²}` (tutorial §2.2.2).
- `theta3(q,50)` prints up to `2q^64`; `theta3(q,100)` up to `2q^121`; `theta3(q^25,20)` up to `2q^625` → the sum runs to `n = floor(√T)+1`. The plan's `while k*k < T` stops one term early, so the output never matches the doc string it cites.
- `quinprod(z,q,3)` prints terms up to `q^26` — a sum over `m`, not an `O(q^3)` truncation.
- `tripleprod(z,q,10)` prints `z^±6` terms up to `q^21`.

So `theta`, `theta2`, `theta3`, `theta4`, `tripleprod`, `quinprod`, `winquist` return **exact Laurent polynomials** with Maple's summation bound (read each doc page for the bound, test against the printed output verbatim). Only the genuinely infinite products — `etaq`, `jacprod` — truncate at `O(q^T)`.

**BLOCKER — `aqprod` and `qbin` must be exact.** `(q;q)_n` is a polynomial of degree `n(n+1)/2`; the plan returns it truncated at `O(q^(n+1))`, destroying most of it. The tutorial's first example, `Σ q^(n²)/aqprod(q,q,n)` then `series(...,q,50)`, needs the full polynomial. Return the exact polynomial (Sage gives infinite precision automatically when you don't call `add_bigoh`). `qbin` likewise; its zero case should be an exact zero, not `zero().add_bigoh(1)`.

**Consequence for Phase 1:** `QSeries` must accept `T = Infinity` (currently `int(T)` raises). Add: `self.T = T if T is Infinity else int(T)`, and `_binop` takes `min` with Infinity correctly. Tests: `QSeries(exact_poly).T == Infinity`, and `exact * truncated` has the truncated `T`.

## Per-function

- **BLOCKER — `quinprod` signature and formula.** RESEARCH.md read the doc page's `CALLING SEQUENCE: quinprod(a,b,q,T)` header and stopped. Every example on that page and in the tutorial is `quinprod(z,q,T)` — the header is a typo. Revert to 3 arguments (CONTEXT.md had it right). The plan's 7-factor "Watson product" and both identity strings are invented; the real identity (tutorial (6.9), doc page) is
  `(−z;q)∞ (−q/z;q)∞ (z²q;q²)∞ (q/z²;q²)∞ (q;q)∞ = Σ_m ((−z)^{−3m} − (−z)^{3m−1}) q^{m(3m+1)/2}`,
  and `T=int` returns the series side summed over `m` (bound from the doc example: `T=3` yields `m=−4..4`). `prodid`/`seriesid` strings must print this identity, not the invented one.
- **BLOCKER — `winquist`.** The plan forbids scalar `a, b` and replaces the doc-page oracle (`winquist(1,1,q,30) = 1−10q+35q²−30q³−105q⁴+238q⁵…`, which is `(q;q)∞^10`) with a type-only assertion. That is the "test from our own output" anti-pattern in reverse: the oracle was dropped because the implementation couldn't meet it. The tutorial also calls `winquist(q^5,q^3,q^11,10)`, which the plan's `Rab(a)` coercion rejects. Read the doc page for the exact series formula and summation bounds; implement the series side over the passed-in `a, b, q`; keep the `(1,1,q,30)` oracle as a test (if the doc's formula is the product divided by `(1−a)(1−b)`, that is what to implement).
- **BLOCKER — `etaq`.** `qexp_eta` lives in `sage.modular.etaproducts` (which CLAUDE.md bans) and its signature is `qexp_eta(ps_ring, prec)` — it takes a *ring*, so `qexp_eta(qvar**k, T)` fails. Drop the wrapper: `prod(1 − q**(k*n) for n in 1..(T−1)//k)`, truncated at `O(q^T)`, computed on the passed-in `q`. (Or Euler's pentagonal sum — sparse and fast.) Amend D-01 accordingly.
- **BUG — `qbin` import.** `from sage.arith.misc import q_binomial` is a submodule import (Phase 1 lesson); use `from sage.all import q_binomial`. Maple `qbin(q,m,n)` → `q_binomial(n, m, q)` is correct.
- **BUG — `sift`** builds its result in a fresh `QQ` ring; use `s.series.parent()` so `GF(p)` input survives. Otherwise correct, and the `T_out` matches the tutorial (`sift(PD,q,5,1,199)` → 40 terms).
- **NOTE — `theta2`** has a dead `coeff = …` line; loop is otherwise right. Check the summation bound against the doc page: `theta2(q,100)/q^(1/4)` prints up to `q^156` (`n=12`), which is not `floor(√T)+1`.
- **NOTE — `checkmult`.** Fine. The multiplicative test uses `f = 1` (`a(1)=0`), which is vacuous; use a real oracle that doesn't depend on our code: `etaq(q,1,T)**24` is `Σ τ(n)q^n` shifted, with `τ(2)=−24, τ(3)=252, τ(6)=−6048 = τ(2)τ(3)`.

## Wrong expected values in the Wave-0 tests

- `test_aqprod_tutorial_canonical`: `(1−q)(1−q²)(1−q³)(1−q⁴) = 1 − q − q² + 2q⁵ − q⁸ − q⁹ + q¹⁰`. The test expects `coeff[5] = 1`; it is `2`.
- `test_sift_e0`: the oracle `E0 = eta(q^5)^5/eta(q)` is invented. The tutorial (§6.2) prints `E0` exactly: `1 + q − q³ − q⁷ − q⁸ − q¹⁴ + q²⁰ + q²⁹ + q³¹ + q⁴² − q⁵² − q⁶⁶ − q⁶⁹ − q⁸⁵ + q⁹⁹`. Assert that list. (Its product form is `(q⁵;q⁵)(q²;q⁵)(q³;q⁵)/((q;q⁵)(q⁴;q⁵))`, not an eta quotient.)
- `test_theta3_coefficients` / `test_theta4_coefficients`: cite "exact string" but only check up to `q^16`. Assert the full printed polynomial including `2q^64` — that is what catches the summation-bound error.
- `test_theta3_theta4_product_identity`: correct identity, but only works once `theta4(q**2, T)` honours its argument (see top).

## 02-VALIDATION.md

- The automated commands reference `::test_aqprod`, `::test_qbin`, …; the actual test names are `test_aqprod_basic`, `test_qbin_33_66`, etc. Every per-task command will report "not found". Use `-k aqprod` style selectors or the real names.
- RESEARCH.md says SageMath 10.x; the runtime is 9.5. Record it.

## CONTEXT.md amendments

- **D-01 →** `qbin` wraps `q_binomial` (imported from `sage.all`); `etaq` is a direct product. No `qexp_eta`.
- **D-03 →** bivariate/identity functions compute on the caller's objects; no internal ring construction, no scalar/bivariate branching. `winquist(1,1,q,T)` and `winquist(q^5,q^3,q^11,T)` must both work.
- **New D-11 →** `theta*`, `tripleprod`, `quinprod`, `winquist` return exact Laurent polynomials with Maple's summation bounds (bound taken from each doc page's example); `aqprod`, `qbin` return exact polynomials; only `etaq`, `jacprod` truncate at `O(q^T)`. `QSeries` accepts `T = Infinity`.
- **quinprod →** `quinprod(z, q, T)`, 3 arguments.
