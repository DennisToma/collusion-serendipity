No remaining blocking bugs found in the seven requested files.

- Admission exceptions set the terminal event under `admission_lock`, using `threading.Event.set` directly to avoid recursive locking. In-memory two-thread checks passed for preflight, deadline, and headroom failures: the waiting partner reached neither another preflight nor transport.
- Parsing, outcomes, reported offers, and deviation regrets consistently apply the condition-specific offset. Independent reconstruction separately normalizes gross quotes.
- Runtime fingerprinting includes authentication and selected Node/proxy/certificate environment inputs. Its stated limitations match the design’s accepted scope.
- Independent reconstruction checks seeded pair selection and seat order. The valid chronology fixture passes; both mutated receipts are rejected.

Validation: 15 read-only-compatible tests passed, including exhaustive economics/translation checks, condition-specific parsing, overlap checks, and chronology mutations. Syntax checks passed.

The full dry/mock-LIVE and disk-tamper fixtures were **not rerun**: they require temporary writes under `/var/tmp`, which this read-only sandbox prohibits. No edits, temporary files, or live model calls were made.

Legitimate auth/config refresh triggering terminal abort remains an explicitly accepted operational risk, not a new blocker.