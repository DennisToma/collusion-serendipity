One finding: **P2 — the publication guard can overwrite a concurrent edit.** In [s66_publication_final.py:39](/home/factory/collusion/collusion-serendipity/scripts/s66_publication_final.py:39), validation and writing occur in separate loops. An edit after a file’s validation but before its write is silently discarded. The editorial probes only insert mutations before validation, so they do not establish the stated “never discard an intervening edit” guarantee. Protect the validation/write window with locking respected by writers, or narrow that guarantee.

The remaining focused checks pass:

- **Terminology:** “upper sign-flip p” accurately describes enumeration of signed block differences. Independent enumeration gives **0.93750**.
- **Preservation:** all **19 frozen source hashes**, the scientific result, and every artifact hash recorded in the release receipt match current bytes. The overlay changes wording and entry-point references without changing numerical values.
- **Isolation:** the normal publication path renders in scratch space and rejects pre-existing unexpected artifact changes before canonical writes.
- **Entry points:** the published offline command and clean-clone helper both use `scripts/s66_release_final.py`; its patch correctly routes frozen release rendering through the additive overlay.
- **Clone evidence:** no S66 clean-clone receipt exists yet, and the additive helpers remain uncommitted. Successful origin reproduction is therefore pending.

Read-only review only; no edits, release execution, or simulated-agent calls.