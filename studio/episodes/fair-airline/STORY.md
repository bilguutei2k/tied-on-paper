# Tied on Paper

Status: script draft v1, by Sol 6.1, 2026-10-08; not locked.
Working title is configured in TITLE.json. Owner title/claims approval and
publishing approval are PENDING; numerical checks pass.

## Argument: “The average depends on the flights”

| Beat | What the viewer learns | Evidence |
|---|---|---|
| Belief | Published operating rankings put United and Southwest adjacent, around 78% on time. | FA-C042–043, FA-C046–047, FA-C050–051; CONTEXT |
| Obvious answer | Near-equal national rates suggest equally punctual service. | FA-C007, FA-C026; interpretation to test |
| Flaw | National averages mix different routes, airports and departure times; arrival deadlines also differ. | METHOD; Amendment 1 |
| Fairer test | Compare the same directional route, scheduled day and two-hour departure window, with common cell weights and a two-point line. | FA-C004–005; Amendment 1 |
| Honest uncertainty | Two earlier simulation gates failed; the interval was redesigned before any 2023–25 flight outcomes were opened. Fresh selection and independent validation passed. | Amendment 2; FA-C073–075; analysis/PROGRESS.md |
| Verdict | United's own-timetable advantage is +6.3 points in 2023–24 and +8.2 in 2025; both envelopes clear two points: replicated. | FA-C001–003 |
| What it cannot tell us | Shared deadlines shrink the gap; departure delays remain different. Small, Denver-heavy, operator-only overlap and time-of-day heterogeneity limit the conclusion. | FA-C006, FA-C025, FA-C054–056, FA-C058, FA-C060, FA-C062–064, FA-C066, FA-C068; review caveats |

Wording rules: say **United-operated versus Southwest-operated comparable
flights**, scored against **each operator's own published arrival timetable**.
United Express and other codeshare operators are excluded. “On time” means
strictly less than fifteen minutes late; cancellations, diversions and
indeterminate outcomes fail. Use **unadjusted all-flights** for national rates,
not “unmatched.” The permitted decisive label is **UA advantage above two
points**; in viewer language, **United advantage above two points**. The same
label in both periods permits **replicated**. Alternatives are **no material
UA advantage under this rule** and **inconclusive**. Do not revive the retired
all-airline table verdict or claim a two-period national-versus-matched reversal:
United already led nationally in 2023–24. Intervals are **nominal 99% missingness
envelopes**, describing repeated outcomes/calendar shocks on fixed schedules;
they are not census counting error or future-flight predictions. The two-point
scale predates the pilot for another test; its amended use and scope are
post-pilot, pre-confirmation. Say the two failed gates and subsequent interval
redesign plainly. Every added timetable, departure, concentration and time-of-day
check is **exploratory, post-hoc, not registered** and inherits no verdict.
No causal airline-choice effect, intentional-padding conclusion, recommendation
or best-airline ranking. First person; claim tags and source labels are not spoken.

## Scene table

| Scene | Viewer question | Evidence | Visual | Why next? |
|---|---|---|---|---|
| S01 Tied on paper | What would I infer from the rankings? | FA-C046–047, FA-C050–051 | Small table: annual operating rows, adjacent ranks; Night hook. | Define on time. |
| S02 Fifteen minutes | What counts as a success? | FA-C005; Amendment 1; CONTEXT | Q measure cards: timely / late / cancelled; illustrative boundary clock. | Look behind the average. |
| S03 The mixed basket | Are the averages comparing the same trips? | FA-C007, FA-C026; METHOD | Two-part split: separate networks → common opportunities, schematic. | Specify a comparable cell. |
| S04 Same trip, same window | What gets matched? | FA-C005; Amendment 1 | Q route/date/window cards; illustrative DEN → LAX, reverse arrow separated. | Give cells common influence. |
| S05 Same basket, same line | What is the actual test? | FA-C004–006, FA-C025; Amendment 1 | Q weighting schematic → N reference line at +2 points. | Check the uncertainty. |
| S06 Two failed checks | Was the interval fixed before outcomes? | Amendment 2; FA-C073–075 | Q chronology: FAIL / FAIL / REDESIGN / FRESH PASS / OUTCOMES. | Open the primary result. |
| S07 The first result | Does the interval clear the line? | FA-C001, FA-C009, FA-C011 | N observed gap and nominal 99% envelope, A only. | Open a separate period. |
| S08 The replication | Does the decisive label repeat? | FA-C002–003 | N B reveal beside sealed A; one mint REPLICATED. | Check dependence on matching. |
| S09 The nearby tests | Does another window change the picture? | FA-C020–022, FA-C038–040 | Small table of registered descriptive sensitivities; no verdict stamps. | Ask what the timetable measures. |
| S10 Whose deadline? | Is the advantage partly a deadline comparison? | FA-C054–055, FA-C062–063 | Two-part split: scheduled/actual duration, then own/shared allowance; exploratory label. | Inspect departures. |
| S11 Leaving late | Can arrival padding explain that? | FA-C056, FA-C064 | Q late-departure cards with scheduled denominators; exploratory label. | Bound the population. |
| S12 The boundary of the answer | Where and when does this apply? | FA-C006, FA-C025, FA-C058, FA-C060, FA-C066, FA-C068 | Q coverage/Denver cards → early/late small table → Night conclusion. | End with scope. |

