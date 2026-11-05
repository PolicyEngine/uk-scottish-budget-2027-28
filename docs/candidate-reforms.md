# Candidate reforms

Ranked by likelihood. Routes are for policyengine-uk 2.151.0 (the certified bundle) unless stated. Every entry in `reforms.py` is a placeholder until the Budget is published.

| # | Measure | Likelihood | Plausible range | Route | Data or model need |
|---|---|---|---|---|---|
| 1 | Starter and basic thresholds raised | High | 0% to 7.4%; central case 3.5% on the full thresholds: £17,116 and £30,559 (encoded 4,546 and 17,989) | dashboard-param | Baselines differ by release (#1) |
| 2 | Higher, advanced and top thresholds frozen | High (committed to 2028-29) | £43,662 / £75,000 / £125,140 | ledger (already in the baseline) | None |
| 2b | New band before the 42% rate | Low | – | dashboard-structural | Bracket insert |
| 3 | Rate changes | Low | ±1p on intermediate or higher | dashboard-param | Income tax base (#7) |
| 4 | Scottish property income rates | Medium | 0 to +2p on each band, or deferred | needs-pe-uk-first | New parameter and formula; thin records (#2) |
| 5 | Scottish Child Payment | Medium | £29.20 at 3.5% CPI is in the baseline; an above-inflation rise is possible | dashboard-param | None |
| 6 | Scottish Child Payment premium for under-ones | High (announced) | £40 a week | dashboard-param (contrib switch) | Start date (2027-04-01 in the parameter) |
| 7 | £100 payment for Bands A to D | High | About 1.9m homes; possibly Band E or CTR recipients | needs-pe-uk-first | England only, 2.175.4 only, £0 from 2027-28 (#3) |
| 8 | Council tax freeze or cap | Medium | Freeze, a cap of 3–5%, or local discretion | dashboard-structural | Re-projection; gross base looks low (#4) |
| 9 | Council tax Bands I and J | Medium (from April 2028) | Ratios to be set | not-computable | No Band J, no home over £2m (#5) |
| 10 | Uprating of other Scottish benefits | High | 3.5% CPI; carer supplement possibly higher | dashboard-param where modelled | Supplement not uprated on 2.151.0 (#1) |
| 10b | ADP changes | Low | – | not-computable | ADP carried as PIP (#6) |
| 11 | Young parent top-up | Low | £0 to about £100 a month a family | needs-pe-uk-first | No variable (#6) |
| 12 | Benefit cap mitigation | Low | – | needs-pe-uk-first | No DHP variable (#6) |
| 13 | LBTT, including ADS | Low (review ongoing) | ADS 8% to 10%, or nil band raised | dashboard-param | Purchases are a seeded draw |
| 14 | Air Departure Tax | Medium | Match UK APD | ledger | Not a household measure |
| 15 | Non-domestic rates | Medium | Poundage frozen or CPI-linked | ledger | Business tax |

Spending measures (bus fares, breakfast clubs, childcare, housing, public sector pay) go in the ledger only.

## Official figures to reconcile against

- Scottish Fiscal Commission, Scotland's Economic and Fiscal Forecasts (Budget day): policy costings, income tax by band, social security by payment. January 2026 edition: Scottish income tax £22,828m in 2027-28; income tax policy costings −£50m (2026-27), +£72m (2027-28); under-one premium £3m (2027-28) and £7m a year from 2028-29.
- Scottish Government tax ready reckoners 2026-27 (include behaviour): +1p starter £110m, basic £258m, intermediate £154m, higher £101m, advanced £25m, top £4m; higher threshold +£1,000 −£141m.
- Scottish Government distributional analysis of the Budget.
- HMRC Scottish income tax outturn 2024-25.
