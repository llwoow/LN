# LN 课程建设与验收台

此模块是 LN 的维护工具，位于 /audit/，由仓库 README 的链接进入；学习页面不增加规范或验收入口。不维护第二份课程正文、不创建独立站点。源码数据来自现有课程 manifest、文件树及正文锚点。

清单覆盖全部课程 manifest，包括高中目录、已接入资料和各课程原有阅读及模型入口。分批整改的内容核读、来源与未解决问题从 [进度](../PROGRESS.md) 进入。

## 判定规则

- **骨架状态**：现有课程声明为 outline，或暂无可定位的独立正文。只能说明目录或接入缺失，不自动认定其他知识点不存在。
- **部分接入**：对应源文件存在。页面内容、数学准确性、公式推导、例题正确性、移动端排版和交互均**不因此通过**。
- **明确存在的问题**：源文件路径损坏，或有人记录了可复现的问题（源码位置、实际现象及复现步骤）；未经确认的猜想只标记为推测。
- **已验证**：人工登记，且独立运行测试、浏览器操作或学科核读证据已提供；必须包含源文件摘要、7–40 位提交 SHA、HTTPS 证据、具体观察、复现步骤、验收标准、验证范围和审查者。源码改变后原记录自动降回部分接入/骨架，并提示复核。
- **规范差异**：项目规范只是对照标准；不因项目中有 README、REVIEW、计划、PR 描述或 CI 名称就自动生成“通过”。实际差异需要读到代码/正文后逐条记录。
- **发布阻断**：确认问题中主动标记 blocker 的条目以及 manifest 已指向的缺失文件；“未记录”不代表不存在。

源码线索（例如公式、figure、button、href 的静态标记）帮助审查者定位，不等于学科正确或交互已通过。章节“接入率”和“已验证率”分列，任何百分比均不可描述成读者已理解或课程质量。

## 版本化与隐私

1. 在已构建的 LN 页面的 /audit/ 下登记审查；保存操作先写本机 localStorage，可离线继续编辑，不能自动提交 Git。
2. 导出 JSON，检查公开信息（不要上传隐私、原始教材图片/PDF、账户标识等），在 PR 中将导出的 records 数组合并至 audit/records.json。为便于历史追踪，每次修改都由 Git commit 记录；同时可以在 PR 中附代码、测试日志或获授权截图链接。
3. 其他设备或新浏览器读取仓库版 audit/records.json；也可人工导入导出 JSON。浏览器本机记录不会跨设备同步。
4. 完成后先通过 python scripts/build-course-audit.py --output dist/audit/inventory.json、Python/Node、静态构建、Playwright 浏览器测试、发布规范与学科人工核验。合并 PR 后再核实生产部署。未经 GitHub Pages/Sites 实际更新不声称已上线。

正文页面入口取自现有课程真实 ID；知识点链接取自 HTML 中有 id 的标题，不猜测空锚点。此项目只发布审核索引及文字记录，不打包任何教材原件、截图原件或用户私人学习记录。

## 开发

- 生成器：scripts/build-course-audit.py（随 scripts/build-static.py 自动运行）
- 网页：audit/index.html、audit/audit.css、audit/audit.js
- 记录：audit/records.json（schemaVersion=1）
- Python 测试：tests/test_course_audit.py
- 浏览器回归：tests/browser_smoke_pages.py 的 /LN/audit/ 路径