Visual implementation: Paper/Night surfaces, Ink rules, Big Shoulders claims,
Plex Mono numbers and the source/scope caption throughout. United uses player-a,
Southwest player-b; color is accompanied by names. Bind every empirical value
to its claim key. Small tables stay within four columns and four rows. Adapt
N's existing dot/range grammar as proposed here: percentage-point axis includes
zero and the +2 materiality rule, with nominal 99% envelope labels instead of the
reference component's 95% resampling captions. Mint appears only for the
registered decisive conclusion. Record that adaptation in DIRECTION before
renderer use; no renderer is created in this script task. Route/window pictures
are marked SCHEMATIC, with no invented flight records or route-specific gap.
Exploratory panels carry “POST-HOC · NOT REGISTERED” adjacent to their values.
Durations use gate-to-gate block minutes; shared allowance starts at each
scheduled departure, never a literal shared wall-clock arrival deadline. Portrait
versions stack panels separately within the safe area; content ends above y=1500.
Original typography and geometry only; no airline logos or copied report pages.

## Script (v1)

### S01 Tied on paper

> I look at an airline punctuality table because I would quite like my flight to arrive when it says it will. Apparently, this is a statistical ambition.
> In the published operating rankings, United and Southwest sit side by side. In 2024, their on-time rates are 78.60% and 78.57%. In 2025, both are still about seventy-eight percent, with Southwest just ahead. [FA-C046, FA-C047, FA-C050, FA-C051]
> My obvious answer is: equally punctual. But I want to know whether that apparent tie survives comparing similar trips. I'm testing United-operated and Southwest-operated flights. United Express and other codeshare operators are excluded. [FA-C001]

Source card: official annual DOT operating tables linked in [CONTEXT](analysis/CONTEXT.md).
Keep annual labels visible; do not use marketing-network ranks for this population.

### S02 Fifteen minutes

> First, “on time” needs a definition. Here, a flight succeeds if it completes without cancellation or diversion and arrives less than fifteen minutes after its own published arrival time. Exactly fifteen minutes late fails. [FA-C005]
> A cancellation is a failure, not a flight that conveniently vanishes from the denominator. Diversions fail too. If the outcome cannot be determined, the primary score counts it as a failure and the interval allows for that uncertainty.
> The published national tables already retain failed scheduled services. My objection isn't that they forgot cancellations. It's that their averages describe different collections of flights.

Definition/source: [Amendment 1](analysis/amendment/AMENDMENT-1.md), scoring;
[CONTEXT](analysis/CONTEXT.md), DOT denominator and boundary definitions.

### S03 The mixed basket

> Across all reported flights in 2023–2024, United is at 78.34% and Southwest at 77.91%. In 2025, they're at 77.65% and 77.76%. These are unadjusted all-flights rates. [FA-C007, FA-C026]
> I can count those flights perfectly and still be making an awkward comparison. One airline's average mixes its routes, airports and departure times; the other's mixes a different network.
> Imagine comparing runners on different courses, then debating the stopwatch's accuracy. The stopwatch may be fine. I need a more comparable course.
> So I restrict the question to opportunities both operators actually served. That changes the population I'm describing.

Methodological inference: METHOD, “Belief → obvious answer → flaw → fairer test”;
no quantified network explanation or causal attribution.

