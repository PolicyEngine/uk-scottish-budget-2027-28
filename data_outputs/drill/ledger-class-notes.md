# Lines where ledger cause class = national gap class (lesson 7)
- S2, S10 (trap rows): cause baseline_mismatch, gap baseline_mismatch: already in the baseline, so the only "gap" is that nothing is costed.
- S6, S7, S15 (ledger): cause coverage, gap coverage: outside the model, so the official figure is recorded and no model figure exists.
- S9, S13 (not-computable): cause coverage (rule: a line that cannot be computed takes coverage), gap coverage.
- S14: cause timing_fiscal_calendar (paid in 2026-27, before the scored years), gap timing_fiscal_calendar for 2027-28/2028-29 (nothing to compare). Model 2026-27 estimate -185m vs costing -189m (2%).
All coded lines have different classes: S1 parameter/basis, S3 parameter/basis, S4 formula/basis, S5 parameter/within 10%, S8 data_calibration/basis, S11 parameter/data_calibration, S12 formula/data_calibration.
