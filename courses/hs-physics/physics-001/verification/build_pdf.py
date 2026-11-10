from pathlib import Path
import json,re,hashlib,subprocess
R=Path(__file__).resolve().parent.parent;D=json.loads((R/'content.json').read_text());out=R/'verification/build';out.mkdir(exist_ok=True)
def esc(t):
 return ''.join({'&':r'\&','%':r'\%','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','\\':r'\textbackslash{}'}.get(c,c) for c in t)
def inline(s):
 parts=re.split(r'(\$[^$]+\$)',s)
 return ''.join(p if p.startswith('$') else esc(p) for p in parts)
def block(s):
 a=[]
 for line in s.split('\n'):
  line=line.strip()
  if not line:continue
  if line.startswith('$$') and line.endswith('$$'):a.append('\\begin{equation*}\n'+line[2:-2]+'\n\\end{equation*}\n')
  else:a.append(inline(line)+'\n\n')
 return ''.join(a)
def items(xs):return '\\begin{itemize}\n'+''.join('\\item '+inline(x)+'\n' for x in xs)+'\\end{itemize}\n'
tex=r'''\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\setmainfont{Noto Serif CJK SC}[BoldFont={Noto Sans CJK SC Bold}]
\setsansfont{Noto Sans CJK SC}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip=0pt plus 1pt
\usepackage[margin=22mm,top=22mm,bottom=23mm,headheight=16pt]{geometry}
\usepackage{amsmath,amssymb,graphicx,xcolor,booktabs,longtable,array,enumitem,needspace,titlesec,fancyhdr,lastpage}
\usepackage[unicode,colorlinks=true,linkcolor=blueblack,urlcolor=blueblack,bookmarksopen=true,pdftitle={物理001：逐题精讲与方法图谱},pdfauthor={高考复习项目}]{hyperref}
\definecolor{blueblack}{HTML}{205B82}
\definecolor{teal}{HTML}{107B79}
\definecolor{muted}{HTML}{60747E}
\definecolor{amber}{HTML}{9A6324}
\usepackage[most]{tcolorbox}
\newtcolorbox{notebox}[1]{colback=blueblack!3,colframe=blueblack!25,boxrule=.4pt,arc=0mm,left=3mm,right=3mm,top=2mm,bottom=2mm,title={#1},coltitle=blueblack,fonttitle=\sffamily\bfseries,colbacktitle=blueblack!6,breakable}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\widowpenalty=10000\clubpenalty=10000\displaywidowpenalty=10000
\linespread{1.28}
\setlist[itemize]{leftmargin=1.5em,itemsep=3pt,topsep=4pt,parsep=1pt}
\setlength{\emergencystretch}{3em}
\titleformat{\section}{\Large\sffamily\bfseries\color{blueblack}}{}{0pt}{}
\titleformat{\subsection}{\normalsize\sffamily\bfseries\color{teal}}{}{0pt}{}
\titlespacing*{\section}{0pt}{0pt}{12pt}
\titlespacing*{\subsection}{0pt}{12pt}{4pt}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\sffamily\color{muted}物理001 / 逐题精讲}
\fancyhead[R]{\small\sffamily\color{muted}2027届 · 海南复习项目}
\fancyfoot[L]{\scriptsize\color{muted}运动图解版 1.2 · 2026-11-07}
\fancyfoot[R]{\small\thepage\ / \pageref{LastPage}}
\renewcommand{\headrulewidth}{.3pt}
\renewcommand{\contentsname}{目录}
\renewcommand{\arraystretch}{1.35}
\begin{document}
\thispagestyle{empty}
\vspace*{20mm}
{\sffamily\color{teal}\large 海南 · 2027届高考复习}\par
\vspace{10mm}
{\sffamily\bfseries\fontsize{32}{44}\selectfont 物理001\\逐题精讲与方法图谱}\par
\vspace{7mm}
{\large 从受力图、矢量与图像，走到多过程临界问题}\par
\vspace{15mm}
\noindent\rule{\textwidth}{.6pt}
\vspace{5mm}
{\large 18题完整知识讲解\quad /\quad 16幅重绘辅助图}\par
{\large 严谨步骤 · 20段运动动画配套 · 方法迁移 · 关键帧回看}\par
\vspace{10mm}
\begin{notebox}{版本说明}
本书以用户提供的8张高三物理试卷图片为依据，按原题顺序独立推导。它是学习讲解稿，不是官方答案或官方评分细则。第7题保留原图裁切与文字辨读说明；第11题标明模型边界。未收到本套学生作答，故不据此虚拟批改或认定个人错因。
\end{notebox}
\vfill
{\color{muted}内容版本 1.2\quad 2026年11月7日\\配套网页与本PDF使用同一份逐题内容数据。}\par
\clearpage
\section*{使用说明与证据边界}\addcontentsline{toc}{section}{使用说明与证据边界}
建议先独立做题，再依次阅读“思路入口—严谨推导—方法总结—关联知识—易错点—迁移练习”。每一题都从研究对象、方向和适用条件开始，尽量避免只给公式与答案。
\begin{notebox}{怎样阅读不同难度的内容}
基础阶段：优先读第1—6、8、10、12、16题，训练单位、受力、位移与速度的区分。\\
综合阶段：读第9、11、13、17、18题，重点检查临界条件、分段状态与守恒边界。\\
实验阶段：第14、15题独立成组，训练读数、图像斜率截距、控制变量与误差分析。\\
本版每题先设“先补这一点基础”，再给一个短问题自查。学生解法以高中课内知识为主，不用微积分；模型提醒只说明适用条件，不作为额外考试要求。
\end{notebox}
\subsection*{已核验与未能确认的事项}
'''+items(D['meta']['notes'])+r'''
\subsection*{图与公式的使用约定}
普通PDF不能直接播放GIF；本版在对应题目插入关键帧，点击链接可到网页播放。离线包内有GIF原件与同源视频。动画暂停时物理时钟也暂停；第2、9、14题的场景切换均按独立示意处理。

图为依据可见条件重新绘制的教学图，除坐标图外不保证长度按实际比例。实线表示当前模型中的实际过程，虚线表示分量、参考线、外推或渐近线，并在图题中解释。力图中的箭头用于说明方向；未给定数值的图不能拿箭头像素长度进行测量。

所有速度、加速度、位移在计算题中使用同一坐标下的符号；“速率”“大小”与有符号分量分开。每个守恒关系都要检查对象与时间区间。
\subsection*{区域与教材定位}
本资料服务于海南、2027届、物理化学生物选科的复习项目。用户提供的试卷未显示足以确认命题地区与官方性质的信息，因此不称其为海南官方试题。本版按高中物理知识模块建立索引；具体学校教材版本与2027年正式考试文件仍需另据权威来源核验。
\clearpage
\section*{答案速查与重点核对}\addcontentsline{toc}{section}{答案速查与重点核对}
\begin{longtable}{p{12mm}p{35mm}p{105mm}}
\toprule 题号 & 结论 & 最关键的入口\\\midrule\endhead
'''
keys=[('1','C','基本单位而非导出单位'),('2','D','初速度为零且只受重力'),('3','D','重力与它的全部分力不能重复计算'),('4','B','重力功−20J；摩擦功−20J；外力功40J'),('5','D','甲4个真实力，乙5个真实力'),('6','A',r'$\rho=3\pi(1+1/n)^3/(GT^2)$'),('7','C（辨读）',r'乙按 $3m/2$ 辨读，分别列式得 $T=3mg/5$；保留原图裁切说明'),('8','B',r'$J=\sqrt2mv$；净功为0'),('9','AC','共同角速度；需求与最大静摩擦比较'),('10','BD',r'$v_0=1\,\mathrm{m/s}$；总时间0.2s'),('11','BC*','恒功率使加速度递减；末速表述有理想化'),('12','AD','上升与下降阻力方向相反，分别用动能定理'),('13','ABD',r'匀速段 $x_0\sim2x_0$；$K=ma_0/(2x_0)$'),('14','见逐空解答',r'$4;\ 1.00\times10^2$；线性范围失效；B；不同；A、C；4:3'),('15','见逐空解答',r'$2.40\,\mathrm{mm};\ 1.0\,\mathrm{m/s};\ m=2h/k;\ g=kF_0/(2h)$'),('16',r'$5\,\mathrm{m/s^2};\ 40\,\mathrm m$','从开始刹车计时，不含反应距离'),('17',r'$\mu=\sqrt3/2$','质量0.40kg；圆弧半径1.25m'),('18','6m/s、2m/s',r'第一问间距1.50m；最终1.25m；第三问质量2.10kg')]
for a,b,c in keys:tex+=inline(a)+' & '+inline(b)+' & '+inline(c)+r'\\'+'\n'
tex+=r'''\bottomrule\end{longtable}
{\small * 第11题按高中常规模型选择BC。严格恒功率、恒阻力模型中，终极速度仅能渐近接近；详见该题的模型提醒。第7题按可辨质量分数3m/2讲解，原图裁切说明见该题。}
\clearpage
\begingroup\small\linespread{1.05}\selectfont\setlength{\parskip}{0pt}
\tableofcontents\endgroup
\clearpage
'''
for q in D['questions']:
 tex+=('\\clearpage\n' if q['id'] in [1,7,11] or q['id']>=13 else '\\par\\vspace{7mm}\\Needspace{15\\baselineskip}\n')+'\\section*{第'+str(q['id'])+'题　'+esc(q['title'])+'}\n'
 tex+='\\addcontentsline{toc}{section}{第'+str(q['id'])+'题　'+esc(q['title'])+'}\n'
 tex+='{\\small\\sffamily\\color{muted}'+esc(' · '.join(q['tags']))+'\\quad 原图页'+esc('、'.join(map(str,q['source'])))+'\\quad '+esc(q['status'])+'}\\par\n'
 tex+='\\begin{notebox}{核心题意与作答结论}\n'+block(q['prompt'])+'\\textbf{结论：}'+inline(q['answer'])+'\n\\end{notebox}\n'
 f=q['foundation']
 tex+='\\begin{notebox}{先补这一点基础：'+esc(f['title'])+'}\n'+block(f['text'])+'\\textbf{先想一问：}'+block(f['ask'])+'\\textbf{核对：}'+block(f['answer'])+'\\end{notebox}\n'
 tex+='\\subsection*{思路入口}\n'+inline(q['method'])+'\n\n'
 if q['figure']:
  tex+='\\begin{center}\n\\includegraphics[width=.98\\textwidth]{../../figures/'+q['figure']+'.pdf}\n\\par{\\footnotesize\\color{muted}图'+str(q['id'])+'　'+esc(q['title'])+'（教学重绘）。'+esc(q.get('figure_note','详见正文条件说明。'))+'}\n\\end{center}\n'
 for motion in q.get('animations',[]):
  for plate_index,plate in enumerate(motion['plates']):
   tex+='\\clearpage\n\\subsection*{第'+str(q['id'])+'题 · 运动过程：'+esc(motion['title'])+'}\n'
   tex+='{\\small '+esc(motion['note'])+'}\\par\n'
   tex+='\\begin{center}\n\\includegraphics[width=.95\\textwidth,height=.76\\textheight,keepaspectratio]{../../animations/plates/'+plate+'}\n\\end{center}\n'
   url=motion['url'].replace('#',r'\#')
   tex+='\\begin{notebox}{观看动态过程}\n本页是静态关键帧，常规PDF不会播放GIF。\\par\n\\href{'+url+'}{点击播放 '+esc(motion['id'].upper())+' 动画（网页版，可暂停）}\\quad 离线文件：'+esc(motion['id'])+'.gif\n\\end{notebox}\n'
 if q.get('animations'):tex+='\\clearpage\n'
 for s in q['sections']:tex+='\\Needspace{5\\baselineskip}\n\\subsection*{'+esc(s['title'])+'}\n'+block(s['text'])
 tex+='\\Needspace{6\\baselineskip}\n\\subsection*{方法总结}\n'+block(q['method'])
 tex+='\\subsection*{关联知识与适用边界}\n'+items(q['knowledge'])
 tex+='\\subsection*{常见错误及纠正}\n'+items(q['pitfalls'])
 tex+='\\begin{notebox}{迁移练习与核对}\n'+block(q['transfer'][0])+'\\textbf{核对：}'+block(q['transfer'][1])+'\\end{notebox}\n'