### S04 Same trip, same window

> My unit is a comparable cell: the same directional airport route, the same scheduled departure day, and the same two-hour departure window. Both airlines must have scheduled service in it. [FA-C005]
> For a concrete example, imagine Denver to Los Angeles on the same day, with both departures scheduled between ten in the morning and noon. This is a teaching example, not a pair of observed flight records.
> Los Angeles to Denver is a different cell. Another date is different. A departure outside that window is different. I match scheduled departures, so a delay cannot move a flight into a friendlier comparison.
> The window makes circumstances more alike. It doesn't make them identical.

Schematic definition: [Amendment 1](analysis/amendment/AMENDMENT-1.md), retained
cells; METHOD, “Outcome, support and frozen weighting.” No route outcome asserted.

### S05 Same basket, same line

> Inside each cell, I calculate each operator's success rate. Then I give both operators the same cell weight, based on their combined scheduled-flight count. A busy shared cell matters more than a quiet one, equally for both sides.
> The first period pools 2023–2024. I keep 2025 separate as replication, using that year's own comparable basket. [FA-C006, FA-C025]
> The decision line is two percentage points: one extra timely completion per fifty scheduled flights. United's whole uncertainty interval must sit above it. [FA-C004]
> This single-pair rule was fixed after an exploratory pilot and a failed simulation gate, before confirmation outcomes. I don't get to move the line after seeing the answer. [FA-C004]

Weighting and decisions: Amendment 1; own-timetable scope strip stays visible.

### S06 Two failed checks

> Before opening any 2023–2025 flight outcomes, I tested the uncertainty procedure on simulated outcomes with known answers. Two earlier simulation checks failed. The interval was redesigned after those failures, while the real outcomes stayed closed. [FA-C004, FA-C006, FA-C025]
> The revised method keeps whole stretches of calendar days together across the network, because disruption can travel across airports and persist over time. [FA-C005]
> Fresh simulation runs and a separate validation bank then passed the specified checks. That is evidence under those simulated conditions, not a guarantee for every possible disruption. [FA-C073, FA-C074, FA-C075]
> I want the failed checks in the film. A redesigned test has a history, and that history belongs beside its result.

Documentary disclosure: [Amendment 1](analysis/amendment/AMENDMENT-1.md), failed
gate; [Amendment 2](analysis/amendment2/AMENDMENT-2.md), post-simulation redesign;
[progress](analysis/PROGRESS.md), fresh selection/validation and pre-access seals.
The outcome-blind stage used schedule fields; do not claim no flight data at all
were opened or perfect ignorance of public rankings.

### S07 The first result

> In the comparable 2023–2024 basket, United's common-weighted timely-completion rate is 79.75%; Southwest's is 73.48%. [FA-C009, FA-C011]
> The gap is 6.3 percentage points for United. The nominal 99% uncertainty envelope runs from 4.60 to 7.94 points. The entire envelope clears the two-point line. [FA-C001, FA-C004]
> The permitted verdict is: United advantage above two points. [FA-C001, FA-C004]
> Those bars describe variability under repeated outcomes and calendar disruptions on the fixed schedules. They aren't uncertainty about how many historical flights I counted, or a promise about my next ticket.

N binding: exact dot +6.2721; display +6.3, endpoints +4.60/+7.94,
claim FA-C001. Caption: NOMINAL 99% MISSINGNESS ENVELOPE · OWN TIMETABLE.

### S08 The replication

> I sealed that first result before opening the 2025 outcomes. The second period gets its own test; it cannot rewrite the first. [FA-C002, FA-C003]
> In 2025, the United advantage is 8.2 points. Its nominal 99% envelope runs from 5.31 to 11.00. Again, the whole interval is above two points. [FA-C002, FA-C004]
> The same decisive label repeats: replicated. [FA-C003]
> That doesn't mean the two periods had identical routes or schedules. And it isn't a repeated reversal of the national ranking: United already led nationally in 2023 and 2024. The important finding is a larger difference within these comparable baskets than the national near-tie suggests. [FA-C042, FA-C043, FA-C046, FA-C047]

N binding: exact B dot +8.2027; display +8.2, endpoints +5.31/+11.00,
claim FA-C002. Reveal B only after A is visibly sealed; one REPLICATED chip.

### S09 The nearby tests

