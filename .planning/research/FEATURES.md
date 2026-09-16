# Features Research — qseries-sage

## Dependency Graph (Build Order)

```
Layer 0 — Series representation
  └── PowerSeriesRing/LaurentSeriesRing wrapper, truncation order, QSeries type

Layer 1 — Building blocks (depend on Layer 0)
  ├── aqprod    (q-Pochhammer / rising q-product)
  ├── qbin      (Gaussian binomial coefficient)
  ├── etaq      (Euler's eta q-series)
  ├── jacprod   (Jacobi product)
  ├── theta, theta2, theta3, theta4  (Jacobi theta functions)
  ├── tripleprod, quinprod           (triple/quintuple product identities)
  └── winquist  (Winquist's identity)

Layer 2 — Series utilities (depend on Layer 0)
  ├── sift, qdegree, lqdegree, lqdegree0   (inspection/manipulation)
  ├── checkmult, checkprod                  (verification helpers)
  └── packageversion, changes               (metadata — trivial)

Layer 3 — Symbolic output types (depend on nothing; used by Layer 4)
  ├── EtaProduct class
  └── JacProduct class

Layer 4 — Product conversion (depend on Layers 1, 2, 3)
  ├── prodmake    ← HIGHEST PRIORITY (Andrews' algorithm; others build on it)
  ├── etamake     (wraps prodmake for eta-product form)
  ├── qetamake    (variant of etamake)
  ├── jacprodmake (wraps prodmake for Jacobi form)
  ├── mprodmake   (multi-variable variant)
  ├── qfactor, zqfactor  (factor out q-power)
  ├── jac2prod, jac2series  (JAC → product / series)
  ├── qs2jaccombo   (series → Jacobi combo)
  └── findprod      (search for matching product form)

Layer 5 — Relation finding (depend on Layer 1)
  ├── Exact variants:  findhom, findhomcombo, findnonhom, findnonhomcombo,
  │                   findlincombo, findmaxind, findpoly, findcong
  └── Mod-p variants: findhommodp, findhomcombomodp, findlincombomodp
```

## Table Stakes (Must Have — Tutorial Unusable Without These)

- **Layer 0:** The series representation. Everything else fails without it.
- **aqprod:** Used in virtually every tutorial example.
- **qbin, etaq, jacprod:** Used frequently in building identities.
- **theta, theta2, theta3, theta4:** Core theta function suite.
- **tripleprod:** Jacobi triple product identity — foundational.
- **sift:** Very common in partition theory examples.
- **qdegree, lqdegree:** Needed to inspect series.
- **prodmake:** The key product-recovery algorithm; most of Layer 4 depends on it.
- **etamake:** Most common use case of prodmake.
- **findhom, findhomcombo:** Most common relation-finding use case.
- **findlincombo:** Frequently used in tutorial.

## Differentiators (What Makes This Better Than Raw Sage)

- **Maple-compatible API surface:** `from qseries import *` and tutorial examples just work.
- **Symbolic EtaProduct/JacProduct output:** Readable like Maple, not a wall of series coefficients.
- **prodmake/etamake:** Andrews' algorithm implemented correctly — non-trivial to replicate from scratch.
- **Relation finding suite:** The 11 `find*` functions are the highest-value feature for research; nothing equivalent in Sage.
- **Tutorial notebook:** Lowers the onboarding barrier for new HiPerGator users.

## Anti-Features (Do NOT Build)

- Maple-syntax parser or `.mpl` file importer
- `O(q^T)` symbolic term handling (keep it as a plain integer `T`)
- Global precision / implicit truncation order
- GUI or interactive worksheet mode
- Non-Sage Python fallback (SymPy path)
- Cython acceleration
- Related packages (ETA, thetaids, etc.)

## Complexity Ratings

| Group | Complexity | Reason |
|-------|-----------|--------|
| Layer 0 — Series repr | Medium | Sage coercion rules need care |
| Building blocks | Low–Medium | Math is well-defined; mostly wrapping Sage |
| Series utilities | Low | Mostly index/coefficient operations |
| Symbolic output types | Low | Plain Python classes |
| prodmake/etamake | High | Andrews' algorithm, log-derivative, Möbius recursion |
| Other product conversion | Medium | Build on prodmake once correct |
| Relation finding (exact) | Medium | Nullspace of exact matrix — Sage handles well |
| Relation finding (mod p) | Medium | GF(p) switch; otherwise same structure |
| Packaging | Low | Standard pyproject.toml |
| Tutorial notebook | Low–Medium | Content writing, not implementation |

## Recommended Build Order for Phases

1. Series representation + building blocks (aqprod, qbin, etaq, theta suite, tripleprod, quinprod, winquist, jacprod)
2. Series utilities + symbolic output types
3. prodmake (Andrews' algorithm) — standalone phase due to complexity
4. Remaining product conversion (etamake, jacprodmake, others building on prodmake)
5. Relation finding (exact)
6. Relation finding (mod p)
7. Packaging + tutorial notebook
