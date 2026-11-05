---
phase: 05-relation-finding-exact
plan: 01
status: complete
completed: 2026-11-05
requirements: [REL-01, REL-02, REL-05, REL-06, REL-07, REL-09, REL-10, REL-11]
files_modified: [qseries/_relations.py, tests/test_relations.py]
---

# 05-01 Summary: Relation module skeleton + test scaffold

Executed in a cloud workspace on SageMath via passagemath (Python 3.13), not in the WSL
Sage 9.5 environment. Plans 05-01..05-03 were executed in one pass, so the skip-decorated
stub stage was not kept as a separate commit: `_relations.py` and `tests/test_relations.py`
landed in their final form (see 05-02 and 05-03 summaries).

## Deviations

- `etamake` is imported lazily inside `_print_etaoption` instead of at module top level, so
  `_relations` does not import `_conversion` at load time (no circular-import risk; only the
  `etaoption='yes'` path needs it).
- Helpers kept from the plan: `_compute_N`, `_parse_optional_args`, `_eval_monomial`,
  `_validate_series_lengths`, `_build_kernel_polys`, `_gcd_list`, `_suppress_implied`.
  `_eval_monomial` now returns `(series, r)` so q-shifts are tracked (see 05-02).
- `_parse_optional_args` rejects unknown argument types and enforces `topshift > -20`
  (doc page constraint).
