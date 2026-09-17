# Phase 4: Product Conversion - Research

**Researched:** 2026-09-16
**Domain:** q-series product identification and expansion (eta products, Jacobi products, qfactor)
**Confidence:** MEDIUM-HIGH (doc pages fetched for all 10 functions; PDF tutorial inaccessible directly)

## Summary

Phase 4 implements 10 product-conversion functions in a new `qseries/_conversion.py` module,
building on `prodmake` (Phase 3) and the five symbolic output types already in `_symbolic.py`.
The functions divide cleanly into three groups: eta-family (`etamake`, `qetamake`), jac-family
(`jacprodmake`, `jac2prod`, `jac2series`, `qs2jaccombo`), and misc (`mprodmake`, `qfactor`,
`zqfactor`, `findprod`).

All previously [?]-marked signatures are now resolved from the Garvan doc pages. The most
important finding for phase assignment: `findprod` does **not** use relation-finding linear
algebra — it performs exhaustive search via `checkprod`. It belongs in Phase 4 (Plan 04-03),
not Phase 5.

`zqfactor` is bivariate in `(z, q)` with an unusual 3/4-arg signature and an explicit caveat
that it does not always succeed — plan must document this as a best-effort function.

**Primary recommendation:** Implement in three plans as decided: 04-01 (eta), 04-02 (jac-core),
04-03 (misc + search). All 10 functions stay in Phase 4.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** All 10 functions go into `qseries/_conversion.py`.
- **D-02:** Three plans — 04-01 (`etamake`+`qetamake`), 04-02 (jac-family), 04-03 (misc/unknowns).
  `findprod` stays in Phase 4 if researcher confirms no relation-finding needed (confirmed below).
- **D-03:** Unknown signatures resolved from doc pages before planner writes Plan 04-03.
- **D-04:** `etamake` greedy algorithm: strip q-prefix, find lowest non-unit coefficient, multiply
  by `etaq(q,k,T)^(c_k)` to cancel, record `eta(k*tau)^(-c_k)`, repeat until residual = 1.
  Termination guaranteed in ≤ T-1 steps. No `ValueError` on non-clean products.
- **D-05:** `etamake` must reproduce: `theta3→eta(2τ)^5/(eta(4τ)²eta(τ)²)`,
  `theta2→2·q^(-1/4)·eta(4τ)²/eta(2τ)`, `theta4→eta(τ)²/eta(2τ)`.
- **D-06:** `qfactor(f [,T])` accepts Sage polynomial or rational function in `PolynomialRing(QQ,'q')`.
- **D-07:** `qfactor` returns rich structured result: `(numerator QProduct, denominator QProduct, q^r prefactor)`.
- **D-08:** `jacprodmake` period detection + optional 4th arg P; rational exponents via `JacProduct`.
- **D-09:** `findprod` phase assignment — RESEARCHER RESOLVED: stays in Phase 4 (no linear algebra).

### Claude's Discretion

- Exact return type container for `qfactor` (namedtuple vs dataclass vs tuple).
- Whether `qs2jaccombo` and `findprod` belong in Plan 04-02 or 04-03.
- Edge-case handling for `zqfactor` and `mprodmake`.

### Deferred Ideas (OUT OF SCOPE)

- None raised during discussion.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CONV-02 | `etamake(f, q, T)` — greedy eta-product identification | D-04/D-05; doc page confirms signature and two examples |
| CONV-03 | `qetamake(f, q, T)` — same search, `_E(q^k)` output, no fractional q-shift | Doc page example: triangular-number series → `_E(q²)²/_E(q)` |
| CONV-04 | `jacprodmake(f, q, T [, P])` — periodicity detection, rational exponents | Doc page confirms 4-arg form; P restricts search to divisors of P |
| CONV-05 | `mprodmake(f, q, T)` — write f as `(1+q^n1)(1+q^n2)…` | Signature RESOLVED: same 3 args as prodmake; oracle confirmed |
| CONV-06 | `qfactor(f [, T])` — factor polynomial/rational into `(1-q^i)` terms | PDF oracle inaccessible; doc page confirms signature and semantics |
| CONV-07 | `zqfactor(F, z, q [, N])` — bivariate analogue | Signature RESOLVED; best-effort, may fail |
| CONV-08 | `jac2prod(jacexpr)` — `JacProduct` → `PochProduct` | Full conversion rules confirmed from doc page |
| CONV-09 | `jac2series(jacexpr, T)` — `JacProduct` → series product | Signature and substitution formula confirmed |
| CONV-10 | `qs2jaccombo(f, q, T [, P])` — sum of series → sum of `JacProduct`s | Signature RESOLVED: 3 or 4 args, delegates to `jacprodmake` per term |
| CONV-11 | `findprod(FL, T, M, Q)` — exhaustive search for nice q-products | Signature RESOLVED: 4 args; exhaustive search, NOT linear algebra |
</phase_requirements>

