# LN

按学科分类的轻量学习网页。

直接打开 `index.html`，或运行：

```sh
python -m http.server 4173 --bind 127.0.0.1
```

浏览器访问 http://127.0.0.1:4173 。

- 可折叠侧栏、课程搜索、学科筛选、收藏。
- 每门课程默认进入知识图谱：节点结构固定，支持拖动平移、缩放、章节筛选与搜索，点击节点进入正文；实线表示阅读顺序，虚线表示附说明的知识联系。
- 教材与论文式单栏阅读：公式编号靠右，图表统一编号；公式、图表引用可点击跳转，再点击目标编号或“返回引用处”回到原阅读位置。
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
```

网页引用与编号布局的浏览器回归检查（需已安装 Playwright 和 Chromium，先启动上面的本地 HTTP 服务）：

```sh
python tests/publication.browser.py
```
