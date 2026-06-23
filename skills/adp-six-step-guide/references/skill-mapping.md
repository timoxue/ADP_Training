# ADP 技能详细能力矩阵与选型指南

本文件是第三步「功能映射」的详细参考，帮助将能力需求精确映射到 ADP 平台功能与技能。

---

## 应用模式对照表

选择应用模式是第三步的关键决策，直接影响后续所有配置方式。

### 四种模式核心差异

| 维度 | Claw 模式 | 标准模式 | 单工作流模式 | Multi-Agent 模式 |
|---|---|---|---|---|
| 交互方式 | 自然语言驱动Agent自主决策 | 思考模型+生成模型双模型协同 | 按固定工作流执行 | 多Agent协作，模型自主规划路径 |
| 知识库集成 | 通过Skills调用（知识库问答Skill） | **平台原生集成**，更稳定精确 | 仅在工作流知识节点中使用 | 需启用"知识库问答"工具 |
| 外部数据调用 | **Skills即装即用**（最多80个） | 通过连接器和工作流节点 | 通过工作流节点 | 通过工具和连接器 |
| 独立工作空间 | ✅ 可读写文件、运行代码 | ❌ | ❌ | ❌ |
| 工作流支持 | ❌ 不支持 | ✅ 可添加 | ✅ 单个工作流 | ✅ 可选工作流编排 |
| 模型配置 | 开箱即用（默认Kimi K2.5，可切换） | 需配置思考模型+生成模型 | 同标准模式 | 同标准模式 |
| 模式切换 | ❌ **不可切换到其他模式** | ✅ 可切到单工作流/Multi-Agent | ✅ 可切到标准/Multi-Agent | ✅ 可切到标准/单工作流 |
| 提示词框架 | 框架B（Agent模式） | 框架A（标准模式） | 框架A（标准模式） | 框架B（Agent模式，每个子Agent一段） |
| **应用设置项** | 欢迎语/对话体验/变量/高级设置(同义词) | 内容安全/保守回答/隐私脱敏/长期记忆/模型设置/上下文轮数 | 同标准模式 | 同标准模式 |
| **合规风控** | ❌ **无平台级硬拦截**，只能提示词软约束 | ✅ 平台强制拦截(内容安全+隐私脱敏)+提示词软约束 | 同标准模式 | 同标准模式 |
| 适合场景 | 数据分析、内容生成、自动化处理 | 企业知识服务、严肃问答、产品咨询 | 业务流程统一、操作步骤固定 | 灵活响应、多工具调用、多角色协同 |

### ⚠️ 关键差异：Claw 模式没有合规硬拦截设置项

> **这是模式选择最关键的区别，官方文档未明确写出，但通过以下证据确认：**
>
> 1. **官方文档佐证**：应用设置概述文档明确标注"本文以标准模式应用为例"，所有设置项（模型设置/角色指令/知识库/对话体验/变量与记忆(长期记忆)/高级设置）的描述都是标准模式的。Claw 模式没有被纳入此文档。
> 2. **官方文档佐证**：四种模式文档指出"Claw 模式的工作空间、Skills、连接器等配置与其他三种模式差异较大"。
> 3. **实际界面验证**：Claw 模式应用设置仅有 4 个菜单项——欢迎语、对话体验、变量、高级设置(同义词)。内容安全、保守回答、隐私脱敏、长期记忆、上下文轮数、双模型设置——这些全部不存在。
>
> **影响**：
> - 合规场景（金融/医疗/法律）需要平台级硬拦截，Claw 模式只能靠提示词软约束，**可被 prompt injection 绕过**
> - 长期记忆场景无法实现
> - 长对话场景无法调整上下文轮数
> - 一旦选了 Claw 模式，不可切换，只能新建应用从头来

### 模式切换规则

