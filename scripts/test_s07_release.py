"""Publication regressions for final-review findings; no live models."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.s07_publish import validate_registration,reject_failed_experiment,publish
from scripts.s07_safe_run import main as safe_run

class PublicationGuard(unittest.TestCase):
    def test_terminal_failure_prevents_resume_and_publish(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
            (Path(tmp)/'failure_game_24080_neutral.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'Terminal failure'):reject_failed_experiment(tmp)
            with patch('sys.argv',['safe_run','--out',tmp]),patch('scripts.s07_safe_run.frozen_run') as call:
                with self.assertRaisesRegex(ValueError,'Terminal failure'):safe_run()
                call.assert_not_called()
            with patch('scripts.s07_publish.analyze') as call:
                with self.assertRaisesRegex(ValueError,'Terminal failure'):publish(tmp)
                call.assert_not_called()
    def test_registration_environment_and_dry_mutations_rejected(self):
        cfg=json.loads(Path('data/s07_legality/config.json').read_text())
        mutations=[('registration_commit','0'*40),('registration_commit','HEAD'),
                   ('temperature_requested',0),('temperature_requested',True),('workers',True),
                   ('environment',dict(python='fake',numpy='fake',scipy='fake')),('dry',True)]
        for field,value in mutations:
            with self.subTest(field=field),tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
                changed=copy.deepcopy(cfg);changed[field]=value
                (Path(tmp)/'config.json').write_text(json.dumps(changed))
                with self.assertRaises(ValueError):validate_registration(tmp)
    def test_live_publication_verification_cannot_be_bypassed(self):
        # There is no allow-dry shortcut in this entry point. Failure of the
        # independent verifier blocks the atomic output even for valid live input.
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
            output=Path(tmp)/'never_published.json'
            with patch('scripts.s07_publish.analyze',return_value={'dry':False}),patch(
                'scripts.s07_publish.verify',side_effect=ValueError('corrupt export')):
                with self.assertRaisesRegex(ValueError,'corrupt export'):
                    publish(out=output,audit=Path(tmp)/'audit.json')
            self.assertFalse(output.exists())

if __name__=='__main__':unittest.main()
