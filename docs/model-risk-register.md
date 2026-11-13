# Model risk register

| Risk | Effect on the day | Likelihood | Mitigation | Issue |
|---|---|---|---|---|
| The pair (build `…-6f918b81`, policyengine-uk 2.177.7) is in no policyengine.py release; it superseded the earlier 2.177.7 build on 13 November 2026 | Figures move when the build changes; route notes and figures written on 2.151.0 or 2.174.1 need re-checking on 2.177.7 | Medium | Engine and SHA-256 guards in `engine.py`; one constant to switch (`data_build.DATA_BUILD`); every figure labelled "build uk-frs-calibration-attempt-20261112T133744Z-6f918b81, policyengine-uk 2.177.7, not in a policyengine.py release" | #1 |
| No Scottish property income rate parameter | No parameter route | Medium | Modifier in `measures/scottish_property_rates.py`; parameter upstream later | #2 |
| £100 payment England only, £0 from 2027-28 | A Scottish payment reads £0 | High | Modifier in `measures/energy_payment_scotland.py`; confirm tax year | #3 |
| Council tax freeze needs re-projection | g = 0 overstates the cut | Medium | g = weight growth from the installed release, before data load (`measures/council_tax_freeze.py`); time it in the drill | #4 |
| No Band J, no Scottish home over £2m | Band J reads £0 | Medium | Publish as not computable | #5 |
| Missing Scottish payments | Changes read £0 | Medium | Not computable or needs-pe-uk-first | #6 |
| Income tax base moves 8% between builds | Rate costings move by £8–20m per 1p | Medium | Engine check against HMRC outturn | #7 |
| Local fit unchecked | Scotland-only results | Certain | State it on the Method tab; council view only after the fit is checked | #8 |
| Static versus behavioural basis | Gaps against official costings, largest for the top bands; most gaps over 10% are basis (7 of 11 line-years on the last check), not take-up | Certain | Declare the basis once; give each gap a cause (`docs/RUNBOOK.md`, Gap reasons at G3) | – |
| Hand-built households claim by default | `would_claim_uc` and `would_claim_scp` default to true, so an example household the data say does not claim would get UC and SCP | Certain for hand-built households | Mark the preset `"claims": False` or call `calculate(..., claims=False)`; population runs use stored take-up draws | – |
