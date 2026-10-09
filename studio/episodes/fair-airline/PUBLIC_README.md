# Tied on Paper: do near-equal airline averages survive a common basket?

The data, code and checks behind the film. The current owner claim/title lock
and publication approval are **PENDING**; this file prepares the public release.
The release title is read from `TITLE.json`.

**Companion page:** [COMPANION_URL — fill after owner-approved publication]
**Film:** [VIDEO_URL — fill after upload]

## The question and answer

United and Southwest look nearly tied in national on-time averages, around
78%. What happens if we compare overlapping flights on the same directional
route, scheduled date and two-hour departure window, using common weights?

Against each operator's **own arrival timetable**, United-operated flights
completed less than 15 minutes late **6.27 percentage points** more often in
2023–2024 and **8.20 points** more often in 2025. The nominal 99% missingness
envelopes are **4.60–7.94** and **5.31–11.00 points**. Both clear the two-point
line, so the registered result replicates. Cancellations and diversions fail;
exactly 15 minutes late fails. United Express and other operators are excluded.

This is a small, Denver-heavy overlap: roughly 11–12% of United schedules and
6% of Southwest schedules; Denver touches 79.31% / 82.22% of comparison weight.
The post-hoc shared elapsed-time-allowance check reduces the arrival gaps to
2.59 / 4.33 points. United's scheduled blocks are 4.52 / 4.45 minutes longer;
actual blocks on the completed-cell subset are 4.79 / 6.23 minutes longer.
Those checks are exploratory, post-hoc and not registered.

## What this cannot tell us

Matching the basket does not align arrival promises. Timetable choices, fleet,
staffing and operating circumstances remain bundled. This identifies neither
a causal airline-choice effect nor deliberate padding, passenger arrival,
connection success, safety or the best airline. The average is not a universal
time-of-day advantage. Fixed-schedule block uncertainty is not a forecast.
Two simulation gates failed before the interval redesign; the passing gate
validates the stated synthetic processes rather than every possible process.

## Where things are

All episode paths are under `studio/episodes/fair-airline/`.

| What | File |
| --- | --- |
| Original contract and failed gates | `METHOD.md`, `analysis/GATE.md` |
| Narrowed question and second failed gate | `analysis/amendment/` |
| Pre-outcome interval redesign and fresh passing gate | `analysis/amendment2/` |
| A-before-B seals, estimator and registered outputs | `analysis/confirm/`, `analysis/results.json`, `analysis/qa.json` |
| Findings, contrary evidence and reporting limits | `analysis/FINDINGS.md`, `analysis/review.md`, `analysis/review_checks/` |
| Independent blind derivation | `recheck/` |
| Claim ledger and fresh arithmetic verification | `CLAIMS.json`, `analysis/verify_claims.py`, `analysis/claims_check.json` |
| Script, animation and edit | `STORY.md`, `scenes/`, `EDIT.json` |
| Self-contained interactive companion | `companion/` |
| Prior design files actually cited by METHOD | `../../../ideation/rounds/r2/verify-S6.json`, `../../../ideation/rounds/r7/airline-redteam.md`, `fair-airline-METHOD.v2.md` |
| Original pre-filter commit identifiers | `analysis/source-commits.json` (public-history hashes differ) |

House animation and assembly are in `studio/render/` and `studio/tools/`.
The prior approvals in the methodological history concern outcome access;
they are not editorial or publishing approval for this film.

## How to reproduce

Use Python 3.12 and the packages/versions in `analysis/environment.json`; the independent recheck is documented in
`recheck/RECHECK.md`. `analysis/confirm/README.md` documents the seed,
scoring fixtures, starts and A-before-B protocol. Work in a disposable copy:
several historical runners write reports and check original Git seals.

1. Download the monthly archives at the addresses below; compare SHA-256 to
   `data/flights-manifest.json` before decoding. Keep all raw and row-level files
   private. Source lookups are in `data/docs-manifest.json`.
2. `analysis/snapshot.py` constructs the schedule-only support;
   `analysis/confirm/prepare.py` generates seeded starts;
   `analysis/confirm/analyze.py A` then `... B` score the periods. These historic
   seal-checking commands require the original audited Git IDs, not rewritten
   public-history IDs; do not silently bypass their checks. See the original
   IDs in `analysis/source-commits.json` and the artifact hashes in the reports.