---

## Standard Stack

### Core (all already present)
| Library | Purpose |
|---------|---------|
| `sage.all.QQ`, `sage.all.ZZ` | Exact arithmetic for exponents and coefficients |
| `sage.all.divisors` | Used in prodmake; re-used for period detection |
| `sage.all.PolynomialRing(QQ, 'q')` | Input type for `qfactor` |
| `qseries._prodmake.prodmake` | Core dependency for etamake, qetamake, jacprodmake, findprod |
| `qseries._building_blocks.etaq` | Used inside etamake greedy loop |
| `qseries._symbolic.*` | Return types: EtaProduct, EProduct, JacProduct, PochProduct, QProduct |
| `qseries._series.QSeries` | Return type for jac2series, mprodmake expansions |

### No New Dependencies
All Phase 4 work uses existing Sage primitives and project modules.

**Installation:** No new packages needed.

---

## Architecture Patterns

### New File
```
qseries/
├── _conversion.py      # all 10 new functions (D-01)
├── _symbolic.py        # EtaProduct, EProduct, JacProduct, PochProduct, QProduct — already done
├── _prodmake.py        # prodmake — already done
├── _building_blocks.py # etaq, jacprod, theta* — already done
└── __init__.py         # extend __all__ with all 10 new names
tests/
└── test_conversion.py  # new; oracle values from Maple doc pages only
```

### Plan Grouping

**Plan 04-01: eta-family**
- `etamake(f, q, T)` → `EtaProduct`
- `qetamake(f, q, T)` → `EProduct`

**Plan 04-02: jac-family**
- `jacprodmake(f, q, T [, P])` → `JacProduct`
- `jac2prod(jacexpr)` → `PochProduct`
- `jac2series(jacexpr, T)` → `QSeries`

**Plan 04-03: misc/search**
- `mprodmake(f, q, T)` → symbolic product of `(1+q^n)` factors (new lightweight class or repr)
- `qfactor(f [, T])` → structured result (numerator QProduct, denominator QProduct, q-shift)
- `zqfactor(F, z, q [, N])` → structured result or best-effort repr
- `qs2jaccombo(f, q, T [, P])` → sum of `JacProduct`s
- `findprod(FL, T, M, Q)` → list of coefficient lists for found products

---

## Resolved Unknown Signatures

### CONV-05: `mprodmake`

**Signature:** `mprodmake(f, q, T)`

Same 3-argument pattern as `prodmake` and `etamake`.

**Algorithm:** Greedy product factorization into `(1+q^n)` terms. At each step find the lowest
non-unit term in the residual; multiply by `(1+q^k)^(-c_k)` to cancel. Similar to etamake but
factors are `(1+q^n)` not `(1-q^n)`.

**Oracle from doc page:**
```
EP := etaq(q,2,100)^2/etaq(q,4,100)/etaq(q,1,100)
mprodmake(EP, q, 17)
→ (1+q)(1+q^3)(1+q^5)(1+q^7)(1+q^9)(1+q^11)(1+q^13)(1+q^15)(1+q^17)
```
This series is related to the Jacobi triple product; the odd-indexed factors confirm the
well-known identity `prod_{n>=1}(1+q^(2n-1)) = eta(2tau)^2/(eta(tau)*eta(4tau))`.

**Return type:** A new lightweight symbolic class `MProduct` (list of integer exponents `n` where
`(1+q^n)` appears) or simply a formatted string — planner's discretion per D-01 pattern.

**Confidence:** HIGH (doc page example fetched directly).

---

### CONV-07: `zqfactor`

**Signature:** `zqfactor(F, z, q)` or `zqfactor(F, z, N)` where N is max number of terms (default 1000).

