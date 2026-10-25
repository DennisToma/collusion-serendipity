"""Regression for corrected S65 Markdown table layout; no live calls."""
import contextlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from sim.bonus_pooling import main
from scripts.s65_analyze import analyze
from scripts.s65_publication_final import render

class Tests(unittest.TestCase):
    def test_pilot_table_is_contiguous_and_corrected_render_is_idempotent(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);data=root/'data/s65_bonus_pooling'
            with patch.object(sys,'argv',['sim.bonus_pooling','--dry','--out',str(data)]),contextlib.redirect_stdout(io.StringIO()):main()
            result=analyze(data,True);result['dry']=False
            (root/'results').mkdir();(root/'figures').mkdir();(root/'results/s65_bonus_pooling.json').write_text(json.dumps(result))
            with contextlib.chdir(root):
                docs=render();self.assertEqual(docs,render())
                report=docs['REPORT.md'];table=report.split('| Pilot | Result',1)[1].split('\n\n',1)[0]
                self.assertEqual(sum(line.startswith('| S') for line in table.splitlines()),48)
                self.assertEqual(report.count('| S65 · B,'),1)
                self.assertIn('scripts/s65_release_final.py',docs['README.md'])
                self.assertIn('scripts/s65_release_final.py',Path('results/s65_summary.md').read_text())

if __name__=='__main__':unittest.main()
