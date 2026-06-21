# 方案B：制度版本比对助手

> 单工作流模式 | 双文件收集 → 并行解析 → LLM差异分析 → 差异清单输出

---

## 一、培训目标

完成本培训后，你将能够：

1. 在ADP平台上搭建**制度版本比对工作流**（上传旧版+新版文档，自动输出差异清单）
2. 理解双文件并行处理、LLM差异分析、结构化差异输出的完整流程
3. 独立调试和排查版本比对工作流问题

---

## 二、整体架构

### 核心设计：双文件收集 → 文档解析 → LLM差异分析 → 差异清单

```
┌───────────────────────────────────────────────────────────────────┐
│  主工作流 regulation_diff_check（制度版本比对）                       │
│                                                                   │
│  [开始] → [旧版文件收集] → [旧版解析] ──┐                           │
│        → [新版文件收集] → [新版解析] ──┤→ [差异分析(LLM)]           │
│                                          │        │               │
│                                          │        ▼               │
│                                          │   [差异提取(PARAM_EXT)] │
│                                          │        │               │
│                                          │        ▼               │
│                                          │   [差异清单输出(ANSWER)] │
│                                          │        │               │
│                                          └────────▼               │
│                                              [结束]                │
└───────────────────────────────────────────────────────────────────┘
```

### 工作原理

1. 用户上传2个文件：旧版制度文档 + 新版制度文档（分两次提示上传）
2. 两个FILE_COLLECTION节点分别收集旧版和新版
3. 两个DocParse插件节点分别解析旧版和新版文档内容
4. LLM节点同时接收两份文档文本，执行逐条差异分析
5. PARAM_EXT节点从分析结果中结构化提取差异项
6. ANSWER节点输出格式化差异清单

!!! tip "推荐拓扑：两个独立的FILE_COLLECTION"
    虽然单个FILE_COLLECTION可以收集2个文件，但无法用索引将FileList[0]和FileList[1]分别路由到两个DocParse节点。使用两个独立的FILE_COLLECTION（各MaxFiles=1）更简单可靠，不需要数组索引。

---

## 三、前置条件

| 条件 | 说明 |
|---|---|
| ADP账号 | 已登录腾讯云ADP平台 |
| 应用已创建 | 单工作流模式 |
| 知识库已配置 | 合规规则库分类已建好（用于法规依据引用） |

---

## 四、搭建工作流 regulation_diff_check

### 步骤1：创建工作流

**操作路径**：ADP控制台 → 应用管理 → 选择应用 → 工作流管理 → 新建工作流

| 字段 | 填写内容 |
|---|---|
| 工作流名称 | `regulation_diff_check` |
| 描述 | 制度版本比对-差异清单自动生成 |

点击「确定」→ 进入画布编辑器。

---

### 步骤2：搭建8节点工作流

从左侧节点面板依次拖入以下节点，并按拓扑连线：

```
[开始] → [旧版文件收集] → [旧版文档解析] ──┐
      → [新版文件收集] → [新版文档解析] ──┤→ [差异分析] → [差异提取] → [差异清单输出] → [结束]
```

**连线操作**：

1. [开始] → [旧版文件收集]
2. [开始] → [新版文件收集]
3. [旧版文件收集] → [旧版文档解析]
4. [新版文件收集] → [新版文档解析]
5. [旧版文档解析] → [差异分析]
6. [新版文档解析] → [差异分析]
7. [差异分析] → [差异提取]
8. [差异提取] → [差异清单输出]
9. [差异清单输出] → [结束]

!!! warning "拓扑注意"
    这是一个「分叉再汇合」的拓扑：[开始]同时连到两个FILE_COLLECTION，两个DocParse都连到LLM。不是直线流。

---

### 步骤3：配置「开始」节点

点击「开始」节点 → 右侧配置面板 → 确认Outputs为空数组。

> START节点不需要定义工作流参数，因为此工作流不作为子工作流被调用。

