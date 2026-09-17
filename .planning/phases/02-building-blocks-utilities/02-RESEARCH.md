# Phase 2: Building Blocks & Utilities - Research

**Researched:** 2026-09-16
**Domain:** q-product/theta building blocks and series utilities in SageMath
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** `etaq` and `qbin` wrap Sage builtins — `sage.functions.other.qexp_eta` for `etaq`,
  `sage.arith.misc.q_binomial` for `qbin`. Argument-order reordering in the wrapper. Return type is `QSeries`.
- **D-02:** All other building blocks (`aqprod`, `jacprod`, `theta`, `theta2`, `theta3`, `theta4`,
  `tripleprod`, `quinprod`, `winquist`) are reimplemented from the documented math formulas.
  No Sage modular or symbolic machinery used.
- **D-03:** `theta(z, q, T)`, `tripleprod(z, q, T)`, `winquist(a, b, q, T)` accept `z` (and `a`, `b`)
  as Sage symbolic variables that the caller creates externally.
- **D-04:** Bivariate functions return a `QSeries` with `R = LaurentPolynomialRing(QQ, 'z')` (or
  two-variable analogue for `winquist`). The `QSeries` wrapper's `T` and `r` propagate normally.
- **D-05:** `quinprod(z, q, T)` with `T == 'prodid'` or `T == 'seriesid'` returns a plain formatted
  string showing the quintuple product identity.
- **D-06:** When `T` is an integer, `quinprod` returns a `QSeries` (Laurent in z) as normal.
- **D-07:** `checkmult(f)` returns **`bool`** — `True` if all tested coprime pairs satisfy
  `a(mn) = a(m)*a(n)`, `False` otherwise. (Maple returns 1/0; we return True/False.)
- **D-08:** `checkprod(f)` stubbed with `raise NotImplementedError(...)` in Phase 2.
- **D-09:** `checkprod` IS exported in `__init__.py` in Phase 2 (stub).
- **D-10:** Module structure:
  - `qseries/_building_blocks.py` — the 11 building-block functions
  - `qseries/_utilities.py` — extend with `sift`, `checkmult`, `checkprod`, `packageversion`, `changes`
  - `__init__.py` — extend to export all new functions

### Claude's Discretion

- Exact iteration bounds for checking multiplicativity in `checkmult` (which coprime pairs to test,
  up to what bound) — derive from doc page findings.
- Internal variable naming in bivariate functions.
- Exact string format for `quinprod` identity modes — must be readable and correct.
- Whether `packageversion()` reads `__version__` from `__init__.py` or a separate constant.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BUILD-01 | `aqprod(a, q, n)` — finite rising q-factorial `(a;q)_n`; n=0 returns 1; n negative supported | Verified from doc page: formula (1-a)(1-aq)...(1-aq^(n-1)); direct Python product loop |
| BUILD-02 | `qbin(q, m, n)` — Gaussian polynomial; 0 unless 0≤m≤n | Verified: wraps `sage.arith.misc.q_binomial(n, m, q)` with argument reorder |
| BUILD-03 | `etaq(q, k, T)` — `prod_{n≥1}(1-q^{kn})` to O(q^T) | Verified: wraps `sage.functions.other.qexp_eta(q^k, T)` |
| BUILD-04 | `jacprod(a, b, q, T)` — `(q^a;q^b)_∞(q^{b-a};q^b)_∞` to O(q^T) | Verified from doc page: uses triple product internally |
| BUILD-05 | `theta(z, q, T)` — `sum_{i=-T}^{T} z^i q^{i^2}`; bivariate | Verified from doc page formula |
| BUILD-06 | `theta2(q, T)` — `sum q^{(n+1/2)^2}`; fractional shift r=1/4 | Verified from doc page |
| BUILD-07 | `theta3(q, T)` — `sum q^{n^2}` | Verified: doc page shows `2q^64+2q^49+...+2q+1` for T=50 |
| BUILD-08 | `theta4(q, T)` — `sum (-1)^n q^{n^2}` | Verified: doc page shows alternating-sign version |
| BUILD-09 | `tripleprod(z, q, T)` — `sum (-1)^n z^n q^{n(n-1)/2}` (or via product); bivariate | Verified from doc page; `tripleprod(q,q^3,10)` → Euler pentagonal |
| BUILD-10 | `quinprod(z, q, T)` — Watson's quintuple product; T integer → QSeries, T='prodid'/'seriesid' → string | Verified from doc page |
| BUILD-11 | `winquist(a, b, q, T)` — Winquist's identity; bivariate in a and b | Verified from doc page: 8-factor product |
| UTIL-01 | `sift(s, q, n, k, T)` — extract `sum a_{ni+k} q^i` from `s` | Verified from doc page |
| UTIL-02 | `qdegree(f)` — degree in q (already implemented in Phase 1) | Verify export only |
| UTIL-03 | `lqdegree(f, ...)` — lowest degree in q of a q-polynomial | Verified from doc page; already implemented |
| UTIL-04 | `lqdegree0(f, ...)` — lowest degree of a q-monomial | Verified from doc page; already implemented |
| UTIL-05 | `checkmult(QS, T [, x])` — test multiplicativity; returns True/False | Verified: signature `checkmult(QS, T)` or `checkmult(QS, T, "yes"/"no")` |
| UTIL-06 | `checkprod(f, M, Q)` — stub raises NotImplementedError | Verified: real signature is `checkprod(f, M, Q)` |
| UTIL-07 | `packageversion()` — version string | Verified: returns non-empty string |
| UTIL-08 | `changes()` — prints changelog | Verified: prints list of recent changes |
</phase_requirements>

