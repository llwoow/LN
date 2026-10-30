# LN

按学科分类的轻量学习网页。

教学以理解系统、独立推导和迁移为目标，统一标准见 [TEACHING.md](TEACHING.md)。每节先呈现问题、模型或证据、推理、完整分步例子、边界、检验和迁移；原讲义、原计算和练习后置保留。逐节审查记录见 [TEACHING-REVIEW.md](TEACHING-REVIEW.md)。

直接打开 `index.html`，或运行：

```sh
python -m http.server 4173 --bind 127.0.0.1
```

浏览器访问 http://127.0.0.1:4173 。

- 可折叠侧栏、课程搜索、学科筛选、收藏。
- 每门课程默认进入知识图谱：节点结构固定，支持拖动平移、缩放、章节筛选与搜索，点击节点进入正文；实线表示阅读顺序，虚线表示附说明的知识联系。
- 教材与论文式单栏阅读：公式编号靠右，图表统一编号；公式、图表引用可点击跳转，再点击目标编号或“返回引用处”回到原阅读位置。
- 物理符号、重要缩写与英文术语支持释义小窗：查看原定义、单位或英文全称；跳转原文后可返回阅读位置。
- 五套配色，日间 / 夜间 / 跟随系统。
- 原生 HTML、CSS、JavaScript，无需安装依赖。
- 已整合电机学：磁路、变压器、直流电机、第二章作业及直流电机 3D 交互模型。不含音频。
- 课程正文、公式字体和模型按需加载；保留原讲义 PDF。仅展示已有真实材料的课程。

`/` 或 `Ctrl/Cmd + K` 搜索，`Esc` 关闭设置或手机侧栏。

界面规范见 `DESIGN.md`。外观、收藏与侧栏状态保存在当前浏览器；本地 HTTP 预览的存储行为通常更稳定。

材料核查及转换说明见 `courses/electrical-machines/REVIEW.md`。检查命令：

```sh
python -m unittest discover -s tests -v
node tests/motor-winding.test.cjs
node tests/knowledge-map.test.cjs
python scripts/build-reference-index.py --check
python scripts/build-glossary.py --check
```

网页引用与编号布局的浏览器回归检查（需已安装 Playwright 和 Chromium，先启动上面的本地 HTTP 服务）：

```sh
python tests/publication.browser.py
python tests/glossary.browser.py
python tests/glossary-coverage.browser.py
```

定义索引配置见 `courses/electrical-machines/glossary.json`。新增材料时指定原符号表或真实定义段落，核对术语释义，再运行 `python scripts/build-glossary.py`；同名符号按材料分组解析。

局部符号或术语可用 `sections` 限定适用阅读单元；范围内定义优先，未覆盖的小节不套用，避免将空载量与零序量等混淆。

高中入口为 `#highschool`，九科课程与专业课程分开。结构底本是所附海南2027届核验报告（50册主索引、235节点），候选版本与未确认事项见“教材与来源”；讲解与例题为原创整理，参考资源保留实际核验范围。

高中内容保存在 `courses/hs-*/content.json`，节点和册次底本为同目录的 `source-index.json`。修改后运行：

```sh
python scripts/build-highschool.py
python scripts/build-reference-index.py
python scripts/build-glossary.py
python -m unittest discover -s tests -v
python tests/highschool.browser.py
```

数学公式以本地KaTeX 0.16.11预渲染（MIT许可见 `scripts/vendor/KATEX-LICENSE`）。高中释义按科加载，原首页无需加载全部九科定义；静态打包会从已提交的内容重新生成。

学习主线在 `courses/highschool/learning-paths.json`，可复用的术语别名在 `shared-terms.json`；局部符号继续按阅读单元消歧。典型题使用节点的 `workedExamples` 字段，构建器统一生成分步解析、变式答案及连续公式编号。

新增内容的针对性检查：`node tests/definition-reuse.test.cjs`；`python tests/highschool-deepening.browser.py` 检查17条主线、十六道分步题、跨节原定义返回与窄屏展开排版，并回归斜拉力符号消歧、交变电流定义及GIS释义与返回。

主教学正文保存在每科的 `understanding.json`，包含七个具体教学字段与逐节 `review`，不得以通用提示填充。电机学运行 `python scripts/build-electrical-understanding.py` 后再重建引用和释义；原材料保留，新增公式以 `U.` 独立编号。`python tests/learning.browser.py` 在桌面和390／320px检查全部274个阅读单元，包含原PDF与3D模型的原创讲解。

静态发布会运行 `scripts/check-teaching.py`，缺少主讲解或逐节审查的已注册课程不能打包。`definition-anchors.json` 保留已发布释义链接的稳定锚点；增补正文时不要按段落位置重新生成这份映射。

实作入口为 `#resources`，课程顶部与固定目录也可就地打开，关闭后保留阅读位置。逐项来源、任务、许可与复算范围在 `courses/resources/catalog.json`，构建命令为 `python scripts/build-resource-library.py`；核验记录见 [RESOURCE-REVIEW.md](RESOURCE-REVIEW.md)。复算代码与结果保存在 `assets/practice/`，公开规格、真实观测和仿真分开标注，原始日志访问失败不计为已经复算。