3. `analysis/confirm/verify_numpy.py A` / `B`, the blind recheck and
   `analysis/review_checks/review_checks.py` document separate recomputations.
   The full claim verifier also needs the exposed 2015 pilot Parquets under
   `ideation/data/S6/`; their official source ZIP/CSV hashes are preserved in
   `analysis/pilot-source-manifest.json`. Those microdata are not bundled.
4. With the manifest-matched local inputs restored, run:

```sh
python analysis/verify_claims.py  # from the episode, in the scientific environment
python3 ../../tools/story_check.py .
python3 scenes/build_data.py
python3 companion/build.py
```

Scene and companion builds can run from the public aggregate evidence without
raw records. `companion/build.py` binds immutable analytical bytes, the reviewed
ledger semantics, and the current passing verifier. Locking changes statuses
and approval metadata, never observations. The HTML embeds its evidence and
fonts; no network is needed for interaction. Existing audio is required for
film reassembly; use `NARRATED_BUILD.md` for rendering and QA commands.

## Sources, addresses and hashes

Bureau of Transportation Statistics, Reporting Carrier On-Time Performance:
https://www.transtats.bts.gov/ONTIME/ . Field dictionary:
https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ .
Attribution: **Bureau of Transportation Statistics; independent processing.**
The monthly manifest retains retrieval metadata, member names, CRCs and hashes.

| Monthly source address | SHA-256 of downloaded ZIP |
| --- | --- |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_1.zip | `327924faa362d360747e9e4cf37f461c877441916321754f1789fadd61fd403a` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_2.zip | `bfa6eb7bebb53f10603110aa11bdebf00a89f51d870b331f6565181bb943ddbf` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_3.zip | `1a61dce7c50e5c4f074ebff69a833840f4c6be4e71d4a4707be540ace9e6d58b` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_4.zip | `adf3ecf6e3763a55c2acfc1fcf1c0ee0ac5a7ca079cb16cf15be5e39b921f7b4` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_5.zip | `aec2e926b11e55f88dd0ac48b649492048b4eba0983f1a564e746546568185b4` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_6.zip | `67dc6b993ba2e7c2175a874da7a8fbf12081c23c87523c0a5cd7d2f3e50450a1` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_7.zip | `b1b73635dcb2add363bb001d95c3f951e0ce4fc32130cbc76b565a531ced2146` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_8.zip | `d374aa3ec2b844d47c675d17cf71f2ade0af07b20670f9b8a2c6c1f5fe5d57bd` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_9.zip | `4e7bc3f76857accd1d4e493f03fb5ba2c1f68e82496cf16fd61addf4d8464cfa` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_10.zip | `a92cc51c6bb1e7fcf2732e27ac36ebbc92293acf8e3c0b33126abe28698ecf51` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_11.zip | `9ad54595568704a1cb7d821908611c220cf36da4d9a5ccea03b4deb9053b5025` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2023_12.zip | `c8391a3f06749b6ee4dec493fb7974f398b9d066a4e731c4cbb8932eddb774ce` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_1.zip | `fe089b45523f9d4ac0ccd0e176a543d274e914ee5ae5bd384dbaafc7dc06ebfd` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_2.zip | `8463683d100504a97847497d2f2281008fd9add9639bf7436a9747032df15f9a` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_3.zip | `e2c5021406f480e813a52a2ed795c251eb1169613da6a416daf88236db8c9013` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_4.zip | `d8b1e88626a7375d351962917fe5ec132660c1636dc8b91f778627c769e0e15a` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_5.zip | `03e4ae26c2d1247de02d0b9a4d87160f8021718abf475a1421de9c45b7d68b04` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_6.zip | `4f329439fd6892aaf89b32908191b2a007e70f775e2551181a22e704ef28a0ab` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_7.zip | `4d992fee134137b3fa43094d7e8cf4a8e6feaa6a422cffb4063f1ed6c7f3f731` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_8.zip | `58d651379af90cc44635657e95fe098567ff954046aec21d6d2cd18424a317f9` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_9.zip | `c0df7503b0050ca46099dab1edfffa33464a0a1031ad712c542af6a4ecece24c` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_10.zip | `a417136d6c1663736437dfeeacefa5b93b82e9db322c863c2f57b19bdd3f04fb` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_11.zip | `26b6e89e7c1f66163a412380c743c648eb470a9017074de4efbd209f1e09860a` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_12.zip | `a324577aa76d1f0aa36239f8010b6b5270fea0ff5ac846177753b76a42c5d01c` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_1.zip | `868387dcedaef1b8d8392e608e642219fde50d594c3cf2094aec858167629ccf` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_2.zip | `12dc8dbdb3c8b3c20d4c00a8b188196ae202f781a8760871ae502a9c733d0ecd` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_3.zip | `9c80fbc2112cdbf3f0613ec2001ba019b3ad75511cd69657080736e7eda9cef4` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_4.zip | `f3718431e988e2afd53a1714dfca37f67355b6fc06b02eb506bffa39300d608c` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_5.zip | `17c3419d7169b313b2bc8ddd3fd57e1e2d4d959c35f2da17f6a5610d4bac7d63` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_6.zip | `087b75e4e059516ca1181e58955d062f341933adb2706e5b2404ed10c9ecbdc6` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_7.zip | `74309a3a734d5104b4c212390c06eb3acacff15124b9cea49ba7d69a609a0d19` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_8.zip | `405668b8a807266236a635efbc1e9364abfb756db1a5c895e45abc9c7b7684f1` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_9.zip | `adc722b1c14944451b20ddcdbeec69bbc092310ab8044f758b8f4b82fde8d017` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_10.zip | `05d14d3fd67fa3e04b97c4d6bc7386f4a6c1cda13d2506cf0e9f0a6c620ed111` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_11.zip | `6d5b68eea3ebb25f3cb2843e701a6c809b5455301b3bbd7802a20d522ed770c8` |
| https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_12.zip | `a2af96d186bc9997fef47382b8589198281c9a722286d88f30032af8ee7dcd0f` |

