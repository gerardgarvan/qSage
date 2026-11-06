# qseries-sage vs Maple qseries: parity report

Battery seed 20261106, 130 cases. Maple: Maple 2026.2, X86 64 WINDOWS, Oct 31 2026, Build ID 2051430. qseries: []. (qs2jaccombo_1 was run by hand in Maple 2026.2: the battery file used for this run predated that case.)

| status | count |
|---|---|
| KNOWN-MAPLE | 5 |
| MATCH | 124 |
| VALUE-MATCH | 1 |

## KNOWN-MAPLE (5)

### `theta2_q3` (coeffs)

Maple cannot take coefficients of fractional powers of q (Maple: unable to compute coeff)

- Maple input: `CL(expand(simplify(theta2(q^3,10)/q^(3/4))),0,40)`
- Maple result: `ERROR unable to compute coeff`
- Python result: `[2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0]`

### `etamake_theta2` (eta)

Maple etamake cannot handle the q^(1/4) factor of theta2 (Maple: invalid argument for sign, lcoeff or tcoeff)

- Maple input: `etamake(theta2(q,100),q,100)`
- Maple result: `ERROR invalid argument for sign, lcoeff or tcoeff`
- Python result: `2 * eta(2*tau)^-1 * eta(4*tau)^2`

### `findhommodp_e4_5` (rels)

Maple findhommodp skips the q^0 coefficient (README)

- Maple input: `findhommodp([E4S(100),E6S(100),1],5,q,1,0)`
- Maple result: `{X[1], X[3]}`
- Python result: `{X1 - X3}`

### `findhommodp_e6_7` (rels)

Maple findhommodp skips the q^0 coefficient (README)

- Maple input: `findhommodp([E4S(100),E6S(100),1],7,q,1,0)`
- Maple result: `{X[2], X[3]}`
- Python result: `{X2 - X3}`

### `findhommodp_deg2_5` (rels)

Maple findhommodp skips the q^0 coefficient (README)

- Maple input: `findhommodp([E4S(100),E6S(100)],5,q,2,0)`
- Maple result: `{X[1]^2}`
- Python result: `set()`


## VALUE-MATCH (1)

### `findnonhomcombo_watson` (combo)

overlapping but not identical sets of combinations

- Maple input: `findnonhomcombo(S(q^2*etaq(q,7,100)^8/etaq(q,1,100)^8,100),[S(q*etaq(q,7,100)^4/etaq(q,1,100)^4,100),S(q^2*etaq(q,49,100)/etaq(q,1,100),100)],q,7,-15)`
- Maple result: `{X[1]^2}`
- Python result: `{X1^2, 343*X2^7 + 343*X2^6 + 147*X2^5 + 49*X1*X2^3 + 49*X2^4 + 35*X1*X2^2 + 21*X2^3 + 7*X1*X2 + 7*X2^2 + X2}`


## MATCH (124)