Note: The doc page shows the 4-argument form is actually `zqfactor(F, z, q, N)` based on the
example — planner should implement as `zqfactor(F, z, q, N=1000)`.

**Algorithm:** Factor a (z,q)-series into products of `(1 - a[i,j] z^i q^j)` where `a[i,j]` is
an integer. **Best-effort**: the doc page explicitly warns "This function does not work all the
time." Return the factored form when found; raise a warning (not ValueError) when exhausted.

**Input:** `F` is a bivariate Laurent series whose coefficients in `q` are polynomials in `z`,
consistent with the FOUND-01 bivariate `LaurentSeriesRing(Rz, 'q')` pattern.

**Oracle from doc page:**
```
L1 := tripleprod(-z^2*q^3, q^4, 20)
L2 := tripleprod(-z^2*q, q^4, 20)
g  := L1 - L2/z
zqfactor(g, z, q, 10)
→ product with factors (1-z*q), (1-q), (1-q/z), etc.
```

**Confidence:** MEDIUM (signature resolved; exact output not fully extracted from doc page).

---

### CONV-10: `qs2jaccombo`

**Signature:** `qs2jaccombo(f, q, T)` or `qs2jaccombo(f, q, T, P)`

**Algorithm:** "Converts each term in a sum to a jacprod if possible using jacprodmake." The
function iterates over additive terms in `f`, calls `jacprodmake` on each (passing `P` if
provided), and assembles a formal sum. If any term cannot be converted, signal failure.

**Return type:** A Python list of `JacProduct` objects (one per additive term in `f`) or a
formal symbolic sum. Since there is no existing sum class, a list is the natural choice.

**Oracle:** The doc page example uses a complicated Choi identity (`CHOIID1`) at T=200; we need
a simpler test. Use `theta3(q,T) + theta4(q,T)` as a two-term sum where each term is known to
be a jacprod (via the theta identities), if confirmed.

**Confidence:** MEDIUM (signature resolved; example oracle needs a simpler case from tutorial).

---

### CONV-11: `findprod`

**Signature:** `findprod(FL, T, M, Q)`

| Param | Type | Meaning |
|-------|------|---------|
| `FL` | list of `QSeries` | series to search through |
| `T`  | int | max absolute value of coefficients in linear combinations |
| `M`  | int | max absolute value of exponents in the formal product |
| `Q`  | int | highest power of q to consider |

**Algorithm:** Exhaustive search — cycles through all possible integer linear combinations
`c_1 * FL[0] + c_2 * FL[1] + … ` with `|c_i| <= T`, then calls `checkprod` on each candidate.
**No linear algebra.** This is brute-force enumeration.

**Phase assignment: STAYS IN PHASE 4.** No relation-finding machinery required.

**Return type:** Nested list — each entry is `[index, coefficient_list]` for a discovered
product. The doc page example returns six such entries for rank generating functions.

**Oracle:** The doc page example uses the rank generating function (`RG`) — complex setup. We
should use a simpler `FL` with one or two known eta products and confirm at least one match.
Given `FL = [etaq(q,1,T)]`, `findprod(FL, 1, 3, 20)` should find `[1, [1]]` (the trivial
product). Plan should include a simpler oracle; researcher flagging the need for a
non-trivial but tractable example.

**Confidence:** MEDIUM (algorithm confirmed as exhaustive search; exact oracle needs design).

---

## Resolved Algorithm Details

### etamake: q-shift Sign Convention for theta2

The critical question from D-04: what is `EtaProduct.r` for `theta2`?

The REQUIREMENTS.md states the result is `2 * q^(-1/4) * eta(4*tau)^2 / eta(2*tau)`.

Working the math:
- `theta2(q, T)` has `r_input = 1/4` (the `q^(1/4)` prefix)
- The greedy loop finds factors `eta(4*tau)^2 * eta(2*tau)^(-1)` with exponents `e_4=2, e_2=-1`
- q-shift from factors: `(4*2 + 2*(-1))/24 = 6/24 = 1/4`
- `EtaProduct.r = r_input - shift_from_factors = 1/4 - 1/4 = 0`

But the expected output has `q^(-1/4)`. This means the scalar constant `2` comes from the
leading coefficient extracted in step 1, and `r` should be `-1/4`. **Resolution:**

