I found two medium-severity protocol/validation issues and one low-severity parser defect. I found no payoff or decision-rule arithmetic bug. No files were edited and no live models were run.

1. **Medium — inboxes include the sender’s own messages.**  
   [legality.py:93](/home/factory/collusion/collusion-serendipity/sim/legality.py:93) sends the entire pair transcript to both members, ignoring each message’s `recipient`. I reproduced both firms receiving their own previous messages. This conflicts with the inherited prompt’s “Only that firm reads your messages” and supplies persistent self-message memory in otherwise fresh contexts.

   **Remedy:** filter messages by recipient, or explicitly register a shared pair transcript and revise the prompt. [test_s07.py:43](/home/factory/collusion/collusion-serendipity/scripts/test_s07.py:43) currently accepts this behavior; test the intended sender/recipient boundary explicitly. I found no same-round, outsider, or reasoning-field leakage through the harness itself.

2. **Medium — the analyzer can emit results without completing mandatory publication checks.**  
   [s07_analyze.py:130](/home/factory/collusion/collusion-serendipity/scripts/s07_analyze.py:130) verifies cached replay, but the CLI writes its result without checking exported trajectories/metadata or independently verifying the calculation. I reproduced an unchanged successful analysis after corrupting `trajectories.jsonl`. The separate verifier rejects that corruption and also checks the call-start deadline.

   This is a publication-gating gap, rather than an incorrect primary estimate: the documented workflow is protected **if the separate verifier runs successfully**.

   **Remedy:** provide one mandatory publication entry point that runs analysis and independent verification before releasing validated results. Bind verification to the exact result and input hashes.

3. **Low — “strict JSON” accepts nonstandard and ambiguous inputs.**  
   [legality.py:28](/home/factory/collusion/collusion-serendipity/sim/legality.py:28) uses default `json.loads`. I reproduced acceptance of an unused `NaN` field and duplicate quantity keys, including `quantity:99` followed by `quantity:6`. These responses bypass the promised malformed-response retry behavior.

   **Remedy:** reject nonstandard constants and duplicate keys; explicitly define allowed fields. Add these cases to [test_s07.py:13](/home/factory/collusion/collusion-serendipity/scripts/test_s07.py:13).

The following are material limitations or unresolved guarantees, rather than demonstrated outcome bugs:

- **Backend isolation is unverified, with potentially high impact.** The inherited [llm.py:82](/home/factory/collusion/collusion-serendipity/llm.py:82) launches Codex with a read-only sandbox and a textual instruction against commands. Read-only access does not establish isolation from experiment files or other arms. Tool activity is not retained in the cached final answer. Disable tools or enforce filesystem isolation, and retain execution events before claiming complete information-boundary verification. I observed no actual backend leak.
- **Five blocks support only a fragile exploratory screen.** The sign-flip calculation is exact enumeration conditional on the stated exchangeability/symmetry assumptions. It does not establish those assumptions. Bootstrap and t intervals cannot repair dependence or portfolio multiplicity.
- **The estimand is assigned-pair output under the complete cue package.** All three firms receive treatment. Increased pair output need not imply increased total market output because outsider output can fall. Neither output nor message content establishes agreement, compliance, or collusion. The absence of a no-channel arm prevents a channel-mediated causal claim.
- **Hashes establish consistency, not historical authenticity.** They cannot independently prove preregistration timing, absence of earlier tuning, or backend identity. The files changed during this review; freeze an identifiable snapshot before calls.

The registered arithmetic checks out: rounds 4–12 contribute 18 pair actions per game; the overall contrast is the sum of five integer difference numerators divided by 90. Payoffs and the stated integer Nash equilibria are correct. Bootstrap resampling uses game-block contrasts, the t interval uses four degrees of freedom, and sign-flip enumeration retains ties.

The classification matches the design, including the asymmetric reverse screen. With five blocks, HIT’s p-value gate requires five strictly positive contrasts; its positive bootstrap-bound condition is consequently redundant. DUD remains a queue label, not evidence of equivalence.

Four tests passed without writes. A synthetic 360-call pipeline also passed analysis and independent verification entirely in memory; the updated replay rejected an unused cache key. The review reflects the reread version containing that protection.