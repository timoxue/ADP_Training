# Skills · Claude Code 技能库

本目录收录本项目配套的 Claude Code Skills，可直接安装到本地 Claude Code 使用。

## 技能列表

| 技能 | 说明 | 适用场景 |
|------|------|---------|
| [adp-prompt-builder](adp-prompt-builder/) | ADP 提示词框架构建器，对话式引导逐步写好角色指令 | 搭建 ADP 应用时写提示词 |
| [adp-six-step-guide](adp-six-step-guide/) | ADP 六步推理链引导，从业务痛点到可运行智能体全流程 | 规划和搭建 ADP 智能体应用 |
| [a-stock-data](a-stock-data/) | A股全栈数据工具包，七层27端点，行情/研报/信号/公告 | 投研、量化、个股分析 |
| [wiki-crawler](wiki-crawler/) | 文档站全量爬取，自动转存为结构化 Markdown | 离线备份文档、知识库导入 |

## 一键安装所有技能

```bash
# 克隆仓库
git clone git@github.com:timoxue/ADP_Training.git
cd ADP_Training

# macOS / Linux
cp -r skills/adp-prompt-builder ~/.claude/skills/
cp -r skills/adp-six-step-guide ~/.claude/skills/
cp -r skills/a-stock-data ~/.claude/skills/
cp -r skills/wiki-crawler ~/.claude/skills/

# Windows（Git Bash）
for skill in adp-prompt-builder adp-six-step-guide a-stock-data wiki-crawler; do
  cp -r "skills/$skill" "$USERPROFILE/.claude/skills/"
done
```

安装完成后重启 Claude Code：

```bash
claude
```

## 单独安装某个技能

每个技能目录下的 README.md 有独立的安装步骤，按需选装。

## 技能依赖

| 技能 | 额外依赖 |
|------|---------|
| adp-prompt-builder | 无 |
| adp-six-step-guide | 无 |
| a-stock-data | `pip install mootdx requests` |
| wiki-crawler | `pip install playwright markdownify beautifulsoup4 requests` + `playwright install chromium` |

## 目录结构

```
skills/
├── README.md                    ← 本文件
├── adp-prompt-builder/
│   ├── SKILL.md
│   └── README.md
├── adp-six-step-guide/
│   ├── SKILL.md
│   ├── README.md
│   └── references/              ← 7 个参考文件
├── a-stock-data/
│   ├── SKILL.md
│   └── README.md
└── wiki-crawler/
    ├── SKILL.md
    ├── README.md
    └── scripts/
        └── wiki_crawler.py
```
