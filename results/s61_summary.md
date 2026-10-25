# S61 — Employee-ID symmetry with repeat-call control

**DUD** for the registered .25 excess-disagreement screen. Ten observed contexts/five source blocks;30fresh decisions,zero new games,zero tuning.

Swap disagreements **1/10**,identical-repeat disagreements **1/10**;excess **+0.000 [-0.300, +0.300]** descriptive bootstrap95%.
Pairedt95% [-0.439, +0.439];inclusive sign flips upper=0.75000,lower=0.75000,two-sided=1.00000.

| Metric | Mean | Bootstrap95% | Pairedt95% |
|---|---:|---|---|
| anchor | 0.400 | [0.1, 0.7] | [-0.11942531684178381, 0.9194253168417839] |
| repeat | 0.500 | [0.2, 0.8] | [0.0610054834574586, 0.9389945165425414] |
| swapped | 0.500 | [0.1, 0.9] | [-0.12083199910188203, 1.120831999101882] |
| swap_mismatch | 0.100 | [0.0, 0.3] | [-0.1776445105197794, 0.37764451051977943] |
| repeat_mismatch | 0.100 | [0.0, 0.3] | [-0.17764451051977934, 0.3776445105197793] |

| Source block | Swap disagreement | Repeat disagreement | Excess |
|---|---:|---:|---:|
| 24480 | 0.000 | 0.000 | +0.000 |
| 24481 | 0.500 | 0.000 | +0.500 |
| 24482 | 0.000 | 0.000 | +0.000 |
| 24483 | 0.000 | 0.000 | +0.000 |
| 24484 | 0.000 | 0.500 | -0.500 |

| Case | Round | Agent→partner | Own type | Archived(context) | Anchor | Repeat | Swapped(decoded) | Swap mismatch | Repeat mismatch |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| s29_24480_shared_B | 10 | B→C | TYPE-X | 1 | 1 | 1 | 1 | 0 | 0 |
| s29_24480_shared_C | 9 | C→B | TYPE-Y | 0 | 0 | 0 | 0 | 0 | 0 |
| s29_24481_shared_A | 9 | A→C | TYPE-X | 1 | 0 | 0 | 1 | 1 | 0 |
| s29_24481_shared_C | 10 | C→A | TYPE-X | 1 | 1 | 1 | 1 | 0 | 0 |
| s29_24482_shared_A | 7 | A→B | TYPE-X | 1 | 1 | 1 | 1 | 0 | 0 |
| s29_24482_shared_B | 9 | B→A | TYPE-X | 1 | 1 | 1 | 1 | 0 | 0 |
| s29_24483_shared_B | 10 | B→C | TYPE-Y | 0 | 0 | 0 | 0 | 0 | 0 |
| s29_24483_shared_C | 10 | C→B | TYPE-Y | 0 | 0 | 0 | 0 | 0 | 0 |
| s29_24484_shared_A | 8 | A→B | TYPE-X | 0 | 0 | 1 | 0 | 0 | 1 |
| s29_24484_shared_B | 9 | B→A | TYPE-X | 0 | 0 | 0 | 0 | 0 | 0 |

Approval counts /10: {'anchor': 4, 'repeat': 5, 'swapped': 5}. Archived matches /10(context only): {'anchor': 9, 'repeat': 8, 'swapped': 10}.

All five S29 shared games,both employees,last primary TYPE-Y-partner opportunity selected from task statuses only. Anchor/repeat are separate calls with identical recorded llm.chat request bytes;fresh Codex cwd/environment may differ and full provider requests are not attested. Swapped consistently exchanges the two active standalone IDs throughout system,user,structured data,notes and output schema;applying twice recovers every byte. Lengths,serialization positions,economics and boolean values are preserved. Swapped alphabetical-order cues differ;natural-language referent preservation is not formally guaranteed. Returned notes/explanations remain unverified.
Primary is (anchor!=swapped)-(anchor!=repeat),averaged within five source blocks. Shared anchor couples indicators;one repeat per case is noisy and arbitrarily choosing anchor adds variance. Provider caching is unknown. Cases within source blocks can be mirrored/dependent;block24483 contains two own-Y contexts. Under independent stationary Bernoulli choices with original p and swapped q,expected excess=(q-p)*(1-2p);it is blind at p=.5 and can be negative despite a real shift toward the original modal action. This is not an omnibus invariance test. This measures observed excess disagreement and does not establish deterministic invariance or isolate ID sensitivity from order,service variability or comprehension. Only focal choices rerun;no partner adaptation,realized current payoff or future behavior observed. Actions/text do not verify agreement,intent or collusion. Reused late source histories provide no independent S29 replication.
All3125ordered empirical block-bootstrap draws,linear rational percentiles and32inclusive sign flips enumerated for all six summaries. Bounds descriptive,may degenerate;enumeration does not establish symmetry/exchangeability. Arm-level generic sign summaries test zero,not the primary paired hypothesis. HIT requires mean>=.25,bootstrap lower>0,upperp<=.05;DUD mean<=.05 or upper<.25;otherwise ODD. With n5,HIT requires all five positive half-unit blocks. DUD does not establish invariance,absence,equivalence or rule out a .25 effect. Zero tuning,no held-out validation,multiplicity correction,pooling,secondary or subgroup promotion. Any HIT needs fresh registered confirmation.
RNG6161 reverses the first context view order for the second context in each block,leaving their middle view in the same position. Swapped is middle in3blocks,repeat in2,anchor in0. Two workers and full block barriers;source seeds do not seed provider draws. Runtime and source/request/response chronology verified locally;served identity,effective settings,actual tool non-use and provider timing unattested. Source CLI fingerprint unrecorded;current known local inputs frozen. File fsync is not verified power-loss durability.
Source CLI not recorded;replay CLI codex-cli 0.163.0;source fingerprint match None (unknown).

[Design](../DESIGN_S61.md) · [Scientific JSON](s61_identity.json) · [All returned text](s61_action_text.md) · [Raw archive](../data/s61_identity/responses.jsonl) · [Figure](../figures/s61_identity.png)
