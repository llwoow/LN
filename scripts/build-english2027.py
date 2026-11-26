"""Adapt the reviewed English manuscript to LN's reader and shared practice.

This renders existing teaching content, not a chapter/template generator.
The source directory contains no learner records or private document attachments.
"""
from pathlib import Path
import html, json, re

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'courses/hs-english/review-2027'
BASE='courses/hs-english/review-2027'
COURSE='hs-english'
M=json.loads((F/'manuscript.json').read_text())
D=json.loads((F/'practice.json').read_text())
S={s['id']:s for s in json.loads((F/'sources.json').read_text())}
E=lambda v:html.escape(str(v),quote=True)
dump=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':'))
sid=lambda code:'english-2027-'+code.lower()
route=lambda code:'#course/'+COURSE+'/'+sid(code)
qid=lambda code:'hs-english2027-'+code
groups={'01-knowledge':'复习讲义 · 知识体系','02-methods':'复习讲义 · 题型方法','03-practice':'复习讲义 · 训练与详解'}

# Concrete changes of conditions, keyed to the actual question/context.
# These are discussion prompts, not independently unseen assessment items.
transfers={
'L01':'如果最终通知改为“five, not half past four”，应记录哪个时间？解释为何原约定不是最后安排。',
'L02':'把购票结尾改为“I borrowed another phone and completed the payment online”。原先的购票地点判断还成立吗？',
'L03':'如果报告已经交完，但说话者随后说“I have a fever”，缺席原因应怎样改变？',
'L04':'若改成“Both the jacket and the bag belong to my sister”，哪些所有关系与原段不同？',
'L05':'若结尾改为“Bus twelve is cancelled too; let us walk”，最终建议是什么？',
'L06':'把原订座数改为十、取消三人：分别回答“originally”和“now”，为什么不能混用？',
'L07':'如果刚取消的三人中两人又能参加，在原八席基础上最后需几席？写清事件顺序。',
'L08':'如果开场改为六点四十且仍提前十五分钟，几点到？提前量对应哪个时间？',
'L09':'若对话明确说园子用于给食堂供菜，能否仍选“提供实践学习”？说明主要目的与附带好处的区别。',
'L10':'把too much sun改为not enough water，解释为什么不能只听见plants就沿用原答案。',
'L11':'若最后一句改成“We will sell some vegetables after the younger students visit”，区分先做什么和最终计划。',
'L12':'如果说明书已读懂，但发现缺了桥梁支架，主要困难如何变化？',
'L13':'若改成“Mr Lee works in the model shop”，职业判断应由哪个明确信息支持？',
'L14':'如果最后改为“I will keep the parts here; you take the sheet”，谁马上做什么？',
'L15':'若借相机用于家庭采访，不能只因出现interview就判断为班级项目。怎样核对项目归属？',
'L16':'若通常借期仍三天、已批准延长到一周，区分usual period与this time。',
'L17':'如果提醒改成“Keep your card; return the charger and the case”，分别列出保留物与归还物。',
'L18':'把集合地点改成北门、木棚仍为途中停留点：怎样用事件角色排除干扰？',
'L19':'若森林路线因修路关闭而改走湖边，重新写出原因—路线关系。',
'L20':'若九点出发、全程延长半小时，预计结束时间如何变化？别把出发时间当结束时间。',
'R01':'如果“十六岁以下”改为“十四岁以下”，一名正好十四岁的学生还必须由成人陪同吗？',
'R02':'若图书护理新增五元材料费，“只有一个场次收费”的结论还成立吗？',
'R03':'如果截止时间是Thursday afternoon，周四晚上发送符合要求吗？区分报名截止与活动开始。',
'R04':'若首段任务明确改为种花，而调查饮水站只是额外建议，哪项应是first asked？',
'R05':'把问卷改为先问“有什么实际困难”，它是否仍预设喜欢甜饮料是主因？',
'R06':'若学生说水站很近、排队太慢，距离造成的不便还是有效证据吗？',
'R07':'若结尾只报告标牌数量增加，没有反思过程，能否照搬原文主旨？指出缺失的证据。',
'R08':'如果改为抽签分配到两组，自愿参加阅读室的判断如何改变？',
'R09':'即使增加随机分组，教师知晓分组和测量方式的限制是否自动消失？',
'R10':'把the distinction替换为a comparison，明确它所连接的两个完整观点。',
'R11':'若作者只要求关闭阅读室，现有“认可价值但限制效果主张”的态度还成立吗？',
'R12':'若借阅计数只用于奖金、不用于排班，最初用途的问题应怎样重定位？',
'R13':'假如计数升高且独立讨论记录也改善，是否仍只能断定阅读没有变好？',
'R14':'一个指标下降时也要直接废弃它吗？分别提出需求变化与行为变化的竞争解释。',
'R15':'如果全文改为比较长短书各自用途，原标题是否仍准确覆盖中心任务？',
'S01':'把Without it改为Without these records，选项与前文应提供怎样可识别的复数指代？',
'S02':'删去前面两种错因后，These are different problems还可直接回指吗？',
'S03':'若前一步不是关掉解释而是一直看答案，This checks whether...的检验还成立吗？',
'S04':'若后文不再对照熟悉答案，而是转向笔记长度，D选项的衔接优势还在吗？',
'S05':'如果末段中心改为建立完整资料档案，“不必成为第二本教材”还适合该段吗？',
'C01':'若前文说作者临时接手、来不及准备，planned every detail是否仍有依据？',
'C02':'把动作改为“the only visitor left before we began”，事件是到达还是离开？',
'C03':'若后来来了十二位客人，empty chairs的依据会发生什么变化？',
'C04':'若作者已决定照常开始并打开录音设备，应怎样重新判断record与cancel？',
'C05':'把every silence改成every page，需要配合怎样的动作才语义相容？',
'C06':'如果作者不断打断老人，waited还能总结其动作吗？',
'C07':'若老人说明故事中的晚间聚会从未发生，shared与imaginary的依据怎样变化？',
'C08':'若情境改为会后给老人写信，writing to与listening to各需要什么事实？',
'C09':'把诊所候诊改成书店捐书，to spare前的名词可能变化吗？先补足语境再判断。',
'C10':'如果每周人数减少，nearly full还与人数趋势相符吗？',
'C11':'若外侧座位供需要付费的人使用，原先“先旁听”的作用是否仍成立？',
'C12':'把后半句改为“so every activity follows it exactly”，however还是therefore更能表达关系？',
'C13':'若作者保持安静，fill the space为何不再描述他实际采取的动作？',
'C14':'若首场来了超出预期的客人，failure的起点判断还需要哪些新证据？',
'C15':'如果段落只讨论预算而非对人的关注，important与expensive应怎样重新依上下文比较？',
'G01':'把last month改为every Monday，主语仍是our class时，open需要什么限定形式？',
'G02':'把asked us改为made us，think前是否仍有to？再把made改为被动检验。',
'G03':'改成“students, ___ helped us choose chairs”，从句不再有ideas，关系词职责如何变化？',
'G04':'改成“The books ___ (donate) last month.”，没有were placed后，空格是否改承担谓语？',
'G05':'对比one book at a time与I was at home at the time，解释两个短语的不同。',
'G06':'去掉than，改成“the ___ (popular) room in our school”，比较范围怎样改变？',
'G07':'把enjoy改为hope，后面的动词形式如何改变，为什么不只根据中文“喜欢”判断？',
'G08':'把not only去掉、so everyone feels welcome保留，还能只靠固定搭配决定连接词吗？',
'G09':'改成“We felt deeply ___ (satisfy)”，中心由抽象名词变成了什么成分？',
'G10':'把语境改为教室仍闲置且无法进入，useful/usable还表达相同结果吗？',
'W01':'若收信人改为来校参观的小学生，标签建议的解释和语体应怎样调整？',
'W02':'若第二段开头改为“After the exhibition, Tom returned alone”，第一段必须建立哪些新的时序与动机？',
'M01':'把useful改为unusual，a/an如何改变？依据是字母还是读音？',
'M02':'把two children改成one child，名词和后面的be需要怎样一致？',
'M03':'把主语改为“The reports from our class”，is还是are？找真正的中心。',
'M04':'把yesterday改为every year，visited还对应相同时间含义吗？',
'M05':'如果叙述按顺序写“We arrived and the meeting began”，为什么未必使用过去完成？',
'M06':'若强调每天清扫而非此时正在清扫，进行被动如何变为一般现在被动？',
'M07':'改成“The bridge ___ (build) in 2010.”，没有is still in use后空格职责如何变化？',
'M08':'把made us改为asked us，宾补中是否需恢复to？',
'M09':'把We were made改为The teacher made us，to如何变化？',
'M10':'比较look forward to hearing与want to hear，两个to承担相同职责吗？',
'M11':'把spoke改为gave a ___ explanation，clear是否仍需副词形式？',
'M12':'比较tastes good与tasted the soup carefully，taste的系动词和实义动词用法如何不同？',
'M13':'把visited改为stayed，village在从句内是否仍是直接宾语？',
'M14':'把stayed改为visited，原来的where为何不再合适？',
'M15':'把句意改为询问她是否需要帮助，应怎样改写完整宾语从句？',
'M16':'把从句放入“I do not know ___ he will come”，if在新的位置是否有可能成立？',
'M17':'改写为“The task was difficult, but we continued”，解释为何but前不再需要although。',
'M18':'把语境改成对现在不真实的假设，if从句与主句的时间形式要一起怎样改变？',
'M19':'分别用would/could/might join解释愿望或结果、能力或可能、较弱可能。短句怎样补充语境才能区分？',
'M20':'把主语改为“The evidence”，suggest意为表明时，是否还机械用should？',
'M21':'若改回直接问话“Where ...?”，陈述语序如何变为疑问语序？',
'M22':'比较be responsible for与depend on，中文意义不能替代哪项搭配检查？',
'M23':'改成“The attempt was a great ___”，需要形容词还是名词？',
'M24':'把陈述部分改成“You have not finished”，附加疑问的肯否怎样变化？'}

