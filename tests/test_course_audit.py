"""Evidence discipline and real-manifest coverage for LN audit inventory."""
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
inventory = runpy.run_path(str(ROOT / 'scripts/build-course-audit.py'))


class CourseAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = inventory['make_inventory'](ROOT)
        cls.rows = cls.data['sections']

    def test_exact_scope(self):
        ids = {row['courseId'] for row in self.rows}
        self.assertEqual(ids, {'automatic-control', 'electromagnetic-compatibility', 'electrical-machines'})
        self.assertTrue(all(row['group'].startswith(('第2章', '第3章'))
                            for row in self.rows if row['courseId'] == 'electrical-machines'))

    def test_automatic_control_outline_is_not_verified(self):
        control = [row for row in self.rows if row['courseId'] == 'automatic-control']
        manifest = inventory['assignment']((ROOT / 'courses/automatic-control/manifest.js').read_text(encoding='utf-8'))
        self.assertEqual({row['id'] for row in control}, {section['id'] for section in manifest['sections']})
        self.assertEqual({row['id'] for row in control if row['kind'] == 'outline'},
                         {section['id'] for section in manifest['sections'] if section['kind'] == 'outline'})
        self.assertTrue(all(row['status'] == '骨架状态' for row in control if row['kind'] == 'outline'))
        self.assertFalse(any(row['status'] == '已验证' for row in self.rows))

    def test_grounded_paths_and_anchor_links(self):
        for row in self.rows:
            if row['status'] == '部分接入':
                self.assertTrue((ROOT / row['sourcePath']).is_file())
                self.assertEqual(len(row['sourceDigest']), 64)
            self.assertEqual(row['entryHash'], '#course/' + row['courseId'] + '/' + row['id'])
        transformer = next(row for row in self.rows if row['id'] == 'transformer-sec27')
        self.assertTrue(transformer['subsections'], 'HTML headings should be parsed from real lesson data')

    def test_emc_entries_are_file_checked_not_declared_complete(self):
        emc = [row for row in self.rows if row['courseId'] == 'electromagnetic-compatibility']
        self.assertEqual(len(emc), 40)
        self.assertTrue(any(row['signals']['图示标记'] for row in emc))
        self.assertTrue(all(row['status'] != '已验证' for row in emc))


if __name__ == '__main__':
    unittest.main()
