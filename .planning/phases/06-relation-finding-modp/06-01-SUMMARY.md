---
phase: 06-relation-finding-modp
plan: 01
status: complete
completed: 2026-11-05
requirements: [REL-03, REL-04, REL-08]
files_modified: [qseries/_relations.py, qseries/__init__.py, tests/test_relations_modp.py]
---

# 06-01 Summary: mod-p relation finders

Phase 6 was executed as a single plan: the mod-p functions reuse the Phase 5 kernel machinery
(`_kernel_search`), so no separate scaffold/implementation waves were needed.

## Signatures (from Garvan's doc pages)

| Function | Calling sequence | Source |
|---|---|---|
| `findhomcombomodp` | `(f, L, p, q, n, topshift, etaoption)` | doc page (confirmed) |
| `findlincombomodp` | `(f, L, SL, p, q, topshift)` | doc page (confirmed) |
| `findhommodp` | `(L, p, q, n, topshift)` | doc page (confirmed 2026-11-05) |

Note: ROADMAP success criterion 1 wrote `findhommodp(f_list, q, p, 2, 0)`; the doc-page order
puts `p` before `q`.

## Implementation

- `_kernel_search(..., F=QQ)` gained a field parameter; coefficient rows are reduced into
  `GF(p)` by `_to_field` (ValueError if a denominator is divisible by p), the kernel is taken
  over `GF(p)`, and relations are polynomials in `X1..Xk` over `GF(p)`.
- `_check_prime(p)` runs first in every mod-p function: non-integers, 0, 1, negatives and
  composites raise `ValueError` before any series work or printing.
- N follows the exact versions: C = 21 for `findhommodp`, C = 20 for the combo variants.
- `findlincombomodp` prints `nx = , k` (as on the doc page) and `%NOT A LINEAR COMBO.%` when
  there is no combination.

## Oracles reproduced

| Check | Result |
|---|---|
| Doc page: `findlincombomodp(F1, BB13, SBB13, 13, q, -8)` with `F1 = sift(E4^16 E6 P, q, 13, 6, 299)` | `{-6*X1}` (= −6·ETA1¹¹·E6·E4), prints `nx = , 6`, `# of terms , 19` |
| `findhomcombomodp(F1, BB13, 13, q, 1, -8)` | same `{-6*X1}`, 19 terms (7 rows + 20 − 8) |
| E4 ≡ 1 (mod 5) since 240 = 2⁴·3·5 | `findhommodp([E4, E6, 1], 5, q, 1)` = `{X1 − X3}`; `findhom` over QQ finds none |
| E6 ≡ 1 (mod 7) since 504 = 2³·3²·7 | relation `X2 − X3` |
| mod 13 | no relation (240, 504 are units mod 13) |
| `findhomcombomodp(E6, [E4, E6], 5, q, 2)` | contains `X1·X2` (E4·E6 ≡ E6 mod 5) |
| p ∈ {1, 12, 0, −7, 'x'} | `ValueError` in all three functions, nothing printed |

Tests: `tests/test_relations_modp.py`, 13 tests. Full local run (Phase 5 + 6 files): 28 passed in ~2 s.

## Not verified here

Run on passagemath/Sage 10.x with a local stand-in for `sift` that matches `_utilities.sift`
for this input (23 terms). The full suite on Sage 9.5 in WSL still needs to be run.