```
Claw 模式 ←──不可切换──→ 其他三种模式（标准/单工作流/Multi-Agent）

标准模式 ←──可互切──→ 单工作流模式 ←──可互切──→ Multi-Agent 模式
                                                    ↑                    |
                                                    └──可互切──→ 标准模式┘
```

**关键结论**：
- 选 Claw = 锁死路径，未来无法切到标准/工作流/Multi-Agent
- 选标准 = 保留扩展空间，后续可切到单工作流或 Multi-Agent
- 模式切换时：知识库和工作流保持不变，但提示词、模型配置、连接器等不继承

### 模式选择决策树

```
Q1: 应用需要读写文件/运行代码吗？
  ├─ 是 → Claw 模式
  └─ 否 → Q2

Q2: 应用需要平台级合规硬拦截（内容安全/保守回答/隐私脱敏）吗？
  ├─ 是 → ❌ 不能选 Claw（Claw 没有这些设置项），进入 Q3
  └─ 否 → Q3

Q3: 应用有固定执行流程吗？
  ├─ 是 → 单工作流模式
  └─ 否 → Q4

Q4: 应用需要多个角色协作吗？
  ├─ 是 → Multi-Agent 模式
  └─ 否 → Q5

Q5: 应用核心是严肃问答/知识服务吗？
  ├─ 是 → 标准模式（知识库原生集成更稳定）
  └─ 否 → Q6

Q6: 应用需要灵活调用多种外部工具/Skills？
  ├─ 是 → Claw 模式（Skills即装即用）或 Multi-Agent 模式
  └─ 否 → 标准模式
```

### 各模式下的数据调用方式

| 数据需求 | Claw 模式 | 标准模式 | 单工作流模式 | Multi-Agent 模式 |
|---|---|---|---|---|
| 知识库检索 | 知识库问答 Skill | 平台原生知识库问答 | 工作流中知识检索节点 | 知识库问答工具 |
| A股数据 | a-stock-data Skill | 连接器（如已上线）或工作流API节点 | 工作流API节点 | 工具调用 |
| 新闻搜索 | news Skill | 连接器或工作流API节点 | 工作流API节点 | 工具调用 |
| 微信文章 | wechat-article-search Skill | 连接器或工作流API节点 | 工作流API节点 | 工具调用 |
| 文档生成 | word/excel/ppt/pdf Skills | 工作流中对应节点 | 工作流中对应节点 | 工具调用 |
| 图片/3D | adp-multimodal-generation Skill | 连接器 | 工作流中对应节点 | 工具调用 |

### 典型场景模式推荐

| 场景 | 推荐模式 | 理由 | 替代方案 |
|---|---|---|---|
| 投研分析（多数据源灵活调用） | Claw | Skills即装即用，a-stock-data/news/wechat一键挂载 | Multi-Agent（多角色协作时） |
| 投后风险预警（严肃问答） | **标准** | 知识库原生更稳定，双模型协同推理更精确，未来可切工作流 | Claw（如需灵活调用Skills） |
| 财富顾问（合规问答） | **标准** | 合规场景需稳定精确，平台安全+保守回答兜底 | — |
| 客服咨询（固定流程） | **单工作流** | 流程统一，步骤固定 | 标准模式+工作流 |
| 多角色投研（研究员+销售+基金经理） | **Multi-Agent** | 多角色分工协作 | Claw+提示词角色分级 |

---

## 平台 Skills/工具搜索能力

> 不要只靠经验手动映射——ADP 平台有 100+ 个 Skills，可能有你不知道的高匹配度选项。

### 搜索方法

**方法1：describe_skill_list（搜索 Skills 广场）**

```bash
# 列出所有可用 Skills（最多100个）
python3 scripts/adp_mcp.py call describe_skill_list '{"app_id":"<app_id>","limit":100,"offset":0}'
```

返回字段：
- `skill_id`：挂载时用这个，不是 name
- `profile.name`：技能名称
- `profile.description`：技能描述（用于匹配度判断）
- `current_version`：当前版本

**方法2：describe_plugin_list（搜索工具/插件）**

