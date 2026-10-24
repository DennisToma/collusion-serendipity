"""Guard terminal failure state before calling the archived frozen runner."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s07_publish import reject_failed_experiment
from sim.legality import main as frozen_run


def main():
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--out',default='data/s07_legality')
    args,_=parser.parse_known_args()
    reject_failed_experiment(args.out)
    frozen_run()

if __name__=='__main__':main()
