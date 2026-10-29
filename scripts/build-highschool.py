"""Build authored lessons against the supplied, version-aware Hainan textbook index.

Run before the shared reference/glossary builders. KaTeX is vendored for offline builds.
"""
from pathlib import Path
import argparse
import html
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ORDER = ['chinese','math','english','physics','chemistry','biology','politics','history','geography']
MAIN = {'chinese','math','english','physics','chemistry','biology'}
MATH = re.compile(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', re.S)


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def render(markup, prefix):
    matches = list(MATH.finditer(markup))
    if not matches:
        return markup
    expressions = [{'tex': html.unescape(m[1] if m[1] is not None else m[2]), 'display': m[1] is not None} for m in matches]
    proc = subprocess.run(['node', str(ROOT/'scripts/render-math.cjs')], input=dump(expressions), text=True, capture_output=True)
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


def worked_examples(lesson):
    output=[];used=set()
    for example in lesson.get('workedExamples',[]):
        identifier=example['id']
        if not re.fullmatch(r'[a-z][a-z0-9-]*',identifier) or identifier in used:raise ValueError('Invalid worked example id: '+identifier)
        used.add(identifier)
        if len(example['steps'])<2:raise ValueError('Worked example needs a reasoning sequence: '+identifier)
        steps=''.join('<li><h4>'+html.escape(step['title'])+'</h4>'+step['html']+'</li>' for step in example['steps'])
        output.append('<section class="worked-example" id="worked-'+identifier+'" data-worked-example="'+identifier+'"><h3>典型题 · '+html.escape(example['title'])+'</h3>'+example['question']+'<details class="worked-solution"><summary>分步解析</summary><ol class="worked-steps">'+steps+'</ol><h4>结果与核查</h4>'+example['conclusion']+'<h4>易错点</h4>'+example['pitfall']+'</details><details class="study-answer"><summary>变式自测与答案</summary>'+example['selfTest']['question']+'<details><summary>查看答案</summary>'+example['selfTest']['answer']+'</details></details></section>')
    return ''.join(output)


def build(partial=False):
    courses = []
    cross_links = json.loads((ROOT/'courses/highschool/cross-links.json').read_text())
    reused_terms = json.loads((ROOT/'courses/highschool/shared-terms.json').read_text())
    learning_paths = json.loads((ROOT/'courses/highschool/learning-paths.json').read_text())
    for slug in ORDER:
        folder = ROOT/'courses'/('hs-'+slug)
        data = json.loads((folder/'source-index.json').read_text())
        authored_file = folder/'content.json'
        if not authored_file.exists():
            if partial: continue
            raise ValueError('Missing authored lessons: '+slug)
        authored = json.loads(authored_file.read_text())
        lessons = {l['id']: l for l in authored['lessons']}
        expected = {n['知识节点编号'] for n in data['nodes']}
        if set(lessons) != expected or len(lessons) != len(authored['lessons']):
            raise ValueError('Node coverage mismatch: '+slug+' '+str(expected-set(lessons)))
        books = {b['教材编号']: b for b in data['books'] if b['索引层级'] == '主索引'}
        source_map = {s['来源编号']: {'id':s['来源编号'],'title':s['标题'],'url':s['网址'],'scope':s['支持的结论']} for s in data['sources']}
        source_map.update({s['id']:s for s in authored.get('sources',[])})
        course_id = 'hs-'+slug
        manifest = {'id':course_id,'title':data['subject'],'level':'highschool','category':'高中','track':'复习主线' if slug in MAIN else '合格考与拓展','topics':[authored['summary']],'summary':authored['summary'],'versionNote':data['overview'][0]['地区核验状态'],'sections':[],'resources':{},'knowledgeMap':{'nodes':[],'links':[],'chapters':[]}}
        manifest['glossary'] = 'courses/'+course_id+'/glossary-index.js'
        glossary = {'lazy':True,'symbolDefinitions':[],'terms':[]}
        reuse = {(e['section'],e['term']):e for e in reused_terms.get(course_id,[])}
        graph = manifest['knowledgeMap']; edges=set(); targets={n:n.lower() for n in expected}
        graph['paths']=learning_paths.get(course_id,[])
        path_ids=set()
        for path in graph['paths']:
            if path['id'] in path_ids or len(path['steps'])<2:raise ValueError('Invalid learning path: '+path['id'])
            path_ids.add(path['id'])
            if len({s['section'] for s in path['steps']})!=len(path['steps']):raise ValueError('Repeated learning path step: '+path['id'])
            for step in path['steps']:
                if step['section'] not in targets.values() or not step['focus']:raise ValueError('Invalid learning path target: '+path['id'])
        for book in books.values():
            group = book['册次']
            manifest['resources'][group] = {'links':[{'label':'教材入口','href':'https://jc.pep.com.cn/'},{'label':'版本与来源','href':'#highschool/resources'}]}
            graph['chapters'].append({'group':group,'description':book['课程类别']+' · '+book['版本']})
        lesson_dir = folder/'lessons'; lesson_dir.mkdir(exist_ok=True)
        for node in data['nodes']:
            identifier = node['知识节点编号']; section = targets[identifier]; lesson = lessons[identifier]
            book_id = '-'.join(identifier.split('-')[:2]); book = books[book_id]
            # These are LN's own equation labels, never presented as original textbook numbers.
            prefix = str(list(books).index(book_id)+1)+'.'+str(int(identifier.rsplit('K',1)[1]))
            body = '<h2>'+html.escape(node['模块或主题'])+'</h2>'+render(lesson['body']+worked_examples(lesson),prefix)
            paths=[p for p in graph['paths'] if any(s['section']==section for s in p['steps'])]
            if paths:
                path_body=[]
                for path in paths:
                    steps=[]
                    for step in path['steps']:
                        target=next(n for n in data['nodes'] if n['知识节点编号'].lower()==step['section'])
                        steps.append('<li><a href="#course/'+course_id+'/'+step['section']+'"'+(' aria-current="page"' if step['section']==section else '')+'>'+html.escape(target['模块或主题'])+'</a><p>'+html.escape(step['focus'])+'</p></li>')
                    path_body.append('<section><h4>'+html.escape(path['title'])+'</h4><p>'+html.escape(path['summary'])+'</p><ol>'+''.join(steps)+'</ol></section>')
                body+='<details class="study-pathways"><summary>所在学习主线</summary>'+''.join(path_body)+'</details>'
            related=[]
            for edge in lesson.get('related',[]):
                other = edge['to']
                if other not in targets or other == identifier:
                    raise ValueError('Invalid relation in '+identifier+': '+other)
                label = edge['label']; description = edge['description']
                if not label or not description:raise ValueError('Unexplained relation: '+identifier)
                pair=(section,targets[other])
                if pair not in edges:
                    graph['links'].append({'from':section,'to':targets[other],'label':label,'description':description});edges.add(pair)
                other_node = next(n for n in data['nodes'] if n['知识节点编号']==other)
                related.append('<li><a href="#course/'+course_id+'/'+targets[other]+'">'+html.escape(other_node['模块或主题'])+'</a>：'+html.escape(description)+'</li>')
            if related:body+='<aside class="study-connections"><h3>知识联系</h3><ul>'+''.join(related)+'</ul></aside>'
            cross=[]
            for connection in cross_links:
                current={'course':course_id,'section':section}
                if current not in [connection['from'],connection['to']]:continue
                other=connection['to'] if current==connection['from'] else connection['from']
                cross.append('<li><a href="#course/'+other['course']+'/'+other['section']+'">'+html.escape(connection['label'])+'</a>：'+html.escape(connection['description'])+'</li>')
            if cross:body+='<aside class="study-connections"><h3>跨学科联系</h3><ul>'+''.join(cross)+'</ul></aside>'
            citations=[]
            for sid in lesson.get('sources',[]):
                if sid not in source_map:raise ValueError('Unknown source '+sid+' in '+identifier)
                source=source_map[sid]
                citations.append('<li><a href="'+html.escape(source['url'],quote=True)+'" target="_blank" rel="noopener">'+html.escape(source['title'])+'</a>'+(('：'+html.escape(source['scope'])) if source.get('scope') else '')+'</li>')
            body+='<details class="study-sources"><summary>教材对应与参考</summary><p>'+html.escape(book['版本']+' · '+book['册次'])+'。模块对应来自所附核验报告；本节讲解、例题与自测为整理编写，公式编号为本站编号。</p>'
            body+='<p>'+html.escape(book['海南使用状态'])+'</p><ul>'+''.join(citations)+'</ul></details>'
            src='courses/'+course_id+'/lessons/'+section+'.js'
            (ROOT/src).write_text('window.LN_LESSONS=window.LN_LESSONS||{};\nwindow.LN_LESSONS['+dump(course_id+'/'+section)+']='+dump({'html':body})+';\n')
            concepts=[t['title'] for t in lesson.get('terms',[])]+[s['title'] for s in lesson.get('symbols',[])]
            keywords=[alias for term in lesson.get('terms',[]) for alias in term['aliases']]+concepts
            manifest['sections'].append({'id':section,'title':node['模块或主题'],'group':book['册次'],'kind':'html','src':src,'curriculum':node['课程类别'],'keywords':[identifier,node['能力要点'],node['版本'],*keywords]})
            graph['nodes'].append({'section':section,'title':node['模块或主题'],'note':lesson.get('mapNote') or ' · '.join(concepts[:2]) or node['课程类别'],'keywords':keywords})
            for kind,key in [('terms','terms'),('symbols','symbolDefinitions')]:
                for entry in lesson.get(kind,[]):
                    definition={**entry,'id':section+'-'+entry['id'],'section':section,'sections':[section]}
                    shared = reuse.get((identifier,entry['id'])) if kind=='terms' else None
                    if shared:
                        if not set(shared['aliases']) <= set(entry['aliases']):raise ValueError('Unreviewed shared alias: '+entry['id'])
                        definition['reuseAliases']=shared['aliases']
                        definition['caseSensitiveAliases']=shared.get('caseSensitiveAliases',[])
                    glossary[key].append(definition)
        if set(reuse) != {(l['id'],t['id']) for l in authored['lessons'] for t in l['terms'] if (l['id'],t['id']) in reuse}:
            raise ValueError('Unknown shared definition in '+course_id)
        (folder/'manifest.js').write_text('window.LN_HS_'+slug.upper()+'='+dump(manifest)+';\n')
        (folder/'glossary.json').write_text(json.dumps(glossary,ensure_ascii=False,indent=2)+'\n')
        courses.append(manifest)
    (ROOT/'courses/highschool/courses.js').write_text('window.LN_HIGH_SCHOOL_COURSES='+dump(courses)+';\n')
    print('Built '+str(len(courses))+' high-school subjects, '+str(sum(len(c['sections']) for c in courses))+' authored lessons.')


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--partial',action='store_true');args=parser.parse_args();build(args.partial)
