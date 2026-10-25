# S33 dataset

Ten two-person synthetic workplace games: five paired blocks24640..24644,
baseline versus reporting/amnesty, ten rounds. Primary rounds3..10; five fresh
exploratory blocks are the statistical unit. See [design](../../DESIGN_S33.md)
for the frozen screening rule and operational contract. Zero tuning or pooling.

`trajectories.jsonl` is the observable export: statuses, review actions, final
charges, scores and organizational loss. Private report flags are removed.
Reports can still be inferred partly from charges or voluntary note content.

`ground_truth.jsonl` contains private reports, shared notepad contents, private
reasoning and call provenance. `game_*.json` are internal full records and also
contain report flags; they are not observable-only detector inputs. Raw request
and response audits in `raw/` include private scenario information and support
exact offline reconstruction. No sibling detector is applied in this pilot.

Condition assignment is observed; agreement, coordinated-action, realized
collusion and hard-negative labels remain null. Adverse approvals alone are
not verified collusion. Simulated bonus and organizational costs are toy rules.
Both arms use shared notes and the same report schema. Treatment activates
contingent additional sanctions and immunity; these effects are not separated.

Live generation is one-shot and must not be relaunched to replace an outcome.
Offline reproduction after completion: `uv run python scripts/s33_release.py`.
