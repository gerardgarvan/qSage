# Maple parity battery

Checks qseries-sage against Frank Garvan's Maple qseries package on 130 cases covering all 41
functions plus `zqfactor`: doc-page and tutorial examples, edge cases, and seeded random cases
(eta-quotients, theta products, products of (1 - q^n), linear combinations).

## Files

| File | Purpose |
|---|---|
| `cases.py` | The battery: each case in Maple and Python syntax, plus how to compare the results |
| `make_maple.py` | Writes `qseries_battery.mpl` from `cases.py` |
| `qseries_battery.mpl` | The script to run in Maple (generated; committed so it can be sent as is) |
| `compare.py` | Runs the Python side and compares with Maple's `maple_results.txt` |
| `maple_results.txt` | Maple's output (add when received; it becomes permanent oracle data) |
| `parity_report.md` | The comparison report (generated) |

## Running

In Maple, with the qseries package available:

```
read "qseries_battery.mpl";
```

This writes `maple_results.txt` (one line per case; errors are logged and the run continues).

Then, from the repo root:

```
sage -python parity/compare.py --selftest                 # parser checks
sage -python parity/compare.py parity/maple_results.txt   # -> parity/parity_report.md
```

Without a results file, `compare.py` just runs the Python side of every case.

## Statuses

- **MATCH**: same canonical form (e.g. the same eta-quotient, the same relation space).
- **VALUE-MATCH**: different form, same q-series (e.g. an equivalent JAC product).
- **DIFFER**: investigate; either a bug in the port or a convention difference to document.
- **REVIEW**: no automatic comparison (jac2prod, findprod, qs2jaccombo, checkprod); both outputs shown.
- **MAPLE-ERROR / PY-ERROR / MISSING**: the case did not run on one side.

After changing `cases.py`, rerun `python3 parity/make_maple.py` and send the new `.mpl` file.
