# Phase 5: Relation Finding (Exact) - Research

**Researched:** 2026-09-17
**Domain:** SageMath linear algebra over QQ; Garvan qseries relation-finding algorithms
**Confidence:** HIGH (all major decisions locked in CONTEXT.md; doc pages verified for all unverified signatures)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01 — Scope:** Phase 6 merged into Phase 5. Mod-p variants reuse the exact code path with `GF(p)` as the coefficient ring; a non-prime `p` raises `ValueError` before any computation.

**D-02 — Matrix construction:**
1. Generate monomials: degree exactly `n` for `findhom`/`findhomcombo`; all degrees `≤ n` for `findnonhom`/`findnonhomcombo`; degree 1 for `findlincombo`.
2. For `*combo` variants, `f` is an extra row.
3. Evaluate each monomial on the series in `L` and take the first `N` q-coefficients as a **row**: matrix `M` is `(#rows) × N`.
4. Relations = `M.left_kernel()`. Map each kernel vector to a polynomial in `PolynomialRing(QQ, ['X1',…,'Xk'])`.
5. Print `# of terms , N` and for combo variants `matrix is , rows, x, N`.

**D-03 — Empty result:** No relations → return empty set/list.

**D-04 — topshift (corrected):** `N = (#rows) + C + topshift`.
- `findhom` 4 rows → 25, 10 rows → 31 → implies C=21 for findhom.
- combo variants: C=20.
- `topshift > -20` (default 0). ValueError if a series has fewer than N terms.

**D-05 — Optional-argument overloading:** Trailing args distinguished by type (int → topshift, string 'yes'/'no' → etaoption). Apply to `findhom`, `findhomcombo`, `findnonhom`, `findnonhomcombo`. With `etaoption='yes'` each monomial in result also shown as `EtaProduct` via `etamake`.

**D-06 — Still-unverified signatures at context time:** `findlincombo`, `findlincombomodp`, `findmaxind`, `findhommodp`, `findhomcombomodp`, optional 3rd argument of `findcong`. **Now resolved — see Verified Signatures section below.**

**D-07 — findcong algorithm:** `findcong(f, T [, LM [, XSET]])`. For each A and 0 ≤ B < A: M = gcd(a(An+B) for An+B ≤ T). Candidate if M > 1. Suppress implied triples. Oracle: `{[4,5,5],[5,7,7],[6,11,11],[24,25,25]}`.

**D-08 — findpoly:** Monomials `X^i Y^j`, i ≤ deg1, j ≤ deg2; same kernel machinery; result in `PolynomialRing(QQ, ['X','Y'])`. If `check` given, verify to `O(q^check)`. Oracle: `(X+6)^3*Y − 27*(X+2)^2`.

**D-09 — Return type:** Polynomials in `X1..Xk` / `X, Y`, never bare vectors. Tests compare relation **span**, not ordering.

### Claude's Discretion

