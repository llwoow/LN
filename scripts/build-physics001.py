"""Render the supplied physics001 manuscript into LN; preserve its authored reasoning.

No teaching template or quantity gate: this script only renders the supplied prose,
media, scoped definitions and reviewed practice metadata. Run before build-highschool.
"""
from pathlib import Path
import html, json, re, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='courses/hs-physics/physics-001'
FOLDER=ROOT/BASE
COURSE='hs-physics'
D=json.loads((FOLDER/'content.json').read_text())
def dump(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))
def sid(i):return 'physics-001-q'+str(i).zfill(2)
def route(i,anchor=''):return '#course/'+COURSE+'/'+sid(i)+('/'+anchor if anchor else '')
def esc(value):return html.escape(str(value),quote=True)
MATH=re.compile(r'\$\$(.*?)\$\$|(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)',re.S)
# One local KaTeX batch; the manuscript is authoritative, not generated from topic names.
def tex(value):
    return re.sub(r'\\tag\{([甲乙])\}',r'\\tag{\\text{\1}}',value).replace(r'{\rm 合}',r'{\text{合}}')
def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for item in value.values():yield from strings(item)
    elif isinstance(value,list):
        for item in value:yield from strings(item)
expressions=list(dict.fromkeys((tex(m[1] or m[2]),m[1] is not None) for text in strings(D) for m in MATH.finditer(text)))
proc=subprocess.run(['node',str(ROOT/'scripts/render-math.cjs')],input=dump([{'tex':t,'display':d} for t,d in expressions]),text=True,capture_output=True)
if proc.returncode:raise ValueError(proc.stderr[-2500:])
RENDERED=dict(zip(expressions,json.loads(proc.stdout)))
from functools import lru_cache
@lru_cache(maxsize=None)
def rich(text):
    matches=list(MATH.finditer(text))
    values=iter(RENDERED[(tex(m[1] or m[2]),m[1] is not None)] for m in matches)
    def sub(m):
        rendered=next(values)
        label=next((c for c in ['甲','乙'] if r'\tag{'+c+'}' in m[0]),None)
        attr=(' data-equation-source-label="'+label+'" id="equation-'+('jia' if label=='甲' else 'yi')+'"') if label else ''
        return ('</p><div class="math display"'+attr+'>'+rendered+'</div><p>') if m[1] is not None else '<span class="math inline">'+rendered+'</span>'
    # Escape prose first; TeX is independently rendered and escaped by KaTeX.
    chunks=[];end=0
    for m in matches:
        chunks.append(esc(text[end:m.start()]).replace('\n','<br>'));chunks.append(sub(m));end=m.end()
    chunks.append(esc(text[end:]).replace('\n','<br>'))
    return re.sub(r'<p>\s*</p>','','<p>'+''.join(chunks)+'</p>')
def lst(items):return '<ul>'+''.join('<li>'+rich(s)+'</li>' for s in items)+'</ul>'
def lesson(identifier,markup,**extra):
    path=ROOT/'courses/hs-physics/lessons'/(identifier+'.js');path.parent.mkdir(exist_ok=True)
    path.write_text('window.LN_LESSONS=window.LN_LESSONS||{};window.LN_LESSONS['+dump(COURSE+'/'+identifier)+']='+dump({'html':markup,**extra})+';\n')