> I also checked nearby choices specified before the outcomes. With one-hour or four-hour windows, the estimated United gaps stay in the same direction in both periods. [FA-C021, FA-C022, FA-C039, FA-C040]
> Matching reciprocal nearest departures within thirty minutes gives gaps of 6.7 and 9.1 points. [FA-C020, FA-C038]
> Those are descriptive sensitivity checks. They cannot replace the registered result, and consistency doesn't make this a result about every flight.
> Now I need to ask a different question: what does arriving on time actually reward? Both airlines are being judged against the timetable they publish themselves. That deserves a closer look.

Small-table caption: REGISTERED DESCRIPTIVE SENSITIVITIES · NO ADDITIONAL VERDICT.

### S10 Whose deadline?

> These next checks are exploratory: post-hoc, not registered. United schedules about 4.5 minutes longer on the shared basket in both periods. But its actual gate-to-gate duration is longer too: about 4.8 minutes in 2023–2024 and 6.2 in 2025, among cells with completed observations for both operators. Longer schedules don't establish deliberate padding. [FA-C054, FA-C062]
> I then give both airlines a shared elapsed-time allowance from their own scheduled departure, using the midpoint of their cell-average scheduled durations and the same fifteen-minute cutoff. This isn't one wall-clock arrival deadline.
> The United gaps shrink to 2.6 and 4.3 points. That shows deadline sensitivity; it doesn't tell me how much padding caused. These exploratory results do not inherit the registered verdict. [FA-C055, FA-C063]

Adjacent labels: actual-duration subset covers 97.73% / 98.55% of weight
(FA-C054/062). Shared-allowance gaps 2.59 / 4.33; descriptive nominal 99% ranges
[1.08,4.09] / [1.97,6.82] (FA-C055/063). No materiality badge on these ranges.

### S11 Leaving late

> I can also look at leaving, before an arrival deadline enters the story. This departure check is exploratory too.
> Southwest has noncancelled departures fifteen minutes or more late about 10.1 points more often in 2023–2024 and 13.1 points more often in 2025. The denominator is all scheduled flights; a cancellation isn't counted as an observed late departure. [FA-C056, FA-C064]
> Including cancellations as failures in a timely-departure score gives United advantages of 9.9 and 13.3 points. [FA-C056, FA-C064]
> Arrival padding cannot mechanically explain departure delays. But scheduled departure choices and operating circumstances still travel with the airline. I haven't isolated a cause, or the effect of choosing United for a ticket.

Q cards: POST-HOC · NOT REGISTERED · COMMON CELL WEIGHTS · ALL SCHEDULED DENOMINATOR.
Diversions remain eligible for this departure endpoint; never add cancellations
to the observed late-departure numerator.

### S12 The boundary of the answer

> Finally, this is a small overlap: about eleven to twelve percent of United-operated schedules and six percent of Southwest's. United Express is excluded. [FA-C006, FA-C025]
> An exploratory concentration check finds about eighty percent of the comparison weight touches Denver. [FA-C058, FA-C066]
> Another exploratory, post-hoc check splits scheduled departures by local time. Before ten in the morning, the gaps are near zero: minus 0.4 and plus 1.4 points. From four in the afternoon onward, they're 11.7 and 12.9. The overall average conceals a very different day. [FA-C060, FA-C068]
> I can say United kept its own timetable more often on these comparable operating services, with a result that replicated. I can't turn that into faster travel, a causal explanation, rebooking outcomes, a recommendation or a best-airline ranking. [FA-C001, FA-C002, FA-C003]
> Next time I see a national tie, I want to ask which flights went into it, and whose deadline they had to meet.

Scope strip: OPERATOR ONLY · SMALL OVERLAP · DENVER-HEAVY · OWN TIMETABLE.
Early/late panel: POST-HOC · NOT REGISTERED; ranges/group membership linked
through FA-C060/068. Do not stamp “morning flights are better.” End evidence
card links METHOD, both amendments, FINDINGS, CLAIMS, CONTEXT and review.

## Short 1

### Short 1: Tied on paper

Vertical visual: annual small table → N A/B stacked range bars. Persistent
scope: United-operated / Southwest-operated domestic nonstop overlap,
2023–24 and 2025; United Express excluded; own timetable; cancellations fail.

