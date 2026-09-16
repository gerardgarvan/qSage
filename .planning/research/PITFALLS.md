# Pitfalls Research — qseries-sage

## 1. Sage Power Series Precision / Truncation Semantics

**Pitfall:** Sage's `PowerSeriesRing` default precision is 20. Operations that exceed precision silently truncate. Two series with different precisions combined give `min(prec)` — but only if both are in the same ring.

**Warning signs:** Test results differ by one or two terms; `O(q^20)` appears unexpectedly in output.

**Prevention:**
- Always pass explicit `prec=T` when creating series from the ring.
- Store T on the QSeries wrapper and propagate via `min`.
- Never use the default ring — always `PowerSeriesRing(QQ, 'q', default_prec=T)`.

**Phase:** Series representation layer (Phase 1).

---

## 2. LaurentSeriesRing Indexing and Valuation

**Pitfall:** Sage's `LaurentSeriesRing` coefficient indexing uses `f[n]` for the coefficient of `q^n`. Maple's `lqdegree` returns the lowest-degree exponent. Off-by-one errors are easy when Maple conventions differ.

**Warning signs:** `lqdegree` returns n-1 or n+1 vs expected; `checkmult` fails on examples that should pass.

**Prevention:**
- Read the Maple doc page for `lqdegree` / `lqdegree0` carefully.
- Write tests against documented examples before implementing.
- Clarify: does Maple count `O(q^T)` in degree? (It doesn't.)

**Phase:** Series representation layer / utilities (Phase 1–2).

---

## 3. Andrews' Algorithm — Log-Derivative Implementation

**Pitfall:** The log-derivative `f'/f` of a q-product requires dividing series, which introduces truncation error. The standard implementation computes `d/dq log f = f'/f` and reads off exponents from the partial fractions at roots of unity — but the series version must work with finite truncation.

Common error: forgetting to handle the `q^(1/N)` substitution when the product has fractional q-powers.

**Warning signs:** `prodmake` works on simple examples but fails when the product involves a half-integer q-power prefix.

**Prevention:**
- Implement prodmake for integer-exponent products first; add fractional-power prefix handling separately.
- Verify against the Maple doc's `prodmake` examples using high truncation order (T ≥ 50).
- Cross-check: apply `aqprod` with recovered exponents and compare with original series.

**Phase:** prodmake phase (Phase 4).

---

## 4. Relation Finding — Coefficient Matrix Rank

**Pitfall:** If truncation order T is too small relative to the number of monomials d, the coefficient matrix is underdetermined and the nullspace is larger than the true relation space. This gives spurious relations.

**Warning signs:** `findhom` returns relations that don't verify when expanded to higher T.

**Prevention:**
- Use T ≥ 2*d + buffer as a rule of thumb.
- Add a verification step: check each returned relation holds to `2*T` order.
- Document the T requirement in the function docstring.

**Phase:** Relation finding (Phase 5–6).

---

## 5. Mod-p Arithmetic — GF(p) Ring Choice

**Pitfall:** `GF(p)` in Sage is the field with p elements (correct). But `ZZ/pZZ` gives `IntegerModRing(p)`, which has zero-divisors for composite p — wrong for linear algebra. Using the wrong ring gives incorrect nullspaces.

**Warning signs:** `findhommodp` crashes on small p; or returns too many/few relations.

**Prevention:**
- Always use `GF(p)` (prime p only) for mod-p functions. The functions should assert primality of p.
- Document: mod-p functions require prime p.

**Phase:** Relation finding mod-p (Phase 6).

---

## 6. Testing Without Maple — False-Positive Tests

**Pitfall:** If test expected values are computed from the same implementation being tested (e.g., "compute result, then hardcode it as expected"), bugs are invisible.

**Warning signs:** All tests pass immediately without debugging.

**Prevention:**
- Expected values must come from the Maple documentation pages — not computed by the code.
- For undocumented cases, use an *independent* check: verify a product identity to high order by expanding both sides as separate series and comparing coefficients.
- Do not hardcode outputs by running your own code.

**Phase:** Every phase — apply from day 1.

---

## 7. Relation Ordering Ambiguity

**Pitfall:** `findhom` returns a basis for the relation space, but Sage's `right_kernel()` uses a canonical form that may differ from Maple's output ordering. Tests that compare against exact Maple output will fail even when the answer is mathematically correct.

**Warning signs:** Tests fail on ordering but pass when the relation set is compared as a set.

**Prevention:**
- Tests should verify: (1) dimension of relation space is correct, (2) each returned relation holds when evaluated, not (3) exact string match with Maple output.
- Add a helper `verify_relation(f_list, coeffs)` that checks the linear combination is zero.

**Phase:** Relation finding (Phase 5–6).

---

## 8. HiPerGator Deployment — sage -pip install

**Pitfall:** `sage -pip install .` installs into Sage's internal Python environment. On HiPerGator, this may be read-only for regular users. Using `--user` installs to `~/.sage/local/lib/python3.x/site-packages/` which may not be on Sage's path automatically.

**Warning signs:** `from qseries import *` raises `ModuleNotFoundError` after install.

**Prevention:**
- Test the install path on HiPerGator early (Phase 7 / packaging).
- If `--user` path isn't on Sage's sys.path, use `sage -python setup.py develop` or add the path explicitly.
- Document the exact install command for HiPerGator users.

**Phase:** Packaging (Phase 7).

---

## 9. Licensing — Source Translation vs. Reimplementation

**Pitfall:** Translating Maple source code (even with significant rewriting) may constitute a derivative work of Garvan's copyright. Publishing without permission or attribution is a legal risk.

**Warning signs:** Any code that structurally mirrors the Maple source line-by-line.

**Prevention:**
- Contact Frank Garvan before writing code. qseries.org has contact info.
- Preferred approach: reimplement from documented behavior (function signatures, expected I/O from doc pages), not from source.
- If source is consulted for algorithmic understanding (not copying), document this and the license status.

**Phase:** Blocks Phase 1 — resolve before writing any code.

---

## 10. Package Naming — Import Shadowing

**Pitfall:** Naming the package `qseries` risks shadowing other packages or being confused with the Maple package in search results. More concretely: if a user has any other file named `qseries.py` in their working directory, `from qseries import *` will import that file instead.

**Warning signs:** Mysterious `AttributeError` on functions that should exist.

**Prevention:**
- Decide name (`qseries` vs `qseries_sage`) before packaging phase and commit to it.
- Document: "do not create a file named `qseries.py` in your working directory."
- `qseries_sage` is unambiguous but breaks name parity with Maple.

**Phase:** Packaging (Phase 7) — decide in Phase 1 planning.

---

## 11. Jacobi Product Convention Mismatches

**Pitfall:** Maple's `jacprod(a, b, q, T)` uses conventions that may differ from standard references. Sign conventions for theta functions (theta2 vs theta3 vs standard Whittaker-Watson) vary by author.

**Warning signs:** `theta2` gives a series that differs by a factor of `q^(1/4)` or a sign from the expected output.

**Prevention:**
- For each theta function, identify the exact Maple doc-page formula and use it as spec.
- Add a comment in the code citing the Maple doc page for the convention.
- Cross-check theta function implementations against the Jacobi triple product identity (testable without Maple).

**Phase:** Building blocks (Phase 2).