---

### 步骤4：配置两个FILE_COLLECTION节点

=== "旧版文件收集"

    | 配置项 | 填写值 |
    |---|---|
    | 节点名称 | 旧版文件收集 |
    | Question | "请上传旧版制度文档（1个文件，支持doc/docx/pdf/txt）" |
    | SupportedFileTypes | FILE_TYPE_DOCUMENT |
    | MaxAllowedUploadFileCount | **1** |

=== "新版文件收集"

    | 配置项 | 填写值 |
    |---|---|
    | 节点名称 | 新版文件收集 |
    | Question | "请上传新版制度文档（1个文件，支持doc/docx/pdf/txt）" |
    | SupportedFileTypes | FILE_TYPE_DOCUMENT |
    | MaxAllowedUploadFileCount | **1** |

**两个节点输出字段说明**：

| 节点 | 输出路径 | 说明 |
|---|---|---|
| 旧版文件收集 | Output.FileList[0].FileURL | 旧版文件URL |
| 新版文件收集 | Output.FileList[0].FileURL | 新版文件URL |

---

### 步骤5：配置两个「DocParse」插件节点

两个节点的配置方式相同，插件都选 DocParse：

| 配置项 | 值 |
|---|---|
| 插件名称 | DocParse |
| ToolID | 44b4c776-b1a4-4b3a-a2dc-7355c1ad193b |
| 支持格式 | PDF, DOC, DOCX, TXT, XLSX, CSV |

| 节点 | 解析来源 | 输出字段 |
|---|---|---|
| 旧版文档解析 | 旧版文件收集的输出 | Output.Data.Answer（旧版文档Markdown文本） |
| 新版文档解析 | 新版文件收集的输出 | Output.Data.Answer（新版文档Markdown文本） |

---

### 步骤6：配置「差异分析(LLM)」节点

这是核心节点，同时接收两份文档文本，执行逐条差异比对。

**6.1 基础配置**

| 参数 | 填写值 | 原因 |
|---|---|---|
| 节点名称 | 差异分析 | — |
| 模型(ModelName) | `Deepseek/deepseek-v3.2` | 长文本分析能力强 |
| Temperature | `0` | 差异比对需要精确，不允许随机 |
| TopP | `0.8` | 标准采样范围 |
| MaxTokens | `8192` | 制度文档较长，需要更大输出空间 |
| OutputFormat | `LLM_OUTPUT_TEXT` | 纯文本输出 |

**6.2 输入变量配置**

| 变量名 | 引用类型 | 引用节点 | 引用字段 | 说明 |
|---|---|---|---|---|
| `old_content` | 引用节点输出 | 旧版文档解析 | Output.Data.Answer | 旧版文档全文 |
| `new_content` | 引用节点输出 | 新版文档解析 | Output.Data.Answer | 新版文档全文 |

**操作方式**：

1. 点击「添加变量」→ 变量名输入 `old_content`
2. 引用类型选「引用节点输出」→ 引用节点选「旧版文档解析」→ 引用字段选 `Output.Data.Answer`
3. 重复以上步骤添加 `new_content`，引用「新版文档解析」

**6.3 系统提示词(SystemPrompt)**

```
你是「制度版本比对助手」，专门负责对制度文档的新旧版本进行逐条差异比对。你的职责是精准识别新增条款、删除条款、修改条款，并标注修改类型和影响程度。
```

**6.4 主提示词(Prompt)**

