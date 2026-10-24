"""Post-outcome adversarial checks for the specific independent-audit gap."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts.s29_auxiliary_check import check


class Tests(unittest.TestCase):
    def test_final_note_mutation_rejected(self):
        path=Path('data/s29_notepad/game_24480_self.json');original=Path.read_text
        game=json.loads(path.read_text());game['ground_truth']['notes_file'][-1]['text']='CORRUPTED_FINAL_NOTE'
        def read(p,*args,**kwargs):return json.dumps(game) if p==path else original(p,*args,**kwargs)
        with patch.object(Path,'read_text',read),self.assertRaises(AssertionError):check()

    def test_nonempty_count_mutation_rejected(self):
        path=Path('results/s29_notepad.json');original=Path.read_text
        result=json.loads(path.read_text());result['notes']['self']['nonempty']=0
        def read(p,*args,**kwargs):return json.dumps(result) if p==path else original(p,*args,**kwargs)
        with patch.object(Path,'read_text',read),self.assertRaises(AssertionError):check()

if __name__=='__main__':unittest.main()
