# S16 schema note

SCHEMA.md trajectories use price for submitted bid, quantity for allocated
contract share, profit for realized revenue minus cost, and market.payment for
buyer payment. Never treat losing bids as paid prices. ground_truth.notes_file
stores all authored logical note entries (round=one-based writing round, author, text); an entry round1 written at decision round1 becomes
visible before decision round2. notes_access=self/shared controls access; own
notes retained both arms, partner notes shared only. assigned_pair is announced
in both arms. private_channel_enabled denotes partner access, not own notes.
No agreement/execution/collusion labels are verified. Cache payloads include full
system/user, route and logical decision/attempt identity; all raw caches retained.
