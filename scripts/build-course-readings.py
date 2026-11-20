"""Render maintained course manuscripts registered in existing manifests."""
import argparse
import json
from pathlib import Path
import runpy
from lesson_math import render

ROOT = Path(__file__).resolve().parents[1]


def build(check=False):
    assignment = runpy.run_path(str(ROOT / 'scripts/build-reference-index.py'))['assignment']
    count = 0
    for manifest_path in sorted((ROOT / 'courses').glob('*/manifest.js')):
        course = assignment(manifest_path)
        for section in course['sections']:
            if 'manuscript' not in section:
                continue
            manuscript = ROOT / section['manuscript']
            if section['kind'] != 'html' or manuscript.parent != manifest_path.parent / 'readings':
                raise ValueError(f"Invalid manuscript path for {section['id']}")
            key = f"{course['id']}/{section['id']}"
            lesson = render(manuscript.read_text(encoding='utf-8'), section['equationPrefix'])
            prefix = 'window.LN_LESSONS=window.LN_LESSONS||{};window.LN_LESSONS['
            payload = prefix + json.dumps(key) + ']=' + json.dumps({'html': lesson}, ensure_ascii=False) + ';\n'
            target = ROOT / section['src']
            if check:
                if not target.is_file() or target.read_text(encoding='utf-8') != payload:
                    raise ValueError(f"Stale compiled reading for {key}")
            else:
                target.write_text(payload, encoding='utf-8')
            count += 1
    print(f"Checked {count} compiled readings." if check else f"Rendered {count} course readings.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
