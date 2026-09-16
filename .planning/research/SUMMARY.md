# Research Summary — qseries-sage

## Stack

**Core:** Python 3.10+ inside SageMath 10.x. No additional runtime dependencies beyond SageMath and pure-Python PyPI packages.

**Series arithmetic:** `PowerSeriesRing(QQ, 'q', prec=T)` and `LaurentSeriesRing(QQ, 'q')` for exact truncated series. `GF(p)` coefficient ring for mod-p variants.

**Symbolic output:** Plain Python dataclasses (`EtaProduct`, `JacProduct`) — not Sage's symbolic ring. Printable, convertible back to series, trivially testable.

**Testing:** `pytest` under `sage -python -m pytest`. Expected values from Maple documentation, not from running our own code.

**Packaging:** `pyproject.toml` + setuptools. `sage -pip install --user .` for HiPerGator.

## Table Stakes Features

These must work for the package to be useful:
- QSeries wrapper with explicit truncation order T
- `aqprod` — used in virtually every tutorial example
- Full theta function suite (theta, theta2, theta3, theta4)
- `tripleprod` — foundational identity
- `sift`, `qdegree`, `lqdegree` — series inspection
- `prodmake` — Andrews' algorithm (highest complexity; everything in Layer 4 builds on it)
- `etamake` — most common product recovery use case
- `findhom`, `findhomcombo`, `findlincombo` — most-used relation finders

## Architecture

7-module layout with a single flat public namespace:

```
_series.py       → QSeries wrapper (foundation)
_symbolic.py     → EtaProduct, JacProduct (independent)
_building_blocks.py → 11 core q-product/theta functions
_utilities.py    → 8 inspection/metadata functions
_prodmake.py     → Andrews' algorithm (isolated; highest complexity)
_conversion.py   → remaining 10 product conversion functions
_relations.py    → 11 relation finding functions (exact + mod-p)
```

Data flows: building blocks → series representation → product conversion (via prodmake) → relation finding (via coefficient matrix nullspace).

## Watch Out For

1. **Sage series truncation defaults** — always pass explicit `prec=T`, never rely on default precision 20.
2. **Andrews' algorithm edge cases** — fractional q-power prefixes in prodmake; verify with high T.
3. **Relation finding underdetermination** — T must be ≥ 2*degree; include a verify step on returned relations.
4. **GF(p) vs ZZ/pZZ** — always use `GF(p)` for mod-p functions; assert prime p.
5. **Test oracle discipline** — expected values from Maple docs only; never from our own code.
6. **Relation ordering** — test relation *sets* not ordered lists; Sage's kernel basis differs from Maple's.
7. **Licensing** — contact Garvan before writing code; reimplement from docs, not source.
8. **HiPerGator install path** — test `sage -pip install --user .` early; document the install command.
9. **Theta conventions** — each function's convention cited to the Maple doc page; cross-check via triple product identity.

## Recommended Phase Sequence

| Phase | Content |
|-------|---------|
| 1 | License decision + QSeries wrapper + EtaProduct/JacProduct types |
| 2 | 11 building-block functions + 8 series utilities |
| 3 | prodmake (Andrews' algorithm) — standalone due to complexity |
| 4 | Remaining product conversion (etamake, jacprodmake, others) |
| 5 | Relation finding — exact (findhom*, findlin*, findpoly, findcong, findmaxind) |
| 6 | Relation finding — mod-p variants |
| 7 | Packaging (pyproject.toml, HiPerGator test) + tutorial notebook |