```
## 比对任务
对以下旧版和新版制度文档进行逐条差异比对，输出完整的差异清单。

## 比对规则
1. 按章节/条款维度逐条比对，不要遗漏任何差异
2. 每个差异项必须标注以下信息：
   - 章节位置（如"第三章第十二条"）
   - 差异类型：added（新增）/ deleted（删除）/ modified（修改）
   - 旧版内容（added类型为空）
   - 新版内容（deleted类型为空）
   - 变更说明（一句话描述变更要点）
   - 影响程度：major（重大变更）/ minor（一般变更）/ editorial（文字修订）
3. 影响程度判定标准：
   - major：涉及合规要求、审批流程、权责划分、处罚标准等实质性变更
   - minor：涉及流程优化、时限调整、表格格式等操作性变更
   - editorial：涉及错别字修正、条款编号调整、表述优化等文字性变更
4. 如新版新增了整章节，逐条列出新增条款
5. 如旧版章节在新版中被整体删除，标注为deleted

## 输出格式
按以下格式输出每个差异项：

---
差异项 #1
章节位置：第X章第X条
差异类型：added/deleted/modified
旧版内容：（原文或"无"）
新版内容：（原文或"无"）
变更说明：一句话描述
影响程度：major/minor/editorial
---

## 旧版文档
{{old_content}}

## 新版文档
{{new_content}}
```

!!! warning "变量名一致"
    Prompt中的 `{{old_content}}` 和 `{{new_content}}` 必须和输入变量名完全一致。

---

### 步骤7：配置「差异提取(PARAMETER_EXTRACTOR)」节点

**7.1 基础配置**

| 参数 | 填写值 |
|---|---|
| 模型(ModelName) | `Youtu/youtu-intent-pro` |
| Temperature | `0` |

**7.2 输入变量**

| 变量名 | 引用节点 | 引用字段 |
|---|---|---|
| `user_input` | 差异分析 | Output.Content |

**7.3 提取提示词(UserConstraint)**

```
请从以下差异分析结果中精确提取参数：{{user_input}}

提取规则：
- diff_count：差异项总数，纯数字
- major_count：重大变更(major)数量，纯数字
- minor_count：一般变更(minor)数量，纯数字
- editorial_count：文字修订(editorial)数量，纯数字
- added_items：新增条款清单，每项格式为"章节位置→新版内容摘要"，多项用分号分隔
- deleted_items：删除条款清单，每项格式为"章节位置→旧版内容摘要"，多项用分号分隔
- modified_items：修改条款清单，每项格式为"章节位置→变更说明"，多项用分号分隔
- summary：整体变更概述，一段话总结本次版本变更的主要内容
```

**7.4 参数定义（8个）**

| # | 参数名 | 类型 | 必填 | 描述（≤30字符） |
|---|---|---|---|---|
| 1 | `diff_count` | STRING | 是 | 差异项总数 |
| 2 | `major_count` | STRING | 是 | 重大变更数量 |
| 3 | `minor_count` | STRING | 是 | 一般变更数量 |
| 4 | `editorial_count` | STRING | 是 | 文字修订数量 |
| 5 | `added_items` | STRING | 否 | 新增条款清单 |
| 6 | `deleted_items` | STRING | 否 | 删除条款清单 |
| 7 | `modified_items` | STRING | 否 | 修改条款清单 |
| 8 | `summary` | STRING | 是 | 整体变更概述 |

**7.5 输出定义（8个）**

!!! danger "必须手动补齐8个输出字段"
    不能只保留默认的 `keyword`，否则下游ANSWER引用时会报"变量值必填"错误。

| # | 输出字段名 | 类型 |
|---|---|---|
| 1 | `diff_count` | STRING |
| 2 | `major_count` | STRING |
| 3 | `minor_count` | STRING |
| 4 | `editorial_count` | STRING |
| 5 | `added_items` | STRING |
| 6 | `deleted_items` | STRING |
| 7 | `modified_items` | STRING |
| 8 | `summary` | STRING |

---

### 步骤8：配置「差异清单输出(ANSWER)」节点

**8.1 输入变量（8个，全部引用差异提取的输出）**

| 变量名 | 引用节点 | 引用字段 |
|---|---|---|
| `diff_count` | 差异提取 | Output.diff_count |
| `major_count` | 差异提取 | Output.major_count |
| `minor_count` | 差异提取 | Output.minor_count |
| `editorial_count` | 差异提取 | Output.editorial_count |
| `added_items` | 差异提取 | Output.added_items |
| `deleted_items` | 差异提取 | Output.deleted_items |
| `modified_items` | 差异提取 | Output.modified_items |
| `summary` | 差异提取 | Output.summary |

