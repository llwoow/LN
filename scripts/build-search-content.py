"""Index only public, shipped lesson text and TeX at real section/heading targets."""
import json
import re
from pathlib import Path
from importlib import import_module

reference = import_module('build-reference-index')
def clean(value):
    return ' '.join(value.split())

def build(root):
    rows = []
    for path in sorted((root / 'courses').glob('*/manifest.js')):
        course = reference.assignment(path)
        for section in course['sections']:
            if section.get('kind') == 'outline' or not section.get('src'):
                continue
            source = root / section['src']
            if not source.is_file():
                continue
            payload = reference.assignment(source)
            if not isinstance(payload, dict) or not payload.get('html'):
                continue
            doc = reference.Document(payload['html']).root
            anchor, title, chunks = '', section['title'], []
            def flush():
                body = clean(' '.join(chunks))
                if body:
                    rows.append(dict(course=course['id'], section=section['id'], anchor=anchor, title=title, kind='正文', text=body))
            def visit(node):
                nonlocal anchor, title, chunks
                if isinstance(node, str):
                    chunks.append(node)
                    return
                if node.tag in {'script','style','svg','template'} or 'katex-html' in node.classes:
                    return
                if node.tag in {'h2','h3','h4'} and node.attrs.get('id') and node.text().strip():
                    flush()
                    anchor, title, chunks = node.attrs['id'], clean(node.text()), []
                if node.tag == 'annotation' and node.attrs.get('encoding') == 'application/x-tex':
                    tex = clean(node.text() or ''.join(c for c in node.children if isinstance(c,str)))
                    if tex:
                        rows.append(dict(course=course['id'],section=section['id'],anchor=anchor,title=tex,kind='公式',text=tex))
                    return
                for child in node.children:
                    visit(child)
            visit(doc)
            flush()
    return rows

if __name__ == '__main__':
    import sys
    root = Path(sys.argv[1]).resolve()
    (root / 'courses/search-content.json').write_text(json.dumps(build(root),ensure_ascii=False,separators=(',',':')),encoding='utf-8')
