"""Exercise release boundaries with isolated repositories and real deployment files."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PublicationBoundaries(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ln-publication-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'scripts').mkdir()
        shutil.copy2(ROOT / 'scripts/check-publication.py', self.root / 'scripts/check-publication.py')
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)

    def track(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        subprocess.run(['git', 'add', '-f', name], cwd=self.root, check=True)

    def check_gate(self, *args):
        return subprocess.run(['python', str(self.root / 'scripts/check-publication.py'), *args], capture_output=True, text=True)

    def test_public_contact_and_environment_example_are_allowed(self):
        self.track('README.md', 'owner@users.noreply.github.com')
        self.track('.env.example', 'EXAMPLE_ONLY=1')
        self.assertEqual(self.check_gate().returncode, 0)

    def test_tracked_local_credentials_are_blocked(self):
        self.track('.env.local', 'EXAMPLE_ONLY=1')
        result = self.check_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn('private file/path', result.stdout)

    def test_private_chat_and_contact_are_blocked_without_echoing_them(self):
        private_link = 'https://chatgpt.com/c/' + '0' * 36
        personal_contact = 'example-learner@' + 'gmail' + '.com'
        self.track('notes.txt', private_link + '\n' + personal_contact)
        result = self.check_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn('private session/attachment link', result.stdout)
        self.assertIn('personal contact email', result.stdout)
        self.assertNotIn(private_link, result.stdout)
        self.assertNotIn(personal_contact, result.stdout)

    def test_ignored_files_in_dist_are_still_blocked(self):
        (self.root / 'dist').mkdir()
        (self.root / 'dist/index.html').write_text('<title>LN</title>')
        (self.root / 'dist/credentials.json').write_text('{}')
        result = self.check_gate('--dist')
        self.assertEqual(result.returncode, 1)
        self.assertIn('credentials.json', result.stdout)

if __name__ == '__main__':
    unittest.main()
