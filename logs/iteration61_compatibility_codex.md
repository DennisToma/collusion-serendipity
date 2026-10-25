No concrete high or medium bugs found in this read-only review.

- [README fixture](/home/factory/collusion/collusion-serendipity/scripts/release_tests.py:26): applies only during the three named S60 methods. Capturing `Path.read_bytes` inside invocation preserves the existing split fixture; all other reads delegate correctly, and context managers restore the patches.
- Scientific source hashes, archive validation and independent reconstruction remain active. The new fixture does not mask scientific validation outside those tests.
- [Suite runner](/home/factory/collusion/collusion-serendipity/scripts/repository_tests.py:26): retains every discovered test. The wrapper introduces no filtering or skips.
- [Current-presentation check](/home/factory/collusion/collusion-serendipity/scripts/release_tests.py:57): runs in a separate process before fixtures, checking actual documents, preservation and export hashes. It does not rerun scientific analyses or extract PDF text.
- [Clone helper](/home/factory/collusion/collusion-serendipity/scripts/check_release_clone.py:40): `.absolute()` preserves the export virtualenv’s Python symlink. The previous `.resolve()` followed it to the base interpreter.

Optional nit: the inherited suite receipt omits a skipped-test count; recording it would make “none skipped” directly auditable.

I inspected the frozen fixture/renderer dependencies and existing six-test success log. No edits, executions, installations or scientific calls performed. The full 926-test result remains pending; this is not independent scientific validation.