def lesson(code,markup,**extra):
    payload={'course':COURSE,'id':sid(code),'html':markup,**extra}
    (ROOT/'courses/hs-english/lessons'/f'{sid(code)}.js').write_text('window.LN_LESSONS=window.LN_LESSONS||{};window.LN_LESSONS['+dump(COURSE+'/'+sid(code))+']='+dump(payload)+';\n')

def button(q):
    return '<button class="secondary-button" data-open-practice data-practice-course="hs-english" data-practice-question="'+qid(q['id'])+'">练习 '+q['id']+'</button>'

allsections=[]
intro='<section class="english2027"><h2>英语复习讲义</h2><p>按知识体系、题型方法、训练与详解阅读。先保留初答，再核对句法或文本证据。</p><nav class="english-entry-links">'+''.join('<a href="'+route(code)+'">'+label+'</a>' for code,label in [('K03','句子结构'),('K00','知识体系'),('T00','题型方法'),('P00','训练与详解')])+'</nav><p>采用近年海南使用的新课标Ⅱ卷结构；2027具体英语安排以当年正式说明为准。教材按知识对应，不猜测个人用书页码。</p><h3>学习记录</h3><div data-english-records></div></section>'
lesson('home',intro,english2027='home')
allsections.append({'id':sid('home'),'title':'英语复习讲义','group':groups['01-knowledge'],'kind':'html','supplement':'english-2027','navigationLabel':'英语讲义','note':'讲义入口与学习记录','src':'courses/hs-english/lessons/'+sid('home')+'.js'})
definition_ids={'K03':'sentence-components','K08':'passive-voice','K09':'nonfinite-verb','K11':'relative-clause','K12':'noun-clause','K13':'adverbial-clause','K19':'reported-speech'}
reference_sections={'P13':'听力','P14':'阅读理解','P15':'七选五','P16':'完形填空','P17':'语法填空','P18':'基础迁移','P19':'应用文','P20':'读后续写'}
for chapter in M['chapters']:
    code=chapter['id'];body=chapter['html']
    body=body.replace('<h2>','<h3>').replace('</h2>','</h3>').replace('<h1>','<h2>').replace('</h1>','</h2>')
    body=body.replace('<figure>','<figure tabindex="0" aria-label="示意图，可横向阅读">')
    body=body.replace('src="figures/','src="'+BASE+'/figures/')
    def cite(m):
        s=S[m[1]];title={'S03':'英语课标','S04':'课标修订说明','S06':'2024全国Ⅱ卷','S02':'海南考试提示'}.get(m[1],s['title'])
        return '<a class="source-citation" href="'+E(s['url'])+'" target="_blank" rel="noopener">参考：'+E(title)+'</a>'
    body=re.sub(r'<a href="#source-(S\d\d)">\[S\d\d\]</a>',cite,body)
    if code=='K00':
        body=re.sub(r'<p>(?:这张表是|2025修订版|已保留的).*?</p>','',body)
        body+='<p>按近年结构学习；2027安排以当年海南正式说明为准。教材版本未确认时，按知识点对应，不将不同版本的Unit号强行合并。</p><p><a class="source-citation" href="'+E(S['S02']['url'])+'" target="_blank" rel="noopener">参考：海南考试提示</a> · <a class="source-citation" href="'+E(S['S03']['url'])+'" target="_blank" rel="noopener">参考：英语课标</a></p>'
    if code=='T09':
        body='<h2>T09 回查与复做</h2><p>按本次失误回查知识与例句，再换材料复做。看过分析后的正确答案保留为复做记录。</p><ul>'+''.join('<li><a href="'+route(c)+'">'+t+'</a></li>' for c,t in [('K21','知识与题型索引'),('T08','复盘与评分边界'),('P21','复盘记录')])+'</ul>'
    if code=='K21':body=re.sub(r'<p>来源编号与访问范围.*?</p>','',body)
    body=body.replace('公开转载未附本套可核验的官方评分稿，本段结论是独立句法分析，不冒充官方解析。','')
    body=body.replace('此处按语法填空段落中的相邻两空定位，不沿用转载整理版重新编排的全卷题号','这里分析段落中的相邻两空')
    body=body.replace('题面整理版的全卷题号与原版可能不同，按年份、卷型和写作第一节定位，不冒用整理版号码。','')
    body=body.replace('R09选A，因为把没有随机分组误读成已有随机分组','R08选A，因为把没有随机分组误读成已有随机分组')
    if code in definition_ids:body=body.replace('<p>','<p id="'+definition_ids[code]+'">',1)
    if code in ['K06','K09','T02','T03','T07']:body+='<section data-english-lab="'+code+'"></section>'
    if code.startswith('P'):
        relevant=[]
        if code=='P01':relevant=[q for q in D['questions'] if q['section']=='听力']
        elif 'P02'<=code<='P10':
            passage={'P02':'RA','P03':'RB','P04':'RC','P05':'RD','P06':'S','P07':'C','P08':'G','P09':'W1','P10':'W2'}[code]
            relevant=[q for q in D['questions'] if q.get('passage')==passage]
        elif code=='P11':relevant=[q for q in D['questions'] if q['section']=='基础迁移']
        if relevant:body='<h2>'+E(chapter['title'])+'</h2><p>在练习中保留初答与理由，提交后对照分析。题目材料随题提供。</p><div class="english-question-links">'+''.join(button(q) for q in relevant)+'</div>'
        if code=='P13':
            for clip in D['clips']:
                body=body.replace('<h3>'+clip['id']+' 原文</h3>','<h3>'+clip['id']+' 听力</h3><p>合成练习音。</p><audio controls preload="none" src="'+BASE+'/'+clip['audio']+'"></audio>')
        # Worked answers and knowledge IDs link into the same LN course.
        body=re.sub(r'(?<![\w/-])([KT]\d\d)(?!\w)',lambda m:'<a href="'+route(m[1])+'">'+m[1]+'</a>' if m[1] in {c['id'] for c in M['chapters']} else m[1],body)
    if code=='P12':
        rows=[]
        for q in D['questions']:
            if q['section']=='基础迁移' or q['type']=='open':continue
            answers=' / '.join(o['text'] for o in q.get('options',[]) if o['id'] in q.get('answer',[])) if q.get('options') else ' / '.join(q['answer'])
            rows.append('<tr><td>'+q['id']+'</td><td>'+E(answers)+'</td></tr>')
        body='<h2>P12 答案总表</h2><p>练习中的选项顺序会变化，按内容核对答案。查看本表后，对应题目的后续作答记为参考后作答。</p><div class="table-wrap"><table><tr><th>题号</th><th>参考内容</th></tr>'+''.join(rows)+'</table></div>'
    if code in ['P13','P14','P15','P16']:
        for q in D['questions']:
            if not q.get('options'):continue
            answer_text=' / '.join(o['text'] for o in q['options'] if o['id'] in q['answer'])
            body=body.replace('<h3>'+q['id']+' · 参考 '+ ' / '.join(q['answer'])+'</h3>','<h3>'+q['id']+' · '+E(answer_text)+'</h3>')
        body=re.sub(r'(<li>)[A-G] ',r'\1',body)
    references=[]
    if code=='P12':references=[qid(q['id']) for q in D['questions'] if q['type']!='open' and q['section']!='基础迁移']
    elif code in reference_sections:references=[qid(q['id']) for q in D['questions'] if q['section']==reference_sections[code]]
    lesson(code,'<section class="english2027">'+body+'</section>',english2027=code,referenceQuestions=references)
    allsections.append({'id':sid(code),'title':('T09 回查与复做' if code=='T09' else chapter['title']),'group':groups[chapter['book']],'kind':'html','supplement':'english-2027','note':{'K':'知识与例句','T':'题型方法','P':'训练与详解'}[code[0]],'keywords':[code,chapter['title']],'src':'courses/hs-english/lessons/'+sid(code)+'.js'})

