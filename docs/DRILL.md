# Drills

Each drill is a timed rehearsal of the day on a mock statement. Its plan (clock, gates, roles, rubric and packet hashes) is `DRILL.md` at the root of its drill branch, and only there; the drill issue links to it rather than restating it. The drill on Friday 13 November 2026 is PR #12.

Rules for every drill:

- The drill branch is cut from `template-dashboard` (stacked on the template PR, so it has the pipeline, the page and CI) and its PR is a draft labelled `not for merge`. It is never merged.
- The packet is written and held outside this repository by the drill owner, who is not the integrator. Only its SHA-256 hashes are committed, in the drill branch's `DRILL.md`.
- The drill builds the page with `NEXT_PUBLIC_MOCK=1`, so the banner starts with MOCK on every view, and checks the served page with `scripts/smoke-built-site.sh <url> MOCK`.
- Nothing from a drill is deployed, posted or shared outside the drill PR and the drill issue.
