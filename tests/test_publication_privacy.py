"""Exercise release boundaries with isolated repositories and real deployment files."""
from pathlib import Path
import shutil
import hashlib
import json
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

    def test_source_documents_and_disguised_pdf_are_blocked(self):
        self.track('notes.pdf', '%PDF-1.7 example')
        self.track('renamed.txt', '%PDF-1.7 example')
        self.track('sheet.xlsx', 'example')
        result = self.check_gate()
        self.assertEqual(result.returncode, 1)
        for name in ['notes.pdf', 'renamed.txt', 'sheet.xlsx']:
            self.assertIn(name, result.stdout)

    def test_external_pdf_citation_is_allowed(self):
        self.track('source.html', '<a href="https://docs.example.org/reference.pdf">Source</a>')
        self.assertEqual(self.check_gate().returncode, 0)

    def clear_document(self, name, rights='user_owned', publish=True):
        self.track('lesson.html', '<article><h1>Explanation</h1><p>A complete teaching example lives here.</p></article>')
        entry={'path':name,'rights':rights,'owner':'Example author','evidence':'Explicit ownership and public supplement decision for this synthetic fixture.',
               'publish':publish,'reviewed':True,'web_path':'lesson.html',
               'sha256':hashlib.sha256((self.root/name).read_bytes()).hexdigest()}
        self.track('publication-rights.json', json.dumps({'documents':[entry]}))

    def test_owned_pdf_is_not_rejected_for_its_format(self):
        self.track('notes.pdf', '%PDF-1.7 owned synthetic fixture')
        self.clear_document('notes.pdf')
        self.assertEqual(self.check_gate().returncode, 0)

    def test_authorization_must_be_explicit_and_match_actual_content(self):
        self.track('notes.pdf', '%PDF-1.7 authorized synthetic fixture')
        self.clear_document('notes.pdf', rights='authorized')
        self.assertEqual(self.check_gate().returncode, 0)
        self.track('notes.pdf', '%PDF-1.7 changed after review')
        self.assertEqual(self.check_gate().returncode, 1)

    def test_owned_document_does_not_replace_the_converted_page(self):
        self.track('notes.pdf', '%PDF-1.7 owned synthetic fixture')
        self.clear_document('notes.pdf')
        (self.root/'lesson.html').unlink()
        self.assertEqual(self.check_gate().returncode, 1)

    def test_rights_record_does_not_grant_publication_by_itself(self):
        self.track('notes.pdf', '%PDF-1.7 owned synthetic fixture')
        self.clear_document('notes.pdf', publish=False)
        self.assertEqual(self.check_gate().returncode, 1)

    def test_ownership_does_not_bypass_privacy_or_disguised_formats(self):
        self.track('renamed.txt', '%PDF-1.7 synthetic fixture')
        self.clear_document('renamed.txt')
        self.assertEqual(self.check_gate().returncode, 1)
        self.assertIn('disguised',self.check_gate().stdout)
        self.track('private/notes.pdf', '%PDF-1.7 synthetic private fixture')
        self.clear_document('private/notes.pdf')
        self.assertIn('private file/path',self.check_gate().stdout)

    def test_rights_cleared_artifact_is_checked_in_built_output(self):
        self.track('notes.pdf', '%PDF-1.7 owned synthetic fixture')
        self.clear_document('notes.pdf')
        (self.root/'dist').mkdir()
        for name in ['notes.pdf','lesson.html']:
            shutil.copy2(self.root/name,self.root/'dist'/name)
        (self.root/'dist/index.html').write_text('<title>LN</title>')
        self.assertEqual(self.check_gate('--dist').returncode, 0)
        (self.root/'dist/notes.pdf').write_text('%PDF-1.7 substituted bytes')
        self.assertEqual(self.check_gate('--dist').returncode, 1)

    def test_full_page_scans_are_blocked_in_public_output(self):
        name = 'courses/hs-physics/physics-001/originals/page.jpg'
        self.track(name, 'example image payload')
        result = self.check_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn('source scan or full-page mirror', result.stdout)

if __name__ == '__main__':
    unittest.main()
