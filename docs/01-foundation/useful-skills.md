# 推荐 Skills 分类

> ADP Skills 广场有 100+ 个技能。以下是证券行业最常用的分类与推荐。

---

## 知识与检索类

| Skill | 用途 | 适合场景 |
|-------|------|---------|
| `tencentcloud-adp-kb-management` | 知识库文档管理（创建分类、上传文档） | 所有需要知识库的应用 |
| `tencentcloud-adp-kb-search` | 知识库内容语义检索 | 精细化检索、多知识库并行查询 |
| `tencentcloud-adp-rerank` | 检索结果重排序，提升精准度 | 知识库文档量大、精度不够时 |
| `summarize-cn` | URL 或文件智能摘要（中文优化） | 研报速读、公告摘要 |

---

## A 股数据类

| Skill | 用途 | 典型调用 |
|-------|------|---------|
| `a-stock-data` | A 股全栈数据：行情/研报/信号/资金/新闻/财务/公告，七层 27 个端点 | "查宁德时代近三年 ROE""拉今日龙虎榜" |
| `instant-data-qa` | 自然语言对结构化数据提问（Text-to-SQL） | "哪些客户今年净申购超 100 万" |
| `data-analysis-workflow` | 上传 Excel/CSV 自动分析并生成图表 | 同业数据对比、业绩归因 |
| `dcf-model` | 折现现金流估值模型 | 企业内在价值测算 |

!!! info "a-stock-data 详细文档"
    七层架构、27 个端点说明、防封铁律、代码示例见 [a-stock-data 详解](skill-a-stock-data.md)。

---

## 资讯与舆情类

| Skill | 用途 | 典型调用 |
|-------|------|---------|
| `news` | 新闻搜索（国内外主流媒体） | "搜索光伏行业最新政策动态" |
| `wechat-article-search` | 微信公众号文章搜索 | "搜索券商研报中对储能的最新观点" |
| `tencent-fact-check` | 事实核查 / 辟谣 | 核验网络流传信息的真实性 |

---

## 内容生成与文档类

| Skill | 用途 | 典型调用 |
|-------|------|---------|
| `word-docx` | 生成 Word 文档 | 研报初稿、合规报告 |
| `excel-xlsx` | 生成 Excel 表格 | 数据汇总、对比表 |
| `powerpoint-pptx` | 生成 PPT 大纲 | 管理层汇报材料 |
| `pdf` | 读取或生成 PDF | 合同解析、产品说明书 |
| `svg-visualizer` | 生成 SVG / HTML 可视化图表 | 数据趋势图、结构图 |
| `business-weekly-monthly-report` | 自动生成周报 / 月报 | 部门经营简报 |

---

## 合规与审核类

| Skill | 用途 | 典型调用 |
|-------|------|---------|
| `contract-review` | 合同解析 + 风险条款提示 | 业务合同审查初筛 |
| `adp-prompt-builder` | 结构化提示词构建助手 | 帮助快速写出合规提示词 |
| `skills-security-check` | Skill 安全审计 | 上线前检查 Skill 风险 |

---

## 企业集成类

| Skill | 用途 | 典型调用 |
|-------|------|---------|
| `wecom-unified` | 企业微信消息 / 通讯录 / 文档 | 推送简报到企业微信群 |
| `tencent-docs` | 创建 / 编辑腾讯文档 | 在线协作文档生成 |
| `tencentcloud-asr-recognition` | 语音转文字（会议录音） | 会议纪要自动生成 |
| `tencentcloud-long-text-to-voice` | 文字转语音 | 研报语音播报 |
| `agent-browser` | 浏览器自动化（网页导航 / 截图） | 抓取非 API 页面数据 |

---

## 证券行业推荐组合

根据场景选择技能组合：

=== "投研助手"

    **必选**
    - `tencentcloud-adp-kb-management`（知识库）
    - `a-stock-data`（行情与财务数据）
    - `news`（行业资讯）

    **可选**
    - `wechat-article-search`（公众号观点）
    - `data-analysis-workflow`（数据可视化）
    - `dcf-model`（估值建模）

=== "财富投顾助手"

    **必选**
    - `tencentcloud-adp-kb-management`（产品知识库）

    **注意**：财富投顾场景合规要求高，**不建议**接入 `a-stock-data` 等实时数据 Skill，避免被误触发为投资建议。合规配置应走**平台安全设置**（内容安全 + 保守回答 + 隐私脱敏），而不只靠 Skill。

=== "投后经营助手"

    **必选**
    - `summarize-cn`（公告摘要）
    - `wecom-unified`（企业微信推送）

    **可选**
    - `news`（持仓公司舆情）
    - `agent-browser`（抓取公告网站）

=== "合规风控"

    **必选**
    - `tencentcloud-adp-kb-management`（制度文档知识库）

    **工作流节点替代 Skill**：合规预检更适合用**单工作流模式**（标签提取 → 条件判断 → 风险清单），而不是直接挂 Skill。

---

!!! info "如何找到更多 Skill"
    打开 ADP 控制台 → 左侧「技能广场」→ 按分类或关键词搜索。  
    每个 Skill 的 description 字段描述了它的触发场景，是判断是否适合的最快方式。
