# Drill 8 run clock (not for merge)

Times, SHAs, versions, build id and pass/fail only. No packet content.

- Run branch: local `drill8-run` (never pushed), cut from `origin/engine-2.177.7-microcosm-9e18f010` at `b08bb96`, merged with `origin/drill-plan` (`dc03e21`).
- Start SHA: `e29990f104bb8d54c451aa49357a3af523e22229`, clean tree.
- Engine: policyengine-uk 2.177.7, policyengine-core 3.34.10, no policyengine.py.
- Build: `uk-frs-calibration-attempt-20261112T133744Z-6f918b81`, SHA-256 `e268e3af7932784ad4471f008097a5acc6c3c5bc15c4c54fbb5a489b2a0ac9ae`; `engine_matches_build: true`; build manifest engine 2.177.7.
- Roles: one agent holds integrator, reconciler and scorer (deviation).

| Step | Start | End | Machine time | People time | SHA |
|---|---|---|---|---|---|
| G0 | 13:02 | 13:03 (posted) | 1 min | 1 min | e29990f |
| G1 | 14:00 | 14:02 | 0 min | 2 min | 2ca5309 |
| G2 | 14:02 | 14:24 | 19 min (7 measures + package, peak 17.8 GB, lock held 14:02:53-14:21:51) | 5 min | 6265874 (results 47ae634a) |
| Documents received | 14:40:13 | 14:40:13 | - | - | sha256 4/4 PASS |
| G3 | 14:40 | 14:52 | 8 min (2 reruns 14:41-14:46, final package 14:46-14:49, peak 17.9 GB) | 4 min | 2c6cded (results fdf0242f); scoring run 1 |
| Correction received | | | | | |
| G5 (due 15:35) | | | | | |
| G4 (due 15:40) | | | | | |
| Stop | | | | | |

Releases: 01-statement 14:00:06, sha256 PASS. 02-documents, 02-costings, 02-households, 02-scoring-sheet 14:40:13, sha256 4/4 PASS.
