No concrete bug found in the patch’s stated scope. Terminal failure is now atomic with logical admission.

- [AdmissionAbort.set](/home/factory/collusion/collusion-serendipity/sim/notepad.py:50) sets the event while holding the same lock that [TenderCache.call](/home/factory/collusion/collusion-serendipity/sim/notepad.py:97) holds across abort checks, preflight, and logical admission. Once that transition occurs, subsequent uncached requests cannot be admitted.
- Transport runs outside that lock. A request admitted earlier can begin or finish transport after abort, consistent with DESIGN_S29.md. Transport cancellation is unnecessary for this guarantee.
- [The serialization test](/home/factory/collusion/collusion-serendipity/scripts/test_s29.py:114) exercises the intended ordering: abort cannot finish during preflight; the admitted request completes after abort; a subsequent uncached request is rejected without another transport call.
- Failure remains closed to publication: generation propagates failures without recording successful completion, and [analysis](/home/factory/collusion/collusion-serendipity/scripts/s29_analyze.py:111) requires a complete execution journal and rejects both game failure markers and transport-failure logs.

The atomic boundary is the locked abort transition; an exception occurring earlier does not itself establish that boundary. This matches the documented transition semantics.

Static review only; no edits, tests, or live model calls.