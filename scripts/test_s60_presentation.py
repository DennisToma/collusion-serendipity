"""Ensure the post-outcome publication guard rejects false displayed claims."""
from pathlib import Path
import unittest
from scripts.s60_publish_check import ARTIFACTS,DOCUMENTS,compare_rendered,render_expected,render_documents_expected,compare_documents

class Tests(unittest.TestCase):
    def test_full_frozen_renderer_matches_without_changing_originals(self):
        before={name:Path(name).read_bytes() for name in ARTIFACTS}
        self.assertEqual(set(compare_rendered(render_expected())),set(ARTIFACTS))
        self.assertTrue(all(Path(name).read_bytes()==blob for name,blob in before.items()))

    def test_front_report_drift_is_rejected_without_rewriting(self):
        before={name:Path(name).read_bytes() for name in DOCUMENTS}
        generated=render_documents_expected()
        self.assertEqual(set(compare_documents(generated)),set(DOCUMENTS))
        changed=dict(before);changed['REPORT.md']=changed['REPORT.md'].replace(b'+0.150',b'+0.900',1)
        self.assertNotEqual(changed['REPORT.md'],before['REPORT.md'])
        with self.assertRaisesRegex(AssertionError,'Displayed artifact differs.*REPORT.md'):
            compare_documents(generated,read_bytes=changed.__getitem__)
        self.assertTrue(all(Path(name).read_bytes()==blob for name,blob in before.items()))

    def test_readme_false_claim_is_rejected(self):
        generated=render_documents_expected()
        current={name:Path(name).read_bytes() for name in DOCUMENTS}
        current['README.md']=current['README.md'].replace(b'Ten fresh paired workplace games',b'Confirmed HIT +0.900',1)
        self.assertNotEqual(current['README.md'],Path('README.md').read_bytes())
        with self.assertRaisesRegex(AssertionError,'Displayed artifact differs.*README.md'):
            compare_documents(generated,read_bytes=current.__getitem__)

    def test_later_pilots_can_append_and_archive_the_front_summary(self):
        import re
        generated=render_documents_expected();current=dict(generated)
        report=current['REPORT.md'].decode().replace('· Iteration 43 ·','· Iteration 44 ·')
        report=re.sub(r'<!-- S60 summary start -->.*?<!-- S60 summary end -->','<!-- S60 summary start --><!-- S60 summary end -->',report,flags=re.S)
        current['REPORT.md']=report.encode()
        for name in ['README.md','REPORT_DETAILS.md','HITS.md']:
            current[name]+=b'\n\n## S62 later pilot\nFuture work.\n'
        self.assertEqual(set(compare_documents(generated,read_bytes=current.__getitem__)),set(DOCUMENTS))

    def test_false_verdict_and_effect_are_rejected_with_valid_links(self):
        expected={name:b'canonical' for name in ARTIFACTS}
        expected[ARTIFACTS[0]]=b'ODD +0.150 [Design](../DESIGN_S60.md)'
        changed=dict(expected);changed[ARTIFACTS[0]]=b'HIT +0.900 [Design](../DESIGN_S60.md)'
        with self.assertRaisesRegex(AssertionError,'Displayed artifact differs.*s60_summary'):
            compare_rendered(expected,read_bytes=changed.__getitem__)

    def test_each_appendix_and_figure_is_required_and_bound(self):
        expected={name:b'canonical-'+name.encode() for name in ARTIFACTS}
        for name in ARTIFACTS:
            changed=dict(expected);changed[name]+=b'changed'
            with self.assertRaisesRegex(AssertionError,'Displayed artifact differs'):
                compare_rendered(expected,read_bytes=changed.__getitem__)
        with self.assertRaises(AssertionError):compare_rendered({ARTIFACTS[0]:b'only summary'})

if __name__=='__main__':unittest.main()
