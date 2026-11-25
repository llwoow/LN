# 2026-11-24 电磁兼容增量讲解

范围：1.4、2.2、7.3、7.4；保留原章节 ID、路由及既有正文。新增独立讲解和原创示意图；未上传教材照片或对话原件。

- 1.4：栅氧电场、ESD 损伤、非热效应与证据辨析、法拉第积分展开。工频环境控制值参考生态环境部 https://www.mee.gov.cn/xxgk2018/xxgk/xxgk13/201910/t20191031_740017_wh.html ，标准状态参考 https://std.samr.gov.cn/gb/search/gbDetailed?id=71F772D7ECC9D3A7E05397BE0A0AB82A 。低频健康证据参考 WHO https://www.who.int/teams/environment-climate-change-and-health/radiation-and-health/non-ionizing/exposure 及 NCI https://www.cancer.gov/about-cancer/causes-prevention/risk/radiation/electromagnetic-fields-fact-sheet 。教材历史个案未找到原始研究，不作为确定事实。
- 2.2：公共回流/等效源、串联分压、麦克斯韦方程到平面深度解、峰值相量与平均焦耳损耗等效。公式与示意图在对应段落内。
- 7.3/7.4：损伤机制及保护路径关联，避免重复介绍。图谱新增三条课程内联系。
- 四个新增模型默认值与原十一模型全部控制参数端点已在 ECMAScript 最小 DOM 环境检查（15 个模型、96 个单参数端点），未发现非有限值。新增默认值：1 GV/m、1.57 mV/m、0.400 V、66.1 μm 与 7.57。修改 Node 断言及浏览器测试覆盖；浏览器真实渲染及全仓 CI 尚未执行，不能视为通过。
- 在正文折叠诊断题之外，使用 Git blob 读取完整练习库并追加 8 道原创诊断题（选择、数值计算），总题量 192→200，EMC 18→26。旧题数据、题库版本、存储键均保留；新题绑定真实阅读锚点。已核对原始和生成题库内容一致，真实浏览器作答测试尚待执行。
- 本次基于本轮所示教材片段和现有课程小节，未核读教材全文；新增健康资料为官方公开页面，未上传原件。
