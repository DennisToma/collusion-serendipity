No remaining concrete correctness bugs found in the two fixes.

- Overlap requires an actual pair of local call intervals with strictly positive intersection; touching endpoints and overlapping game envelopes alone fail.
- Report anchors, header, and S45 markers are validated before any summary, figure, or report write.
- Synthetic tests cover alternating non-overlapping calls and missing markers.

Review only; no edits or execution. Provider execution remains explicitly unattested.