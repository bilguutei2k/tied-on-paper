# Pre-confirmation gate status

**BLOCKED — no simulation gate has run.**

No confirmation outcome columns were materialized, decoded into analysis tables, summarized or plotted. No synthetic datasets or bootstrap draws were generated.

METHOD requires: “Commit the support manifest BEFORE synthetic outcomes or power results are inspected.” It also requires a committed scenario manifest and executable generator before the first simulated outcome. The owner prohibits this agent from writing `.git`; Claude commits. No commit barrier is waived.

The complete Monte Carlo runner and executable scenario manifest are not implemented in this staged handoff. `gate.py` is an honest prerequisite checker and blocked-report writer; it is not evidence of executed simulations.

| Gate | Result | Registered acceptance rule |
|---|---|---|
| validity | BLOCKED / NOT RUN | Each |mean G,D error| + 1.96*MCSE <=0.002; One-sided 95% exact binomial lower bound on whole-family coverage >=0.92; At least 4750/5000 joint draws per valid dataset; >=95% datasets valid; every component SD >0; No substantive verdict from 1% missingness, invalid-data or above-cutoff fixtures |
| calibration | BLOCKED / NOT RUN | Every required single-edge probability calibration feasible; full-vector residual <=1e-6; Complete frozen unordered-pair x period x contrast x scoring-assignment family; Least squared distance to fixed base, one carrier/cell probability, bounds [0.05,0.99] |
| boundary_false_verdict | BLOCKED / NOT RUN | Each applicable one-sided 95% exact binomial upper bound <=0.025; False changes if true R<=0.02; false survives if true H>=0.02; latent truth also judged under missingness |
| power | BLOCKED / NOT RUN | Each supported pair/direction at delta=.04: designated-pair joint power lower exact 95% bound >=0.80; Whole-table survival lower exact 95% bound >=0.80 for all-zero and calibrated stable-order cases; All registered baseline/shock/seasonality levels, with no missingness and .05% informative missingness |
| independent_validation | BLOCKED / NOT RUN | Only first fully passing resampler, fresh bank1, same acceptance rules; failure stops |

Selection: exactly 1,000 datasets/scenario, 5,000 draws/dataset; independent validation: exactly 2,000 datasets/scenario, 5,000 draws/dataset. No attempts, resampler selection, bias estimates, coverage counts, false-verdict counts or power estimates exist.

The schedule eligibility and deterministic fixtures are separate structural checks; passing those cannot clear validity or power.

## Frozen sets

| Set | Size | SHA-256 |
|---|---:|---|
| cells | 14494757 | `820ea4b4ebb37e5497761cc1b0d2cad3a05a68d75f58517a97f88a53e8d127a7` |
| components | 336 | `6e6d5d89e8aa8f5ff212ba03f9d7b9b42293259fc25bdbe73882ebec17b4e183` |
| incident_carriers | 8 | `731a9156db4ba82758451558e7493564c5e49e8bf716d33b636c3940996c8190` |
| omission_airports | 5 | `b9839ef9e312c6132f409169fc9af43fb692c9146d6ed634fa9d5222e9f095b3` |
| pair_cells | 2746293 | `370c2efedd25032ca6566c56738c1b376fddbf8fb6cbcba33bbb60d8aedbf7be` |
| routes | 1855 | `9e822e55480ef9b035f95f4c158022b23c02e6e9bc5fa458d49e13957532cc2f` |
| source_rows | 20928579 | `435742cb0a81ed7d908555709b673019274c1c887d0f74587c4ee8e20d861747` |
| supported_pairs | 28 | `509ecca0cc156f1f59d9a107b1f3459bc76e8fa70ecfe4c0cbe9be689ba2b28f` |
| weeks | 159 | `ac2ed213bef5c5fe19d98ee2f658f5d42e2acbf0a3883811428f33e8bd6458b1` |

## Required handoff

Claude must commit the support artifacts. Then implement and commit the full deterministic calibration/scenario manifest and executable generator, without generating simulated outcomes before that commit. Only then run the complete registered selection and validation banks. Confirmation outcomes remain closed regardless of any later gate result until the gate report is committed.

Source-specific raw redistribution terms remain unresolved. Publish retrieval code, URLs/hashes and aggregates; raw ZIPs, documentation snapshots and row-level derivatives remain ignored. See DEVIATIONS.md and data/docs-manifest.json.