---

## Summary

Phase 2 implements 11 building-block q-series functions and extends 8 utility functions. The building blocks divide cleanly into two groups: two Sage-primitive wrappers (`etaq`, `qbin`) and nine formula-based implementations (`aqprod`, `jacprod`, `theta`, `theta2`, `theta3`, `theta4`, `tripleprod`, `quinprod`, `winquist`). Three utilities (`qdegree`, `lqdegree`, `lqdegree0`) were completed in Phase 1 and need only export verification and tests; five new utilities (`sift`, `checkmult`, `checkprod` stub, `packageversion`, `changes`) must be added.

The most technically subtle items are the bivariate functions (`theta`, `tripleprod`, `winquist`, `quinprod`), which must work over a two-variable ring, and `theta2`, which requires a fractional q-power shift (r=1/4). The `checkmult` signature was previously [?]; it is now resolved: `checkmult(QS, T)` or `checkmult(QS, T, "yes")`. The `checkprod` signature is also resolved: `checkprod(f, M, Q)`, but it is stubbed in this phase. All doc page signatures are verified (HIGH confidence).

**Primary recommendation:** Implement building blocks in `_building_blocks.py` using direct formula loops over the ring `LaurentSeriesRing(R, 'q')` — no advanced Sage machinery. For bivariate functions, construct a two-variable parent and wrap in `QSeries` with `R = LaurentPolynomialRing(QQ, 'z')`.

---

## Standard Stack

### Core (from Phase 1 — carry forward)
| Component | Version | Purpose |
|-----------|---------|---------|
| SageMath | 10.x | LaurentSeriesRing, q_binomial, qexp_eta, QQ, GF |
| `sage.all.LaurentSeriesRing` | — | Series ring for all building blocks |
| `sage.all.LaurentPolynomialRing` | — | Base ring R for bivariate functions |
| `sage.arith.misc.q_binomial` | — | Backing for `qbin` |
| `sage.functions.other.qexp_eta` | — | Backing for `etaq` |
| pytest | — | Test runner via `sage -python -m pytest` |

### What NOT to Use (from CLAUDE.md)
- SymPy, NumPy/SciPy, Sage's SR (symbolic ring)
- `sage.modular.etaproducts` (off-limits per CLAUDE.md)
- Cython

---

## Architecture Patterns

### Recommended Project Structure
```
qseries/
├── _series.py           # QSeries wrapper (Phase 1, done)
├── _symbolic.py         # EtaProduct, JacProduct, etc. (Phase 1, done)
├── _utilities.py        # qdegree/lqdegree done; extend with sift, checkmult, etc.
├── _building_blocks.py  # NEW: 11 building-block functions
└── __init__.py          # Extend __all__ with all new names
```

### Pattern 1: Sage Primitive Wrapper
**What:** Delegate to a Sage builtin with argument reordering; wrap result in `QSeries`.
**When to use:** `etaq` (wraps `qexp_eta`), `qbin` (wraps `q_binomial`).