The exposed 2015 pilot's 12 ZIP and CSV hashes are in
`analysis/pilot-source-manifest.json`; its addresses use the same official
PREZIP reporting-carrier product. Source-specific manifest fingerprints:

- `data/flights-manifest.json`: `919dd12d739751cf66d5fb34075c6b43e7fa05f801fde506d0c3479f46577a86`
- `data/docs-manifest.json`: `675ffb6f333dd5345741aabacf85afb48174ff1e9fee2ec3d1736238d4c3a59d`
- `data/history-manifest.json`: `ec7c97cb68d046eb0afe59ff0dfdc22e62350ad9336d9c633cc4063f7ff1a5cc`
- `analysis/pilot-source-manifest.json`: `46a88e523d9ee69ce28bfe9c811cf0e7b476b4bd328260802411ac42af037805`
- `analysis/results.json`: `5ad0c9319304bb645c966aca253d00035913105b900f58b6fd8be694e66597de`
- `analysis/review_checks/results.json`: `0a430fc236035ca94043a76cbb9e49e076f5947ed0bfd763b8cc2ab71736a959`

Annual DOT Air Travel Consumer Reports (Tables 1C/1D):

- 2023: https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202024%20ATCR%20revised%203-06-2025.pdf
- 2024: https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202025%20ATCR.pdf
- 2025: https://www.transportation.gov/sites/dot.gov/files/2026-03/February%20%202026%20ATCR.pdf

The official annual pages were checked online, without saving or redistributing
PDFs; no downloaded-PDF hash is claimed. `analysis/CONTEXT.md` preserves the
numeric extraction and distinguishes operating rows from marketing networks.
Failed historical source requests have addresses/statuses, not fabricated hashes.

## Licence notes

Repository-authored material follows the root `LICENSE`. Source data retains
its own terms: reporting-carrier raw redistribution rights remain unresolved
in the source manifest. No raw ZIP, flight-level derivative or saved third-party
page is redistributed. Do not transfer another BTS product's public-domain
label to this one. Keep addresses and hashes (LESSONS 10).
Embedded Big Shoulders Display, Source Serif 4 and IBM Plex Mono fonts use SIL
Open Font License; licence texts are in `studio/render/fonts/OFL-*.txt` and the
companion's embedded CSS. No carrier logos or third-party artwork are used.
