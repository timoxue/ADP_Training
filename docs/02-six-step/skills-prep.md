# 功能映射与模式选择（第三步）

> 将能力拆解的结果映射到 ADP 平台具体功能，并选定应用模式。这是最关键的决策节点。

---

## ADP 能力映射表

| 能力类别 | ADP 平台功能 | 对应技能 |
|---|---|---|
| 知识检索 | 知识库（文档上传+向量检索） | `tencentcloud-adp-kb-management` |
| 知识检索（搜索） | 知识库内容检索 | `tencentcloud-adp-kb-search` |
| 知识检索（重排序） | 检索结果重排序 | `tencentcloud-adp-rerank` |
| 数据查询（A股） | A股数据/新闻/微信搜索 | `a-stock-data`、`news`、`wechat-article-search` |
| 数据查询（经营数据） | 自然语言问数据→SQL→可视化 | `instant-data-qa` |
| 数据查询（数据分析） | 上传Excel/CSV自动分析 | `data-analysis-workflow` |
| 提示词设计 | 角色指令/系统提示词 | `adp-prompt-builder` |
| 应用管理 | 创建/配置/发布应用 | `adp-app-manager` |
| Multi-Agent 创建 | 多Agent应用框架 | `public-adp-multiagent-creator` |
| 标准模式创建 | 标准模式应用创建 | `public-adp-standardagent-creator` |
| 多模态生成 | 图片/3D 生成 | `adp-multimodal-generation` |
| 外部集成 | 连接器/插件 | `adp-plugin-manager` |
| 工作流编排 | 多步骤流程 | `adp-workflow-package-generator` |
| 安全审查 | Skill 安全审计 | `skills-security-check` |
| 文档生成 | Word/Excel/PPT/PDF | `word-docx`/`excel-xlsx`/`powerpoint-pptx`/`pdf` |
| 合同审核 | 合同解析+风险评估 | `contract-review` |
| 舆情核验 | 事实核查/辟谣 | `tencent-fact-check` |
| 网页摘要 | URL/文件智能摘要 | `summarize-cn` |
| 语音识别 | 音频转文字 | `tencentcloud-asr-recognition` |
| 企业微信 | 企微消息/通讯录/文档 | `wecom-unified` |
| 腾讯文档 | 创建/编辑在线文档 | `tencent-docs` |
| 图表可视化 | SVG/HTML 图表生成 | `svg-visualizer` |
| 浏览器自动化 | 网页导航/点击/截图 | `agent-browser` |
| DCF估值 | 折现现金流模型 | `dcf-model` |
| 经营周月报 | 自动生成周报/月报 | `business-weekly-monthly-report` |

!!! tip "务必执行平台搜索"
    上表只是经验初筛。平台 Skills 广场有 100+ 个技能，用 `describe_skill_list` 搜索补充，避免遗漏高匹配度选项。例如"投研小团队"可能匹配到 `dcf-model`（估值）、`tencent-fact-check`（舆情核验）等。

---

## 映射输出模板

```
能力1：[知识检索]
  → 经验初筛：tencentcloud-adp-kb-management（★★★ 完全匹配）
  → 平台搜索补充：tencentcloud-adp-kb-search（★★☆）、tencentcloud-adp-rerank（★☆☆）
  → 最终选择：tencentcloud-adp-kb-management + tencentcloud-adp-kb-search

能力2：[数据查询]
  → 经验初筛：a-stock-data（★★★ A股全栈数据）
  → 平台搜索补充：instant-data-qa（★★☆ 经营数据SQL查询）
  → 最终选择：a-stock-data + instant-data-qa
```

---

## 四种应用模式对照

!!! danger "选模式前必读"
    - **Claw 模式创建后不可切换到其他模式**，选错只能从头来
    - **Claw 模式没有**内容安全/保守回答/隐私脱敏/长期记忆/上下文轮数等平台级设置
    - 金融合规场景必须有平台级硬拦截 → **不能选 Claw 模式**

| 维度 | Claw 模式 | 标准模式 | 单工作流模式 | Multi-Agent 模式 |
|---|---|---|---|---|
| 交互方式 | 自然语言驱动Agent自主决策 | 思考模型+生成模型双模型协同 | 按固定工作流执行 | 多Agent协作 |
| 知识库集成 | 通过Skills调用 | 平台原生集成，更稳定精确 | 工作流知识节点中使用 | 需启用"知识库问答"工具 |
| 外部数据 | Skills即装即用（最多80个） | 通过连接器和工作流节点 | 通过工作流节点 | 通过工具和连接器 |
| 独立工作空间 | ✅ 可读写文件、运行代码 | ❌ | ❌ | ❌ |
| 工作流支持 | ❌ 不支持 | ✅ 可添加 | ✅ 单个工作流 | ✅ 可选工作流编排 |
| 模式切换 | ❌ **不可切换** | ✅ 可切到单工作流/Multi-Agent | ✅ 可切到标准/Multi-Agent | ✅ 可切到标准/单工作流 |
| **应用设置项** | 欢迎语/对话体验/变量/高级设置(同义词)仅4项 | 内容安全/保守回答/隐私脱敏/长期记忆/模型设置/上下文轮数完整设置 | 同标准模式 | 同标准模式 |
| **合规风控** | ❌ 无平台级硬拦截，只能提示词软约束 | ✅ 平台强制拦截+提示词软约束 | 同标准模式 | 同标准模式 |
| 适合场景 | 数据分析、内容生成、自动化处理 | 企业知识服务、严肃问答、产品咨询 | 业务流程固定的服务 | 灵活响应、多工具、多角色协同 |

---

## 模式选择决策树

```
① 需要读写文件/运行代码？
   → 是 → Claw 模式
   → 否 ↓

② 需要平台级合规硬拦截（内容安全/保守回答/隐私脱敏）？
   → 是 → ❌ 不能选 Claw → 选标准/单工作流/Multi-Agent
   → 否 ↓

③ 有固定执行流程？
   → 是 → 单工作流模式
   → 否 ↓

④ 需要多个角色协作？
   → 是 → Multi-Agent 模式
   → 否 ↓

⑤ 核心是严肃问答/知识服务？
   → 是 → 标准模式
   → 否 → Multi-Agent 模式 或 Claw 模式
```

---

## 案例：三个典型应用的模式选择

=== "投研助手"

    **选择：Claw 模式**

    - 需要灵活调用 a-stock-data / news / wechat 等多个 Skills
    - 投研场景无合规硬拦截需求
    - Skills 即装即用，调用灵活
    - ⚠️ Claw 模式创建后不可切换；无平台级硬拦截

=== "财富顾问助手"

    **选择：标准模式**

    - 合规场景必须有平台级硬拦截（内容安全+保守回答+隐私脱敏）
    - Claw 模式没有这些设置项，排除
    - 知识库原生集成更稳定精确
    - 需要长期记忆（跨会话记住客户风险偏好）

=== "投研小团队"

    **选择：Multi-Agent 模式**

    - 多角色并行是核心诉求：财务/行业/舆情/风控 4 个子Agent同时工作
    - 无合规硬拦截需求
    - 无固定执行流程
    - ⚠️ 主要风险：调度Agent可能误判；子Agent输出格式需标准化

---

## 技能匹配度评级说明

| 评级 | 含义 |
|---|---|
| ★★★ 完全匹配 | 技能描述与能力需求完全一致，直接使用 |
| ★★☆ 高度匹配 | 核心功能一致，可能需要少量提示词适配 |
| ★☆☆ 部分匹配 | 覆盖部分需求，需组合其他技能 |
