# Amendment 2 — outcome-blind gate results

**PASS**. Design/code checkpoint: `8a33153`. Confirmation outcomes remain unopened.

Amendment 2 was designed after seeing Amendment 1’s synthetic failure, after two failed outcome-blind gates and before any confirmation outcome. Bank 0 informed design and supplies no acceptance evidence here. The sole candidate is the sealed 28-day studentized block interval; no fallback or Amendment 3 was attempted.

The comparison, two-point line, frozen support, periods, scoring, missingness envelope, generator, all 20 scenarios and acceptance/early-stop rules are unchanged. Exactly 1,999 draws per dataset. All reported probability bounds are one-sided 95% exact binomial bounds; bias is in percentage points.

| Bank | Scenario/profile | A/B truth (pp) | Max bias bound (pp) | Joint coverage % [lower] | Max false upper % | Min required power lower % | Pass |
|---|---|---|---|---|---|---|---|
| 2 | 0: independent | 2/2 | 0.0174 | 98.90 [98.186] | 1.181 | — | True |
| 2 | 1: independent | 0/0 | 0.0254 | 99.10 [98.435] | 0.299 | 99.701 | True |
| 2 | 2: independent | 4/4 | 0.0195 | 98.60 [97.820] | 0.299 | 99.701 | True |
| 2 | 3: shared_daily | 2/2 | 0.0121 | 98.60 [97.820] | 1.311 | — | True |
| 2 | 4: shared_daily | 0/0 | 0.0166 | 98.90 [98.186] | 0.299 | 99.701 | True |
| 2 | 5: shared_daily | 4/4 | 0.0124 | 99.40 [98.819] | 0.299 | 99.701 | True |
| 2 | 6: differential_daily | 2/2 | 0.0302 | 98.40 [97.580] | 1.181 | — | True |
| 2 | 7: differential_daily | 0/0 | 0.0246 | 98.80 [98.063] | 0.299 | 99.701 | True |
| 2 | 8: differential_daily | 4/4 | 0.0252 | 98.30 [97.461] | 0.299 | 99.372 | True |
| 2 | 9: serial_daily | 2/2 | 0.0449 | 98.50 [97.700] | 1.181 | — | True |
| 2 | 10: serial_daily | 0/0 | 0.0397 | 98.90 [98.186] | 0.299 | 92.834 | True |
| 2 | 11: serial_daily | 4/4 | 0.0437 | 98.50 [97.700] | 0.299 | 89.156 | True |
| 2 | 12: serial_missing | 2/2 | 0.0369 | 97.50 [96.526] | 1.311 | — | True |
| 2 | 13: serial_missing | 0/0 | 0.0324 | 98.00 [97.107] | 0.299 | 90.553 | True |
| 2 | 14: serial_missing | 4/4 | 0.0261 | 97.60 [96.641] | 0.299 | 89.692 | True |
| 2 | 15: serial_daily | 2/4 | 0.0291 | 98.70 [97.941] | 0.913 | 90.229 | True |
| 2 | 16: serial_daily | 4/2 | 0.0279 | 98.70 [97.941] | 0.774 | 99.527 | True |
| 2 | 17: serial_daily | 0/4 | 0.0350 | 98.30 [97.461] | 0.299 | 91.093 | True |
| 2 | 18: serial_daily | 4/0 | 0.0316 | 98.60 [97.820] | 0.299 | 94.490 | True |
| 2 | 19: serial_daily | 3/3 | 0.0360 | 99.00 [98.310] | 0.299 | — | True |
| 1 | 0: independent | 2/2 | 0.0090 | 98.90 [98.433] | 0.784 | — | True |
| 1 | 1: independent | 0/0 | 0.0121 | 98.80 [98.316] | 0.150 | 99.850 | True |
| 1 | 2: independent | 4/4 | 0.0107 | 98.65 [98.143] | 0.150 | 99.850 | True |
| 1 | 3: shared_daily | 2/2 | 0.0082 | 99.05 [98.609] | 0.591 | — | True |
| 1 | 4: shared_daily | 0/0 | 0.0140 | 98.85 [98.375] | 0.150 | 99.850 | True |
| 1 | 5: shared_daily | 4/4 | 0.0136 | 99.20 [98.787] | 0.150 | 99.850 | True |
| 1 | 6: differential_daily | 2/2 | 0.0138 | 99.20 [98.787] | 0.784 | — | True |
| 1 | 7: differential_daily | 0/0 | 0.0138 | 98.85 [98.375] | 0.150 | 99.686 | True |
| 1 | 8: differential_daily | 4/4 | 0.0155 | 99.00 [98.550] | 0.150 | 99.850 | True |
| 1 | 9: serial_daily | 2/2 | 0.0195 | 98.00 [97.404] | 1.153 | — | True |
| 1 | 10: serial_daily | 0/0 | 0.0199 | 98.80 [98.316] | 0.150 | 92.307 | True |
| 1 | 11: serial_daily | 4/4 | 0.0275 | 98.65 [98.143] | 0.150 | 92.520 | True |
| 1 | 12: serial_missing | 2/2 | 0.0178 | 98.55 [98.028] | 0.591 | — | True |
| 1 | 13: serial_missing | 0/0 | 0.0293 | 98.45 [97.914] | 0.150 | 91.777 | True |
| 1 | 14: serial_missing | 4/4 | 0.0197 | 98.65 [98.143] | 0.150 | 91.301 | True |
| 1 | 15: serial_daily | 2/4 | 0.0172 | 98.25 [97.686] | 1.153 | 91.936 | True |
| 1 | 16: serial_daily | 4/2 | 0.0252 | 98.15 [97.573] | 0.721 | 99.850 | True |
| 1 | 17: serial_daily | 0/4 | 0.0243 | 97.95 [97.348] | 0.150 | 91.406 | True |
| 1 | 18: serial_daily | 4/0 | 0.0259 | 98.35 [97.800] | 0.150 | 92.520 | True |
| 1 | 19: serial_daily | 3/3 | 0.0187 | 98.50 [97.971] | 0.150 | — | True |