```bash
# 列出已安装的工具/插件
python3 scripts/adp_mcp.py call describe_plugin_list '{"app_id":"<app_id>","limit":50,"offset":0}'
```

**方法3：adp-plugin-manager（搜索连接器）**

当 Skills 和内置工具都不满足时，用 `adp-plugin-manager` 搜索第三方连接器（腾讯文档、企业微信、GitHub 等）。

### 匹配度判断标准

| 匹配度 | 判断条件 | 示例 |
|---|---|---|
| ★★★ 完全匹配 | 技能描述与能力需求完全一致 | 需要知识库管理 → `tencentcloud-adp-kb-management` |
| ★★☆ 高度匹配 | 核心功能一致，可能需要少量提示词适配 | 需要数据分析 → `data-analysis-workflow` 或 `instant-data-qa` |
| ★☆☆ 部分匹配 | 覆盖部分需求，需组合其他技能 | 需要估值分析 → `dcf-model`（仅DCF，不含其他估值方法） |

### 搜索流程

```
输入：第二步拆解出的能力清单（如：知识检索、数据查询、合规风控）

Step 1：经验初筛
  → 从上面的「ADP 能力映射表」中快速找到候选技能
  → 标注匹配度

Step 2：平台搜索补充
  → 调用 describe_skill_list 获取全部 100+ Skills
  → 逐个用 name + description 做关键词匹配
  → 找出经验初筛遗漏的高匹配度技能
  → 常见遗漏：
    - tencentcloud-adp-kb-search（知识检索专用，比 kb-management 更精准）
    - tencentcloud-adp-rerank（检索结果重排序优化）
    - instant-data-qa（经营数据自然语言查询→SQL→可视化）
    - dcf-model（DCF 估值模型）
    - tencent-fact-check（事实核查/辟谣）
    - summarize-cn（网页/文件摘要）
    - contract-review（合同审核）
    - business-weekly-monthly-report（自动周报月报）
    - svg-visualizer（图表可视化）

Step 3：合并 + 排序
  → 合并两轮结果
  → 按匹配度从高到低排序
  → 输出最终映射表
```

### 平台 Skills 全量清单（截至当前版本，共100个）

> 以下是平台 Skills 广场的全量列表，按类别整理。实际搜索时以 `describe_skill_list` 返回结果为准。

| 类别 | Skills |
|---|---|
| ADP 平台管理 | adp-app-manager, adp-prompt-builder, adp-skill-manager, adp-plugin-manager, adp-workflow-package-generator, adp-multimodal-generation, public-adp-standardagent-creator, public-adp-multiagent-creator, adp-app-chat, skills-security-check |
| 知识库 | tencentcloud-adp-kb-management, tencentcloud-adp-kb-search, tencentcloud-adp-rerank |
| A股/金融 | a-stock-data, dcf-model, finance-budget-planning |
| 数据分析 | data-analysis-workflow, instant-data-qa, data-analysis, data-quality-check, business-weekly-monthly-report |
| 新闻/舆情 | news, wechat-article-search, tencent-fact-check |
| 文档生成 | word-docx, excel-xlsx, powerpoint-pptx, pdf, doc-coauthoring, summarize-cn, ai-proposal-generator |
| 文档转换 | tencent-pdf-to-office-document, tencent-document-to-pdf, tencent-Image-to-office-document, tencent-document-translation, tencent-document-conversion |
| 多模态 | tencentcloud-hunyuan-image, tencentcloud-hunyuan-3d, tencentcloud-hunyuan-3d-pro, openai-vision, tencentcloud-image-understanding, tencentcloud-video-understand |
| OCR/结构化 | tencentcloud-general-accurate-ocr, tencentcloud-structured-visual-extraction(Basic/Multimodal) |
| 语音 | tencentcloud-asr-recognition, tencentcloud-long-text-to-voice, tencentcloud-short-text-to-speech-synthesis |
| 图片处理 | tencent-image-processing, tencentcloud-image-flag-landmark-logo-recognition, tencentcloud-face-beautify, tencentcloud-AI-face-protection-shield |
| 视频 | tencentcloud-video-processing, tencentcloud-variety-show-video-clip-splitting |
| 办公协同 | tencent-docs, wecom-unified, lark-unified, tencent-meeting-mcp, ima-skill, lexiang-knowledge-base |
| 合同/法务 | contract-review, contract-clause-diff, contract-compliance-check |
| HR/招聘 | interview-prep, jd-publish, offer-drafting, salary-tax-calculator, hr-employee-analytics |
| 营销/文案 | copywriter-cn, multi-platform-content-generation, customer-success |
| 开发/工程 | skill-creator, mcp, cloudbase, tdesign-miniprogram, agent-browser, qqbrowser-skill |
| 设计 | frontend-design-3, theme-factory, canvas-design, svg-visualizer, tencentcloud-mindmap-generator, slack-gif-creator |
| 地图 | tencentmap-webservice-skill, tencentmap-lbs-skill |
| 医疗 | tencent-ai-drug-consultant, tencent-diagnosis, tencent-drug-instructions, tencent-medical-encyclopedia |
| 其他 | tencentcloud-cos, tencentcloud-cls, tapd-openapi, andonq, brainstorming, writing-plans, file-organizer-skill, planning-with-files, startup-coach-workshop, competitive-analysis, lead-enrichment, dify2adp |

