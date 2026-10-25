S43’s implementation supports the stated narrow question: how adding this table changes a fresh focal offer at fixed histories. I found one minor verification bug, with no payoff or primary-analysis arithmetic error. Review was read-only; no model calls.

Selection uses all ten specified source games, round10, first incumbent in the initial ordered roster. Current source hashes and case manifest match; roster, round9 offers, economic metadata, private-note ownership and archived-response bindings are checked. Selection remains post hoc. Both fresh arms retain identical histories, system text and notes; control reproduces the source prompt, and treatment adds only the table supplement. The archived current answer is withheld.

The outcome is correctly the **focal integer offer**, not realized worker payment. Rivals are never rerun.

The exact counterfactual table below gives **(own labor share, own profit)**. These are the three observed round9 rival profiles:

| Own offer | Rivals [10] or [10,9] | Rivals [10,10] |
|---|---|---|
| Every integer 0–9 | (0, 0) | (0, 0) |
| 10 | (1/2, 5) | (1/3, 10/3) |
| 11 | (1, 9) | (1, 9) |
| 12 | (1, 8) | (1, 8) |
| 13 | (1, 7) | (1, 7) |
| 14 | (1, 6) | (1, 6) |
| 15 | (1, 5) | (1, 5) |
| 16 | (1, 4) | (1, 4) |
| 17 | (1, 3) | (1, 3) |
| 18 | (1, 2) | (1, 2) |
| 19 | (1, 1) | (1, 1) |
| 20 | (1, 0) | (1, 0) |

The prompt contains no action recommendation.

Schedule and arithmetic match the design: seed4343, two concurrent case workers, sequential views, seed-block barriers; two cases averaged within each of five equally weighted blocks; 3,125 bootstrap draws, rational linear percentiles, 32 inclusive sign flips, and HIT-first classification. Four read-only tests passed, including all 9,702 profile/action payoff checks.

Failure/cache/source controls appear sound by inspection: explicit routing, one attempt, strict parsing, raw-before-acceptance persistence, drift checks, terminal-failure rejection, writer lock and external one-shot receipt. **Registration remains pending:** S43 files are untracked, and no launch receipt or live archive exists. Live chronology and release reproduction therefore remain unverified.

Concrete remaining bug: [s43_independent.py](/home/factory/collusion/collusion-serendipity/scripts/s43_independent.py:76) ignores `mean_exact` and `ci95_exact`. An entirely in-memory reproduction passed with contrast numeric mean/bounds zero but exact fields `999` and `[998,1000]`. Full release recomputation would catch this; standalone independent verification does not.

Acknowledged limits: the intervention bundles arithmetic, scenario salience, length and ordering; it cannot identify mechanism, coordination, worker-payment effects or trajectory effects. Five selected blocks provide weak generalization; sign-flip calibration requires assumptions. Provider identity, effective settings, tool non-use and crash accounting remain unattested. Twenty-minute headroom is an availability convention. Earlier pilots were not reviewed.