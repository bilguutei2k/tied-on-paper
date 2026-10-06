# Scenario/generator commit handoff

Support is committed in `af8e89f`; METHOD and its registration `3672298` are
unchanged. Confirmation outcomes remain closed. Zero synthetic outcomes,
bootstrap draws, bank attempts or production arrays have been generated.

The next barrier is METHOD's instruction: “Before the first simulated outcome
is generated, commit a machine-readable scenario manifest and executable
generator”. Claude must commit this stage; this agent cannot write `.git`.

`scenario-manifest.json` specifies the entire Cartesian family, fixed process
IDs, coefficients, covariance, status/masking, calibration objective and
constraints, solver, tolerance, streams and full expected-truth expressions.
`scenarios.py` is its lossless iterator. There are 62,333 templates × 150 stress
settings × 10 missingness mechanisms, or 93,499,500 process IDs. Every supported
edge/direction and all 210 sets of two vertex-disjoint edges are included;
two-edge infeasibility is determined numerically, never from performance.

`simulation-structure.json` seals the numeric counts/base coefficients and
linear national/shared expectation operator. Its private derivatives have
4,354,655 probability cells mapped to all 15,243,703 candidate source flights.
They contain schedule, probability and count fields only. Original support
rosters, cells, memberships and their hashes are unchanged.

`generator.py` implements the probit, continuous stationary AR shocks and
status/missingness mappings. It verifies committed exact code/manifest bytes
before its outcome entry point constructs any RNG. Native readers receive
Python-opened, hash-verified schedule files; native SQL receives Arrow tables.
`bootstrap.py` implements the exact registered week/block index API and loop
order, and rejects production weights unless both banks have passed.

Expected calibrated probabilities/truths are supplied as exact executable
mathematical expressions, not millions of expanded numeric vectors. This
interpretation is disclosed in DEVIATIONS.md. Full numerical calibration
feasibility, bias, coverage, false-verdict, power and independent validation
have not been certified. The six real-structure probability probes in
`scenario-verification.json` are implementation checks only; the twelve numeric
base expectation vectors in `scenario-base-truth.json` are not simulated data.

Commit the scenario/generator files, verification/base-truth/structure seals,
progress, gate reports and deviations. Include `data/history-manifest.json`
and its acquisition code for the two historical-source 403 records. Raw and
bulk-derived files remain ignored. Their hashes and reproducible construction
code are public; no raw-file release is authorized.

After that commit, finish the complete numeric calibration audit and implement
the Monte Carlo runner behind `gate.py`, retaining the exact bank sizes and
acceptance criteria. Freeze truths before each process emits outcomes, record
all feasible two-edge cases and all mandatory single-edge failures, use the
same generated datasets across the fixed resampler order, and validate only
the first fully passing resampler on the fresh bank. No confirmation outcome
opens regardless of the result until Claude commits the completed gate report.

## Continuation

The scenario/generator seal was committed as `5aa59e2`. The executable full-family runner is now gate.py → gate_runner.py, with gate_runtime.py, gate_statistics.py and gate_fixtures.py. execution-plan.json freezes dispatch and code hashes; runner-verification.json records deterministic verification; calibration-first.json seals numeric probabilities/truth for the first required process. Bank execution remains stopped until the runner checkpoint completes. Earlier handoff text above is historical.
