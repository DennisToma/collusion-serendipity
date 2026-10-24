"""Protocol tests protect fork intervention, delivery and fail-closed publication."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.replay import SEEDS, CONDITIONS, ReplayCache, load_prefix, prompts, run_game
from scripts.s09_analyze import classify, exact_signflip

class Protocol(unittest.TestCase):
    def test_codex_invocation_is_fresh_readonly_and_direct(self):
        import llm
        seen=[]
        def fake_run(cmd,**kw):
            directory=Path(cmd[cmd.index('-C')+1])
            self.assertNotEqual(directory.resolve(),Path.cwd().resolve())
            self.assertEqual(list(directory.iterdir()),[])
            self.assertIn('--skip-git-repo-check',cmd)
            self.assertEqual(cmd[cmd.index('-s')+1],'read-only')
            self.assertIn('Do not run commands or edit files.',cmd[-1])
            self.assertTrue(all(not (p/'AGENTS.md').exists() for p in [directory,*directory.parents]))
            Path(cmd[cmd.index('-o')+1]).write_text('canary')
            seen.append(str(directory))
        with patch('llm.subprocess.run',side_effect=fake_run):
            self.assertEqual(llm._codex([dict(role='user',content='test')],'gpt-6-luna',1,512),('canary','gpt-6-luna'))
        self.assertEqual(len(seen),1)
        self.assertFalse(Path(seen[0]).exists())

    def test_cache_refuses_torn_append_before_recovery(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
            p=Path(tmp)/'responses.jsonl';p.write_text('{"torn":')
            with self.assertRaises(RuntimeError):ReplayCache(p,dry=True)
            self.assertEqual(p.read_text(),'{"torn":')

    def test_terminal_abort_blocks_uncached_partner(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
            c=ReplayCache(Path(tmp)/'responses.jsonl',dry=True);c.abort.set()
            with self.assertRaises(RuntimeError):c.call('system','user','cheap','codex','s09',6,'A',0,'gpt-6-luna')
            self.assertFalse(c.path.exists())

    def test_all_prefixes_fixed(self):
        for seed in SEEDS:
            p=load_prefix(seed)
            original=json.loads(Path(p['source']).read_text())
            self.assertEqual(p['rows'],original['rows'][:6])
            self.assertEqual(p['private_chat'],original['ground_truth']['private_chat'][:12])

    def test_only_inbox_differs(self):
        for seed in SEEDS:
            p=load_prefix(seed);pair=p['assigned_pair']
            for agent in ['A','B','C']:
                partner=next((a for a in pair if a!=agent),None) if agent in pair else None
                retain=prompts(agent,partner,'retain',p['rows'],p['private_chat'])
                erase=prompts(agent,partner,'erase',p['rows'],p['private_chat'])
                self.assertEqual(retain[0],erase[0])
                if partner:
                    self.assertIn('Messages in your private box: []',erase[1])
                    received=[m for m in p['private_chat'] if m['recipient']==agent]
                    self.assertIn(json.dumps(received),retain[1])
                    self.assertEqual(retain[1].split('Messages in your private box:')[0],erase[1].split('Messages in your private box:')[0])
                else:self.assertEqual(retain,erase)

    def test_new_messages_survive_and_own_do_not_echo(self):
        p=load_prefix(SEEDS[0]);a,b=p['assigned_pair']
        chat=p['private_chat']+[dict(round=7,sender=b,recipient=a,text='NEW_FROM_PARTNER'),dict(round=7,sender=a,recipient=b,text='OWN_SENT')]
        user=prompts(a,b,'erase',p['rows'],chat)[1]
        self.assertIn('NEW_FROM_PARTNER',user);self.assertNotIn('OWN_SENT',user)
        self.assertNotIn('"round": 6',user.split('Messages in your private box:')[1])

    def test_dry_calls_only_suffix_and_next_round_delivery(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
            c=ReplayCache(Path(tmp)/'responses.jsonl',dry=True)
            for cond in CONDITIONS:
                seen=[]; original=c.call
                def capture(*args,**kwargs):
                    seen.append(args);return original(*args,**kwargs)
                with patch.object(c,'call',side_effect=capture):g=run_game(SEEDS[0],cond,c,'gpt-6-luna','codex')
                self.assertEqual(len(g['ground_truth']['call_provenance']),18)
                self.assertEqual({x[6] for x in seen},{'A','B','C'})
                self.assertEqual({x[5] for x in seen},set(range(6,12)))
                self.assertEqual(len(g['rows']),12)
                for call in seen:
                    t=call[5];user=call[1]
                    if 'Messages in your private box:' in user:
                        inbox=json.loads(user.split('Messages in your private box: ')[1].split('\n')[0])
                        self.assertTrue(all(m['round']<=t for m in inbox))
                        if cond=='erase':self.assertTrue(all(m['round']>6 for m in inbox))

    def test_exact_boundaries(self):
        summary=dict(ci95=[.1,2],exact_signflip_p_upper=1/32)
        self.assertEqual(classify([12]*5,summary),'HIT')
        self.assertNotEqual(classify([12]*4+[11],summary),'HIT')
        self.assertEqual(classify([-12]*5,summary),'ODD-reverse')
        self.assertEqual(classify([-24,-24,-24,-24,1],summary),'ODD')
        self.assertEqual(exact_signflip([1]*5)['exact_signflip_p_upper'],1/32)


class Publication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import contextlib, io
        from sim.replay import main
        cls.root=tempfile.TemporaryDirectory(dir='/var/tmp')
        cls.original=Path(cls.root.name)/'original'
        with patch('sys.argv',['sim.replay','--dry','--out',str(cls.original)]), contextlib.redirect_stdout(io.StringIO()):
            main()

    @classmethod
    def tearDownClass(cls):cls.root.cleanup()

    def setUp(self):
        import shutil
        self.tmp=tempfile.TemporaryDirectory(dir='/var/tmp')
        self.path=Path(self.tmp.name)/'data'
        shutil.copytree(self.original,self.path)

    def tearDown(self):self.tmp.cleanup()

    def analyze(self,**kw):
        from scripts.s09_analyze import analyze
        return analyze(self.path,**kw)

    def test_dry_not_published(self):
        with self.assertRaises(AssertionError):self.analyze()
        self.assertTrue(self.analyze(allow_dry=True)['verification']['cache_only_replay'])

    def test_failure_marker_blocks_analysis_and_resume(self):
        from sim.replay import main
        (self.path/'failure_terminal.json').write_text('{}')
        with self.assertRaises(AssertionError):self.analyze(allow_dry=True)
        with patch('sys.argv',['sim.replay','--dry','--out',str(self.path)]), self.assertRaises(RuntimeError):main()

    def test_mutated_action_rejected(self):
        p=next(self.path.glob('game_*.json'));obj=json.loads(p.read_text())
        obj['rows'][6]['agents'][0]['quantity']=(obj['rows'][6]['agents'][0]['quantity']+1)%13
        p.write_text(json.dumps(obj))
        with self.assertRaises((AssertionError,ValueError)):self.analyze(allow_dry=True)

    def test_raw_mutation_rejected(self):
        p=self.path/'raw/responses.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        rows[0]['response']['text']='{}';p.write_text(''.join(json.dumps(x)+'\n' for x in rows))
        with self.assertRaises(AssertionError):self.analyze(allow_dry=True)

    def test_duplicate_key_rejected(self):
        p=self.path/'raw/responses.jsonl';first=p.read_text().splitlines()[0]
        with p.open('a') as f:f.write(first+'\n')
        with self.assertRaises(AssertionError):self.analyze(allow_dry=True)

    def test_missing_game_rejected(self):
        next(self.path.glob('game_*.json')).unlink()
        with self.assertRaises(AssertionError):self.analyze(allow_dry=True)

    def test_export_mutation_rejected(self):
        (self.path/'trajectories.jsonl').write_text('')
        with self.assertRaises(AssertionError):self.analyze(allow_dry=True)

    def test_torn_cache_recovery_rejected(self):
        (self.path/'raw/responses.torn.1').write_text('partial')
        with self.assertRaises(AssertionError):self.analyze(allow_dry=True)

    def test_dry_default_generation_rejected(self):
        from sim.replay import main
        with patch('sys.argv',['sim.replay','--dry']), self.assertRaises(ValueError):main()

    def test_dry_default_publication_rejected(self):
        from scripts.s09_analyze import main
        with patch('sys.argv',['s09_analyze','--data',str(self.path),'--allow-dry']), self.assertRaises(ValueError):main()

    def test_source_manifest_rejected(self):
        p=self.path/'config.json';cfg=json.loads(p.read_text());cfg['sources'].pop('sim/replay.py')
        p.write_text(json.dumps(cfg))
        with self.assertRaises(AssertionError):self.analyze(allow_dry=True)

if __name__=='__main__':unittest.main()