- `aqprod_1` (coeffs)
- `aqprod_2` (coeffs)
- `qbin_1` (coeffs)
- `qbin_2` (coeffs)
- `qbin_3` (coeffs)
- `etaq_1` (coeffs)
- `etaq_3` (coeffs)
- `etaq_7` (coeffs)
- `theta3_1` (coeffs)
- `theta4_1` (coeffs)
- `theta2_1` (coeffs)
- `theta_z` (coeffs)
- `tripleprod_z` (coeffs)
- `tripleprod_q` (coeffs)
- `quinprod_z` (coeffs)
- `winquist_ab` (coeffs)
- `winquist_doc` (coeffs)
- `jacprod_1_5` (coeffs)
- `jacprod_2_7` (coeffs)
- `jacprod_3_8` (coeffs)
- `jac2series_doc1` (coeffs)
- `jac2series_doc2` (coeffs)
- `jac2series_doc3` (coeffs)
- `jac2series_ratio` (coeffs)
- `jac2prod_1` (poch)
- `jac2prod_2` (poch)
- `qdegree_1` (number)
- `lqdegree_1` (number)
- `sift_P_5_0` (coeffs)
- `sift_P_5_4` (coeffs)
- `sift_P_7_5` (coeffs)
- `sift_P_11_6` (coeffs)
- `sift_P_3_1` (coeffs)
- `sift_P_2_1` (coeffs)
- `sift_E_5_0` (coeffs)
- `checkmult_doc_S1` (bool)
- `checkmult_doc_S3` (bool)
- `checkmult_delta` (bool)
- `prodmake_tripleprod` (prod)
- `prodmake_RR` (prod)
- `prodmake_rand_0` (prod)
- `prodmake_rand_1` (prod)
- `prodmake_rand_2` (prod)
- `prodmake_rand_3` (prod)
- `prodmake_rand_4` (prod)
- `prodmake_rand_5` (prod)
- `prodmake_rand_6` (prod)
- `prodmake_rand_7` (prod)
- `prodmake_rand_8` (prod)
- `prodmake_rand_9` (prod)
- `etamake_theta3` (eta)
- `etamake_theta4` (eta)
- `etamake_triangular` (eta)
- `etamake_rand_0` (eta)
- `qetamake_rand_0` (qeta)
- `etamake_rand_1` (eta)
- `qetamake_rand_1` (qeta)
- `etamake_rand_2` (eta)
- `qetamake_rand_2` (qeta)
- `etamake_rand_3` (eta)
- `qetamake_rand_3` (qeta)
- `etamake_rand_4` (eta)
- `qetamake_rand_4` (qeta)
- `etamake_rand_5` (eta)
- `qetamake_rand_5` (qeta)
- `etamake_rand_6` (eta)
- `etamake_rand_7` (eta)
- `etamake_rand_8` (eta)
- `etamake_rand_9` (eta)
- `etamake_rand_10` (eta)
- `etamake_rand_11` (eta)
- `qetamake_triangular` (qeta)
- `jacprodmake_tripleprod` (jac)
- `jacprodmake_RR` (jac)
- `jacprodmake_E0` (jac)
- `jacprodmake_theta3` (jac)
- `jacprodmake_doc_XX` (jac)
- `jacprodmake_rand_0` (jac)
- `jacprodmake_rand_1` (jac)
- `jacprodmake_rand_2` (jac)
- `jacprodmake_rand_3` (jac)
- `jacprodmake_rand_4` (jac)
- `jacprodmake_rand_5` (jac)
- `jacprodmake_rand_6` (jac)
- `jacprodmake_rand_7` (jac)
- `qfactor_t8` (qfactor)
- `qfactor_rand_0` (qfactor)
- `qfactor_rand_1` (qfactor)
- `qfactor_rand_2` (qfactor)
- `qfactor_rand_3` (qfactor)
- `qfactor_rand_4` (qfactor)
- `qfactor_rand_5` (qfactor)
- `mprodmake_doc` (mprod)
- `mprodmake_rand_0` (mprod)
- `mprodmake_rand_1` (mprod)
- `mprodmake_rand_2` (mprod)
- `mprodmake_rand_3` (mprod)
- `zqfactor_doc` (zq)
- `zqfactor_plus` (zq)
- `findprod_1` (list)
- `qs2jaccombo_1` (jaccombo)
- `checkprod_1` (list)
- `findhom_theta_1` (rels)
- `findhom_theta_2` (rels)
- `findhom_theta_3` (rels)
- `findnonhom_theta` (rels)
- `findhomcombo_doc` (combo)
- `findhomcombo_doc2` (combo)
- `findlincombo_doc` (lincombo)
- `findlincombo_doc_none` (lincombo)
- `findlincombo_rand_0` (lincombo)
- `findlincombo_rand_1` (lincombo)
- `findlincombo_rand_2` (lincombo)
- `findlincombo_rand_3` (lincombo)
- `findlincombo_rand_4` (lincombo)
- `findmaxind_1` (maxind)
- `findpoly_cubic` (poly)
- `findcong_partitions` (cong)
- `findcong_distinct` (cong)
- `findcong_overpartitions` (cong)
- `findcong_bipartitions` (cong)
- `findcong_composite_gcd` (cong)
- `findlincombomodp_doc` (lincombo)
- `findhomcombomodp_1` (combo)
