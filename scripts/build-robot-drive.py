"""Render manually authored robot-drive prose/TeX and metadata. No teaching synthesis.

The manuscript is authoritative authored content; this script only compiles math,
registers real reading units, and emits source-backed glossary/graph metadata.
"""
from pathlib import Path
import html,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'courses/robot-drive-engineering'
D=json.loads((BASE/'manuscript.json').read_text())
def dump(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
MATH=re.compile(r'\\\[(.*?)\\\]|\\\((.*?)\\\)',re.S)
expressions=list(dict.fromkeys((m[1] if m[1] is not None else m[2],m[1] is not None) for l in D['lessons'] for m in MATH.finditer(l['html'])))
proc=subprocess.run(['node',str(ROOT/'scripts/render-math.cjs')],input=dump([{'tex':html.unescape(t),'display':d} for t,d in expressions]),text=True,capture_output=True)
if proc.returncode:
    for l in D['lessons']:
        items=[{'tex':html.unescape(m[1] if m[1] is not None else m[2]),'display':m[1] is not None} for m in MATH.finditer(l['html'])]
        p=subprocess.run(['node',str(ROOT/'scripts/render-math.cjs')],input=dump(items),text=True,capture_output=True)
        if p.returncode:raise ValueError(l['id']+': '+p.stderr[-2300:])
    raise ValueError(proc.stderr[-2300:])
rendered=dict(zip(expressions,json.loads(proc.stdout)))
def rich(s):
    def sub(m):
        display=m[1] is not None;key=(m[1] if display else m[2],display);markup=rendered[key]
        return markup if display else '<span class="math inline">'+markup+'</span>'
    return MATH.sub(sub,s)
sources={s['id']:s for s in D['sources']}
sections=[]
(BASE/'lessons').mkdir(exist_ok=True)
for i,l in enumerate(D['lessons'],1):
    sid=l['id'];body=rich(l['html'])
    if not body.lstrip().startswith('<section'):body='<section class="article-section" id="'+sid+'">'+body+'</section>'
    refs=[sources[k] for k in l.get('sourceIds',[])];notes=''
    if refs:
        notes='<details class="rd-sources"><summary>核读资料与适用范围</summary><ul>'+''.join('<li><a href="'+html.escape(s['url'],quote=True)+'" target="_blank" rel="noopener">'+html.escape(s['title'])+'</a><p>'+html.escape(s['readScope'])+'</p></li>' for s in refs)+'</ul></details>'
    payload={'html':body+notes}
    (BASE/'lessons'/(sid+'.js')).write_text('window.LN_LESSONS=window.LN_LESSONS||{};window.LN_LESSONS['+dump(D['course']+'/'+sid)+']='+dump(payload)+';\n')
    sections.append({'id':sid,'title':l['title'],'group':l['group'],'kind':'html','src':'courses/robot-drive-engineering/lessons/'+sid+'.js','teachingIndex':i,'keywords':l.get('keywords',[])})
groups=list(dict.fromkeys(s['group'] for s in sections))
manifest={'id':D['course'],'title':D['title'],'category':'工学','topics':['电路与测量','C与DSP','功率电子','FOC','关节控制','仿真辨识','边缘AI','电赛'],
          'sections':sections,'resources':{g:{'links':[{'label':'学习主线','href':'#course/'+D['course']+'/rd-start'},{'label':'知识图谱','href':'#course/'+D['course']+'/map'}]} for g in groups},'glossary':'courses/robot-drive-engineering/glossary-index.js'}
(BASE/'manifest.js').write_text('window.LN_ROBOT_DRIVE='+dump(manifest)+';\n')
# Positions are computed by the shared fixed-layout graph; relations are authored.
notes={
 'rd-start':'从传感器、控制、功率与机械追踪系统', 'rd-circuit-foundations':'KCL、负载与有限增益反馈','rd-c-foundations':'类型、单位、指针和数据边界',
 'rd-measurement':'探头如何改变被测节点','rd-current-sense':'分流压降、增益、偏置与ADC码','rd-analog-filter':'抗混叠与ADC采集建立时间',
 'rd-embedded-c':'中断交错、事务与状态机','rd-sampling-time':'触发、数据就绪和PWM生效','rd-drive-protocol':'序号、CRC、租期与时钟域',
 'rd-mosfet-driver':'门极电荷、自举和损耗','rd-buck-power':'电感斜率与电容电荷平衡','rd-inverter':'中性点、空间矢量和死区',
 'rd-joint-model':'转矩、机械轴侧与传动惯量','rd-foc':'旋转投影、电压方程和电流PI','rd-cascade-control':'分层带宽、离散积分与限幅','rd-trajectory':'梯形轨迹和连续参考约束',
 'rd-python-data':'时间、单位、误差与统计边界','rd-ai-interface':'异步消息的新鲜度与物理契约','rd-edge-inference':'合成回归、ONNX与计时边界','rd-robot-integration':'通信QoS与实时循环分工',
 'rd-simulation':'状态方程、求解步长与对照','rd-identification':'激励、可辨识性与独立验证','rd-experiment-design':'同条件比较及失败证据','rd-contest-project':'测量、信号、电源、运动分支','rd-capstone':'单关节联合项目与验收证据'}
relations=[('rd-circuit-foundations','rd-current-sense','测量模型','KCL、负载和反馈关系用于理解分流放大与ADC接口。'),('rd-current-sense','rd-foc','电流反馈','dq控制依赖符号、增益、偏置和时间一致的电流数据。'),('rd-analog-filter','rd-sampling-time','模拟到时序','有效采集要同时满足模拟建立与硬件触发条件。'),('rd-c-foundations','rd-embedded-c','数据一致性','正确类型与边界之后，还需处理ISR交错和记录事务。'),('rd-sampling-time','rd-foc','闭环延迟','测量到PWM生效的延迟限制电流环可用带宽。'),('rd-mosfet-driver','rd-inverter','实际开关','门极、死区与保护使真实桥不同于理想矢量。'),('rd-joint-model','rd-cascade-control','机械对象','惯量、摩擦、转矩常数决定速度与位置对象。'),('rd-trajectory','rd-ai-interface','参考契约','高层目标需变成受速度和加速度约束的本地参考。'),('rd-drive-protocol','rd-ai-interface','新鲜度','传输校验、序号与观察年龄解决不同问题。'),('rd-python-data','rd-identification','证据处理','单位、校准和时钟决定拟合结果能否解释。'),('rd-simulation','rd-experiment-design','受控比较','固定植物和控制器，隔离消息策略与数值误差。'),('rd-identification','rd-edge-inference','模型外推','拟合一致与换工况预测是两种证据。'),('rd-robot-integration','rd-capstone','系统边界','上层通信不能替代DSP周期与硬件状态。'),('rd-contest-project','rd-capstone','工程交付','版本、接口和复现实验支撑样机与论文结论。')]
graph={'chapters':[{'group':g,'description':{'起点与基础':'选定轴侧、单位与可检查的数据/电路','电路、采样与测量':'从真实测量链获得可解释的反馈','嵌入式与实时系统':'让数据与控制时刻一致','功率电子与驱动硬件':'把逻辑PWM变成有边界的能量转换','电机、机械与闭环控制':'从模型走到受约束的关节运动','Python、边缘AI与机器人集成':'把异步意图接入持续运行的控制系统','仿真、辨识与实验':'保留可复算模型、独立数据和失败结果','工程项目与毕设':'按任务分支并收敛到单关节研究'}[g]} for g in groups],
'nodes':[{'section':s['id'],'title':s['title'],'note':notes[s['id']]} for s in sections],
'links':[{'from':a,'to':b,'label':lab,'description':desc} for a,b,lab,desc in relations]}
(BASE/'knowledge-map.js').write_text('window.LN_ROBOT_DRIVE_MAP='+dump(graph)+';\n')
(BASE/'glossary.json').write_text(json.dumps(D['glossary'],ensure_ascii=False,indent=2)+'\n')
print('Rendered authored robot-drive readings, math, fixed knowledge relations and glossary metadata.')