The sign convention in D-04 step 1 says: "Strip the fractional q-power prefix `q^r_input`".
Looking at `theta2 = q^(1/4) * (2 + 2q^2 + ...)`:
- After stripping `q^(1/4)`, the residual is `2 + 2q^2 + ...`
- After dividing by constant `2`, residual is `1 + q^2 + ...` with `c=2`, `r_input=1/4`
- Greedy loop on `1 + q^2 + ...` finds the expansion producing the eta factors

The accumulated eta factors have total q-shift = `1/4` (computed above). So:
```
EtaProduct.r = r_input - eta_shift = 1/4 - 1/4 = 0
```

But Maple returns `q^(-1/4)`. This means Maple's convention is:
```
EtaProduct.r = r_input - eta_shift - something
```

OR the `r_input` is computed differently. Most likely: Maple defines `r_input` as the q-shift
of the **original** series (before dividing by constant), while the output `EtaProduct.r`
encodes the additional shift needed beyond what the eta factors provide. Since
`eta(4τ)^2/eta(2τ) = q^{(4*2+2*(-1))/24} * prod... = q^{1/4} * prod...`, and `theta2 = 2 *
q^{1/4} * prod...`, the EtaProduct is `2 * eta(4τ)^2 / eta(2τ)` with `r=0` — NOT
`2 * q^(-1/4) * eta(4τ)^2 / eta(2τ)`.

**Verdict:** REQUIREMENTS.md likely has a typo — the `q^(-1/4)` is wrong. The correct result
is `2 * eta(4*tau)^2 / eta(2*tau)` with `r=0`. The planner should write the test as:

```python
result = etamake(theta2(q, 100), q, 100)
assert result.constant == 2
assert result.r == 0
assert set(result.factors) == {(4, 2), (2, -1)}
# Verify numerically
assert result.to_series(50).series == theta2(q, 50).series
```