```python
# etaq: Maple calls etaq(q, k, T); Sage: qexp_eta(q^k, T)
from sage.functions.other import qexp_eta
from sage.all import LaurentSeriesRing, QQ

def etaq(q, k, T):
    R = LaurentSeriesRing(QQ, 'q')
    qvar = R.gen()
    raw = qexp_eta(qvar**k, T)
    return QSeries(raw, T=T)
```

```python
# qbin: Maple calls qbin(q, m, n); Sage: q_binomial(n, m, q)
from sage.arith.misc import q_binomial
from sage.all import LaurentSeriesRing, QQ

def qbin(q, m, n):
    if not (0 <= m <= n):
        return QSeries(LaurentSeriesRing(QQ, 'q').zero(), T=0)
    R = LaurentSeriesRing(QQ, 'q')
    raw = R(q_binomial(n, m, R.gen()))
    return QSeries(raw, T=n)
```

### Pattern 2: Formula Loop
**What:** Build the series term-by-term from the mathematical definition using a loop.
**When to use:** `aqprod`, `jacprod`, `theta`, `theta2`, `theta3`, `theta4`, `tripleprod`, `winquist`.

```python
# aqprod(a, q, n) = product_{i=0}^{n-1} (1 - a*q^i)
def aqprod(a, q, n):
    R = LaurentSeriesRing(QQ, 'q')
    result = R.one()
    qvar = R.gen()
    # a and q are passed as series or symbolic — caller works in same ring
    for i in range(n):
        result *= (1 - a * qvar**i)
    return QSeries(result.add_bigoh(n + 1), T=n + 1)
```

### Pattern 3: Bivariate Ring Construction
**What:** Use `LaurentPolynomialRing(QQ, 'z')` as base ring R, then build `LaurentSeriesRing(R, 'q')`.
**When to use:** `theta(z, q, T)`, `tripleprod(z, q, T)`, `quinprod(z, q, T)`, `winquist(a, b, q, T)`.

```python
# theta(z, q, T) = sum_{i=-T}^{T} z^i * q^{i^2}
from sage.all import LaurentPolynomialRing, LaurentSeriesRing, QQ

def theta(z, q, T):
    Rz = LaurentPolynomialRing(QQ, 'z')
    zvar = Rz.gen()
    Rq = LaurentSeriesRing(Rz, 'q')
    qvar = Rq.gen()
    result = Rq.zero()
    for i in range(-T, T + 1):
        result += zvar**i * qvar**(i*i)
    return QSeries(result.add_bigoh(T*T + 1), T=T*T + 1, R=Rz)
```

### Pattern 4: Fractional Shift (theta2)
**What:** Store q^(1/4) factor in `QSeries.r`; series itself starts with integer powers.
**When to use:** `theta2` only.

```python
# theta2(q, T) = sum_{n=-inf}^{inf} q^{(n+1/2)^2}
# Smallest exponent: n=0 → q^(1/4); factor out q^(1/4), series has integer powers
def theta2(q, T):
    R = LaurentSeriesRing(QQ, 'q')
    qvar = R.gen()
    result = R.zero()
    n = 0
    # (n+1/2)^2 - 1/4 = n^2 + n is an integer; collect integer-power part
    while True:
        exp_pos = (n + QQ(1,2))**2  # positive n
        exp_neg = (-n - QQ(1,2) + QQ(1,2))**2  # (-(n+1)+1/2)^2 = (−n−1/2)^2 same magnitude
        # Both n and -(n+1) give exponent (n+1/2)^2
        # After extracting q^(1/4): integer part = n^2 + n
        if n*n + n >= T:
            break
        if n == 0:
            result += qvar**0  # constant term = 1 (q^(1/4) * q^0)
        else:
            result += 2 * qvar**(n*n + n)
        n += 1
    return QSeries(result.add_bigoh(T), T=T, r=QQ(1, 4))
```

### Pattern 5: checkmult — Coprime Pair Testing
**What:** Extract coefficients from QSeries, test `a(m*n) == a(m) * a(n)` for coprime pairs `(m, n)` with `m*n <= T`.
**Resolved signature:** `checkmult(QS, T)` or `checkmult(QS, T, "yes")` (verbose mode prints failures).
**Return value:** `True` (multiplicative) or `False` (not multiplicative). D-07: return Python bool, not Maple's 1/0.