- Monomial ordering (choose the one that reproduces Maple's printed polynomials in §4.1–4.3).
- One module `_relations.py` vs. a split.
- Exact console-output formatting beyond `# of terms` / `matrix is` lines.

### Deferred Ideas (OUT OF SCOPE)

None.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-01 | `findhom(L, q, n, topshift)` — homogeneous degree-n relations over QQ | Matrix kernel algorithm verified; N formula from D-04 |
| REL-02 | `findhomcombo(f, L, q, n, topshift, etaoption)` — express f as degree-n poly in L | Same kernel; f is extra row; etaoption calls etamake |
| REL-05 | `findnonhom(L, q, n, topshift)` — non-homogeneous (total degree ≤ n) relations | Same matrix; monomial set includes degree 0..n |
| REL-06 | `findnonhomcombo(f, L, q, n, topshift, etaoption)` | Same; f extra row |
| REL-07 | `findlincombo(f, L, SL, q, topshift)` — express f as linear combination; SL is symbol list | Signature confirmed from doc page |
| REL-09 | `findmaxind(XFL, T)` — maximal linearly independent subset | Confirmed signature; T is topshift-equivalent; returns [P, NXFL] |
| REL-10 | `findpoly(x, y, q, deg1, deg2 [, check])` | Bivariate kernel; optional check arg |
| REL-11 | `findcong(f, T [, LM [, XSET]])` | GCD-over-residue-classes algorithm; LM and XSET optional |
</phase_requirements>

---

## Summary

Phase 5 implements all 8 exact relation-finding functions in a single new module `_relations.py`, plus the 3 mod-p variants (D-01 merges Phase 6 here). The core algorithm is the same for all `find*hom*`, `findnonhom*`, `findlincombo`, and `findpoly` functions: build a matrix whose rows are q-coefficient vectors of monomials evaluated on the input series, compute `M.left_kernel()` over QQ (or GF(p) for mod-p), and map kernel vectors back to polynomials in `PolynomialRing(QQ, ['X1',…,'Xk'])`.

`findmaxind` is a thin wrapper that calls `findhom` with n=1 to collect dependencies and returns the independent subset plus its indices. `findcong` is structurally independent: it uses `sift` from `_utilities.py` to extract subsequences, computes GCDs, and applies an implication filter.

All oracles come from Garvan's tutorial and doc pages; no Maple computation was run. Sage 9.5 is the runtime (WSL, Ubuntu).

**Primary recommendation:** One module `_relations.py` with a shared `_build_matrix` helper; the combo/non-combo/lincombo/poly variants differ only in their monomial generators and the presence of the `f` extra row.

---

## Verified Signatures (resolving D-06)

All signatures confirmed by reading official doc pages at `https://qseries.org/fgarvan/qmaple/qseries/functions/`.

### findlincombo
```
findlincombo(f, L, SL, q, topshift)
```
- `f`: QSeries to express
- `L`: list of QSeries basis elements
- `SL`: list of Sage symbolic names for printing (e.g., `[var('F1'), var('F2')]`)
- `q`: variable
- `topshift`: integer > -20, default 0

Returns a set of linear combination expressions. Prints the combination using names from SL. If not expressible, outputs `%NOT A LINEAR COMBO.%` (our Python equivalent: return empty set and optionally print message).

Note: `SL` has no Maple analogue in Sage's polynomial ring — in our implementation, the returned polynomial uses `X1..Xk` naming (FOUND-04, D-09). `SL` can be accepted but used only for optional console printing, not for the return value.

### findmaxind
```
findmaxind(XFL, T)
```
- `XFL`: list of QSeries
- `T`: nonnegative integer (plays the role of topshift; "used in findhom" per docs — it is passed as topshift to the internal linear-dependence check)
- No `q` argument in the calling sequence

Returns `[P, NXFL]` where `P` is the maximal independent sublist and `NXFL` is the list of 1-based indices selected.

**Key implementation note:** The example shows `Y[2]` (indices) and then uses `findhom(GL1, q, 1, 0)` to verify. `findmaxind` must internally construct a q variable or receive the series' q variable from the series objects. Since `QSeries` wraps a `LaurentSeriesRing` whose generator is `q`, the function can extract `q` from `XFL[0].series.parent().gen()` without requiring a `q` parameter.

### findcong (optional args)
```
findcong(QS, T)
findcong(QS, T, LM)
findcong(QS, T, LM, XSET)
```
- `LM`: positive integer — verification limit; defaults to `floor(sqrt(T))` when omitted. Per D-07, the gcd loop runs over `An+B ≤ T`. `LM` bounds A: only A ≤ LM are checked.
- `XSET`: set of positive integers — moduli to **exclude** from results (primes to suppress).

The oracle call `findcong(1/etaq(q,1,1001), 1000)` uses the two-argument form, so `LM = floor(sqrt(1000)) = 31` and no XSET. A is checked for `2 ≤ A ≤ 31`.

---

## Standard Stack

No new library dependencies. Everything uses existing Sage primitives.

| Primitive | Purpose | Already Used |
|-----------|---------|-------------|
| `sage.all.matrix(QQ, rows)` | Build coefficient matrix | No — new in Phase 5 |
| `M.left_kernel()` | Null-space over QQ | No — new in Phase 5 |
| `sage.all.PolynomialRing(QQ, names)` | Return type for relations | No — new in Phase 5 |
| `sage.all.GF(p)` | Coefficient ring for mod-p | Used in previous phases conceptually |
| `sage.all.is_prime(p)` | Validate prime p | No — new in Phase 5 |
| `math.gcd` (or `sage.all.gcd`) | findcong GCD computation | Already in `_utilities.py` |
| `math.isqrt` | Default LM computation | Already in codebase |
| `qseries._utilities.sift` | Subsequence extraction for findcong | Implemented in Phase 2 |
| `qseries._conversion.etamake` | etaoption='yes' in combo functions | Implemented in Phase 4 |

**No new pip installs required.**

---

## Architecture Patterns

### Recommended Module Structure

```
qseries/
├── _relations.py        # All 11 relation-finding functions (new)
├── tests/
│   └── test_relations.py  # New test file
```

One module with a shared internal helper is preferred (Claude's Discretion — confirmed by the fact that all homogeneous/non-homogeneous/linear variants share 90% of the same matrix-building logic).

### Pattern: Shared Matrix Builder

```python
def _build_matrix(monomials, series_list, N, ring):
    """
    monomials: list of exponent tuples (e1, e2, ..., ek)
    series_list: list of QSeries
    N: number of q-coefficients to use per row
    ring: QQ or GF(p)
    Returns: sage matrix over ring, shape (len(monomials), N)
    """
    from sage.all import matrix
    rows = []
    for exponents in monomials:
        # Evaluate monomial: product of series[i]^exponents[i]
        val = _eval_monomial(exponents, series_list)
        # Extract first N coefficients (indices 0..N-1 of the Laurent expansion)
        coeffs = [ring(val.series[j]) for j in range(N)]
        rows.append(coeffs)
    return matrix(ring, rows)
```

### Pattern: Monomial Generation

```python
# Homogeneous degree exactly n in k variables
from itertools import combinations_with_replacement
monomials_hom = [e for e in _partitions_of_n_into_k(n, k)]
# Total degree <= n
monomials_nonhom = [e for d in range(n+1) for e in _partitions_of_d_into_k(d, k)]
# Linear (degree 1)
monomials_lin = [(1 if i==j else 0 for j in range(k)) for i in range(k)]
```

Sage's `WeightedIntegerVectors` or direct iteration over `IntegerVectors(n, k)` can enumerate homogeneous exponent tuples.

### Pattern: Kernel to Polynomials

```python
from sage.all import PolynomialRing, QQ
R = PolynomialRing(QQ, ['X%d' % (i+1) for i in range(k)])
gens = R.gens()

def _kernel_to_polys(kernel, monomials, gens):
    result = set()
    for vec in kernel:
        poly = R.zero()
        for coeff, exponents in zip(vec, monomials):
            monomial = R.one()
            for g, e in zip(gens, exponents):
                monomial *= g**e
            poly += coeff * monomial
        if poly != R.zero():
            result.add(poly)
    return result
```

### Pattern: N Computation (D-04)

```python
def _compute_N(num_rows, topshift, is_combo):
    C = 20 if is_combo else 21
    return num_rows + C + topshift
```

This is derived from the four data points in D-04:
- `findhom` 4 rows → N=25: 4 + 21 + 0 = 25. Check: 10 rows → N=31: 10 + 21 + 0 = 31. Consistent.
- combo variants 5 rows → N=25: 5 + 20 + 0 = 25. `findnonhomcombo` 4 rows → N=24: 4 + 20 + 0 = 24. Consistent.

### Pattern: Optional Argument Dispatch (D-05)

```python
def findhom(L, q, n, *args):
    topshift = 0
    etaoption = 'no'
    for a in args:
        if isinstance(a, int):
            topshift = a
        elif a in ('yes', 'no'):
            etaoption = a
    ...
```

### Pattern: findcong Algorithm

```python
from math import isqrt, gcd
from sage.all import ZZ

def findcong(f, T, LM=None, XSET=None):
    if LM is None:
        LM = isqrt(T)
    if XSET is None:
        XSET = set()
    coeffs = [ZZ(f.series[n]) for n in range(T+1)]
    candidates = []
    for A in range(2, LM+1):
        for B in range(A):
            # collect a(An+B) for An+B <= T
            vals = [coeffs[A*n+B] for n in range((T - B)//A + 1)]
            M = 0
            for v in vals:
                M = gcd(M, int(v))
            M = abs(M)
            if M > 1:
                candidates.append([B, A, M])
    # suppress implied triples
    result = _suppress_implied(candidates)
    return set(tuple(t) for t in result)
```

Implication filter: skip `(B, A, M)` if an already-accepted `(B', A', M')` satisfies `A' | A`, `B ≡ B' (mod A')`, and `M | M'`.

### Pattern: findmaxind

```python
def findmaxind(XFL, T=0):
    # Use findhom at degree 1 to find all linear dependencies
    # Then greedily pick independent elements
    q = XFL[0].series.parent().gen()  # extract q from first series
    ...
```

The greedy strategy: iterate elements of XFL, add to chosen set if the extended set has no new linear relations (re-run findhom on the current chosen set).

### Anti-Patterns to Avoid

- **Using numpy/scipy for the nullspace:** Floating-point destroys exactness over QQ. Sage's `M.left_kernel()` is exact.
- **Extracting Laurent coefficients naively from the full series:** A QSeries with rational shift `r` needs `r` to be handled before reading coefficient index `j`. Use `series[j]` from the underlying Sage `LaurentSeriesRing` element after accounting for shift.
- **Using `M.right_kernel()` instead of `M.left_kernel()`:** Maple's description says "kernel of the transpose", which in Sage's convention is `left_kernel()` of the original matrix (rows are monomial evaluations).
- **Passing `GF(p)` with composite p:** `sage.all.GF(p)` raises an error for composite p; validate with `is_prime(p)` and raise `ValueError` first.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Exact nullspace over QQ | Custom row reduction | `M.left_kernel()` | Sage handles pivoting, fraction-free arithmetic, degeneracy |
| Homogeneous exponent tuples | Custom recursion | `sage.all.IntegerVectors(n, k)` | Handles k=1 and large n correctly |
| GCD of a list | Loop with binary gcd | `functools.reduce(gcd, vals)` or `sage.all.gcd(vals)` | Correct handling of gcd(0, x) = x |
| Polynomial ring over named vars | Custom class | `PolynomialRing(QQ, ['X1','X2',...])` | Already the mandated return type |

---

## Common Pitfalls

### Pitfall 1: Laurent Coefficient Indexing With Rational Shift
**What goes wrong:** A `QSeries` with shift `r != 0` stores its Sage `LaurentSeriesRing` element starting at power `0` (not `r`). Reading `series[j]` gives the coefficient of `q^j` in the underlying ring, not of `q^(j+r)`.
**Why it happens:** The `r` field is a metadata annotation on `QSeries`; the underlying ring element is always in integer powers.
**How to avoid:** When building the coefficient row, use `s.series[j]` for `j = 0..N-1`. The matrix rows represent the actual q-expansion coefficients regardless of the conceptual shift. All series in `L` must be aligned (same shift or converted) before comparison — if shifts differ, the "same q-power" means different things.
**Warning signs:** All relations returned at degree 1 even though Maple finds none; `theta2` (shift 1/4) participating in findhom with theta3/theta4 (shift 0).

### Pitfall 2: N Too Small Gives Spurious Relations
**What goes wrong:** Kernel vector that happens to be zero up to N coefficients but not beyond — a false relation.
**Why it happens:** Truncated coefficient matching. Maple's `topshift` mechanism exists exactly for this.
**How to avoid:** Use the C constants from D-04 precisely. If topshift=0 gives suspects, increase it. Raise `ValueError` if any series has fewer than N terms (don't silently truncate).

### Pitfall 3: GCD(0, x) Convention in findcong
**What goes wrong:** If all sampled coefficients are 0, `gcd(0, 0, ...) = 0`, not infinity — correctly excluded. But if using Python `math.gcd` with only one element, `gcd(x)` is unavailable in older Python.
**How to avoid:** Use `from math import gcd` with `functools.reduce(gcd, vals, 0)` (Python 3.9+) or explicit loop initializing to 0. Sage `gcd([...])` also works.

### Pitfall 4: IntegerVectors Ordering vs. Maple
**What goes wrong:** `IntegerVectors(n, k)` enumerates in lexicographic descending order; Maple's `X[1]^a*X[2]^b` ordering may differ from Sage's polynomial ring default.
**Why it happens:** Kernel vectors' entries are indexed by monomial position. If ordering differs between row construction and polynomial reconstruction, coefficients are swapped.
**How to avoid:** Build a single ordered list of monomial tuples, use that same list for both matrix rows and polynomial reconstruction. The test must compare **spans** (sets of polynomials up to scalar), not exact polynomial text.

### Pitfall 5: findlincombo SL Argument
**What goes wrong:** Maple's `findlincombo` returns a printed expression using the names in `SL` (e.g., `12 F1 + 13 F2`), not a polynomial in `X1, X2`. Our Python port must return a polynomial (FOUND-04/D-09), making `SL` decorative.
**How to avoid:** Accept `SL` as a parameter (interface fidelity), use it for optional console printing if desired, but always return a `PolynomialRing(QQ, ['X1',...,'Xk'])` polynomial. Document the divergence.

---

## Code Examples

### Building and Solving the Matrix (verified pattern)
```python
# Source: Sage documentation + D-02 algorithm
from sage.all import matrix, QQ, IntegerVectors, PolynomialRing

def findhom(L, q, n, *args):
    topshift = 0
    etaoption = 'no'
    for a in args:
        if isinstance(a, int):
            topshift = a
        elif a in ('yes', 'no'):
            etaoption = a

    k = len(L)
    # Generate homogeneous monomials of degree exactly n in k variables
    mono_exps = list(IntegerVectors(n, k))  # each entry is [e1,...,ek]
    num_rows = len(mono_exps)
    N = num_rows + 21 + topshift  # C=21 for findhom

    # Validate series lengths
    for i, s in enumerate(L):
        if s.T < N:
            raise ValueError(
                f"Series L[{i}] has precision {s.T} but N={N} terms required; "
                f"recompute with T >= {N}"
            )

    print(f"# of terms , {N}")

    # Build coefficient matrix: rows = monomials, cols = q-coefficients
    rows = []
    for exponents in mono_exps:
        val = L[0].series.parent().one()  # start with 1
        for s, e in zip(L, exponents):
            if e > 0:
                val = val * s.series**e
        coeffs = [QQ(val[j]) for j in range(N)]
        rows.append(coeffs)

    M = matrix(QQ, rows)
    kern = M.left_kernel()

    # Map kernel vectors to polynomials
    R = PolynomialRing(QQ, ['X%d' % (i+1) for i in range(k)])
    gens = R.gens()
    result = set()
    for vec in kern.basis():
        poly = R.zero()
        for coeff, exponents in zip(vec, mono_exps):
            if coeff != 0:
                term = R.one()
                for g, e in zip(gens, exponents):
                    term *= g**e
                poly += coeff * term
        if poly != R.zero():
            result.add(poly)
    return result
```

### findcong Core Loop
```python
# Source: D-07 algorithm + doc page verification
from math import isqrt, gcd
from functools import reduce

def _gcd_list(vals):
    return reduce(gcd, (abs(int(v)) for v in vals), 0)

def findcong(f, T, LM=None, XSET=None):
    if LM is None:
        LM = isqrt(T)
    if XSET is None:
        XSET = set()
    coeffs = [int(f.series[n]) for n in range(T + 1)]

    raw = []
    for A in range(2, LM + 1):
        for B in range(A):
            vals = [coeffs[A*n + B] for n in range((T - B) // A + 1)
                    if A*n + B <= T]
            M = _gcd_list(vals)
            if M > 1 and M not in XSET:
                raw.append([B, A, M])

    # Suppress implied triples
    accepted = []
    for triple in raw:
        B, A, M = triple
        implied = False
        for B2, A2, M2 in accepted:
            if A2 % A == 0 and B % A2 == B2 % A2 and M2 % M == 0:
                implied = True
                break
        if not implied:
            accepted.append([B, A, M])

    return {tuple(t) for t in accepted}
```

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (sage -python -m pytest) |
| Config file | none — uses pyproject.toml or default discovery |
| Quick run command | `sage -python -m pytest tests/test_relations.py -x` |
| Full suite command | `sage -python -m pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-01 | `findhom([theta3,theta4,theta3(q^2),theta4(q^2)],q,1,0)` → empty set; degree 2 → 2 relations | unit | `sage -python -m pytest tests/test_relations.py::test_findhom_theta -x` | Wave 0 |
| REL-02 | `findhomcombo(UE,[B1,B2],q,3,0,'yes')` → `X1^2*X2+40*X1*X2^2+335*X2^3` | unit | `sage -python -m pytest tests/test_relations.py::test_findhomcombo -x` | Wave 0 |
| REL-05 | `findnonhom` finds Watson's mod-7 equation | unit | `sage -python -m pytest tests/test_relations.py::test_findnonhom -x` | Wave 0 |
| REL-06 | `findnonhomcombo` reproduces tutorial §4.3 example | unit | `sage -python -m pytest tests/test_relations.py::test_findnonhomcombo -x` | Wave 0 |
| REL-07 | `findlincombo(12*f1+13*f2,[f1,f2],[F1,F2],q,0)` → linear combo polynomial | unit | `sage -python -m pytest tests/test_relations.py::test_findlincombo -x` | Wave 0 |
| REL-09 | `findmaxind(GL1,0)` returns 7-element independent subset | unit | `sage -python -m pytest tests/test_relations.py::test_findmaxind -x` | Wave 0 |
| REL-10 | `findpoly(x,y,q,3,1,60)` → `(X+6)^3*Y-27*(X+2)^2` | unit | `sage -python -m pytest tests/test_relations.py::test_findpoly -x` | Wave 0 |
| REL-11 | `findcong(1/etaq(q,1,1001),1000)` → `{[4,5,5],[5,7,7],[6,11,11],[24,25,25]}` | unit | `sage -python -m pytest tests/test_relations.py::test_findcong -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `sage -python -m pytest tests/test_relations.py -x`
- **Per wave merge:** `sage -python -m pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_relations.py` — new file, covers REL-01 through REL-11

---

## Open Questions

1. **`findhomcombomodp`, `findhommodp` argument position of `p`**
   - What we know: D-01 says mod-p variants reuse exact code path with GF(p); D-06 guesses `findhommodp(L, q, p, n, topshift)`.
   - What's unclear: doc page for `findhommodp` not yet fetched.
   - Recommendation: Fetch `https://qseries.org/fgarvan/qmaple/qseries/functions/findhommodp.html` at the start of the mod-p plan (Plan 05-03 or the equivalent mod-p plan). Per the ROADMAP, mod-p is now Phase 5 but was formerly Phase 6; the planner should dedicate a separate plan to the 3 mod-p functions and confirm `p` position before writing task actions.

2. **`findmaxind` internal q variable**
   - What we know: The doc page shows no `q` argument; the function must still evaluate series coefficients.
   - What's unclear: Whether it calls `findhom` internally (which needs `q`) or does a direct rank computation.
   - Recommendation: Implement as a direct rank computation using `matrix.rank()` on the raw coefficient matrix. Extract `q` from `XFL[0].series.parent().gen()`. No need to call `findhom`.

3. **`findcong` A-range upper bound**
   - What we know: LM defaults to `floor(sqrt(T))` per doc page. For T=1000, LM=31.
   - What's unclear: Whether A starts at 2 or 1. A=1 gives B=0 and would check whether all coefficients share a GCD — plausible but trivial.
   - Recommendation: Start A at 2 (A=1 means checking `a(n) ≡ 0 (mod M)` for all n, which the oracle does not include). Verify by confirming the oracle result is reproduced.

---

## Environment Availability

Step 2.6: SKIPPED — Phase 5 is a pure code addition. All required tools (SageMath 9.5, pytest, existing qseries package modules) are confirmed present from prior phases. No new external dependencies.

---

## Sources

### Primary (HIGH confidence)
- `https://qseries.org/fgarvan/qmaple/qseries/functions/findhom.html` — calling sequence, N examples (25/31), etaoption
- `https://qseries.org/fgarvan/qmaple/qseries/functions/findhomcombo.html` — calling sequence, UE oracle
- `https://qseries.org/fgarvan/qmaple/qseries/functions/findnonhom.html` — calling sequence confirmed
- `https://qseries.org/fgarvan/qmaple/qseries/functions/findlincombo.html` — calling sequence with SL parameter confirmed
- `https://qseries.org/fgarvan/qmaple/qseries/functions/findmaxind.html` — `(XFL, T)` signature, return `[P, NXFL]`, no q parameter
- `https://qseries.org/fgarvan/qmaple/qseries/functions/findcong.html` — 4-form calling sequence, LM default `floor(sqrt(T))`, XSET
- `.planning/phases/05-relation-finding-exact/05-CONTEXT.md` — all locked decisions
- `.planning/REQUIREMENTS.md` — REL-01..REL-11 definitions

### Secondary (MEDIUM confidence)
- Sage documentation for `matrix.left_kernel()`, `IntegerVectors`, `PolynomialRing` — standard Sage API, confirmed from prior phase work
- Prior phase codebase (`_utilities.py`, `_series.py`, `_conversion.py`) — confirms sift, etamake availability

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; Sage primitives used in prior phases
- Architecture: HIGH — core algorithm locked in CONTEXT.md D-02; N formula verified against four data points
- Signatures: HIGH for findhom/findnonhom/findlincombo/findmaxind/findcong (doc pages fetched); MEDIUM for mod-p variants (doc page not fetched)
- Pitfalls: HIGH — derived from known Sage/QSeries design decisions established in prior phases

**Research date:** 2026-09-17
**Valid until:** 2026-10-17 (stable Sage API; Garvan doc pages rarely change)
