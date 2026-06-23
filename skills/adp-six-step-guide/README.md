# adp-six-step-guide · ADP 六步推理链引导技能

帮助用户用「六步推理链」方法论从业务痛点出发，一步步完成腾讯云 ADP 智能体应用的设计与搭建。每步有依据、有案例、有验收标准，不跳步，不返工。

## 功能

- **六步递进引导**：业务产出物 → 能力拆解 → 功能映射 → 设计推理 → 分步操作 → 验收
- **四种模式全覆盖**：Claw / 标准 / 单工作流 / Multi-Agent，每种模式有专属操作清单
- **能力映射自动化**：经验初筛 + 平台搜索双轮映射，覆盖 100+ Skills
- **合规治理内嵌**：证券/金融场景六大治理机制、检出/拦截/脱敏三层区分
- **三种搭建方式**：手工搭建 / 半自动 / 全自动（含二次确认保护）
- **附随参考文件**：案例库、技能映射表、操作清单、合规治理、常见坑

## 安装

**前提条件**：已安装 [Claude Code](https://claude.ai/code) CLI

```bash
# 1. 克隆仓库
git clone git@github.com:timoxue/ADP_Training.git

# 2. 复制到 Claude Code skills 目录
# macOS / Linux
cp -r ADP_Training/skills/adp-six-step-guide ~/.claude/skills/

# Windows（Git Bash）
cp -r ADP_Training/skills/adp-six-step-guide "$USERPROFILE/.claude/skills/"

# 3. 重启 Claude Code
claude
```

## 触发方式

```
我想在 ADP 上搭一个投研助手
```
```
帮我用六步推理链分析财富投顾助手的搭建方案
```
```
ADP 标准模式和 Claw 模式怎么选？
```
```
帮我搭一个证券合规预检的工作流应用
```

## 六步流程

```
Step 1  业务产出物   — 先定义交付物：给谁、产出什么格式的结果
Step 2  能力拆解     — 要产出它，需要哪几种能力？P0/P1/P2 优先级
Step 3  功能映射     — 每种能力对应 ADP 哪个 Skill/功能/模式
Step 4  设计推理     — 为什么选它？边界在哪？超出边界怎么兜底
Step 5  分步操作     — 手工/半自动/全自动三选一，逐步确认执行
Step 6  验收         — 验收用例、常见坑、调优方向
```

## 参考文件

| 文件 | 内容 |
|------|------|
| `references/case-studies.md` | 投研助手、财富投顾、投研小团队三个完整案例 |
| `references/skill-mapping.md` | ADP 能力 → Skills 映射表 + 四种模式对照 |
| `references/operation-checklist.md` | 四种模式的完整操作步骤清单 |
| `references/compliance-governance.md` | 六大治理机制、三条红线、检出/拦截/脱敏区分 |
| `references/design-decisions.md` | 常见设计决策：RAG vs API、模式选择、风控层级 |
| `references/pitfalls.md` | 常见错误与避坑指南 |
| `references/templates.md` | 交付物、提示词、验收用例模板 |

## 文件结构

```
adp-six-step-guide/
├── SKILL.md              # Skill 主体
├── README.md             # 本文件
└── references/
    ├── case-studies.md
    ├── skill-mapping.md
    ├── operation-checklist.md
    ├── compliance-governance.md
    ├── design-decisions.md
    ├── pitfalls.md
    └── templates.md
```

## 适用版本

- Claude Code 任意版本
- 腾讯云 ADP 平台（文档版本截至 2026-06）