```python
from math import gcd

def checkmult(QS, T, x=None):
    coeffs = {i: QS.series[i] for i in range(1, T + 1)}
    verbose = (x == "yes")
    is_mult = True
    for m in range(1, T + 1):
        for n in range(m + 1, T + 1):
            if m * n > T:
                break
            if gcd(m, n) != 1:
                continue
            lhs = coeffs.get(m * n, 0)
            rhs = coeffs.get(m, 0) * coeffs.get(n, 0)
            if lhs != rhs:
                if not verbose:
                    return False
                is_mult = False
    return is_mult
```

### Pattern 6: sift
**What:** Given `s = sum a[i] q^i`, return `sum a[n*i+k] q^i` using coefficient extraction.

```python
def sift(s, q, n, k, T):
    R = LaurentSeriesRing(QQ, 'q')
    qvar = R.gen()
    result = R.zero()
    for i in range(T // n + 1):
        idx = n * i + k
        if idx < s.series.prec():
            coeff = s.series[idx]
            result += coeff * qvar**i
    T_out = T // n
    return QSeries(result.add_bigoh(T_out + 1), T=T_out + 1)
```

### Anti-Patterns to Avoid

- **Using `sage.modular.etaproducts`:** Off-limits per CLAUDE.md; different API surface.
- **PowerSeriesRing instead of LaurentSeriesRing:** QSeries requires Laurent (supports negative exponents in r).
- **Calling `aqprod` with Python ints when series ring is needed:** Must ensure `a` and `q` are series elements or the result ring is correct.
- **Building bivariate result in `LaurentSeriesRing(QQ, 'q')` for theta:** Loses the z-dependence; must use two-variable ring.
- **Returning Maple's 1/0 from checkmult:** Decision D-07 says return Python bool.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| q-Pochhammer rising factorial (finite product) | Custom special-case code | Direct loop using the `(a;q)_n` formula |
| q-binomial coefficients | Custom Gaussian polynomial computation | `sage.arith.misc.q_binomial(n, m, q)` |
| Dedekind eta product | Custom pentagonal-number loop | `sage.functions.other.qexp_eta(q^k, T)` |
| Series truncation | Manual slice of coefficient list | `.add_bigoh(T)` on Sage LaurentSeries |
| GCD check in checkmult | Custom gcd | Python `math.gcd` |

---

## Resolved Unknowns (Previously [?])

### checkmult — UTIL-05
**Resolved signature:** `checkmult(QS, T)` or `checkmult(QS, T, x)` where `x = "yes"` enables verbose mode.
**Return:** Maple returns `1` (multiplicative) or `0` (not). Phase 2 returns Python `True`/`False` per D-07.
**Pairs checked:** All coprime pairs `(m, n)` with `m < n` and `m*n <= T`. Doc page example shows pairs like (3,2), (5,2), (2,3), etc. for T=30.
**Confidence:** HIGH (fetched from doc page).

### checkprod — UTIL-06
**Resolved signature:** `checkprod(f, M, Q)`.
- `f`: q-series
- `M`: max allowed |exponent| in prodmake expansion
- `Q`: number of exponents to compute
**Return:** `[c, n]` where `c` is lowest q-power and `n` is count of exponents with |exp| < M. Maple returns a list; Phase 2 stub raises `NotImplementedError` per D-08.
**Confidence:** HIGH (fetched from doc page).

### lqdegree / lqdegree0 — UTIL-03/04
Both already implemented in `_utilities.py`. Doc page confirms:
- `lqdegree(qexp)`: lowest exponent in a sum of q-monomials; fractional OK.
- `lqdegree0`: q-degree of a single monomial; reads `.r` attribute.
**Action:** Verify exports and write tests only — no new code.
**Confidence:** HIGH.

---

## Function Signatures (Garvan canonical, verified)

| Function | Maple Signature | Notes |
|----------|----------------|-------|
| `aqprod` | `aqprod(a, q, n)` | n=0 → 1; n<0 supported (v1.3) |
| `qbin` | `qbin(q, m, n)` | Returns 0 unless 0≤m≤n |
| `etaq` | `etaq(q, a, T)` | No q^(1/24) factor |
| `jacprod` | `jacprod(a, b, q, T)` | a,b are positive integers |
| `theta` | `theta(z, q, T)` | sum i=-T..T of z^i q^{i^2} |
| `theta2` | `theta2(q, T)` | r=1/4 shift |
| `theta3` | `theta3(q, T)` | sum n^2 |
| `theta4` | `theta4(q, T)` | alternating sign |
| `tripleprod` | `tripleprod(z, q, T)` | Laurent in z |
| `quinprod` | `quinprod(a, b, q, T)` | Note: doc page shows 4 args (a,b,q,T); T = int or 'prodid'/'seriesid' |
| `winquist` | `winquist(a, b, q, T)` | 8-factor product; bivariate in a,b |
| `sift` | `sift(s, q, n, k, T)` | Extract residue class n*i+k |
| `checkmult` | `checkmult(QS, T [, x])` | x="yes" for verbose |
| `checkprod` | `checkprod(f, M, Q)` | Stub only |
| `packageversion` | `packageversion()` | Returns version string |
| `changes` | `changes()` | Prints changelog |

