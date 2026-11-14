"""Narrow public-release hygiene checks. Does not establish consent or copyright."""
from pathlib import Path
import argparse
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
for path in paths:
    rel = path.relative_to(base)
    parts = set(rel.parts)
    name = path.name.lower()
    with path.open('rb') as stream:
        signature = stream.read(8)
    if path.suffix.lower() in {'.pdf', '.xlsx', '.xls', '.doc', '.docx', '.ppt', '.pptx', '.zip', '.7z', '.rar'} or signature.startswith((b'%PDF-', b'PK\x03\x04')):
        issues.append((str(rel), 'source document/archive must stay private; use citation or external link'))
    if rel.as_posix().startswith(('courses/hs-physics/physics-001/originals/', 'courses/electrical-machines/assets/homework/page-', 'courses/electrical-machines/assets/quickref/page-')):
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
