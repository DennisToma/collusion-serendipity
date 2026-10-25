One blocking bug remains in the initialization-failure fix.

**[scripts/s40_replay.py:337](/home/factory/collusion/collusion-serendipity/scripts/s40_replay.py:337): a rejected concurrent invocation can invalidate the active run.** While the first process initializes, a second process can compute `new=True`, fail the nonblocking writer lock, then enter the outer exception handler and write `failure.json` without owning that lock. The first process can continue through all twenty model calls, but its final validation rejects the archive because that marker exists.

Record failures only while holding the writer lock; lock-acquisition failures must not modify the archive. Add a mocked contention test confirming the losing invocation leaves the active archive untouched. The source-mismatch and lost-headroom tests do not cover this path.

The immutable git-object baseline addresses the previously identified baseline race: live configuration uses registered object hashes, and working-tree mismatches stop admission.

Static review only, limited to the three requested files. No edits, tests, or model calls.