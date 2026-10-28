"""Index existing equation/figure/table labels without rewriting scientific content."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import argparse
import collections
import json
import re

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
NUMBER = r'(?:\d+|[A-Za-z])(?:[.\-]\d+)+(?:[a-z])?'

class Element:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []
    @property
    def classes(self): return set(self.attrs.get('class', '').split())
    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Element): yield from child.walk()
    def text(self):
        if self.tag in {'annotation', 'svg'} or 'katex-mathml' in self.classes: return ''
        return ''.join(child.text() if isinstance(child, Element) else child for child in self.children)

class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Element('root'); self.stack = [self.root]; self.feed(html)
    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs, self.stack[-1]); self.stack[-1].children.append(node)
        if tag not in VOID: self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID: self.stack.pop()
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag: self.stack = self.stack[:i]; break
    def handle_data(self, value): self.stack[-1].children.append(value)

def assignment(path):
    source = path.read_text('utf-8-sig').strip()
    return json.loads(source[source.rfind(']=') + 2:-1]) if ']=' in source else json.loads(source.split('=', 1)[1][:-1])
def normalize(value): return re.sub(r'[‐‑–—－-]', '.', value.strip())
def label(value):
    match = re.fullmatch(r'(?:公式|式|图|表)?\s*[（(]?\s*(' + NUMBER + r')\s*[)）]?', value.strip())
    return normalize(match[1]) if match else None

def build_index():
    courses = {}; documents = {}; incoming = {}
    for path in sorted((ROOT / 'courses').glob('*/manifest.js')):
        course = assignment(path); courses[course['id']] = course
        for section in course['sections']:
            payload = assignment(ROOT / section['src'])
            if 'html' in payload: documents[(course['id'], section['id'])] = Document(payload['html']).root
    for (course_id, section_id), document in documents.items():
        for node in document.walk():
            href = node.attrs.get('href', '')
            if node.tag == 'a' and href.startswith('#course/'):
                parts = [unquote(part) for part in href.split('/')]
                number = label(node.text())
                if len(parts) >= 4 and number: incoming[(parts[1], parts[2], parts[3])] = number
    result = {}
    for course_id, course in courses.items():
        output = {'sections': {}, 'targets': []}; counters = collections.Counter()
        for section in course['sections']:
            document = documents.get((course_id, section['id']))
            if document is None: continue
            nodes = list(document.walk()); displays = [n for n in nodes if 'math-block' in n.classes or {'math','display'} <= n.classes]
            chapter = re.search(r'第(\d+)章', section['group'])
            prefix = chapter[1] if chapter else str(course['sections'].index(section) + 1)
            # Preserve the imported transformer's section-scoped labels (e.g. S.1, 3.1).
            if section['id'].startswith('transformer-'):
                suffix = section['id'].split('-',1)[1]; prefix = suffix if suffix.isdigit() else ('S' if suffix == 'symbols' else 'A')
            current = {'equations': [], 'figures': [], 'tables': []}
            def append(kind, node, number, index, aliases=()):
                existing = node.attrs.get('id')
                anchor = existing or (kind + '-' + re.sub(r'[^a-zA-Z0-9_-]', '-', number) if number else kind + '-unnumbered-' + str(index + 1))
                used = {target['anchor'] for target in output['targets'] if target['section'] == section['id']}
                if anchor in used: anchor += '-' + str(index + 1)
                target = {'kind': kind, 'number': number, 'anchor': anchor, 'section': section['id'], 'group': section['group'], 'aliases': list(aliases)}
                current[{'equation':'equations','figure':'figures','table':'tables'}[kind]].append(target); output['targets'].append(target)
            for i, node in enumerate(displays):
                tags = [n for n in node.walk() if 'katex-tag' in n.classes or 'tag' in n.classes]
                number = label(node.attrs.get('data-equation', '')) or (label(tags[0].text()) if tags else None)
                aliases = []
                siblings = [n for n in node.parent.children if isinstance(n,Element)]
                position = siblings.index(node)
                if position and 'equation-anchor' in siblings[position-1].classes and siblings[position-1].attrs.get('id'): aliases.append(siblings[position-1].attrs['id'])
                append('equation', node, number, i, aliases)
            for kind, tag in [('figure', 'figure'), ('table', 'table')]:
                for i, node in enumerate(n for n in nodes if n.tag == tag):
                    aliases = []
                    existing = node.attrs.get('id')
                    parent = node.parent
                    while parent and parent.tag not in {'root', 'section', 'article'}:
                        if parent.attrs.get('id', '').startswith('tab:'):
                            aliases.append(parent.attrs['id']); break
                        parent = parent.parent
                    number = incoming.get((course_id, section['id'], existing)) or next((incoming[(course_id, section['id'], alias)] for alias in aliases if (course_id, section['id'], alias) in incoming), None)
                    if not number:
                        captions = [n for n in node.walk() if n.tag in {'figcaption', 'caption'}]
                        match = re.match(r'\s*(?:图|表)\s*(' + NUMBER + ')', captions[0].text()) if captions else None
                        number = normalize(match[1]) if match else None
                    counter_key = (section['group'], prefix, kind)
                    if number and number.startswith(prefix + '.') and number.split('.')[-1].isdigit(): counters[counter_key] = max(counters[counter_key], int(number.split('.')[-1]))
                    if not number:
                        counters[counter_key] += 1; number = prefix + '.' + str(counters[counter_key])
                    append(kind, node, number, i, aliases)
            output['sections'][section['id']] = current
        result[course_id] = output
    return result

def render_index(): return '// Generated by scripts/build-reference-index.py; source labels are preserved.\nwindow.LN_PUBLICATION_INDEX=' + json.dumps(build_index(), ensure_ascii=False, separators=(',', ':')) + ';\n'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, default=ROOT/'reference-index.js'); parser.add_argument('--check', action='store_true'); args=parser.parse_args()
    source = render_index()
    if args.check:
        if not args.output.exists() or args.output.read_text() != source: raise SystemExit('Reference index is stale. Run python scripts/build-reference-index.py.')
        print('Reference index matches current material.')
    else:
        args.output.write_text(source)
        data=build_index();print('Indexed ' + str(sum(len(c['targets']) for c in data.values())) + ' equation, figure and table targets.')
