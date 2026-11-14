"""Render the user's solved Chapter 2 exercises as native HTML and local KaTeX."""
from pathlib import Path
import html
import json
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
COURSE=ROOT/'courses/electrical-machines'
REF=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))
render=runpy.run_path(str(ROOT/'scripts/build-highschool.py'))['render']
EXPECTED=['2-2','2-3','2-4','2-6','2-7','2-12','2-13','2-17','2-19','2-20','2-22','2-25','2-26']

def build():
 data=json.loads((COURSE/'homework-source.json').read_text());questions=data['questions']
 assert [q['number'] for q in questions]==EXPECTED,'Original question numbers must remain complete and ordered'
 payload=REF['assignment'](COURSE/'lessons/transformer-homework.js')
 course=REF['assignment'](COURSE/'manifest.js');sections={s['id']:s for s in course['sections']}
 body='<h2>第二章已做习题与详解</h2><p>保留13道题的题目、解答、图示和差异说明。公式直接阅读，图可点开放大。</p>'
 body+='<nav class="homework-navigation" aria-label="习题定位"><label for="homework-question">按题定位</label><select id="homework-question" data-homework-jump>'+''.join('<option value="'+q['number']+'">'+html.escape(q['number']+' '+q['title'])+'</option>' for q in questions)+'</select></nav><span id="page-1" class="equation-anchor" aria-label="原PDF第1页"></span>'
 for q in questions:
  number=q['number'];anchor='question-'+number
  links=[]
  for key in q['knowledge']:
   assert key in sections,(number,key)
   links.append('<a href="#course/electrical-machines/'+key+'">'+html.escape(sections[key]['title'])+'</a>')
  content='<blockquote class="homework-prompt"><h4>题目</h4>'+q['prompt']+'</blockquote>'+q['solution']
  # Each original question gets its own stable label namespace, independent of page breaks.
  content=render(content,'H.'+number.replace('-','.'))
  content=re.sub(r'(<img class="homework-diagram" src="([^"]+)"[^>]*>)',lambda m:'<a class="homework-diagram-link" href="'+m[2]+'" target="_blank" rel="noopener" aria-label="放大查看本题原图">'+m[1]+'</a>',content)
  assert 'katex-error' not in content,number
  body+='<section class="homework-problem" id="problem-'+number+'" data-homework-question="'+number+'"><h3 id="'+anchor+'">'+html.escape(number+' '+q['title'])+'</h3>'+content+'<nav class="homework-knowledge" aria-label="本题知识点">'+''.join(links)+'</nav><p><button type="button" class="secondary-button" data-open-practice data-practice-course="electrical-machines" data-practice-section="transformer-homework" data-practice-question="hw-'+number+'" aria-haspopup="dialog" aria-controls="practice-dialog">本题收藏、标记与重做</button></p></section>'
 body+='<details class="homework-source"><summary>参考</summary><p>《电机学》、课堂题稿。<a href="https://www.cmpedu.com/books/book/2027021.htm" target="_blank" rel="noopener">教材</a> · <a href="assets/practice/homework/reproduce.py" download>数值复算代码</a> · <a href="assets/practice/homework/results.json" download>复算结果</a></p></details>'
 body+='<details class="study-symbols"><summary>符号、单位与约定</summary>'+''.join('<p id="'+d['anchor']+'"><strong>'+html.escape(d['title'])+'：</strong>'+html.escape(d['description'])+'</p>' for d in data['definitions'])+'</details>'
 payload.pop('pdf',None);payload.pop('pages',None)
 payload.update(html=body,questions=[{**x,'anchor':'question-'+x['number']} for x in payload['questions']],webSource='courses/electrical-machines/homework-source.json')
 (COURSE/'lessons/transformer-homework.js').write_text('window.LN_LESSONS=window.LN_LESSONS||{};\nwindow.LN_LESSONS["electrical-machines/transformer-homework"]='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n')
 for section in course['sections']:
  if section['id']=='transformer-homework':section.update(kind='html',title='第二章已做习题 · 13题')
 (COURSE/'manifest.js').write_text('window.LN_ELECTRICAL_MACHINES='+json.dumps(course,ensure_ascii=False,separators=(',',':'))+';\n')
 bank_path=ROOT/'courses/practice/bank.json';bank=json.loads(bank_path.read_text())
 bank['questions']=[q for q in bank['questions'] if not q['id'].startswith('hw-2-')]
 for q in questions:
  numerical=q['number'] in ['2-17','2-19','2-22','2-25','2-26']
  bank['questions'].append({'id':'hw-'+q['number'],'course':'electrical-machines','sections':['transformer-homework',*q['knowledge']],'readingAnchor':'question-'+q['number'],'title':q['number']+' '+q['title'],'type':'open','prompt':q['promptText'],'steps':q['steps'],'rubric':q['rubric'],'transfer':q['transfer'],'skills':['建模','推导计算' if numerical else '解释表达','边界与反例'],'hint':q['steps'][0],'origin':'用户提供的已做习题整理稿，原PDF第'+','.join(map(str,q['pages']))+'页；网页转写、复算及完整解答可回查。多小问计算保留过程并对照要点，不自动判分。'})
 bank_path.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
 print('Rendered 13 solved exercises as HTML with bibliographic source references.')

if __name__=='__main__':build()