---

### 1. tencentcloud-adp-kb-management（知识库管理）

| 维度 | 说明 |
|---|---|
| 核心能力 | 文档上传/列表/详情/预览/重命名/删除/重试解析、分类增删改查 |
| 适用场景 | 需要自有文档作为知识基础的应用（年报、产品说明书、FAQ、规则文档等） |
| 不适用 | 实时数据查询（用 API）；知识检索/问答（用 kb-search） |
| 环境变量 | `ADP_API_KEY`、`ADP_SPACE_ID`、可选 `ADP_APP_ID` |
| 关键限制 | 文档状态流转需等待（解析中→审核中→学习中→完成）；FAQ 导入不支持 MD 格式，需 CSV/Excel |
| 典型操作 | 创建分类 → 上传文档 → 确认解析完成 → 配置检索参数（混合检索、Top-K 5-10、相似度 0.5-0.7） |

### 2. a-stock-data（A股数据）

| 维度 | 说明 |
|---|---|
| 核心能力 | 7层数据源：行情、研报、信号、资金面、新闻、基础数据、公告 |
| 适用场景 | 投研、估值、龙虎榜、解禁预警、行业轮动等 A 股场景 |
| 不适用 | 非A股市场；订单交易 |
| 环境变量 | `IWENCAI_API_KEY`（问财接口，可选） |
| 关键限制 | mootdx TCP 7709 某些环境不通→用新浪 HTTP 备用；东财接口有频率限制 |
| 优先级 | 通达信/腾讯 > 东财（防封） > 新浪（兜底） |

### 3. adp-app-manager（应用管理）

| 维度 | 说明 |
|---|---|
| 核心能力 | 新建/查看/修改应用、提示词、欢迎语、Skills、工具、工作流、发布上线 |
| 适用场景 | 应用生命周期全流程管理 |
| 不适用 | 删除应用；跨账号操作 |
| 环境变量 | `ADP_API_KEY`、可选 `ADP_APP_ID`、`ADP_DELEGATE_API_KEY`/`ADP_DELEGATE_APP_ID`（平台代理模式） |
| 关键限制 | 所有写操作前必须先读（整段替换）；skill_id 必须用真实 ID；开场问题最多 3 条；批量操作间隔 3 秒+ |
| 14 个工具 | create_app、describe_app、describe_agent_config、describe_skill_list、describe_plugin_list、modify_agent_prompt、modify_app_greeting、modify_agent_skill_list、modify_agent_tool_list、release_app、import_workflow、switch_workflow_state 等 |