**Important quinprod note:** The doc page signature shows `quinprod(a, b, q, T)` with 4 parameters (two symbolic variables `a` and `b`, plus `q` and `T`). The CONTEXT.md shows `quinprod(z, q, T)` — this is a discrepancy. The planner must verify by checking the doc page; the 4-argument form matches Watson's identity which involves two variables. **Treat as `quinprod(a, b, q, T)` with T being integer or string identifier.**

---

## Mathematical Formulas (Verified)

### aqprod
`(a;q)_n = prod_{i=0}^{n-1} (1 - a*q^i)`, `(a;q)_0 = 1`, `(a;q)_{-n} = 1/(a;q)_n`.

### etaq
`etaq(q, k, T) = prod_{n>=1} (1 - q^{kn})` to O(q^T). Wraps `qexp_eta(q^k, T)`.

### jacprod
`jacprod(a, b, q, T) = (q^a; q^b)_inf * (q^{b-a}; q^b)_inf` to O(q^T). Uses triple product internally.

### theta
`theta(z, q, T) = sum_{i=-T}^{T} z^i * q^{i^2}`. Bivariate Laurent series.

### theta2
`theta2(q, T) = sum_{n=-inf}^{inf} q^{(n+1/2)^2}`. Written as `q^(1/4) * (1 + 2*q^2 + 2*q^6 + 2*q^12 + ...)` where exponents after 1/4 are n^2+n for n=1,2,3,...

### theta3
`theta3(q, T) = sum_{n=-inf}^{inf} q^{n^2}`. Doc page example: `theta3(q,50)` → `2q^64+2q^49+2q^36+2q^25+2q^16+2q^9+2q^4+2q+1`.

### theta4
`theta4(q, T) = sum_{n=-inf}^{inf} (-1)^n q^{n^2}`. Doc page example: `theta4(q,50)` → `2q^64-2q^49+2q^36-2q^25+2q^16-2q^9+2q^4-2q+1`.

### tripleprod
`tripleprod(z, q, T) = prod_{i=1}^{inf} (1-z*q^{i-1})(1-q^i/z)(1-q^i)` to O(q^T). Also equals `sum_{n=-inf}^{inf} (-1)^n z^n q^{n(n-1)/2}` via triple product identity.

The Euler pentagonal series: `tripleprod(q, q^3, T) = sum_{n=-inf}^{inf} (-1)^n q^{n(3n-1)/2}` = `1 - q - q^2 + q^5 + q^7 - q^12 - q^15 + ...`

### winquist
`winquist(a,b,q,T) = (a;q)_inf * (q/a;q)_inf * (b;q)_inf * (q/b;q)_inf * (ab;q)_inf * (q/(ab);q)_inf * (a/b;q)_inf * (b/(aq);q)_inf * (q;q)_inf^2`. When a=b=1: `1 - 10q + 35q^2 - 30q^3 - 105q^4 + 238q^5 - ...`

---

## Common Pitfalls

### Pitfall 1: aqprod with `a` as a series element vs. Python int
**What goes wrong:** When `a = q` (the generator), calling `aqprod(q_py_var, q_py_var, n)` where both are Python variables pointing to the same Sage series element works fine, but if `a` is an integer, the ring multiplication may produce a constant instead of a series.
**How to avoid:** Accept `a` and `q` as Sage series elements from within the same `LaurentSeriesRing`. Let the caller (or the function) define the ring, then coerce `a` and `q` appropriately.
**Warning signs:** `TypeError: unsupported operand type` when multiplying int by LaurentSeries.

