# Pre-confirmation gate report

**FAIL — Required bias criterion fails in bank 0, process 3240; METHOD bars resampler fallback after bias failure**

Confirmation outcomes remain closed. Synthetic results use the unchanged real schedule.

| Gate | Result | Registered acceptance |
|---|---|---|
| calibration | NOT_COMPLETED | Every mandatory calibration feasible; residual <=1e-6; global count-weighted least-squares solution and complete truth |
| validity | FAIL | Every \|mean error\|+1.96 MCSE <=.002; exact coverage lower bound >=.92; >=95% valid datasets, each >=4750/5000 joint draws and every SD>0; blocking fixtures emit no verdict |
| boundary_false_verdict | NOT_COMPLETED | Every applicable exact one-sided 95% upper false-verdict bound <=.025, including latent truths |
| power | FAIL | Every mandatory designated reversal and all-zero/stable survival exact one-sided 95% lower power bound >=.80 |
| independent_validation | NOT_RUN | First fully passing resampler only, 2000 fresh bank1 datasets/process and 5000 draws; same rules; failure stops |

## Completed attempts

Bank 0, process 3240: 1000 datasets, 5000 draws/candidate/dataset. Maximum bias acceptance bound 0.00483256201 versus .002; 276/336 components fail. All mean errors, MCSEs, exact intervals and bounds are recorded in gate.json.

- Resampler 1: coverage 20/1000 (lower 0.013293); valid datasets 1000; survival 0/1000 (lower 0.000000); tests {'valid_dataset_fraction': True, 'coverage': False, 'latent_envelope_coverage': False, 'false_changes': True, 'false_survives': True, 'power': False}.
- Resampler 4: coverage 237/1000 (lower 0.214976); valid datasets 1000; survival 0/1000 (lower 0.000000); tests {'valid_dataset_fraction': True, 'coverage': False, 'latent_envelope_coverage': False, 'false_changes': True, 'false_survives': True, 'power': False}.
- Resampler 8: coverage 223/1000 (lower 0.201473); valid datasets 1000; survival 0/1000 (lower 0.000000); tests {'valid_dataset_fraction': True, 'coverage': False, 'latent_envelope_coverage': False, 'false_changes': True, 'false_survives': True, 'power': False}.

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

Unattempted processes/banks are unrun after failure, never inferred to pass. No pair, threshold, scenario, family or bank count was reduced. Dispatch and streaming decisions were sealed before synthetic outcomes; see DEVIATIONS.md.

## Independent verification and required stop

`verify_gate.py` independently reproduces all bias/MCSE calculations with compensated sums and all 15 exact interval checks by binomial-tail inversion. The original replicate 0 replays byte-identically for all three resamplers; this creates no new evaluation dataset or bank. See `gate-verification.json`. The worst component's mean error is -0.0023143442053923753 and MCSE is 0.001284805001653249; 0.004832562008632743 is the acceptance bound, not the point bias estimate.

The first calibration residual is 3.414932086379388e-12. All 1,000 datasets have valid intervals with all 5,000 draws under every candidate. Those checks do not overcome the failed bias, coverage or power criteria, or certify unrun scenarios.

**Inconclusive:** the failed pre-confirmation gate cannot settle material stability. Confirmation flight outcomes and annual ranking tables remain unopened; no confirmatory findings or production weights were generated. Checkpoint this gate report through the owner helper, with the resulting hash recorded in PROGRESS.md. METHOD requires a reviewed amendment and new gate before confirmation can proceed.
