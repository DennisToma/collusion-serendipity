S04 is viable as an exploratory **common-sampling** pilot. It cannot establish hub collusion. Read-only review; no live LLM calls. I also checked the S04 adapter and analysis files that appeared during review.

**Must settle before outcomes:**

- **Define failure handling and runtime limits.** The baseline is **600 model calls**, before retries. Cached invalid responses make a failed game fail again on resume. Prespecify incomplete pilot → no HIT/DUD; prohibit selective seed replacement or shortening after inspecting outputs. ([Execution plan](/home/factory/collusion/collusion-serendipity/DESIGN_S04.md:35))
- **Qualify “exact” inference.** Sign flips need justification from randomized arm-to-execution-slot assignment under a sharp no-effect null, or an explicit symmetry assumption. Matching seed numbers does not match LLM randomness—the seed selects the pair. Freeze scheduling/resume rules and explain exchangeability; asynchronous scheduling and backend drift can undermine it. The stated minimum p=.03125 is correct. ([Analysis](/home/factory/collusion/collusion-serendipity/DESIGN_S04.md:44))
- **Make treatment exposure an interpretation gate.** Full-vector disagreement can occur solely in unused components. Check whether switching slots changes the **second assigned member’s recommendation**, across all rounds. The new analyzer measures this, but its HIT/DUD logic does not use it. Zero effective exposure should yield “uninformative manipulation,” including when random outcome differences satisfy HIT thresholds. ([Diagnostic](/home/factory/collusion/collusion-serendipity/scripts/s04_analyze.py:76))

**Can remain explicit limitations:**

- **Lower pair output plus higher pair profit is not evidence of collusion or market harm.** It can reflect correction of excessive production or smaller losses; outsider expansion can offset restraint. Report absolute quantities/profits against Nash, total output, and price alongside the treatment contrast.
- **The estimand is narrow.** Same-model calls may share biases or server randomness; scalar advice hides common identity, and no persistent advisor exists. No-advice and cross-family controls are unnecessary for this narrow contrast, but needed for broader shared-vendor claims.
- **Five blocks, one model, twelve rounds:** weak precision and generalizability; bootstrap/t intervals remain descriptive. Report seed effects and keep secondary metrics exploratory.

The payoff arithmetic and simultaneous-action structure look sound. The original Cournot runner exposes only own-profit history; the new S04 adapter supplies the promised full public profit history.