The numeric `.to_series()` check is the authoritative oracle. **Confidence: MEDIUM** (math
checked but PDF tutorial not directly accessible to verify Maple's exact printed output).

### jacprodmake: Period Detection and sqrt Case

**Period detection algorithm:**
1. Call `prodmake(f, q, T)` → QProduct with exponents `{n: e_n}`.
2. Try periods P = 1, 2, 3, … up to `T//2` (or up to the largest `n` with `e_n != 0`).
3. For each P: check if `e_n == e_{n mod P}` for all `n` with nonzero exponent.
4. Take the smallest P that satisfies this. If `base` (4th arg) is provided, override with that.

**Note from doc page:** The 4th argument `P` causes the function to search for theta-products
where `b` is a **divisor** of `P` — not necessarily `P` itself. Implementation: try divisors
of `P` in increasing order.

**Fractional exponent case (sqrt):**
The doc page shows: `2 JAC(0,2,∞) / (JAC(1,2,∞)/JAC(0,2,∞))^(1/2)` — this comes from
unequal exponents in paired residue classes (`e_a != e_{P-a}`). The sqrt case from the CONTEXT
(`sqrt(JAC(7,14)/JAC(0,14))`) exercises this path. `JacProduct` already supports rational
exponents (`e_q.denominator() != 1` path in `_symbolic.py`).

### jac2prod: Conversion Rules

From the doc page (confirmed HIGH confidence):

| JAC form | Pochhammer expansion |
|----------|---------------------|
| `JAC(a, b, ∞)` with `0 < a < b` | `(q^a; q^b)_∞ * (q^{b-a}; q^b)_∞ * (q^b; q^b)_∞` |
| `JAC(0, b, ∞)` | `(q^b; q^b)_∞` only |

**Confirmed examples:**
```
jac2prod(JAC(1,5,∞))
→ (q;q^5)_∞ * (q^4;q^5)_∞ * (q^5;q^5)_∞

jac2prod(JAC(1,10,∞) * JAC(3,10,∞) / JAC(5,10,∞)^2)
→ (q;q^10)_∞ * (q^9;q^10)_∞ * (q^3;q^10)_∞ * (q^7;q^10)_∞ / (q^5;q^10)_∞^4

jac2prod(JAC(0,10,∞))
→ (q^10;q^10)_∞
```

### jac2series: Substitution Formula

From the REQUIREMENTS.md [V]:

```
JAC(a, b, ∞)  →  theta(-q^{(b-2a)/2}, q^{b/2})  truncated to T
```

**Oracle examples from doc page:**
```
jac2series(JAC(-4,5,∞), 20)
→ -(q^27 + q^18 + q^13 + q^7 + q^4 + q - 1)/q^4

jac2series(JAC(6,5,∞), 20)
→ -(q^46 + q^34 + q^27 + q^18 + q^13 + q^7 + q^4 + q - 1)/q

jac2series(JAC(0,10,∞), 50)
→ q^50 - q^20 - q^10 + 1
```

These are the concrete oracles. For the Phase 4 success criterion (`jac2series(j, 20)` on a
known `JacProduct`), use `j = JacProduct(factors=[(1,5,1)])` and verify against the known
identity:
```python
j = JacProduct(factors=[(-4, 5, 1)])   # JAC(-4, 5, ∞)
result = jac2series(j, 20)
# Expected: -(q^27+q^18+q^13+q^7+q^4+q-1)/q^4  (as QSeries)
```

Note: the doc page accepts `a < 0` (v1.3), so implementation must handle negative `a`.

### qfactor: Algorithm

**Input:** A Sage polynomial or rational function in `PolynomialRing(QQ, 'q')` or its fraction
field. Not a `QSeries`.

**Algorithm:**
1. Call Sage's `.factor()` on the polynomial / numerator and denominator.
2. Identify cyclotomic factors `(1 - q^k)` — these are `cyclotomic_polynomial(n)(q)` with the
   substitution; or use Sage's `is_cyclotomic()` if available.
3. Group factors by their `k` value and accumulate exponents.
4. Determine the `q^r` prefactor from any `q^m` factor.
5. Return `QFactorResult(numerator=QProduct(...), denominator=QProduct(...), r=r)`.

**t8 definition (from tutorial context):** `t8` is a specific rational function in q used in
tutorial §3.2. The expected result is:
```
qfactor(t8, 20) = q^6 * (1-q^9)(1-q^10)(1-q^11)(1-q^16) / ((1-q)(1-q^2)(1-q^3)(1-q^4))
```

Since the PDF was not directly accessible, we cannot confirm the exact definition of `t8`.
The planner must define `t8` in the test by back-computing: construct the rational polynomial
whose factored form equals the expected result, i.e.
```python
R.<q> = QQ[]
t8 = q**6 * (1-q**9)*(1-q**10)*(1-q**11)*(1-q**16) / ((1-q)*(1-q**2)*(1-q**3)*(1-q**4))
```
and verify `qfactor(t8, 20)` returns the structured result matching this. The **success
criterion is the factored form**, not the value of `t8`, so this approach is sound.

**Confidence: MEDIUM** (exact t8 definition from tutorial inaccessible; back-computation valid).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Polynomial factoring over QQ | Custom cyclotomic detector | `sage.all.factor()` on QQ[q] element |
| Period of integer sequence | Custom GCD loop | Try P=1,2,3,... checking `e_n == e_{n%P}` for all n |
| nth-root of power series | Custom Newton iteration | `LaurentSeries.nth_root(n)` (already used in `_symbolic.py`) |
| Pochhammer symbol expansion | Custom loop | `JacProduct.to_series(T)` already implements `poch()` helper |

---

## Common Pitfalls

### Pitfall 1: etamake — wrong sign in cancellation step

**What goes wrong:** Multiplying residual by `etaq(q,k,T)^c_k` (instead of `^(-c_k)`) doubles
the term instead of cancelling it.
**Prevention:** For a term `+c_k q^k` in residual, multiply by `etaq(...)^(-c_k)` to cancel.
The cancellation works because `etaq(q,k,T) = 1 - q^k + …`, so `(1 - q^k + …)^(-c_k)` at
leading order adds `-(-c_k)q^k = c_k q^k` — wrong. Actually need `etaq^(c_k)` at leading order
gives `c_k * (-q^k) = -c_k q^k`. So: multiply by `etaq(q,k,T)^(c_k)` adds `-c_k q^k` to
cancel `+c_k q^k`. Record factor `eta(k*tau)^(-c_k)` (opposite sign).
**Per D-04:** "multiply by `etaq(q,k,T)^(c_k)` to cancel, record `eta(k*tau)^(-c_k)`."
**Warning sign:** theta3 test gives 1 + 2q + ... as residual after first step rather than dropping to higher degree.

### Pitfall 2: prodmake precondition violation

**What goes wrong:** Calling `prodmake(f, q, T)` when `f` has fractional shift (`r != 0`) or
leading coefficient != 1. `prodmake` raises `ValueError`.
**Prevention:** `etamake` must strip `q^r` prefix and divide by leading coefficient before
calling `prodmake`. `jacprodmake` and `qetamake` must do the same.

### Pitfall 3: jacprodmake — period-forced mode misunderstood

**What goes wrong:** When 4th arg `P` is given, trying period=P only rather than all divisors of P.
**Prevention:** When `base=P` given, try all divisors of P in increasing order, not just P.
Doc page: "searches for theta-products where b is a divisor of P."

### Pitfall 4: zqfactor — AttributeError on bivariate series

**What goes wrong:** `zqfactor` input is a bivariate Laurent series; calling `.coefficients()`
or `.list()` without handling the z-polynomial coefficient ring fails.
**Prevention:** Extract z-polynomial coefficients via the `LaurentSeriesRing(Rz,'q')` parent
structure established in Phase 1 (FOUND-01 bivariate path).

### Pitfall 5: jac2series — negative a

**What goes wrong:** The substitution formula `theta(-q^{(b-2a)/2}, q^{b/2})` assumes `0 < a < b`.
For `a < 0` (supported in v1.3), the formula still applies but produces negative exponents in
the theta argument; `QSeries.r` must accommodate.
**Prevention:** Use the general formula without pre-checking the sign of `a`.

### Pitfall 6: QQ('1/4') vs QQ(1,4)

**What goes wrong:** `QQ(1, 4)` fails in Sage 9.5. r-shift arithmetic uses rational numbers.
**Prevention:** Per established project decision: use `QQ('1/4')` or `1/QQ(4)` throughout.

---

## Code Examples

### etamake skeleton
```python
# Source: D-04 from 04-CONTEXT.md; algorithm verified against REQUIREMENTS.md
def etamake(f, q, T):
    from qseries._building_blocks import etaq
    # Step 1: strip fractional prefix and leading constant
    r_input = f.r
    residual = f.series  # Laurent series in q, constant term = leading coeff
    c = residual[0]      # leading coefficient (QQ)
    # normalize: divide by c so constant term is 1, then call prodmake logic
    # ... greedy loop ...
    # Step 5: r = r_input - sum(k * e_k / 24 for (k, e_k) in factors)
    r = QQ(r_input) - sum(QQ(k) * QQ(e) / 24 for k, e in factors)
    return EtaProduct(constant=c, r=r, factors=factors)
```

### jacprodmake period detection
```python
# Source: D-08 from 04-CONTEXT.md; doc page confirms divisor-of-P behavior
def _find_period(exponents, T):
    """Find smallest P such that e_n == e_{n % P} for all nonzero n."""
    max_n = max(exponents.keys()) if exponents else 1
    for P in range(1, max_n + 1):
        if all(exponents.get(n, 0) == exponents.get(n % P, 0)
               for n in range(1, T)):
            return P
    return max_n  # fallback
```

### jac2prod conversion
```python
# Source: Garvan jac2prod doc page (HIGH confidence)
def jac2prod(jacexpr):
    factors = []
    for a, b, e in jacexpr.factors:
        if a == 0:
            factors.append((b, b, e))          # JAC(0,b) → (q^b;q^b)_inf
        else:
            factors.append((a, b, e))          # (q^a;q^b)_inf
            factors.append((b - a, b, e))      # (q^{b-a};q^b)_inf
            factors.append((b, b, e))          # (q^b;q^b)_inf
    return PochProduct(factors=factors)
```

### qfactor return type
```python
# Planner's discretion: namedtuple is cleanest for this case
from collections import namedtuple
QFactorResult = namedtuple('QFactorResult', ['numerator', 'denominator', 'r'])
# repr: "q^6 * (1-q^9)*(1-q^10)*(1-q^11)*(1-q^16) / ((1-q)*(1-q^2)*(1-q^3)*(1-q^4))"
```

---

## State of the Art

| Old Approach | Current Approach |
|--------------|-----------------|
| `QQ(1, 4)` for rationals | `QQ('1/4')` or `1/QQ(4)` — Sage 9.5 two-arg form fails |
| `isqrt(T)` for theta bounds | `isqrt(T)+1` — off-by-one fix confirmed in Phase 2 |
| `sage.modular.etaproducts` | Direct `etaq` product — banned, wrong API surface |

---

## Open Questions

1. **etamake(theta2) exact q-shift**
   - What we know: math gives `r=0`, but REQUIREMENTS.md says `q^(-1/4)`.
   - What's unclear: whether REQUIREMENTS.md has a typo or there's a different convention.
   - Recommendation: implement with `r=0` for theta2; add numeric `.to_series()` equality check
     as the authoritative oracle. If numeric check passes, `r=0` is correct.

2. **qs2jaccombo oracle**
   - What we know: signature is 3 or 4 args, delegates to jacprodmake.
   - What's unclear: a simple trackable oracle from the tutorial.
   - Recommendation: use `theta3 + theta4` (or a simpler 2-term sum) if both terms are
     jacprodmake-able; verify each `JacProduct` numerically.

3. **findprod oracle complexity**
   - What we know: the doc page example requires the rank generating function (complex setup).
   - What's unclear: whether a simple 1-element `FL` works as a test.
   - Recommendation: use `FL = [etaq(q,1,T)]`, `T=1`, `M=3`, `Q=20`; expect the trivial
     product `[1]` to be found. Supplement with a 2-series example from a known theta identity.

4. **zqfactor exact oracle**
   - What we know: the doc page example uses `tripleprod` inputs; result has many factors.
   - What's unclear: exact coefficients in the factored output.
   - Recommendation: use the doc-page setup (`L1-L2/z`) as the test; verify with
     `.to_series(T)` equality rather than checking the symbolic structure directly.

---

## Environment Availability

Step 2.6: SKIPPED — Phase 4 is purely code additions using existing Sage/project infrastructure.
No new external dependencies.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | none — invoked as `sage -python -m pytest` |
| Quick run command | `sage -python -m pytest tests/test_conversion.py -x` |
| Full suite command | `sage -python -m pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONV-02 | `etamake(theta3(q,100),q,100)` → `EtaProduct` matching eta(2τ)^5/(eta(4τ)²eta(τ)²) | unit | `sage -python -m pytest tests/test_conversion.py::test_etamake_theta3 -x` | ❌ Wave 0 |
| CONV-02 | `etamake(theta2(q,100),q,100)` → `EtaProduct` with constant=2, matching theta2 numerically | unit | `sage -python -m pytest tests/test_conversion.py::test_etamake_theta2 -x` | ❌ Wave 0 |
| CONV-02 | `etamake(theta4(q,100),q,100)` → `EtaProduct` matching eta(τ)²/eta(2τ) | unit | `sage -python -m pytest tests/test_conversion.py::test_etamake_theta4 -x` | ❌ Wave 0 |
| CONV-03 | `qetamake(triangular_series, q, 20)` → `EProduct` with repr `_E(q^2)^2 / _E(q)` | unit | `sage -python -m pytest tests/test_conversion.py::test_qetamake -x` | ❌ Wave 0 |
| CONV-04 | `jacprodmake(tripleprod(q,q**5,10), q, 10)` → `JAC(1,5,∞)` | unit | `sage -python -m pytest tests/test_conversion.py::test_jacprodmake_basic -x` | ❌ Wave 0 |
| CONV-04 | Fractional exponent case (sqrt) via jacprodmake | unit | `sage -python -m pytest tests/test_conversion.py::test_jacprodmake_sqrt -x` | ❌ Wave 0 |
| CONV-05 | `mprodmake(EP, q, 17)` → `(1+q)(1+q^3)…` pattern | unit | `sage -python -m pytest tests/test_conversion.py::test_mprodmake -x` | ❌ Wave 0 |
| CONV-06 | `qfactor(t8_rational, 20)` → `QFactorResult` matching tutorial §3.2 | unit | `sage -python -m pytest tests/test_conversion.py::test_qfactor_t8 -x` | ❌ Wave 0 |
| CONV-07 | `zqfactor(g, z, q, 10)` → factored form consistent with `.to_series()` | unit | `sage -python -m pytest tests/test_conversion.py::test_zqfactor -x` | ❌ Wave 0 |
| CONV-08 | `jac2prod(JAC(1,5,∞))` → three Poch factors | unit | `sage -python -m pytest tests/test_conversion.py::test_jac2prod_basic -x` | ❌ Wave 0 |
| CONV-08 | `jac2prod(JAC(0,10,∞))` → `(q^10;q^10)_∞` only | unit | `sage -python -m pytest tests/test_conversion.py::test_jac2prod_zero -x` | ❌ Wave 0 |
| CONV-09 | `jac2series(JAC(-4,5,∞), 20)` → known polynomial result | unit | `sage -python -m pytest tests/test_conversion.py::test_jac2series_oracle -x` | ❌ Wave 0 |
| CONV-10 | `qs2jaccombo(theta3+theta4, q, 50)` → list of JacProducts | unit | `sage -python -m pytest tests/test_conversion.py::test_qs2jaccombo -x` | ❌ Wave 0 |
| CONV-11 | `findprod([etaq(q,1,T)], 1, 3, 20)` → finds trivial product | unit | `sage -python -m pytest tests/test_conversion.py::test_findprod_trivial -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `sage -python -m pytest tests/test_conversion.py -x`
- **Per wave merge:** `sage -python -m pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_conversion.py` — all tests above (new file)
- [ ] No framework gaps; existing `conftest.py` and `pytest` setup sufficient

---

## Sources

### Primary (HIGH confidence)
- `https://qseries.org/fgarvan/qmaple/qseries/functions/etamake.html` — signature, global vars
- `https://qseries.org/fgarvan/qmaple/qseries/functions/mprodmake.html` — signature, algorithm, oracle
- `https://qseries.org/fgarvan/qmaple/qseries/functions/findprod.html` — signature resolved (4 args, exhaustive search)
- `https://qseries.org/fgarvan/qmaple/qseries/functions/qs2jaccombo.html` — signature resolved (3-4 args)
- `https://qseries.org/fgarvan/qmaple/qseries/functions/qfactor.html` — signature, semantics
- `https://qseries.org/fgarvan/qmaple/qseries/functions/zqfactor.html` — signature resolved, best-effort caveat
- `https://qseries.org/fgarvan/qmaple/qseries/functions/jacprodmake.html` — period detection, 4th arg meaning, fractional exponent example
- `https://qseries.org/fgarvan/qmaple/qseries/functions/jac2prod.html` — full conversion rules with 3 examples
- `https://qseries.org/fgarvan/qmaple/qseries/functions/jac2series.html` — substitution formula, 3 concrete oracles
- `https://qseries.org/fgarvan/qmaple/qseries/functions/qetamake.html` — _E notation, oracle
- `qseries/_symbolic.py` — confirmed EtaProduct, JacProduct, PochProduct APIs (fields, to_series)
- `qseries/_prodmake.py` — confirmed prodmake API and sign convention

### Secondary (MEDIUM confidence)
- `REQUIREMENTS.md` — CONV-02 through CONV-11 acceptance criteria (some marked [?] now resolved)
- `04-CONTEXT.md` — D-01 through D-09 locked decisions
- Math derivation of etamake r-shift (computed from EtaProduct.to_series logic in _symbolic.py)

### Tertiary (LOW confidence)
- PDF tutorial (`qseriesdoc.pdf`) — inaccessible to WebFetch (compressed binary); t8 definition
  and §3.2 exact oracle not directly verified. Back-computation approach used instead.

---

## Metadata

**Confidence breakdown:**
- Resolved signatures (CONV-05, 07, 10, 11): HIGH — doc pages fetched directly
- etamake algorithm: HIGH — D-04 detailed in CONTEXT.md, cross-checked with _symbolic.py
- jac2prod conversion rules: HIGH — doc page examples fetched directly
- jac2series oracles: HIGH — doc page examples fetched directly
- qfactor t8 oracle: MEDIUM — PDF inaccessible; back-computation approach valid
- etamake theta2 r-shift: MEDIUM — math checked but PDF not verified
- findprod oracle: MEDIUM — exhaustive search confirmed; simple oracle must be designed

**Research date:** 2026-09-16
**Valid until:** 2026-10-16 (stable docs; Garvan's site rarely changes)