links=[{'from':sid(a),'to':sid(b),'label':label,'description':description} for a,b,label,description in [
 ('K03','K09','成分决定职责','K09先判断空格成分及逻辑主语，再区分非谓语形式；K03给出成分关系。'),
 ('K09','T05','谓语与修饰语','T05对照同一句里的inspire与build，使用K09的职责判断。'),
 ('K11','T05','缺失成分','T05的changes that/which从句运用K11先找缺失宾语的分析。'),
 ('K16','T02','证据范围','两节均区分部分与全体、观察与因果，要求选项与文本范围一致。'),
 ('K13','T03','连接与指代','七选五同时检验连接关系、指代和段落任务。'),
 ('K07','T07','叙述参照','续写要保持事件的先后关系与叙述时间，不只堆情绪描写。')]]
materials=[]
for i,(book,group) in enumerate(groups.items()):
    materials.append({'id':'english-2027-'+str(i+1),'group':group,'label':'英语讲义','description':['词汇、句法、语篇与语音','七类题型的判断方法','训练与参考详解'][i],'sections':[s for s in allsections if s['group']==group],'knowledgeLinks':links if i==0 else [],'links':[{'label':'讲义总览','href':route('home')},{'label':'练习','href':'#practice/hs-english'}]})
(ROOT/'courses/hs-english/supplements.json').write_text(json.dumps({'materials':materials},ensure_ascii=False,indent=2)+'\n')