## Completion and limits

- Bank 2: 20/20 scenarios completed; 19/19 required scenarios passed; 20,000 datasets. Unrun: [].
- Bank 2 worst false-direction exact upper: 1.311%; minimum joint-coverage lower: 96.526%.
- Bank 2 minimum required-power lower: 89.156%.
- Bank 2 descriptive three-point replicated power: 277/1000 (27.70%; exact lower 25.373%). This scenario has no required-power pass claim.
- Bank 2 serial boundary scenario 9: A above/below 4/5; B above/below 6/0, out of 1000 each.
- Bank 1: 20/20 scenarios completed; 19/19 required scenarios passed; 40,000 datasets. Unrun: [].
- Bank 1 worst false-direction exact upper: 1.153%; minimum joint-coverage lower: 97.348%.
- Bank 1 minimum required-power lower: 91.301%.
- Bank 1 descriptive three-point replicated power: 491/2000 (24.55%; exact lower 22.970%). This scenario has no required-power pass claim.
- Bank 1 serial boundary scenario 9: A above/below 15/4; B above/below 13/8, out of 2000 each.

Total: 60,000 distinct evaluation datasets, 119,940,000 joint bootstrap draws. Timing-only and replay datasets are excluded.

## Verification and timing

Independent verification passes: 338 binomial-tail inversions, 40 original-replicate replays, compensated-sum bias checks, event counts, acceptance and early-stop logic, unchanged manifests/functions, direct interval arithmetic and frozen membership/status checks.
Ten-worker bank-90 timing: 0.1620 seconds for ten datasets. Numerical libraries use one thread. Benchmark acceptance was not inspected. Per-scenario runtimes are saved in results.json.

Wording clarification: the sealed draft calls B “independent-labeled”; B is a separately labeled 2025 replication, with no added assumption of independence between A and B. The unchanged generator keeps shocks continuous across physical year boundaries. Bank 1 is the independent validation bank.
The finite-window variance correction and Student-t floor are specified approximations; this gate certifies only the registered fixed-schedule processes. Three-point power is descriptive. A passing gate does not establish an observed airline advantage or authorize confirmation access. Owner approval and later production-code/resampling-array seals are still required.