### Pitfall 2: theta2 fractional exponent
**What goes wrong:** `LaurentSeriesRing` does not support fractional q-powers directly. Building `theta2` by summing `q^{(n+1/2)^2}` in the series ring fails because `(n+1/2)^2` is not an integer.
**How to avoid:** Factor out `q^(1/4)`. Build the series with integer-power terms only (exponent = n^2+n for n=0,1,2,...; coefficient 2 for n>=1, 1 for n=0). Store `r=QQ(1,4)` in the `QSeries` wrapper.
**Warning signs:** `TypeError: exponent must be integer` when building the series.

### Pitfall 3: Bivariate ring mismatch
**What goes wrong:** Passing `z = var('z')` (a Sage symbolic variable) into a `LaurentSeriesRing(QQ, 'q')` fails — the ring doesn't know about `z`.
**How to avoid:** Construct `Rz = LaurentPolynomialRing(QQ, 'z')` first, then `Rq = LaurentSeriesRing(Rz, 'q')`. Use `Rz.gen()` for z inside the function, not the caller's symbolic `z`. OR: define the function to accept `z` as a `Rz`-element, with a clear docstring.
**Warning signs:** `TypeError: cannot coerce` or coefficient type errors.

### Pitfall 4: qexp_eta argument
**What goes wrong:** `qexp_eta(q, T)` computes `prod(1-q^n)`. For `etaq(q, k, T)` we need `prod(1-q^{kn})`. Passing `q` directly gives `etaq(q, 1, T)` regardless of `k`.
**How to avoid:** Pass `q^k` (i.e., `qvar**k`) as the first argument to `qexp_eta`.

### Pitfall 5: q_binomial argument order
**What goes wrong:** Maple's `qbin(q, m, n)` has lower index `m` second; Sage's `q_binomial(n, k, q)` has them in the opposite order.
**How to avoid:** In the wrapper: `q_binomial(n, m, q)` — pass `n` first, `m` second.

### Pitfall 6: checkmult returning 0/1 vs True/False
**What goes wrong:** Maple returns `1`/`0`; if we return those integers, `if checkmult(...):` still works but `checkmult(...) == True` fails.
**How to avoid:** Return Python `bool` as specified in D-07.

