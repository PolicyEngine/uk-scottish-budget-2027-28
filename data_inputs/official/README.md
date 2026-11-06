# Official figures

Official costings go here once published, one CSV per source, with the source URL and the date read in a companion `.md` note. Expected on 3 December 2026: the Scottish Fiscal Commission's policy costings and forecasts, and the Scottish Government's tax ready reckoners and distributional analysis.

- `costings_template.csv`: the columns `scottish-budget reconcile --official` reads (`measure_id, year, official_value_bn, official_source, basis, reason, cause`). `year` is the first year of the fiscal year (2027 for 2027-28); values are £bn, negative a cost. Copy it to `sfc_costings_2027_28.csv` on the day.
- `hmrc_scottish_income_tax_outturn_2024_25.csv`: the HMRC 2024-25 outturn for Scottish non-savings, non-dividend income tax (£18,635m; 3,036,400 taxpayers) and its band shares, the benchmark for the income tax base check in issue #7. Data only; the page does not quote it.
- `../expected_effects.csv`: our expected sign and the latest official figure for each likely measure, before the day. It uses the same `measure_id` and `year` keys, so `reconcile` can read it too.
