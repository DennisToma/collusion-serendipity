"""Post-outcome renderer regression: reproducible in a temporary document tree."""
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from scripts.s25_present_safe import present,CAVEAT


class Presentation(unittest.TestCase):
    def test_repeated_render_is_byte_identical_and_leaves_result_unchanged(self):
        root=Path.cwd()
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            target=Path(td);(target/'results').mkdir();(target/'figures').mkdir()
            for f in ['REPORT.md','results/s25_order.json']:shutil.copyfile(root/f,target/f)
            result_before=(target/'results/s25_order.json').read_bytes()
            old=os.getcwd()
            try:
                os.chdir(target);present()
                files=['REPORT.md','results/s25_summary.md','figures/s25_order.png']
                first={f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files}
                present();self.assertEqual(first,{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files})
                self.assertEqual(Path('results/s25_order.json').read_bytes(),result_before)
                self.assertEqual(Path('REPORT.md').read_text().count(CAVEAT),1)
                self.assertEqual(Path('results/s25_summary.md').read_text().count(CAVEAT),1)
            finally:os.chdir(old)

if __name__=='__main__':unittest.main()