> United and Southwest look almost tied in national punctuality tables. I wanted to compare similar flights instead.
> I matched the same directional route, scheduled day and two-hour departure window. This covers United-operated and Southwest-operated domestic nonstop services, excluding United Express. [FA-C001, FA-C005]
> Against each airline's own arrival timetable, United leads by 6.3 points in 2023–2024 and 8.2 in 2025. Both whole nominal 99% uncertainty envelopes clear the two-point line: replicated. Cancellations count as failures. [FA-C001, FA-C002, FA-C003, FA-C004]
> This is a small, Denver-heavy overlap, not a best-airline ranking. A shared-deadline check shrinks the gaps. I found a comparable-service difference, not advice about which ticket to buy.

Adjacent caveat: exploratory shared-allowance +2.6/+4.3, FA-C055/063;
coverage FA-C006/025, Denver FA-C058/066. No inherited shared-allowance verdict.

## Short 2

### Short 2: Whose deadline?

Vertical visual: Q scheduled/actual duration → own/shared two-part split.
Persistent scope: post-hoc, exploratory, not registered; comparable UA/WN
operating domestic nonstop cells, 2023–24 / 2025; Express excluded.

> “On time” depends on whose timetable I use. In an exploratory check of comparable United-operated and Southwest-operated flights, United schedules about 4.5 minutes longer. It also actually takes longer: 4.8 minutes in 2023–2024 and 6.2 in 2025, on cells with completed flights from both operators. United Express is excluded. [FA-C054, FA-C062]
> With a shared elapsed-time allowance from each scheduled departure, United's arrival advantages shrink to 2.6 and 4.3 points. Cancellations still fail. [FA-C055, FA-C063]
> Southwest also leaves fifteen-plus minutes late more often; arrival padding can't mechanically explain departures. [FA-C056, FA-C064]
> These are post-hoc checks, not registered verdicts. They show why the deadline matters without identifying deliberate padding or telling me which airline to book.

Caption: midpoint cell-mean scheduled allowance, same <15-minute boundary;
actual-duration subset 97.73% / 98.55% weight, FA-C054/062.

## Short 3

### Short 3: The gap changes through the day

Vertical visual: early/late small table, periods stacked; Q Denver scope card.
Persistent scope: EXPLORATORY · POST-HOC · NOT REGISTERED; comparable domestic
nonstop UA/WN operating cells; local scheduled departure time; own timetable.

> An average can hide a clock. I made an exploratory, post-hoc time-of-day check on comparable United-operated and Southwest-operated domestic nonstop flights. United Express is excluded; cancellations fail, and each operator is judged against its own timetable. [FA-C001]
> Before ten in the morning, United's gaps are near zero: minus 0.4 points in 2023–2024, plus 1.4 in 2025. From four in the afternoon onward, they're 11.7 and 12.9 points. [FA-C060, FA-C068]
> That's local scheduled departure time, within the same route, day and window comparisons. About eighty percent of the weight touches Denver. [FA-C058, FA-C066]
> This pattern isn't a registered verdict, a causal explanation or a morning-flight recommendation. It tells me to ask what an average has hidden.

## Timing and evidence

Long-form: **1,240 narration words, approximately 8:16 at 150 words per minute**,
across **12 scenes**. Shorts: **Tied on paper**, 100 words / 0:40;
**Whose deadline?**, 108 words / 0:43; **The gap changes through the day**,
110 words / 0:44. Counts exclude claim tags, source notes and visual instructions.
Numerals will be expanded in voice preparation; chart holds and recorded voice
will be timed after script lock. The spoken duration should remain within 8–10
minutes. Shorts are composed and timed separately.

Evidence: [METHOD](METHOD.md), [Amendment 1](analysis/amendment/AMENDMENT-1.md),
[Amendment 2](analysis/amendment2/AMENDMENT-2.md), [FINDINGS](analysis/FINDINGS.md),
[CLAIMS](CLAIMS.json), [CONTEXT](analysis/CONTEXT.md),
[review](analysis/review.md), [required film caveats](analysis/reviews/astra-methods-1.md),
and [numerical verification](analysis/claims_check.json). Procedural definitions,
gate history and the explicitly illustrative route use these method documents;
they are not invented empirical flight claims. Every empirical script value has
a ledger ID. Claim statuses stay proposed; script-check “not verified” warnings
are expected pending approval and are not resolved by changing the ledger.
