"""Narrow public-release hygiene checks. Does not establish consent or copyright."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dist', action='store_true', help='Inspect the built public static tree')
args = parser.parse_args()
if args.dist:
    base = ROOT / 'dist'
    if not (base / 'index.html').is_file():
        raise SystemExit('Build dist before reviewing its publication files.')
    paths = [p for p in base.rglob('*') if p.is_file()]
else:
    base = ROOT
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    paths = [ROOT / name for name in names if name and (ROOT / name).is_file()]

private_link = re.compile(r'https?://(?:chatgpt\.com|chat\.openai\.com)/c/[0-9a-f-]{32,}|/tmp/codex-remote-attachments/[0-9a-f-]{32,}/', re.I)
personal_mail = re.compile(r'\b[A-Z0-9._%+-]+@(?:gmail\.com|qq\.com|163\.com|126\.com|outlook\.com|hotmail\.com)\b', re.I)
text_exts = {'.py', '.js', '.cjs', '.mjs', '.json', '.html', '.css', '.md', '.txt', '.yml', '.yaml', '.toml', '.csv', '.xml', '.svg', '.c', '.m'}
issues = []
rights = {}
rights_file = ROOT / 'publication-rights.json'
if rights_file.exists():
    try:
        declarations = json.loads(rights_file.read_text(encoding='utf-8'))['documents']
        if not isinstance(declarations, list):
            raise ValueError('documents must be a list')
        for entry in declarations:
            rel = Path(entry['path'])
            if rel.is_absolute() or '..' in rel.parts or rel.as_posix() in rights:
                raise ValueError('invalid or duplicate document path')
            web = Path(entry['web_path'])
            if web.is_absolute() or '..' in web.parts or web.suffix.lower() not in {'.html', '.js'}:
                raise ValueError('web_path must identify a converted web page')
            if (entry.get('publish') is not True or entry.get('reviewed') is not True
                or entry.get('rights') not in {'user_owned', 'authorized'}
                or not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ['owner', 'evidence'])
                or not re.fullmatch('[a-f0-9]{64}', entry.get('sha256', ''))):
                raise ValueError('missing reviewed rights or publication decision')
            rights[rel.as_posix()] = entry
    except (ValueError, KeyError, TypeError) as error:
        issues.append(('publication-rights.json', 'invalid document rights record: '+str(error)))

def cleared_document(path, rel):
    """Check a recorded decision, not independently determine copyright."""
    entry = rights.get(rel.as_posix())
    if not entry:
        return False
    if not (base / entry['web_path']).is_file():
        return False
    return hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']

for path in paths:
    rel = path.relative_to(base)
    parts = set(rel.parts)
    name = path.name.lower()
    with path.open('rb') as stream:
        signature = stream.read(8)
    document = path.suffix.lower() in {'.pdf', '.xlsx', '.xls', '.doc', '.docx', '.ppt', '.pptx', '.zip', '.7z', '.rar'} or signature.startswith((b'%PDF-', b'PK\x03\x04'))
    cleared = cleared_document(path, rel) if document or rel.as_posix() in rights else False
    if document and not cleared:
        issues.append((str(rel), 'document/archive lacks a matching reviewed rights record or converted web page'))
    if signature.startswith(b'%PDF-') and path.suffix.lower() != '.pdf':
        issues.append((str(rel), 'PDF signature must not be disguised by another extension'))
    if not cleared and rel.as_posix().startswith(('courses/hs-physics/physics-001/originals/', 'courses/electrical-machines/assets/homework/page-', 'courses/electrical-machines/assets/quickref/page-')):
        issues.append((str(rel), 'source scan or full-page mirror must stay private'))
    if (name == '.env' or name.startswith('.env.') and not name.endswith(('.example', '.sample'))
        or name in {'id_rsa', 'id_ed25519', 'cookies.sqlite', 'cookies.txt', 'credentials.json'}
        or path.suffix.lower() in {'.pem', '.p12', '.pfx', '.key'}
        or parts.intersection({'.git', 'private', '.private', '.ssh'})
        or rel.as_posix().startswith('resources/local/')):
        issues.append((str(rel), 'private file/path'))
    if path.suffix.lower() not in text_exts or str(rel).startswith(('assets/katex/', 'scripts/vendor/')):
        continue
    text = path.read_text(encoding='utf-8', errors='replace')
    for label, pattern in [('private session/attachment link', private_link), ('personal contact email: consent review required', personal_mail)]:
        for match in pattern.finditer(text):
            issues.append((str(rel) + ':' + str(text[:match.start()].count('\n') + 1), label))
if issues:
    for path, reason in issues:
        print(path + ': ' + reason)
    raise SystemExit(1)
print(f'Checked {len(paths)} publication paths; no prohibited path/link/contact patterns. Visual privacy and rights still require review.')