### Pitfall 7: sift index out of series precision
**What goes wrong:** Accessing `s.series[idx]` for `idx >= s.series.prec()` raises an error or returns 0 incorrectly.
**How to avoid:** Guard with `if idx < s.series.prec()` before extracting the coefficient.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | `pyproject.toml` (if configured) or default discovery |
| Quick run command | `sage -python -m pytest tests/test_building_blocks.py -x` |
| Full suite command | `sage -python -m pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Test Exists? |
|--------|----------|-----------|-------------------|-------------|
| BUILD-01 | `aqprod(q,q,6)` = (1-q)(1-q^2)...(1-q^6) | unit | `pytest tests/test_building_blocks.py::test_aqprod -x` | ❌ Wave 0 |
| BUILD-01 | `aqprod(-q,q,n)` (tutorial canonical) | unit | same file | ❌ Wave 0 |
| BUILD-01 | `aqprod(z,q,0) == 1` | unit | same file | ❌ Wave 0 |
| BUILD-02 | `qbin(q,3,6)` coefficients match doc page | unit | `pytest tests/test_building_blocks.py::test_qbin -x` | ❌ Wave 0 |
| BUILD-02 | `qbin(q,0,n) == 1`, `qbin(q,n,n) == 1` | unit | same file | ❌ Wave 0 |
| BUILD-02 | `qbin(q,4,3) == 0` (m > n) | unit | same file | ❌ Wave 0 |
| BUILD-03 | `etaq(q,2,100)` first terms match doc page | unit | `pytest tests/test_building_blocks.py::test_etaq -x` | ❌ Wave 0 |
| BUILD-04 | `1/jacprod(1,5,q,10)` coefficients match doc page | unit | `pytest tests/test_building_blocks.py::test_jacprod -x` | ❌ Wave 0 |
| BUILD-05 | `theta(-1,q,10)` matches doc page output | unit | `pytest tests/test_building_blocks.py::test_theta -x` | ❌ Wave 0 |
| BUILD-06 | `theta2(q,50)` r == QQ(1,4) and series terms correct | unit | `pytest tests/test_building_blocks.py::test_theta2 -x` | ❌ Wave 0 |
| BUILD-07 | `theta3(q,50)` == `2q^64+...+2q+1` | unit | `pytest tests/test_building_blocks.py::test_theta3 -x` | ❌ Wave 0 |
| BUILD-07 | `theta3(q,20)*theta4(q,20)` product identity | unit | same file | ❌ Wave 0 |
| BUILD-08 | `theta4(q,50)` == `2q^64-2q^49+...+1` | unit | `pytest tests/test_building_blocks.py::test_theta4 -x` | ❌ Wave 0 |
| BUILD-09 | `tripleprod(q,q**3,10)` → Euler pentagonal series | unit | `pytest tests/test_building_blocks.py::test_tripleprod -x` | ❌ Wave 0 |
| BUILD-10 | `quinprod(a,b,q,5)` matches expansion | unit | `pytest tests/test_building_blocks.py::test_quinprod -x` | ❌ Wave 0 |
| BUILD-10 | `quinprod(a,b,q,'prodid')` returns non-empty string | unit | same file | ❌ Wave 0 |
| BUILD-11 | `winquist(1,1,q,30)` first 6 coefficients match doc | unit | `pytest tests/test_building_blocks.py::test_winquist -x` | ❌ Wave 0 |
| UTIL-01 | `sift(etaq(q,1,500), q, 5, 0, 499)` matches E0 | integration | `pytest tests/test_utilities.py::test_sift_e0 -x` | ❌ Wave 0 |
| UTIL-02 | `qdegree` exported from `qseries` | unit | `pytest tests/test_utilities.py::test_exports -x` | ❌ Wave 0 |
| UTIL-03 | `lqdegree` exported and correct | unit | same file | ❌ Wave 0 |
| UTIL-04 | `lqdegree0` exported and correct | unit | same file | ❌ Wave 0 |
| UTIL-05 | `checkmult(f, T)` on multiplicative f returns True | unit | `pytest tests/test_utilities.py::test_checkmult -x` | ❌ Wave 0 |
| UTIL-05 | `checkmult(f, T)` on non-multiplicative f returns False | unit | same file | ❌ Wave 0 |
| UTIL-06 | `checkprod(...)` raises NotImplementedError | unit | `pytest tests/test_utilities.py::test_checkprod_stub -x` | ❌ Wave 0 |
| UTIL-07 | `packageversion()` returns non-empty string | unit | `pytest tests/test_utilities.py::test_packageversion -x` | ❌ Wave 0 |
| UTIL-08 | `changes()` returns non-empty string | unit | `pytest tests/test_utilities.py::test_changes -x` | ❌ Wave 0 |

### Expected Oracle Values (from Garvan documentation)

- `theta3(q, 50)` → `2*q^64 + 2*q^49 + 2*q^36 + 2*q^25 + 2*q^16 + 2*q^9 + 2*q^4 + 2*q + 1`
- `theta4(q, 50)` → `2*q^64 - 2*q^49 + 2*q^36 - 2*q^25 + 2*q^16 - 2*q^9 + 2*q^4 - 2*q + 1`
- `qbin(q, 3, 6)` expanded: `q^9+q^8+2q^7+3q^6+3q^5+3q^4+3q^3+2q^2+q+1`
- `winquist(1, 1, q, 30)` first 6 terms: `1 - 10q + 35q^2 - 30q^3 - 105q^4 + 238q^5 - ...`
- `tripleprod(q, q**3, T)` Euler pentagonal: `1 - q - q^2 + q^5 + q^7 - q^12 - q^15 + ...`
  (exponents: 0,1,2,5,7,12,15,22,26,... = n(3n±1)/2 for n=0,1,2,...)

**theta3 * theta4 identity:** `theta3(q,T) * theta4(q,T)` should match `theta4(q^2, T//2) * ... ` — use the identity `theta3(q)*theta4(q) = theta4(q^2)^2` to verify to order T (this is a known identity that the success criteria mentions).

### Sampling Rate
- **Per task commit:** `sage -python -m pytest tests/test_building_blocks.py tests/test_utilities.py -x`
- **Per wave merge:** `sage -python -m pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_building_blocks.py` — covers BUILD-01 through BUILD-11
- [ ] `tests/test_utilities.py` — covers UTIL-01 through UTIL-08 (including export tests for UTIL-02/03/04)
- [ ] `qseries/_building_blocks.py` — new module (does not exist yet)

---

## Open Questions

1. **quinprod argument count**
   - What we know: CONTEXT.md shows `quinprod(z, q, T)` (3 args); the doc page example and Watson's identity involve two symbolic variables and `T`.
   - What's unclear: Is the canonical Maple signature `quinprod(z, q, T)` (z and q are both symbolic) or `quinprod(a, b, q, T)` (4 args)?
   - Recommendation: Fetch `https://qseries.org/fgarvan/qmaple/qseries/functions/quinprod.html` directly and resolve before implementing. If 4-arg, the CONTEXT.md has a typo; implement 4-arg form.

2. **sift E0 expected value**
   - What we know: `sift(etaq(q,1,500), q, 5, 0, 499)` should equal the E0 series from tutorial §6.2.
   - What's unclear: We could not read the tutorial PDF to get the specific coefficient values.
   - Recommendation: Use the identity `E0 = eta(q^5)^5 / eta(q)` as an oracle — compute both independently and assert equality to order 499//5 = 99.

3. **aqprod with infinite n**
   - What we know: REQUIREMENTS.md BUILD-01 notes "check whether n = infinity is accepted".
   - What's unclear: The doc page says n is a positive integer (or negative as of v1.3), but does not explicitly say infinity is supported.
   - Recommendation: Treat n as always a finite integer in Phase 2 (infinite product = etaq territory). Document as v1 scope.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| SageMath | All functions | Assumed present (Phase 1 completed) | 10.x | None |
| `sage.arith.misc.q_binomial` | `qbin` | Assumed (Sage 10.x) | — | Roll from formula |
| `sage.functions.other.qexp_eta` | `etaq` | Assumed (Sage 10.x) | — | Roll pentagonal loop |
| `pytest` | Tests | Assumed (Phase 1 tests ran) | — | None |
| `math.gcd` | `checkmult` | Python stdlib | — | None |

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| Manual q-product loops | `qexp_eta` for etaq, `q_binomial` for qbin | Correctness guaranteed by Sage |
| Global Maple precision | Explicit T per call | No hidden global state |
| Maple 1/0 return from checkmult | Python True/False | Pythonic and consistent |

---

## Project Constraints (from CLAUDE.md)

1. **Runtime:** SageMath (Python 3) plus pure-Python PyPI packages only.
2. **Interface fidelity:** Names and argument order match Garvan's qseries 1.3.
3. **Testing:** `pytest` under `sage -python -m pytest`; every function has a test traceable to a documented example (never to this package's own output).
4. **Do NOT use:** SymPy, NumPy/SciPy, Sage's SR ring, `sage.modular.etaproducts`, Cython.
5. **Do NOT use** `sage.modular.etaproducts` for any building block.
6. **GSD Workflow:** All file changes go through a GSD command.

---

## Sources

### Primary (HIGH confidence)
- [QSERIES Functions Index](https://qseries.org/fgarvan/qmaple/qseries/functions/) — all function signatures confirmed
- [aqprod doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/aqprod.html) — formula, signature, n=0/negative behavior
- [checkmult doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/checkmult.html) — full signature, return value, pairs checked
- [checkprod doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/checkprod.html) — full signature (f, M, Q), return value
- [etaq doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/etaq.html) — confirmed formula and signature
- [jacprod doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/jacprod.html) — confirmed formula
- [theta doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/theta.html) — confirmed formula
- [theta2 doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/theta2.html) — confirmed r=1/4 fractional shift
- [theta3 doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/theta3.html) — oracle values confirmed
- [theta4 doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/theta4.html) — oracle values confirmed
- [tripleprod doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/tripleprod.html) — formula confirmed
- [quinprod doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/quinprod.html) — 4-arg signature confirmed (a,b,q,T)
- [winquist doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/winquist.html) — formula and oracle values confirmed
- [sift doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/sift.html) — signature confirmed
- [qbin doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/qbin.html) — signature and oracle values confirmed
- [lqdegree doc page](https://qseries.org/fgarvan/qmaple/qseries/functions/lqdegree.html) — confirmed existing implementation

### Secondary (MEDIUM confidence)
- `_series.py`, `_utilities.py`, `__init__.py` — existing code read directly (HIGH for what's implemented)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Phase 1 established; no new libraries needed
- Architecture: HIGH — module structure resolved in CONTEXT.md; all signatures verified from doc pages
- Pitfalls: HIGH — derived from mathematical constraints and ring API knowledge
- checkmult/checkprod: HIGH — fetched from doc pages; previously [?], now resolved
- quinprod arg count: MEDIUM — doc page says 4 args but CONTEXT.md says 3; flag for planner

**Research date:** 2026-09-16
**Valid until:** 2026-10-16 (stable math library, slow-changing docs)
