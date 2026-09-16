# Stack Research — qseries-sage

## Core Runtime

| Component | Choice | Version | Confidence |
|-----------|--------|---------|------------|
| Language | Python 3 (inside SageMath) | Python 3.10+ (Sage 10.x ships 3.10+) | High |
| Math engine | SageMath | 10.x (HiPerGator) / 10.3+ (stock) | High |
| Package manager | `sage -pip install .` | — | High |
| Build backend | `pyproject.toml` + `flit-core` or `setuptools` | setuptools ≥ 68 | High |

## Series Arithmetic Layer

**Use:** `sage.rings.power_series_ring.PowerSeriesRing(QQ, 'q')` and `sage.rings.laurent_series_ring.LaurentSeriesRing(QQ, 'q')`.

These are the right primitives — they carry truncation order, support exact arithmetic over QQ, and have GF(p) variants for mod-p work.

**Do NOT use:** `sage.symbolic` for series arithmetic — it's a CAS ring, not an analytic series ring. Coercion to `SR` loses truncation semantics and is slow.

**Truncation propagation:** Sage's rings handle this via `O(q^T)`. Keep the `T` argument explicit on every public function, mirroring Maple's `(f, q, T)` signature. Never set a global precision.

## Existing Sage Primitives to Wrap

| Sage primitive | Wraps to qseries function | Notes |
|---|---|---|
| `sage.arith.misc.q_binomial(n, k, q)` | `qbin` | Check argument order — Sage uses (n,k,q), Maple uses (q,n,k) |
| `sage.functions.other.qexp_eta(q, prec)` | `etaq` | Sage returns series directly |
| `sage.modular.etaproducts` | Reference for eta arithmetic | Do NOT expose — different API surface |
| `sage.rings.finite_rings.GF(p)` | Coefficient ring for `*modp` functions | Use directly |

## Symbolic Output Layer

**Use:** Plain Python dataclasses or `__repr__`-overriding classes. No Sage symbolic ring.

```python
@dataclass
class EtaProduct:
    # exponent list: [(level, exponent), ...]
    # rational q-power prefix
```

**Why not `sage.symbolic`:** SR equality checking requires `simplify()` calls that are unreliable for this domain. Custom classes give `==` by field comparison — trivially testable.

## Testing

| Tool | Role |
|---|---|
| `pytest` | Primary test runner, invoked as `sage -python -m pytest` |
| `sage.doctest` | Optional — for doctests in docstrings if desired |
| No `mock` | All Sage arithmetic is exact; no mocking needed |

**HiPerGator note:** `sage -python -m pytest tests/` works without root. Confirm `pytest` is installed in the Sage venv: `sage -pip install pytest`.

## Packaging

`pyproject.toml` with `[build-system] requires = ["setuptools>=68"]`. Avoid `setup.py` — deprecated path. Key metadata:

```toml
[project]
name = "qseries-sage"          # or "qseries" — TBD pending naming decision
requires-python = ">=3.10"
dependencies = []              # SageMath is the runtime, not a pip dependency
```

**HiPerGator install:** `sage -pip install --user .` (no root). Confirm `--user` flag works on HiPerGator's Sage installation or use a venv.

## What NOT to Use

- **SymPy** — no exact power-series ring, no nullspace over QQ built in
- **NumPy/SciPy** — floating-point; relation finding requires exact arithmetic
- **Sage's `SR` (symbolic ring)** — wrong semantics for truncated series
- **Maple compatibility layer** — explicitly out of scope
- **Cython** — out of scope for v1.0
