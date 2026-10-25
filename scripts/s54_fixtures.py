"""Post-run test fixture isolation; never applied to real archive validation."""
from contextlib import contextmanager
import os
from pathlib import Path
import tempfile


@contextmanager
def empty_live_destination():
    """The negative NEW-launch test needs no completed default dataset.

    Its launch script still comes from the unchanged frozen source. The real
    archive remains at its real path; only this one synthetic test changes cwd.
    """
    root=Path.cwd().resolve()
    with tempfile.TemporaryDirectory(prefix='s54_empty_launch_',dir='/var/tmp') as td:
        sandbox=Path(td)
        (sandbox/'scripts').symlink_to(root/'scripts',target_is_directory=True)
        os.chdir(sandbox)
        try:yield
        finally:os.chdir(root)
