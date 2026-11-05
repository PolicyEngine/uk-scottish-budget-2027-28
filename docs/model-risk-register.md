# Model risk register

| Risk | Effect on the day | Likelihood | Mitigation | Issue |
|---|---|---|---|---|
| Bundle pins policyengine-uk 2.151.0 | Baseline lacks the Pension Tax Allowance and the £100 payment; starter and basic baselines differ from 2.175.4 | High | Recertified bundle before 13 November, or label figures "unvalidated under this engine" | #1 |
| No Scottish property income rate parameter | Measure 4 cannot be costed | Medium | Parameter and formula branch upstream | #2 |
| £100 payment England only, £0 from 2027-28 | A Scottish payment reads £0 | High | Add SCOTLAND; confirm tax year | #3 |
| Council tax freeze needs re-projection | Slow run; g = 0 overstates the cut | Medium | Documented switch; time it in the drill | #4 |
| No Band J, no Scottish home over £2m | Band J reads £0 | Medium | Publish as not computable | #5 |
| Missing Scottish payments | Changes read £0 | Medium | Not computable or needs-pe-uk-first | #6 |
| Income tax base moves 8% between builds | Rate costings move by £8–20m per 1p | Medium | Engine check against HMRC outturn | #7 |
| No local geography | Scotland-only results | Certain | State it on the Method tab | #8 |
| Static versus behavioural basis | Gaps against official costings, largest for the top bands | Certain | Declare the basis once; give each gap a cause | – |