tex+=r'''\clearpage
\section*{附录A　知识模块与题号索引}\addcontentsline{toc}{section}{附录A　知识模块与题号索引}
知识点按物理关系组织，便于把一题的入口迁移到另一题。此表不代替已经确认版本的教材目录。
\begin{longtable}{p{30mm}p{35mm}p{85mm}}
\toprule 模块 & 对应题号 & 需要真正掌握的关系\\\midrule\endhead
单位与模型 & 1、2、7、11 & 基本单位；参考系；原始条件；模型适用区间\\
矢量与受力 & 3、5、8 & 原力与分力；隔离对象；作用反作用；矢量差\\
摩擦与约束 & 4、5、7、9、13 & 相对运动；静摩擦范围；绳长约束；状态切换\\
直线运动 & 2、11、16、18 & 匀变速适用条件；速度图面积；事件后重新列式\\
抛体运动 & 2、10 & 分运动同时间；速度角与位移角不同\\
圆周与天体 & 3、6、9、14、17 & 向心合力；半径与高度；同角速度；临界摩擦\\
功、能量、功率 & 4、8、11、12、13、16、17、18 & 功的正负；动能定理；守恒边界；供能与耗散\\
动量与碰撞 & 8、18 & 冲量矢量；短时外力冲量；一维弹性碰撞\\
实验与数据 & 14、15、17 & 读数、单位、有效数字、拟合、斜率与截距\\
图像与临界 & 9、11、13、15、17、18 & 先推函数再对系数；区分实线虚线；证明最小值位置\\
\bottomrule\end{longtable}
\subsection*{五条贯穿全卷的检查规则}
\begin{enumerate}[leftmargin=1.5em]
\item 每列一个方程，先交代研究对象、阶段和正方向。
\item 式子左右量纲一致，答案保留单位，符号与“大小”分开。
\item 使用守恒关系前，明确外力冲量、非保守力做功等条件。
\item 发生停止、接触改变、绳绷紧、相对速度变零或碰撞时，检查模型是否切换。
\item 解出数值后代回原条件，检查事件顺序与后续过程。
\end{enumerate}
\clearpage
\section*{附录B　自测与薄弱点记录模板}\addcontentsline{toc}{section}{附录B　自测与薄弱点记录模板}
目前没有本套学生作答，因此下表是待填写模板，不是已经诊断的薄弱点。历史截图中的物理14/100只能作为该次考试的背景信息，不能据此认定本套的每题对错。
\begin{longtable}{p{10mm}p{29mm}p{34mm}p{29mm}p{35mm}}
\toprule 题号 & 自评/实际得分 & 首个卡住的步骤 & 错因证据 & 复做日期与结果\\\midrule\endhead
'''
for i in range(1,19):tex+=str(i)+r' & & & & \\[0.5mm]'+'\n'
tex+=r'''\bottomrule\end{longtable}
错因可记录为：概念不清、模型识别错误、对象或方向错误、条件漏读、图像读错、代数运算、单位或有效数字、事件遗漏。必须写出作答中的具体证据，不能只填“粗心”。第7题原图裁切与辨读情况单独记录，不作为学生的知识错误。

网页可以保存每题的自评与文字笔记，并导出记录。记录只保存在当前浏览器本地，不会自动同步，也不会上传老师或其他人。自评不是考试分数。
\clearpage
\section*{附录C　原始资料、核验与版本记录}\addcontentsline{toc}{section}{附录C　原始资料、核验与版本记录}
\subsection*{原图顺序与题目衔接}
\begin{longtable}{p{12mm}p{35mm}p{58mm}p{40mm}}
\toprule 页序 & 原始文件 & 内容与接续 & SHA-256前12位\\\midrule\endhead
'''
inputs=R/'originals'
desc=['第1、2题；第3题题干','第3题选项；第4—6题','第7—9题；第10题题干','第10题选项；第11—13题','第14题；第15题题干','第15题接续；第16题','第17题','第18题']
for i,p in enumerate(sorted(inputs.glob('*.jpg'))):tex+=str(i+1)+' & '+esc(p.name)+' & '+esc(desc[i])+' & {\\ttfamily\\scriptsize '+hashlib.sha256(p.read_bytes()).hexdigest()[:12]+'}'+r'\\'+'\n'
tex+=r'''\bottomrule\end{longtable}
原图8张已经覆盖题号1—18的连贯顺序；“查看器显示12张”不等于这份题目正文有12页。第7题仍有局部遮挡；第14、16、18题存在边缘裁切，但后者核心求解条件可读。原图没有被改写为“完整官方原卷”。
\subsection*{解答核验重点}
单位与量纲复核：第1、6、15题。\\
受力与能量双重核对：第4、16题。\\
分段动力学与图像一致性：第11、13题。\\
图像给定点代回：第17题。\\
动量、弹性碰撞、事件顺序和终态边界：第18题。\\
原图质量分数辨读与标准连接体解法复核：第7题。
\subsection*{版本与更新规则}
1.2版：增加20段运动动画、逐题关键帧与播放链接，并保留18题基础衔接与自查问答，第7题改用具体质量分步列式；第11、13题去掉微积分表达，第18题展开质量计算的代数步骤。附16幅辅助图和18道迁移练习。配套网页从同一content.json生成；新的清晰原图、官方答案或学生答卷到来后，应保留旧版，再更新相应题目、评分与错因记录。

本书未使用未经允许的其他会话内容。当前历史会话检索接口要求额外访问权限，未读取到用户其他项目的教学要求；本版依据此次明确提出的要求制作。
\end{document}
'''
tex=re.sub(r'p\{([0-9]+mm)\}',lambda m:r'>{\raggedright\arraybackslash}p{'+m[1]+'}',tex)
tex=tex.replace(r'\addcontentsline',r'\phantomsection\addcontentsline')
(out/'physics001.tex').write_text(tex)
for i in range(3):
 r=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','physics001.tex'],cwd=out,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (out/f'compile-{i+1}.log').write_text(r.stdout)
 if r.returncode:print(r.stdout[-4000:]);raise SystemExit(r.returncode)
print(r.stdout[-700:])
