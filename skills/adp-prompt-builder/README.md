# ADP 提示词框架构建器

基于腾讯云智能体开发平台（ADP）官方文档提炼的提示词构建技能，通过对话式引导帮助你逐步完成一个符合 ADP 最佳实践的角色指令。

## 功能

- 支持**标准模式 / Agent 模式 / Multi-Agent 模式**三种应用类型
- 逐步引导补全角色、风格、输出要求、能力限制四大框架要素
- 内置 ADP 平台变量语法（`{{SYS.Memory}}`、`{{API.UserName}}` 等）
- 专设**证券 / 金融 / 医疗等受监管行业**合规确认环节
- 输出可直接粘贴进 ADP 平台「角色指令」文本框的完整提示词

## 安装

### 前提条件

- 已安装 [Claude Code](https://claude.ai/code) CLI

### 步骤

**1. 克隆此仓库（或只下载 skill 文件夹）**

```bash
git clone git@github.com:timoxue/ADP_Training.git
```

**2. 将 skill 复制到 Claude Code 的 skills 目录**

```bash
# macOS / Linux
cp -r ADP_Training/skills/adp-prompt-builder ~/.claude/skills/

# Windows（Git Bash）
cp -r ADP_Training/skills/adp-prompt-builder "C:/Users/<你的用户名>/.claude/skills/"
```

**3. 重启 Claude Code 使 skill 生效**

```bash
claude
```

### 验证安装

启动 Claude Code 后，输入以下内容触发 skill：

```
我想用 ADP 平台搭建一个智能助手
```

Claude 会自动识别并进入引导流程。

## 使用方式

直接描述你的需求即可触发：

```
帮我写一个 ADP 应用的提示词，标准模式，客服场景
```

```
我的 ADP 提示词写好了，帮我检查一下框架是否完整
```

```
我在券商搭 ADP 研报助手，帮我完善提示词
```

## 引导流程

```
Step 1  确认应用模式（标准 / Agent / Multi-Agent）
Step 2  收集现有提示词草稿或需求描述
Step 3  诊断缺失的框架要素
Step 4  逐项补全（每次只问一个问题）
Step 4.5  个性化变量需求确认
Step 4.6  受监管行业合规确认（证券 / 银行 / 医疗等）
Step 5  输出完整提示词（可直接粘贴）
Step 6  提示 ADP 平台后续优化功能
```

## ADP 平台对应功能

| Skill 引导项 | ADP 平台位置 |
|-------------|-------------|
| 角色指令框架 | 应用设置 → 角色指令 |
| AI 一键优化 | 角色指令 → 一键优化 |
| 保存为模板 | 角色指令 → 模板 → 保存为模板 |
| 版本管理 | 角色指令 → 版本 |
| 变量 `{{API.XXX}}` | 应用设置 → 变量与记忆 |
| 保守回答 | 应用设置 → 回复设置 |
| 内容安全 | 应用设置 → 内容安全 |

## 文件结构

```
adp-prompt-builder/
├── SKILL.md      # Skill 主体（Claude Code 读取此文件）
└── README.md     # 本文件
```

## 适用版本

- Claude Code 任意版本
- 腾讯云 ADP 平台（文档版本截至 2026-06）
