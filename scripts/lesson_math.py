"""Render authored TeX without changing the organization of the reading."""
from pathlib import Path
import html
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MATH = re.compile(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', re.S)


def render(markup, prefix):
    matches = list(MATH.finditer(markup))
    if not matches:
        return markup
    expressions = [{'tex': html.unescape(m[1] if m[1] is not None else m[2]), 'display': m[1] is not None} for m in matches]
    proc = subprocess.run(['node', str(ROOT/'scripts/render-math.cjs')], input=json.dumps(expressions, ensure_ascii=False), text=True, capture_output=True)
    if proc.returncode:
        raise ValueError('Math rendering failed in '+prefix+': '+proc.stderr[-1800:])
    rendered = iter(json.loads(proc.stdout)); sequence = 0
    def substitute(match):
        nonlocal sequence
        formula = next(rendered)
        if match[1] is not None:
            sequence += 1
            return '<div class="math display" data-equation="'+prefix+'.'+str(sequence)+'">'+formula+'</div>'
        return '<span class="math inline">'+formula+'</span>'
    return MATH.sub(substitute, markup)