terms=[]
for title,english,code,anchor,description in [
 ('主语','subject','K03','sentence-components','说明句子正在谈论的对象。'),('谓语','predicate','K03','sentence-components','表达主语的动作或状态。'),
 ('宾语','object','K03','sentence-components','通常表示动作指向的对象。'),('表语','subject complement','K03','sentence-components','在系动词后说明主语的性质、状态或身份。'),
 ('补语','complement','K03','sentence-components','补充说明主语或宾语。'),('定语','attribute','K03','sentence-components','修饰名词。'),('状语','adverbial','K03','sentence-components','说明时间、地点、原因、方式等关系。'),
 ('被动语态','passive voice','K08','passive-voice','以受事为叙述中心，常用be加过去分词；时态与一致由助动词系统体现。'),
 ('非谓语','non-finite verb','K09','nonfinite-verb','自身不承担完整的时态、人称功能；按句法角色、逻辑主语和动作关系选形式。'),
 ('定语从句','relative clause','K11','relative-clause','围绕先行词增加说明；关系词要看它在从句中所承担的成分。'),
 ('名词性从句','noun clause','K12','noun-clause','整体作主语、宾语、表语或同位语的从句。'),
 ('状语从句','adverbial clause','K13','adverbial-clause','表达时间、原因、条件、让步、目的、结果或比较关系的从句。'),
 ('间接引语','reported speech','K19','reported-speech','将话语嵌入新的叙述，结合参照检查人称、时间、地点和语序。')]:
    terms.append({'id':anchor+'-'+str(len(terms)),'aliases':[title,english],'title':title,'english':english,'description':description,'section':sid(code),'sections':[s['id'] for s in allsections],'match':{'K03':'主语说明谈论的对象','K08':'被动语态把受事','K09':'非谓语形式本身','K11':'定语从句围绕先行词','K12':'名词性从句可以','K13':'状语从句表达时间','K19':'直接引语保留'}[code]})
