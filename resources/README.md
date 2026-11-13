# 本地资源

用户提供的原始教材、试卷及旧答案统一放在 `local/` 下；整个 `/resources/local/` 已由根目录 `.gitignore` 忽略，不进入常规 Git 提交和静态站点源码。

功率半导体器件本批材料位于 `local/power-semiconductors/`：5 份原始 PDF 保留原名和原字节，`manifest.json` 记录页数、大小与 SHA-256；`extracted/` 是本地提取文字和核读页图。

独立编写的第二章答案、矢量图、来源定位和审查记录位于 `../answers/power-semiconductors/chapter-2/`，打印版位于 `../output/pdf/`。忽略本地资源不会自动屏蔽这些原创答卷。
