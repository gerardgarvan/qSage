# Architecture Research — qseries-sage

## Component Map

```
┌─────────────────────────────────────────────────────────────┐
│  Public API  (qseries/__init__.py — `from qseries import *`)│
│  41 functions + QProduct/EtaProduct/EProduct/JacProduct/PochProduct │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
┌────────────▼────────────┐  ┌────────────▼───────────────────┐
│  Product Conversion     │  │  Relation Finding              │
│  prodmake, etamake,     │  │  findhom*, findlin*, findpoly, │
│  jacprodmake, qetamake, │  │  findcong, findmaxind          │
│  jac2prod, findprod,    │  │  (exact + mod-p variants)      │
│  qs2jaccombo, ...       │  └────────────┬───────────────────┘
└────────────┬────────────┘               │
             │                            │
┌────────────▼────────────────────────────▼───────────────────┐
│  Building Blocks                                            │
│  aqprod, qbin, etaq, jacprod,                               │
│  theta, theta2, theta3, theta4,                             │
│  tripleprod, quinprod, winquist                             │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│  Series Representation Layer                                │
│  QSeries wrapper around PowerSeriesRing/LaurentSeriesRing   │
│  Truncation order T tracked per-instance                    │
│  QQ coefficient ring (exact) / GF(p) for mod-p variants    │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│  SageMath (runtime)                                         │
│  PowerSeriesRing, LaurentSeriesRing, GF, matrix, nullspace  │
└─────────────────────────────────────────────────────────────┘

Symbolic Output Layer (parallel, no series dependency):
┌─────────────────────────────────────────────────────────────┐
│  EtaProduct / JacProduct                                    │
│  Python dataclasses with __repr__ matching Maple output     │
│  .to_series(T) method converts back to QSeries             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

**Series construction path:**
```
User call: aqprod(a, q, T)
  → Series repr layer: LaurentSeriesRing(R, 'q') where R = QQ (default) or GF(p)
  → Returns QSeries(series, T, shift=0) with truncation order T
```

**prodmake path (Andrews' recurrence — no linear algebra):**
```
Input: QSeries f with f = 1 + c_1*q + c_2*q^2 + ... (normalised)
  → Write f = prod(1-q^n)^{a_n}; take log: log f = -sum_n a_n sum_{k≥1} q^{kn}/k
  → Equivalently: n*b_n = sum_{j=1}^{n} b_{n-j} * sigma(j),  where b_n = coeff of q^n in log f,
                  sigma(j) = sum_{d|j} d * a_d
  → Solve recurrence for a_n by Möbius-style inversion: a_n given b_1..b_n
  → Returns QProduct with exponent list {n: a_n}
```

**etamake path (greedy eta-multiplication loop):**
```
Input: QSeries f
  → At each step: read leading coefficient c_k of q^k; multiply f by etaq(q,k,T)^(-c_k)
  → Accumulate (k, c_k) pairs into EtaProduct, tracking rational q-power shift
  → Iterate until f = 1 + O(q^T)
  → Returns EtaProduct with constant, rational q^r, and eta(k*tau) exponents
```

**jacprodmake path:**
```
prodmake → detect periodicity in {a_n} sequence → return JacProduct
```

**qfactor path:**
```
Input: polynomial or rational function p(q) in QQ[q] (NOT a QSeries)
  → Factor p over QQ[q] via Sage's factor()
  → Match cyclotomic factors to finite q-products via prodmake
  → Returns factored form as displayable product
```

**Relation-finding path (find* family only — uses right_kernel):**
```
Input: list of QSeries [f1, f2, ...], degree bound d
  → Build monomial list up to degree d
  → Construct coefficient matrix: rows = coefficients in q, cols = monomials
  → Sage: M.right_kernel() for relations over QQ (or GF(p) for mod-p)
  → Return Sage polynomials in X1..Xk (PolynomialRing(QQ, ['X1','X2',...]))
```

## Module Structure

```
qseries/
├── __init__.py          # exports all 41 functions + QProduct, EtaProduct, EProduct, JacProduct, PochProduct
├── _series.py           # QSeries wrapper: pluggable base ring R, truncation T, rational shift r
├── _symbolic.py         # QProduct, EtaProduct, EProduct, JacProduct, PochProduct (five classes)
├── _building_blocks.py  # aqprod, qbin, etaq, jacprod, theta*, tripleprod, quinprod, winquist
├── _utilities.py        # sift, qdegree, lqdegree, lqdegree0, checkmult, checkprod, packageversion, changes
├── _prodmake.py         # prodmake (Andrews' algorithm) — isolated for complexity
├── _conversion.py       # etamake, qetamake, jacprodmake, mprodmake, qfactor, zqfactor, jac2prod, jac2series, qs2jaccombo, findprod
└── _relations.py        # findhom, findhomcombo, findhommodp, ..., findpoly, findcong
```

Single public namespace via `__init__.py` — no sub-package imports needed by users.

## Key Interface Decisions

**Truncation order T:** Stored on the QSeries wrapper. When two QSeries are combined, result uses `min(T1, T2)`. Every public function that creates a series takes `T` as the last positional argument (matching Maple).

**QSeries vs raw Sage series:** Public functions return QSeries wrappers, not raw Sage PowerSeries. This ensures truncation tracking. Internal computations may use raw Sage series, then wrap before returning.

**GF(p) selection:** `*modp` functions accept a `p` argument and instantiate `LaurentSeriesRing(GF(p), 'q')` internally. No separate class needed. Functions must assert `p` is prime.

**Relation return type:** Sage polynomials in `X1..Xk` from `PolynomialRing(QQ, ['X1','X2',...])` (or `GF(p)` for mod-p variants). Order is not guaranteed to match Maple — tests compare relation *spans*, not ordered lists.

**qfactor input:** A polynomial or rational function in `QQ[q]`, not a `QSeries`. The function calls Sage's `factor()` on it before any prodmake step.

## Build Order (Phase Sequence)

1. `_series.py` — QSeries wrapper (blocks everything)
2. `_symbolic.py` — EtaProduct/JacProduct (independent, needed for Layer 4)
3. `_building_blocks.py` — 11 functions (depends on `_series`)
4. `_utilities.py` — 8 functions (depends on `_series`)
5. `_prodmake.py` — Andrews' algorithm (depends on `_series`, `_symbolic`)
6. `_conversion.py` — remaining product conversion (depends on `_prodmake`)
7. `_relations.py` — all 11 relation finders (depends on `_series`, `_building_blocks`)
8. Packaging + tutorial notebook