(ROOT/'courses/hs-english/glossary.json').write_text(json.dumps({'lazy':True,'symbolDefinitions':[],'terms':terms},ensure_ascii=False,indent=2)+'\n')

# Register original teaching entries in the existing bank, without changing its
# version or any established question/option identities.
bankpath=ROOT/'courses/practice/bank.json';bank=json.loads(bankpath.read_text())
bank['questions']=[q for q in bank['questions'] if q.get('collection')!='english-2027']
for q in D['questions']:
    passage=D['passages'].get(q.get('passage'))
    prompt=('<div class="english-passage"><h3>'+E(passage['title'])+'</h3>'+''.join('<p>'+E(p).replace('\n','<br>')+'</p>' for p in passage['text'].split('\n\n'))+'</div>') if passage else ''
    clip=next((c for c in D['clips'] if c['id']==q.get('passage')),None)
    if clip:prompt='<p>合成练习音。</p><audio controls preload="none" src="'+BASE+'/'+clip['audio']+'"></audio><details data-practice-transcript><summary>查看本段原文</summary>'+prompt+'</details>'
    correct='；'.join(o['feedback'] for o in q.get('options',[]) if o['id'] in q.get('answer',[]))
    entry={'id':qid(q['id']),'sourceQuestion':q['id'],'collection':'english-2027','passage':q.get('passage'),'course':COURSE,'sections':[sid(k) for k in q['knowledge']],'title':q['id']+' · '+q['prompt'],'type':q['type'],'prompt':q['prompt'],'promptHtml':prompt+'<p>'+E(q['prompt'])+'</p>','steps':[q.get('analysis') or correct],'hint':q.get('hint') or {'听力':'区分原安排、变化与最终决定，留意题目问的是哪个事件。','阅读理解':'找到同一对象与条件下的文本证据，检查选项的范围。','七选五':'把句子放回整段，核对指代、逻辑与信息推进。','完形填空':'跟随人物目标、行动和改变，检查前后文的约束。','语法填空':'先判断空格成分及分句范围，再决定形式。','基础迁移':'找主语、谓语与缺失成分，说明形式的依据。','应用文':'先确定读者、交际目的和题干要点，再写具体信息。','读后续写':'列出已知事实、冲突与两个段首要求，补足中间因果。'}[q['section']],'transfer':transfers[q['id']],'skills':['解释表达','因果与证据'] if q['section'] in ['阅读理解','七选五','完形填空','读后续写'] else ['解释表达','迁移设计'],'origin':'教学练习','scoreStructure':q['score']}
    if q.get('options'):entry.update(options=q['options'],answer=q['answer'])
    elif q['type']=='fill':entry['answer']=q['answer']
    else:
        entry['rubric']=q['rubric'];entry['stepsHtml']=['<div class="english-model">'+E(q['model']).replace('\n','<br>')+'</div><p>'+E(q['analysis'])+'</p>']
    bank['questions'].append(entry)
bankpath.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
print('Adapted English manuscript to LN chapters, scoped terminology and native practice.')