options={
1:['kg·m·s⁻¹','N·s·m⁻¹','kg·s⁻¹','kg·s⁻²'],
2:['火箭落入回收装置内','从匀速飞行的飞机上跳伞后','翼装飞行从悬崖跳下后','蹦极者由静止跳下后绳子被拉直之前'],
3:['小球受到F、F₁和F₂三个力的作用','重力G的两个分力F₁和F₂都存在反作用力','可以先将F₁与G合成，再与F₂、F合成求小球受到的合力','可以先将F₁与F合成，再与F₂合成求小球受到的合力'],
4:['物块的重力做功20 J','物块克服摩擦力做功20 J','外力F做功20 J','合力做功20 J'],
5:['甲对乙的压力和乙对甲的支持力是一对平衡力','乙上、下表面受到的摩擦力均为静摩擦力','甲受到3个力的作用','乙受到5个力的作用'],
6:['ρ = 3π(1+1/n)³/(GT²)','ρ = 3π(1+1/n)²/(GT²)','ρ = π(1+1/n)²/(GT²)','ρ = π(1+1/n)³/(3GT²)'],
8:['机器人对足球的冲量大小为2mv','机器人对足球的冲量大小为√2mv','机器人对足球做功为mv²/2','机器人对足球做功为mv²'],
9:['甲、乙的向心力大小之比为2:1','甲、乙的向心力大小之比为4:1','角速度为√[g/(2R)]时，甲恰好不会脱离圆盘','角速度为√(g/R)时，甲恰好不会脱离圆盘'],
10:['从抛出到落地的水平位移大小为0.1 m','从抛出到落地的竖直位移大小为0.2 m','落地时速度大小为√3 m/s','落地速度与水平方向夹角θ满足 sinθ=2√5/5'],
11:['汽车做匀加速运动','汽车的加速度越来越小','汽车加速行驶的距离大于vₘt/2','汽车加速行驶的距离小于vₘt/2'],
12:['最大高度为 Eₖ₀/[mg(1+k)]','最大高度为 Eₖ₀/[mg(1−k)]','落回地面速度大小为 √[2Eₖ₀/(m(1+k))]','落回地面速度大小为 √[2Eₖ₀(1−k)/(m(1+k))]'],
13:['动摩擦因数 μ=a₀/g','传送带速度大小为 √(3a₀x₀/2)','弹簧的劲度系数为 ma₀/x₀','物块向右运动的最大距离为 (2+√3)x₀']}
answers={1:'C',2:'D',3:'D',4:'B',5:'D',6:'A',8:'B',9:'AC',10:'BD',11:'BC',12:'AD',13:'ABD'}
# Individual misconception feedback, stable option IDs retain the original letters even when shuffled.
feedback={
1:['多出了长度m，代回kv不能得到力的单位。','与kg/s等价，但N是导出单位，未满足只用基本单位的要求。','由k=f/v及N=kg·m/s²，得到kg/s，满足题目要求。','时间指数应为−1，代回kv才有kg·m/s²。'],
2:['回收时的火箭会受发动机推力或其他回收作用，不能按只受重力处理。','相对地面具有飞机带来的水平初速度，不是由静止开始的自由落体。','空气作用不可忽略，翼装靠空气作用改变运动。','绳未拉直、初速为零且忽略空气阻力的这段可按自由落体近似；绳拉直后模型改变。'],
3:['F₁、F₂是对同一个重力的分解，不是额外相互作用。','不能把数学分量各自当成一对相互作用中的独立力。','G=F₁+F₂；把G与两个分量同时加入会重复计算重力。','用F₁、F₂替代G后，可按矢量加法结合律先合成F₁与F，再加F₂。'],
4:['上升时重力做负功，W_G=−mgh=−20 J。','斜面长4 m，摩擦力5 N，克服摩擦做功为20 J。','外力要同时克服重力和摩擦，做功40 J。','匀速使动能不变，合力总功为0。'],
5:['两力分属甲、乙，是作用反作用力；平衡力须作用于同一对象。','甲、乙相对滑动，上表面为滑动摩擦；乙与桌面间才是静摩擦。','甲受重力、乙的支持力、拉力和乙的摩擦力，共4个力。','乙受重力、甲的压力、桌面支持力、甲的摩擦力和桌面摩擦力，共5个力。'],
6:['轨道半径R(1+1/n)，由引力供向心力求M，再除以4πR³/3，得到此式。','体积与R³有关，半径比应出现三次方。','还缺地球体积4πR³/3中的系数3，且半径比不是平方。','由M=4π²r³/(GT²)再除以地球体积，系数应为3π而非π/3。'],
8:['初末动量互相垂直，不能按反向运动把大小直接相加为2mv。','冲量等于动量矢量变化；两段等长互相垂直，用勾股定理得√2mv。','始末速率相同，动能变化为0，机器人的净功为0。','改变动量方向不必改变始末动能；用动能定理可知功为0。'],
9:['同ω、同质量时F=mω²r，半径比2:1就是向心力比2:1。','平方关系属于同线速度情形F=mv²/r；本题共同的是角速度。','边缘临界满足mω²R=0.5mg，得ω=√[g/(2R)]；此时乙尚未达到上限。','此角速度使边缘所需摩擦为mg，超过最大静摩擦0.5mg，不能保持随盘不滑。'],
10:['前0.1 s的速度角给出v₀=1 m/s，总时间0.2 s，水平位移应为0.2 m。','总时间0.2 s，竖直位移gT²/2=0.2 m。','落地vₓ=1、vᵧ=2 m/s，合速率为√5 m/s。','sinθ=vᵧ/v=2/√5=2√5/5，注意这里是速度方向角。'],
11:['恒定功率不是恒定牵引力；v增大时F=P/v减小，a也减小。','阻力不变而牵引力减小，F−f=ma给出a越来越小。','高中常用v—t示意曲线先陡后缓、位于起终点连线上方，曲线下路程大于三角形面积。','图像面积应大于起终点连线下的三角形；严格恒功率起步与有限时刻到极限速度的理想化另见正文。'],
12:['上升阶段重力和阻力均向下，损失动能等于mg(1+k)h。','上升阻力也阻碍上升，不能把重力与阻力相减。','还要计算下降过程中阻力做负功，落地动能为Eₖ₀(1−k)/(1+k)。','分别对上升、下降列动能定理后得到此式；k=0时回到无阻力结果。'],
13:['x=0时弹簧原长，只有滑动摩擦沿水平，μmg=ma₀。','0到x₀的加速度图面积等于v²/2，得v带²=3a₀x₀/2。','虚线延长到2x₀才为零，故K/m=a₀/(2x₀)，不是a₀/x₀。','2x₀后再次滑动，动能定理给出再前进√3x₀；最右端瞬时v=0但a向左。']}
# Each definition is a real printed paragraph, scoped to exactly this question.
symbols={
1:[('k','k','阻力系数，定义于 f=kv；本题单位是 kg/s。')],
3:[('F','F','绳对小球的拉力；图中T表示同一拉力。'),('G','G','地球对小球的重力；F₁、F₂只是G的两个分量。')],
6:[('G','G','万有引力常量，单位 m³/(kg·s²)，不是本题物体的重力。'),('T','T','卫星绕地球一周的周期，单位 s。')],
7:[('T','T','同一根理想轻绳的张力大小，单位 N。'),('a','a','甲向滑轮、乙向下的共同加速度大小，单位 m/s²；方向各自确定。'),('m','m','甲的质量，乙按原图辨读为3m/2；单位 kg。')],
11:[('P','P','汽车发动机的牵引功率，题设保持不变，满足P=Fv，单位 W。'),('f','f','汽车所受恒定阻力的大小，单位 N。')],
12:[('k','k','空气阻力大小与重力大小的比值，0≤k<1，无量纲。')],
13:[('K','K','弹簧劲度系数，单位 N/m；用大写K以免和其他题的k混用。'),('x₀','x_0','加速度变为零区间的起点位置，单位 m；虚线延长线的零点是2x₀。')],
14:[('K','K','弹簧劲度系数，是F—l直线段的斜率，单位 N/m。')],
15:[('k','k','v²—F直线的斜率，满足k=2h/m，单位 m/kg，不是弹簧劲度系数。'),('F','F','拉力传感器测得的单股绳张力，单位 N；作用在a上的向上力也是F。'),('F₀','F_0','v²—F直线在横轴上的截距，满足F₀=mg，单位 N。'),('h','h','a从静止上升到光电门的距离，单位 m。')],
16:[('k','k','汽车受到的阻力大小与重力大小之比，k=0.5，无量纲。')],
17:[('h','h','释放点比A点高的竖直距离，单位 m，不含圆弧AB的高度差。'),('R','R','光滑圆弧轨道的半径，本题求得1.25 m。'),('F','F','小滑块经过B点时对轨道的压力大小，单位 N。')],
18:[('μ','μ','滑块与水平地面的动摩擦因数，本题为0.2，无量纲。'),('m_A','m_A','滑块A的质量，为1 kg。'),('m_B','m_B','第一、二问滑块B的质量，为3 kg；第三问另换成未知质量的C。')]
}
extra_tasks={14:'依次求弹簧原长（保留1位有效数字）、劲度系数（保留3位有效数字）及图线末端弯曲的可能原因；选主要实验方法；研究角速度时选相同或不同半径的塔轮；研究质量时选槽位，并由标尺4格与3格求质量比。',15:'依次求：①游标卡尺读出的遮光片宽度d（mm）；②给定挡光时间时的速度v（保留2位有效数字）；③F、m、g、h、v满足的关系；④用h、k表示m，用h、k、F₀表示g。'}
sections=[{'id':'physics-001','title':'试卷001：讲解与学习记录','group':'试卷001','kind':'html','supplement':'physics-001','src':'courses/hs-physics/lessons/physics-001.js'}]
glossary=[]
for q in D['questions']:
    i=q['id'];identifier=sid(i)
    sections.append({'id':identifier,'title':f'第{i}题 · '+q['title'],'group':'试卷001','kind':'html','supplement':'physics-001','keywords':q['tags'],'src':'courses/hs-physics/lessons/'+identifier+'.js'})
    markup='<section class="physics001" id="question-'+str(i)+'"><h2>第'+str(i)+'题 · '+esc(q['title'])+'</h2><p class="page-meta">'+esc(' / '.join(q['tags']))+'</p><h3>题意与条件</h3>'+rich(q['prompt'])
    if i in [3,5,6]:markup+='<ol type="A">'+''.join('<li>'+esc(t)+'</li>' for t in options[i])+'</ol>'
    if i in extra_tasks:markup+=rich(extra_tasks[i])
    markup+='<p class="source-citation">来源：《高三物理》试卷001，第'+ '、'.join(map(str,q['source']))+'页，第'+str(i)+'题；命题单位与公开原件链接待核。</p>'
    markup+='<h3>'+esc(q['foundation']['title'])+'</h3>'+rich(q['foundation']['text'])
    if q.get('figure'):
        markup+='<figure id="figure-q'+str(i)+'"><img loading="lazy" decoding="async" src="'+BASE+'/figures/'+q['figure']+'.svg" alt="第'+str(i)+'题受力、过程或图像示意"><figcaption>图 '+str(i)+'.1 · '+esc(q.get('figure_note','依据题意重绘的教学示意图。'))+'</figcaption></figure>'
    for clip in q['animations']:
        cid=clip['id'];markup+='<figure class="physics-motion" id="motion-'+cid+'"><video controls playsinline preload="none" poster="'+BASE+'/animations/posters/'+clip['poster']+'" aria-label="'+esc(clip['title'])+'"><source src="'+BASE+'/animations/video/'+clip['video']+'" type="video/mp4"><a href="'+BASE+'/animations/video/'+clip['video']+'">打开视频</a></video><figcaption>图 '+str(i)+'.'+str((2 if q.get('figure') else 1)+q['animations'].index(clip))+' · '+esc(clip['title'])+'。教学仿真；播放时长不等于画面标出的物理时间。</figcaption>'+rich(clip.get('note',''))+'<p><a href="'+BASE+'/animations/gifs/'+clip['gif']+'" download>下载 GIF</a> · <a href="'+BASE+'/animations/video/'+clip['video']+'" download>下载可暂停视频</a></p><details data-gif="'+BASE+'/animations/gifs/'+clip['gif']+'"><summary>播放 GIF 循环</summary><button type="button" class="secondary-button" data-stop-gif>停止 GIF</button><img alt="'+esc(clip['title'])+' GIF循环"></details></figure>'
    if symbols.get(i):
        for k,(title,key,desc) in enumerate(symbols[i]):
            definition='q'+str(i)+'-symbol-'+str(k)
            markup+='<p id="'+definition+'">本题符号 '+esc(title)+'：'+esc(desc)+'</p>'
            glossary.append({'id':definition,'title':title,'keys':[key],'description':desc,'section':identifier,'sections':[identifier],'match':'本题符号 '+title+'：'})
    for j,block in enumerate(q['sections']):markup+='<section id="step-'+str(j+1)+'"><h3>'+esc(block['title'])+'</h3>'+rich(block['text'])+'</section>'
    markup+='<p class="physics-answer"><strong>结论：</strong>'+esc(q['answer'])+'</p><h3>把解法连起来</h3>'+rich(q['method'])
    if str(i) in map(str,[3,7,8,9,10,11,12,13,15,16,17,18]):markup+='<section class="physics-lab" data-physics-lab="'+str(i)+'"></section>'
    markup+='<h3>相关知识与易错处</h3>'+lst(q['knowledge'])+lst(q['pitfalls'])
    markup+='<h3>换个条件再想</h3>'+rich(q['transfer'][0])+'<details><summary>对照推理</summary>'+rich(q['transfer'][1])+'</details>'
    markup+='<h3>复做与记录</h3><button class="secondary-button" data-open-practice data-practice-course="hs-physics" data-practice-section="'+identifier+'" data-practice-question="hs-physics001-'+str(i).zfill(2)+'">收藏、标错或遮住解析复做</button><div data-physics-note="'+str(i)+'"></div></section>'
    lesson(identifier,markup,physics001=i)
