# 进度与维护说明

[返回项目介绍](README.md) · [公开发布规范](PUBLICATION.md) · [隐私与资料审查](PUBLICATION-REVIEW-2026-11-13.md)

更新：2026-11-13。以下记录已接入范围与已知边界，数量不代表内容完整或教学质量通过。

2026-11-13 接入范围：功率半导体器件及第二章答卷；电工材料包含《电气材料基础》7章29节目录（第2章5节有正文）和独立试卷资料；直流电机新增并联支路、功率关联及条件化例题分析。修复内容与原件未核范围见 [本轮审查记录](PR-REVIEW-2026-11-13.md)。模拟评分不作为本轮核实的正式成绩。

变压器新增汤蕴璆《电机学》第5版2.1—2.14原创讲解主线，旧专题与原作业保留。新增24道诊断题及NPTEL原题/图解入口；目录依据、逐节修改与全文未取得的边界见 [TRANSFORMER-REVIEW.md](TRANSFORMER-REVIEW.md)。算例可用 `python assets/practice/transformer/reproduce.py` 独立复算。

练习入口 `#practice`，课程顶部及固定目录也可打开。默认先展示有出处的精选来源，链接原题、解析/评分与知识点，候选和原创补充分开。当前题库169题：50单选、19多选、48计算、52问答，支持错题/收藏再做；记录仅当前浏览器，首答与辅助后结果分开。规范和覆盖限制见 [PRACTICE.md](PRACTICE.md)，来源核查见 [PRACTICE-REVIEW.md](PRACTICE-REVIEW.md)，构建 `python scripts/build-practice.py`。

按学科分类的轻量学习网页。

教学以理解系统、独立推导和迁移为目标，统一标准见 [TEACHING.md](TEACHING.md)。正文按知识自身的逻辑连贯展开，关键推理和具体例子默认可见；统一标准不要求每节使用固定标题或模板。逐节审查记录见 [TEACHING-REVIEW.md](TEACHING-REVIEW.md)。

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
- 已整合电机学：磁路、变压器、直流电机、第二章作业及直流电机 3D 交互模型；新增《电磁兼容原理及应用》10章40节正文、8节较完整原理样章（其余32节为首轮扩写，尚未通过深入审校；详见 `courses/electromagnetic-compatibility/REVIEW.md`）。不含音频。
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

高中入口为 `#highschool`。现阶段保留海南2027届核验报告对应的九科、50册主索引、235个目录节点和17条学习主线。原教材目录页保留标题、原地址及导航，正文留空；物理另增“试卷001”资料组，含原卷、18题详解、20段动画与12个参数交互。课程顶部“试卷讲解”直接进入资料页。“教材与来源”保留原报告、索引表和候选版本。

各科目录底本在 `courses/hs-*/source-index.json`，学习主线在 `courses/highschool/learning-paths.json`。修改后运行：

```sh
python scripts/build-physics001.py
python scripts/build-highschool.py
python scripts/build-reference-index.py
python scripts/build-glossary.py
python -m unittest discover -s tests -v
python tests/highschool.browser.py
```

静态发布运行 `scripts/check-teaching.py`，区分仅有目录的节点和有正文的阅读单元。正文的 `definition-anchors.json` 保留已发布释义链接的稳定锚点。

实作入口为 `#resources`，课程顶部与固定目录也可就地打开，关闭后保留阅读位置。逐项来源、任务、许可与复算范围在 `courses/resources/catalog.json`，构建命令为 `python scripts/build-resource-library.py`；核验记录见 [RESOURCE-REVIEW.md](RESOURCE-REVIEW.md)。复算代码与结果保存在 `assets/practice/`，公开规格、真实观测和仿真分开标注，原始日志访问失败不计为已经复算。

内容、验收与合并要求见 [REQUIREMENTS.md](REQUIREMENTS.md)，执行入口见 [AGENTS.md](AGENTS.md)。变压器正文采用用户二次整理的PDF网页版，阅读框架、高中资料与练习系统来自切换前完整版本；构建不再插入固定七段正文。

物理001的迁入范围、辨读限制与验证证据见 [PHYSICS001-REVIEW.md](PHYSICS001-REVIEW.md)。常规PDF保留关键帧，播放链接指向LN；这次PR合并并部署后链接才对应上线内容。

## 构建与部署

推送或合并到 `main` 后，GitHub Actions 运行检查、执行 `python scripts/build-static.py` 并发布 `dist/` 到 GitHub Pages。工作流失败时保留前一版站点。现有 LN 站点采用独立发布流程；两个域名的浏览器学习记录不自动互通。

[Pages 工作流](https://github.com/llwoow/LN/actions/workflows/pages.yml)支持手动重新运行。公开发布的隐私、许可与历史审查按 [PUBLICATION.md](PUBLICATION.md)执行。