### 4. adp-prompt-builder（提示词构建）

| 维度 | 说明 |
|---|---|
| 核心能力 | 对话式引导补全提示词，支持标准模式/Agent模式/Multi-Agent模式 |
| 适用场景 | 提示词从零设计、优化已有提示词、完成提示词框架填写 |
| 不适用 | 直接修改已上线应用的提示词（用 adp-app-manager） |
| 两种框架 | 框架A：标准模式（角色+风格+输出模块+限制）；框架B：Agent模式（任务目标+任务流程+限制+转交描述） |
| 典型输出 | 完整提示词文本，可直接粘贴或通过 adp-app-manager 提交 |

### 5. adp-plugin-manager（连接器管理）

| 维度 | 说明 |
|---|---|
| 核心能力 | 搜索当前空间可用连接器、推荐合适连接器、引导用户启用 |
| 适用场景 | 需要对接第三方平台（腾讯文档、GitHub、QQ邮箱等） |
| 不适用 | 已有直接可用工具时不触发；不执行连接器操作本身 |
| 环境变量 | `ADP_API_KEY`、`ADP_SPACE_ID` |
| 关键限制 | 只搜索和引导启用，不直接执行连接器操作 |

### 6. adp-workflow-package-generator（工作流生成）

| 维度 | 说明 |
|---|---|
| 核心能力 | 根据意图生成可导入的工作流 zip 包 |
| 适用场景 | 多步骤流程（如：收集信息→查询→分析→生成报告） |
| 不适用 | 简单对话场景（用标准模式） |
| 环境变量 | `ADP_API_KEY` |
| 模型分层 | 弱模型→SKILL_LITE.md；正常→SKILL.md；强→SKILL_DEEP.md |
| 关键限制 | 不要手写 workflow JSON，必须走脚本生成；生成后需 verify_delivery.py 校验 |

### 7. adp-multimodal-generation（多模态生成）

| 维度 | 说明 |
|---|---|
| 核心能力 | 图片生成（文生图/图生图）、3D 模型生成（文生3D/图生3D） |
| 适用场景 | 需要配图、3D 模型、风格改造 |
| 不适用 | 视频生成；跨类别降级（视频不行→不能降为图片） |
| 环境变量 | `ADP_API_KEY` |
| 模型选择 | image.hy（默认）/ image.gi（Gemini/nano banana） / 3d.hy（混元3D） |

### 8. skills-security-check（安全审查）

| 维度 | 说明 |
|---|---|
| 核心能力 | 对 skill.md 及配套文件做安全审计 |
| 适用场景 | 安装第三方技能前、上架技能前 |
| 不适用 | 非 skill 场景的安全审查 |
| 关键限制 | 纯静态分析，不执行被审查的 skill；只允许只读工具 |

---

## 能力→技能快速映射

当用户说"我需要 XXX 能力"时，查此表：

| 用户需求关键词 | 推荐技能 | 备选方案 |
|---|---|---|
| 上传文档/知识库/检索文档 | `tencentcloud-adp-kb-management` | — |
| 股票/行情/研报/A股 | `a-stock-data` | — |
| 创建应用/配置应用/发布 | `adp-app-manager` | — |
| 提示词/角色指令/系统提示词 | `adp-prompt-builder` | — |
| 连接器/插件/对接第三方 | `adp-plugin-manager` | — |
| 工作流/多步骤流程/流程编排 | `adp-workflow-package-generator` | — |
| 生成图片/3D模型 | `adp-multimodal-generation` | — |
| 安全检查/审计 skill | `skills-security-check` | — |
| 数据分析/图表/看板 | `data-analysis-workflow` | — |
| 生成 Word/Excel/PPT/PDF | `word-docx`/`excel-xlsx`/`powerpoint-pptx`/`pdf` | — |
| 搜索/安装技能 | `adp-skill-manager` | — |