links=[{'from':sid(a),'to':sid(b),'label':label,'description':desc} for a,b,label,desc in [
 (4,12,'摩擦与能量','两题均把摩擦做负功写入动能定理；第12题须在上升、下降分别确定阻力方向。'),
 (7,15,'绳长约束','第7题定滑轮两端等位移；第15题含动滑轮，a的位移为b的两倍，不能照搬等加速度。'),
 (8,18,'动量变化与碰撞','第8题用动量矢量变化求冲量；第18题仅在极短弹开或两块互撞时使用系统动量守恒。'),
 (9,13,'静摩擦的上限','第9题所需向心力与最大静摩擦比较；第13题中间阶段静摩擦随弹力增加，不能始终取μmg。'),
 (16,18,'停止距离与事件','第16题由减速求停止距离；第18题每次碰撞后重新判断停止位置和下一事件。'),
 (4,17,'斜面功与圆弧','第17题斜面有摩擦、圆弧光滑，先求A点状态再推进到B，不能全程套机械能守恒。')]]
material={'id':'physics-001','group':'试卷001','description':'依据试卷001整理的逐题讲解、物理仿真与复做记录。','sections':sections,'knowledgeLinks':links,'links':[{'label':'试卷001资料与记录','href':'#course/hs-physics/physics-001'}]}
(ROOT/'courses/hs-physics/supplements.json').write_text(json.dumps({'materials':[material]},ensure_ascii=False,indent=2)+'\n')
(ROOT/'courses/hs-physics/glossary.json').write_text(json.dumps({'lazy':True,'symbolDefinitions':glossary,'terms':[]},ensure_ascii=False,indent=2)+'\n')
overview='<section class="physics001"><h2>试卷001</h2><p>第1—18题的逐题讲解与运动模型。来源：《高三物理》用户提供稿，第1—8页；命题单位与公开原件链接待核。</p>'+lst(D['meta']['notes'])+'<ol>'+''.join('<li><a href="'+route(q['id'])+'">第'+str(q['id'])+'题 · '+esc(q['title'])+'</a></li>' for q in D['questions'])+'</ol><h3>学习笔记</h3><p>可导入此前导出的physics-001记录，按更新时间保留较新笔记。笔记与练习首答记录分别保存在当前浏览器，不换算个人成绩。</p><div data-physics-notebook></div><h3>来源与教材定位</h3><p>原稿标题为“高三物理”，按卷面第1—8页与第1—18题定位。讲解、重绘图与仿真是教学整理，不是官方评分细则。原件未核实命题单位与正式出版信息，不据此认定2027官方考纲或教材全文覆盖。</p><p><a href="https://basic.smartedu.cn/tchMaterial" target="_blank" rel="noopener">国家中小学智慧教育平台：教材入口</a> · <a href="#highschool/resources">教材与来源证据</a></p></section>'
lesson('physics-001',overview,physics001=0)
# Derived practice entries link the full original reasoning; preserve all old identities and bank.version.
bankpath=ROOT/'courses/practice/bank.json';bank=json.loads(bankpath.read_text());bank['questions']=[q for q in bank['questions'] if not q['id'].startswith('hs-physics001-')]
for q in D['questions']:
    i=q['id'];typ=('single' if i<=8 else 'multi') if i in options else 'open'
    # Strip TeX for the existing plain-text practice panel, without treating the result as mathematical typesetting.
    def plain(t):
        # Accessible linear fallback from the same MathML; keep fractions grouped.
        import xml.etree.ElementTree as ET
        def linear(node):
            tag=node.tag.rsplit('}',1)[-1];children=list(node)
            if tag=='annotation':return ''
            if tag=='mfrac':return '('+linear(children[0])+')/('+linear(children[1])+')'
            if tag=='msqrt':return '√('+''.join(linear(c) for c in children)+')'
            if tag in ['msub','msup'] and len(children)==2:return linear(children[0])+('_' if tag=='msub' else '^')+'('+linear(children[1])+')'
            return (node.text or '')+''.join(linear(c)+(c.tail or '') for c in children)
        def replace(match):
            markup=RENDERED[(tex(match[1] or match[2]),match[1] is not None)]
            math=re.search(r'<math\b.*?</math>',markup,re.S)[0]
            return linear(ET.fromstring(math))
        return MATH.sub(replace,t)
    entry={'id':'hs-physics001-'+str(i).zfill(2),'course':COURSE,'sections':[sid(i)],'title':f'原卷第{i}题 · '+q['title'],'type':typ,'hintHtml':rich(q['foundation']['text']),'transferHtml':rich(q['transfer'][0]),'promptHtml':rich(q['prompt']),'stepsHtml':[rich(s['text']).replace('id="equation-', 'id="practice-equation-') for s in q['sections']],'prompt':plain(q['prompt'])+((' '+extra_tasks[i]) if i in extra_tasks else ''),'hint':q['foundation']['text'],'steps':[plain(s['text']) for s in q['sections']],'transfer':plain(q['transfer'][0]),'skills':['建模','推导计算'] if i!=2 else ['建模','边界与反例'],'origin':'用户提供高三物理试卷001，第'+str(i)+'题；原题选项稳定ID保留原字母，显示顺序打乱。本站独立推导解答，非官方评分；未有学生答卷。'}
    if typ!='open':entry.update(options=[{'id':chr(65+j),'text':t,'feedback':feedback[i][j]} for j,t in enumerate(options[i])],answer=list(answers[i]))
    else:
        entry['rubric']=[plain(q['foundation']['text']),plain(q['method']),q['answer']]
        entry['rubricHtml']=[rich(q['foundation']['text']),rich(q['method']),esc(q['answer'])]
        if i==7:entry['origin']+=' 原图分母下沿及配图有裁切，按乙质量3m/2作条件解，不自动判错。'
    bank['questions'].append(entry)
bankpath.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
print('Rendered supplied physics001 manuscript and its reviewed practice entries.')