**8.2 回复模板**

```
📋 制度版本比对差异清单

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 变更统计
- 差异项总数：{{diff_count}} 项
- 🔴 重大变更：{{major_count}} 项
- 🟡 一般变更：{{minor_count}} 项
- 🟢 文字修订：{{editorial_count}} 项

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 变更概述
{{summary}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

➕ 新增条款
{{added_items}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

➖ 删除条款
{{deleted_items}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 修改条款
{{modified_items}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 免责声明：本差异清单由AI系统自动生成，仅供参考。建议人工复核重大变更项，确认比对完整性后正式使用。
```

### 步骤9：保存工作流

点击画布右上角「保存」按钮。

---

## 五、调试测试

=== "测试1：基础差异比对"

    **准备测试文件**：

    旧版（`制度v1.txt`）：
    ```
    第一章 总则
    第一条 本制度适用于公司全体员工。
    第二条 合规管理由合规部负责。

    第二章 营销宣传管理
    第三条 营销宣传材料须经合规部审核后方可发布。
    第四条 禁止使用"保本""保收益"等表述。

    第三章 罚则
    第五条 违反本制度的，处以警告。
    ```

    新版（`制度v2.txt`）：
    ```
    第一章 总则
    第一条 本制度适用于公司全体员工及外包人员。
    第二条 合规管理由合规部负责，各部门应设合规联络员。

    第二章 营销宣传管理
    第三条 营销宣传材料须经合规部审核后方可发布，审核时限为3个工作日。
    第四条 禁止使用"保本""保收益""稳赚""无风险"等表述。

    第三章 罚则
    第五条 违反本制度的，处以警告；情节严重的，处以罚款5000-20000元。

    第四章 附则
    第六条 本制度自发布之日起施行，原制度同时废止。
    ```

    **预期输出**：
    ```
    📋 制度版本比对差异清单

    📊 变更统计
    - 差异项总数：6 项
    - 🔴 重大变更：3 项
    - 🟡 一般变更：2 项
    - 🟢 文字修订：1 项

    📝 变更概述
    本次版本更新主要涉及：适用范围扩大至外包人员、新增合规联络员制度、
    营销宣传审核增加时限要求、禁语词表扩充、罚则加重并新增附则章节。

    ➕ 新增条款
    第四章第六条→本制度自发布之日起施行，原制度同时废止

    ➖ 删除条款
    无整体删除条款

    📝 修改条款
    第一章第一条→适用范围扩大至外包人员；第二章第三条→增加审核时限3个工作日；
    第二章第四条→禁语新增"稳赚""无风险"；第三章第五条→新增罚款5000-20000元
    ```

    **验证要点**：diff_count=6，major_count=3，added_items包含第四章第六条

=== "测试2：大文档"

    上传两份较长制度文档（10页以上），验证LLM能否处理长文本。

    **预期**：MaxTokens=8192应足够。如输出被截断，增大到16384。

=== "测试3：无差异"

    上传两份完全相同的文档。

    **预期**：diff_count=0，summary="两版文档内容一致，未检出差异。"

=== "测试4：整章节删除"

    旧版有5章，新版删除了其中1章。

    **预期**：deleted_items包含被删除章节的所有条款。

---

## 六、调试排查指南

