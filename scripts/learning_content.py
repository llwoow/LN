"""Validate and render authored explanations; prose quality still needs human review."""
from pathlib import Path
from html.parser import HTMLParser
import html
import json
import re

FIELDS = ('question', 'model', 'reasoning', 'example', 'boundaries', 'checks', 'transfer')
HEADINGS = ('问题与观察', '模型与依据', '推理过程', '完整示例', '适用边界', '检验与修正', '独立迁移')
HUMANITIES = {'hs-chinese', 'hs-english', 'hs-history', 'hs-politics'}


class Inspect(HTMLParser):
    def __init__(self, markup):
        super().__init__(); self.tags = []; self.attributes = []; self.feed(markup)
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag); self.attributes.extend(attrs)


def plain(markup):
    return html.unescape(re.sub('<[^>]*>', '', markup))


def load(path, expected):
    records = json.loads(Path(path).read_text())
    if set(records) != set(expected):
        raise ValueError('Understanding coverage mismatch in ' + str(path) + ': ' + str(set(expected) - set(records)))
    seen = set()
    for identifier, record in records.items():
        for field in FIELDS:
            if not isinstance(record.get(field), str) or len(plain(record[field]).strip()) < 20:
                raise ValueError('Missing substantive explanation: ' + identifier + '/' + field)
        prose = ''.join(plain(record[field]) for field in FIELDS)
        if len(prose) < 600:
            raise ValueError('Explanation is too short to reconstruct: ' + identifier)
        if prose in seen:
            raise ValueError('Duplicated explanation: ' + identifier)
        seen.add(prose)
        example = Inspect(record['example'])
        if 'ol' not in example.tags or example.tags.count('li') < 3:
            raise ValueError('Example must expose at least three reasoned steps: ' + identifier)
        inspected = Inspect(''.join(record[field] for field in FIELDS))
        if set(inspected.tags) & {'script', 'iframe', 'object', 'embed', 'form', 'details'}:
            raise ValueError('Understanding must be directly readable and inert: ' + identifier)
        if any(k.startswith('on') or k in {'hidden', 'srcdoc'} for k, _ in inspected.attributes):
            raise ValueError('Hidden or executable explanation: ' + identifier)
        review = record.get('review', {})
        if not all(isinstance(review.get(key), list) and review[key] for key in ('issues', 'changes')):
            raise ValueError('Missing per-unit teaching review: ' + identifier)
    return records


def render(record, prefix, math_renderer, course_id):
    headings = list(HEADINGS)
    if course_id in HUMANITIES:
        headings[1:3] = ['对象与语境', '分析过程']
        headings[4] = '解释边界'
    markup = '<section class="learning-sequence" data-learning-standard="understanding-v1">'
    for field, heading in zip(FIELDS, headings):
        markup += '<section id="learning-' + field + '" data-learning-step="' + field + '"><h3>' + heading + '</h3>' + record[field] + '</section>'
    markup += '</section>'
    # Newly authored diagrams get their own namespace and do not consume source labels.
    for tag, caption, label in [('figure', 'figcaption', '图'), ('table', 'caption', '表')]:
        count = 0
        def label_diagram(match):
            nonlocal count
            count += 1
            content = match[2]
            number = prefix + '.' + str(count)
            heading = re.search(r'<' + caption + r'\b[^>]*>(.*?)</' + caption + '>', content, re.S)
            if heading:
                text = re.sub(r'^(?:图|表)\s*[A-Za-z0-9.\-]+\s*', '', heading[1])
                content = content[:heading.start()] + '<' + caption + '>' + label + number + ' ' + text + '</' + caption + '>' + content[heading.end():]
            else:
                new_caption = '<' + caption + '>' + label + number + ' ' + ('关系示意' if tag == 'figure' else '分析记录') + '</' + caption + '>'
                content = content + new_caption if tag == 'figure' else new_caption + content
            return match[1] + content + '</' + tag + '>'
        markup = re.sub(r'(<' + tag + r'\b[^>]*>)(.*?)</' + tag + '>', label_diagram, markup, flags=re.S)
    return math_renderer(markup, prefix)
