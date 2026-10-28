"""Build source-backed symbol definitions and explicitly reviewed terminology."""
from pathlib import Path
import argparse
import html
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
REF = runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))
Element, Document, assignment = REF['Element'], REF['Document'], REF['assignment']

def raw(node): return ''.join(raw(c) if isinstance(c,Element) else c for c in node.children)
def clean(text): return re.sub('[\u200b\u200c\u200d\ufeff]', '', text).strip()
def canonical(text): return clean(text).replace('ϕ','φ').replace('′',"'").replace('˙','dot:')
def atom(node):
    children=[c for c in node.children if isinstance(c,Element)]
    if node.tag in {'mi','mtext'}:
        value=canonical(raw(node))
        variant=node.attrs.get('mathvariant','')
        if variant in {'script','double-struck'}:return 'cal:'+value
        return 'bold:'+value if 'bold' in variant else value
    if node.tag=='msub' and len(children)>=2:return atom(children[0])+'_'+canonical(raw(children[1])).replace(' ','')
    if node.tag=='msubsup' and len(children)>=3:return atom(children[0])+'_'+canonical(raw(children[1])).replace(' ','')+("'" if '′' in raw(children[2]) or "'" in raw(children[2]) else '')
    if node.tag=='msup' and len(children)>=2:
        base=atom(children[0]);power=raw(children[1]);return base+"'" if '′' in power or "'" in power else base
    if node.tag=='mover' and len(children)>=2:
        return ('dot:' if any(c in raw(children[1]) for c in ['˙','̇','⋅','.']) else '')+atom(children[0])
    if node.tag=='mrow' and len(children)>1 and all(c.tag in {'mi','mtext'} and c.attrs.get('mathvariant')=='normal' for c in children):return ''.join(canonical(raw(c)) for c in children)
    if node.tag in {'mrow','mstyle','mpadded','semantics','math'} and len(children)==1:return atom(children[0])
    return ''

def definition_keys(node):
    result=[]
    def scan(n):
        if n.tag in {'mi','mtext','msub','msup','msubsup','mover'} or (n.tag=='mrow' and atom(n)):
            value=atom(n)
            if value and not value.isdigit():result.append(value)
            return
        depth=0
        for child in n.children:
            if not isinstance(child,Element) or child.tag=='annotation':continue
            token=raw(child)
            if child.tag=='mo' and token=='=':break
            if child.tag=='mo' and token=='(':depth+=1;continue
            if child.tag=='mo' and token==')':depth=max(0,depth-1);continue
            if not depth:scan(child)
    math=[n for n in node.walk() if n.tag=='math']
    for m in math:scan(m)
    return list(dict.fromkeys(result))

def markup(node):
    if isinstance(node,str):return html.escape(node,quote=False)
    if node.tag in {'script','style','iframe','object','form'}:return ''
    attrs=''.join(' '+k+'="'+html.escape(v or '',quote=True)+'"' for k,v in node.attrs.items() if not k.startswith('on') and k not in {'id','href'})
    return '<'+node.tag+attrs+'>'+''.join(markup(c) for c in node.children)+'</'+node.tag+'>'
def inner(node):return ''.join(markup(c) for c in node.children)

def build():
    result={}
    for manifest in sorted((ROOT/'courses').glob('*/manifest.js')):
        course=assignment(manifest);config_path=manifest.parent/'glossary.json'
        if not config_path.exists():continue
        config=json.loads(config_path.read_text());sections={s['id']:s for s in course['sections']};documents={}
        def document(section):
            if section not in documents:documents[section]=Document(assignment(ROOT/sections[section]['src']).get('html','')).root
            return documents[section]
        entries=[]
        for spec in config.get('symbolTables',[]):
            section=sections[spec['section']];tables=[n for n in document(section['id']).walk() if n.tag=='table'];table=tables[spec['table']]
            for row_index,row in enumerate(n for n in table.walk() if n.tag=='tr'):
                cells=[n for n in row.children if isinstance(n,Element) and n.tag=='td']
                if len(cells)<2:continue
                keys=definition_keys(cells[0]);description=clean(cells[1].text())
                # The source explicitly defines these paired symbols on the same row.
                if section['id']=='dc-overview' and 'P=2p' in clean(cells[0].text()):keys.append('p')
                if section['id']=='dc-overview' and 'A=2a' in clean(cells[0].text()):keys.append('a')
                kind='subscript' if description.startswith('下标') or clean(cells[0].text())=='1,2；H,L' else 'symbol'
                if '\\phantom' in raw(cells[0]):continue
                if not keys:continue
                identifier='symbol-'+section['id']+'-'+str(row_index)
                source={'section':section['id'],'anchor':'definition-'+identifier,'table':spec['table'],'row':row_index}
                entries.append({'id':identifier,'kind':kind,'title':clean(cells[0].text()),'symbolHtml':inner(cells[0]),'keys':list(dict.fromkeys(keys)),'description':description,'definitionHtml':inner(cells[1]),'unitHtml':inner(cells[2]) if len(cells)>2 else '', 'group':section['group'],'source':source})
        for spec in config.get('symbolDefinitions',[]):
            nodes=[n for n in document(spec['section']).walk() if n.tag in {'p','h2','h3','h4','li','td'}]
            i,node=next((i,n) for i,n in enumerate(nodes) if spec['match'] in clean(n.text()))
            source={'section':spec['section'],'anchor':node.attrs.get('id') or 'definition-passage-'+str(i),'passage':i}
            entries.append({**spec,'kind':'symbol','definitionHtml':inner(node),'source':source,'group':sections[spec['section']]['group']})
        for term in config.get('terms',[]):
            nodes=[n for n in document(term['section']).walk() if n.tag in {'p','h2','h3','h4','li','td'}]
            matching=[(i,n) for i,n in enumerate(nodes) if term['match'] in clean(n.text())]
            if not matching:raise ValueError('Definition source not found: '+term['id'])
            i,node=matching[0]
            if node.tag in {'h2','h3','h4'}:
                following=next(((j,n) for j,n in enumerate(nodes[i+1:],i+1) if n.tag=='p'),None)
                if following:i,node=following
            source={'section':term['section'],'anchor':node.attrs.get('id') or 'definition-passage-'+str(i),'passage':i}
            entries.append({**term,'kind':'term','source':source,'definitionHtml':inner(node),'group':sections[term['section']]['group']})
        result[course['id']]={'entries':entries}
    return result

def render():return '// Generated by scripts/build-glossary.py from definition tables and reviewed terms.\nwindow.LN_GLOSSARY='+json.dumps(build(),ensure_ascii=False,separators=(',',':'))+';\n'
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'glossary-index.js');parser.add_argument('--check',action='store_true');args=parser.parse_args();text=render()
    if args.check:
        if not args.output.exists() or args.output.read_text()!=text:raise SystemExit('Glossary index is stale. Run python scripts/build-glossary.py.')
        print('Glossary index matches definition sources.')
    else:
        args.output.write_text(text);data=build();print('Indexed '+str(sum(len(c['entries']) for c in data.values()))+' source-backed symbol rows and terms.')
