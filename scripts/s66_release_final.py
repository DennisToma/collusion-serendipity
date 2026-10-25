"""Offline release with the additive S66 editorial overlay, frozen science intact."""
import json,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import s66_release as frozen
from scripts.s66_publication_final import documents

def check():
    with patch.object(frozen,'documents',new=documents):receipt=frozen.check()
    receipt['post_outcome_editorial_overlay']='Sign-flip label,block-specific ceiling caveat,and correct reproduction entry point only;scientific sources/results unchanged'
    Path('logs/s66_release.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt
if __name__=='__main__':check()
