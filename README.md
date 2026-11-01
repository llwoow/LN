# LN

按学科分类的轻量学习网页。

直接打开 `index.html`，或运行：

```sh
python -m http.server 4173 --bind 127.0.0.1
```

浏览器访问 http://127.0.0.1:4173 。

- 可折叠侧栏、课程搜索、学科筛选、收藏。
- 五套配色，日间 / 夜间 / 跟随系统。
- 原生 HTML、CSS、JavaScript，无需安装依赖。
- 已整合电机学：磁路、变压器、直流电机、第二章作业及绕组交互模型。不含音频。
- 课程正文、公式字体和模型按需加载；保留原讲义 PDF。其余课程为占位示例。

`/` 或 `Ctrl/Cmd + K` 搜索，`Esc` 关闭设置或手机侧栏。

项目要求见 [REQUIREMENTS.md](REQUIREMENTS.md)，约束内容质量、实际阅读验收、完成声明及版本合并；执行入口见 [AGENTS.md](AGENTS.md)。界面规范见 `DESIGN.md`。外观、收藏与侧栏状态保存在当前浏览器；本地 HTTP 预览的存储行为通常更稳定。

材料核查及转换说明见 `courses/electrical-machines/REVIEW.md`。检查命令：

```sh
python -m unittest discover -s tests -v
node tests/motor-winding.test.cjs
```
