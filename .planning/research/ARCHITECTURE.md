# Architecture Research — qseries-sage

## Component Map

```
┌─────────────────────────────────────────────────────────────┐
│  Public API  (qseries/__init__.py — `from qseries import *`)│
│  41 functions + EtaProduct + JacProduct                     │
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
  → Series repr layer: PowerSeriesRing(QQ,'q')(...)
  → Returns QSeries with truncation order T
```

**Product-recovery path (prodmake/etamake):**
```
Input: QSeries f (truncated)
  → Take log derivative: f'/f as series
  → Build coefficient matrix M[i,j] = coeff of q^i in known product^j
  → Sage: M.right_kernel() for exact nullspace over QQ
  → Recover exponents via Möbius inversion
  → Construct EtaProduct / JacProduct object
  → Return symbolic output with .to_series() available
```

**Relation-finding path:**
```
Input: list of QSeries [f1, f2, ...], degree bound d, truncation T
  → Build monomial list up to degree d
  → Construct coefficient matrix: rows = monomials, cols = coefficients in q
  → Sage: M.right_kernel() for relations over QQ (or GF(p) for mod-p)
  → Return list of coefficient vectors
```

## Module Structure

```
qseries/
├── __init__.py          # exports all 41 functions + EtaProduct, JacProduct
├── _series.py           # QSeries wrapper class, truncation propagation
├── _symbolic.py         # EtaProduct, JacProduct dataclasses
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

**GF(p) selection:** `*modp` functions accept a `p` argument and instantiate `LaurentSeriesRing(GF(p), 'q')` internally. No separate class needed.

**Relation return type:** List of lists (or list of vectors) of coefficients. Order is not guaranteed to match Maple — tests compare sets of relations, not ordered lists.

## Build Order (Phase Sequence)

1. `_series.py` — QSeries wrapper (blocks everything)
2. `_symbolic.py` — EtaProduct/JacProduct (independent, needed for Layer 4)
3. `_building_blocks.py` — 11 functions (depends on `_series`)
4. `_utilities.py` — 8 functions (depends on `_series`)
5. `_prodmake.py` — Andrews' algorithm (depends on `_series`, `_symbolic`)
6. `_conversion.py` — remaining product conversion (depends on `_prodmake`)
7. `_relations.py` — all 11 relation finders (depends on `_series`, `_building_blocks`)
8. Packaging + tutorial notebook
