# S04 synthetic instrument precheck

Eight separately cached gpt-6-luna/codex advisor calls, two each at four fixed
synthetic public states: empty history; one round of 6/6/6; 4/4/4; 4/4/8.
This is not a seller game and estimates no treatment outcome. No prompt/model
selection followed it. `uv run python scripts/s04_precheck.py` reconstructs the
JSON with paid cache entries (the concurrent call provenance list may reorder).
All prompts are the same ones used by the advisor in the live pilot.
Results and raw call labels/timestamps are retained; client routing labels are
not an independent attestation of model identity. Codex sampling parameters are
not controlled. The precheck is small and deliberately covers varied histories;
its variation rate is not representative of encountered game states.
