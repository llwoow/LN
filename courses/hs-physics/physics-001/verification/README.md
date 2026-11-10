# 来源与复算

`content-v1.2-source.json`、`physics001-v1.2-source.pdf` 保留本次迁入的原整理稿；学生实际答卷未收到。当前 `content.json` 仅将动画URL改为LN路由，正文和答案不改。PDF迁入只改URI注释，原84页打印像素不改，验证见 `pdf-verification.json`。

`motion_models.py` 是给定理想条件下的确定性模型，`render_motion.py` 由同一状态生成GIF、MP4、海报与关键帧。`verify_motion.py` 核对动力学约束与事件，`verify_media.py` 比较GIF采样帧，并检查视频尺寸、编解码与时长。它们是技术与模型一致性检查，不是现实实验或教学效果研究。

运行环境：Python 3.12、NumPy、SciPy、Pillow、PyMuPDF、ffmpeg/ffprobe、Noto CJK字体；网页/练习生成另需Node，使用仓库内KaTeX。渲染器原字体路径为 `/usr/share/fonts/opentype/noto/`，没有该字体需安装后再运行。正式网页不依赖这些生成工具。

生成结果位于同级 `../animations/`；不要在verification下复制第二套媒体。动画时间线在 `../animations/qa/`，是压缩GIF帧与源模型时间的对应数据。`baseline.json` 保留主分支原47条习题的规范化SHA256，用于核对身份与内容兼容。完整迁入范围和限制见仓库根 `PHYSICS001-REVIEW.md`。

`build_pdf.py` 保留XeLaTeX制作代码，输出到 `verification/build/physics001.pdf`，已实跑生成84页，不会覆盖当前供学生下载的PDF。`make_figures.py` 保留Matplotlib静态图源代码（需Matplotlib和Noto CJK字体），运行会重绘同级figures，须另行审查差异。本次直接保留已选图稿，未重新运行静态图绘制。
