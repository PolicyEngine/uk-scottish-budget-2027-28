# Model risk register

| Risk | Effect on the day | Likelihood | Mitigation | Issue |
|---|---|---|---|---|
| Bundle pins policyengine-uk 2.174.1 (policyengine 6.17.2) | The Budget 2026 measures and the carer supplement uprating are in the baseline now; route notes and figures written on 2.151.0 need re-checking on 2.174.1 | Medium | OBR October 2026 forecast overlay for the baseline paths; label figures "unvalidated under this engine" if not on a certified pair | #1 |
| No Scottish property income rate parameter | No parameter route | Medium | Modifier in `measures/scottish_property_rates.py`; parameter upstream later | #2 |
| £100 payment England only, £0 from 2027-28 | A Scottish payment reads £0 | High | Modifier in `measures/energy_payment_scotland.py`; confirm tax year | #3 |
| Council tax freeze needs re-projection | g = 0 overstates the cut | Medium | g = weight growth from the installed release, before data load (`measures/council_tax_freeze.py`); time it in the drill | #4 |
| No Band J, no Scottish home over £2m | Band J reads £0 | Medium | Publish as not computable | #5 |
| Missing Scottish payments | Changes read £0 | Medium | Not computable or needs-pe-uk-first | #6 |
| Income tax base moves 8% between builds | Rate costings move by £8–20m per 1p | Medium | Engine check against HMRC outturn | #7 |
| Local fit unchecked | Scotland-only results | Certain | State it on the Method tab; council view only after the fit is checked | #8 |
| Static versus behavioural basis | Gaps against official costings, largest for the top bands | Certain | Declare the basis once; give each gap a cause | – |