| # | 报错信息 | 位置 | 原因 | 修复 |
|---|---|---|---|---|
| 1 | "引用变量old_content未声明" | LLM | 旧版解析引用路径不对 | 确认引用「旧版文档解析」→Output.Data.Answer |
| 2 | "引用变量new_content未声明" | LLM | 新版解析引用路径不对 | 确认引用「新版文档解析」→Output.Data.Answer |
| 3 | "DocParse解析失败" | DocParse | 文件格式不支持或损坏 | 确认文件为PDF/DOC/DOCX/TXT格式 |
| 4 | "两个DocParse解析了同一个文件" | DocParse | 两个节点都连接了同一个FILE_COLLECTION | 改为两个独立的FILE_COLLECTION节点 |
| 5 | "LLM输出不完整/被截断" | LLM | MaxTokens不够 | 增大MaxTokens到8192或16384 |
| 6 | "差异提取输出为空" | PARAM_EXT | 输出定义只有keyword | 补齐8个输出字段 |
| 7 | "变量值必填" | ANSWER | ANSWER引用的变量在上游不存在 | 确认PARAM_EXT输出定义8个字段已添加 |
| 8 | "LLM只分析了旧版/新版" | LLM | 只接了一个DocParse的输入 | 确认LLM有2个输入变量(old_content+new_content) |
| 9 | "差异项数量不准确" | PARAM_EXT | 模型提取计数不准 | 在UserConstraint中强调"仔细计数，不要遗漏" |

### 数据流断裂检查顺序

```
1. 旧版FILE_COLLECTION → FileCount=1？FileList有内容？
   ↓
2. 新版FILE_COLLECTION → FileCount=1？FileList有内容？
   ↓
3. 旧版DocParse → Output.Data.Answer是否有旧版文档内容？
   ↓
4. 新版DocParse → Output.Data.Answer是否有新版文档内容？
   ↓
5. LLM → Output.Content是否包含逐条差异分析？
   ↓
6. PARAM_EXT → Output.diff_count等8个字段是否有值？
   ↓
7. ANSWER → 输出是否包含统计、概述、新增/删除/修改清单？
```

---

## 七、发布前检查清单

- [ ] 工作流 regulation_diff_check 已保存
- [ ] 调试通过（测试1~测试4）
- [ ] 两个FILE_COLLECTION MaxAllowedUploadFileCount=1
- [ ] 两个DocParse节点分别解析旧版和新版
- [ ] LLM有2个输入变量(old_content+new_content)
- [ ] PARAM_EXT输出定义8个字段已补齐
- [ ] 知识库文档已上传且状态为"导入完成"
- [ ] 安全设置已开启（内容安全/保守回答/隐私脱敏）

**发布操作**：应用管理 → 选择应用 → 发布 → 填写说明 `制度版本比对，双文件上传自动生成差异清单` → 确认发布

---

## 附录A：节点配置速查表

| 节点 | 类型 | 关键配置 |
|---|---|---|
| 开始 | START | Outputs为空 |
| 旧版文件收集 | FILE_COLLECTION | MaxFiles: 1, FileType: DOCUMENT |
| 新版文件收集 | FILE_COLLECTION | MaxFiles: 1, FileType: DOCUMENT |
| 旧版文档解析 | PLUGIN | DocParse, 输出Output.Data.Answer |
| 新版文档解析 | PLUGIN | DocParse, 输出Output.Data.Answer |
| 差异分析 | LLM | Model: deepseek-v3.2, Temp: 0, MaxTokens: 8192, Inputs: old_content+new_content |
| 差异提取 | PARAMETER_EXTRACTOR | Model: youtu-intent-pro, 8参数, 8输出 |
| 差异清单输出 | ANSWER | 8变量引用, 含统计+清单+免责声明 |
| 结束 | END | — |

---

## 附录B：影响程度判定参考

| 影响程度 | 判定标准 | 典型示例 |
|---|---|---|
| 🔴 major | 合规要求、审批流程、权责划分、处罚标准变更 | 罚款金额调整、新增审批层级、适用范围扩大 |
| 🟡 minor | 流程优化、时限调整、表格格式等操作性变更 | 审核时限从5天改为3天、新增联络员制度 |
| 🟢 editorial | 错别字修正、条款编号调整、表述优化 | 文字规范化、错别字纠正、附则说明 |
