"""Publication-gate regressions on complete mocked live archives, no provider calls."""
from datetime import datetime,timezone
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.s21_audit import run,strict,request,stable
from scripts.s21_analyze import analyze
from scripts.s21_release import release


class Publication(unittest.TestCase):
    def test_result_mutation_and_live_archive_replay(self):
        import scripts.s21_audit as audit
        # Mock only registration attestation for synthetic live data. All sources,
        # thirty exact requests/hashes/routes/chronology and parsing remain real.
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            receipt=Path(td)/'launch.json';result_path=Path(td)/'result.json';path=Path(td)/'archive'
            def respond(**req):
                fields=json.loads(req['prompt'])['employee_response']
                author=json.loads(req['prompt'])['target_author']
                value=fields['reviews'][author] if 'reviews' in fields else None
                return dict(text=stable(dict(approved=value,explanation='synthetic')),backend='codex',model='gpt-6.1-sol')
            reg=dict(commit='synthetic',remote='synthetic',observed_utc=datetime.now(timezone.utc).isoformat())
            with patch.object(audit,'registration',return_value=reg),patch.object(audit,'LIVE_RECEIPT',receipt),patch.object(audit,'chat',side_effect=respond):
                # Mock git history checks, retaining every other real validation.
                with patch.object(audit.subprocess,'run'),patch.object(audit.subprocess,'check_output') as git:
                    def original(cmd,**kwargs):
                        source=cmd[2].split(':',1)[1]
                        return Path(source).read_bytes()
                    git.side_effect=original
                    run(path);result=analyze(path);result_path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
                    verified=release(path,result_path);self.assertTrue(verified['passed']);self.assertTrue(verified['archive_unchanged'])
                    changed=copy.deepcopy(result);changed['verdict']='HIT';result_path.write_text(json.dumps(changed,indent=2)+'\n')
                    with self.assertRaises(AssertionError):release(path,result_path)

if __name__=='__main__':unittest.main()
