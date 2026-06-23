# wiki-crawler · Wiki 文档站全量爬取技能

给定一个文档站 URL，自动爬取全部页面并转存为结构化 Markdown 文件，保留侧边栏层级、生成目录索引、下载图片、重写内部链接，支持断点续爬和完整性校验。

## 功能

- **自动侧边栏检测**：支持 Docusaurus、ReadTheDocs、Confluence、MediaWiki 等主流文档框架，检测失败时截图提示手动指定选择器
- **结构化输出**：按侧边栏层级生成目录，文件名格式 `01-section/01-page__slug.md`，自动生成 `README.md` 目录索引
- **图片去重下载**：相同内容（SHA-256）只下载一次，所有引用指向同一文件
- **内部链接重写**：页面间链接自动转换为相对 `.md` 路径
- **断点续爬**：`--resume` 跳过已完成页面，安全中断重启
- **完整性校验**：`--verify` 检查所有文件的 SHA-256，输出 PASS/FAIL

## 安装

**前提条件**：已安装 [Claude Code](https://claude.ai/code) CLI 及 Python 3.8+

```bash
# 1. 克隆仓库
git clone git@github.com:timoxue/ADP_Training.git

# 2. 复制到 Claude Code skills 目录
# macOS / Linux
cp -r ADP_Training/skills/wiki-crawler ~/.claude/skills/

# Windows（Git Bash）
cp -r ADP_Training/skills/wiki-crawler "$USERPROFILE/.claude/skills/"

# 3. 安装 Python 依赖
pip install playwright markdownify beautifulsoup4 requests
playwright install chromium
```

## 触发方式

```
帮我把这个文档站爬下来存成 Markdown：https://docs.example.com
```
```
爬取 https://docs.example.com，保存到 ./output
```
```
上次爬一半中断了，帮我继续：https://docs.example.com
```

## 直接运行脚本

```bash
# 基础用法（自动检测侧边栏）
python ~/.claude/skills/wiki-crawler/scripts/wiki_crawler.py <url> --outdir ./output

# 指定侧边栏选择器
python wiki_crawler.py <url> --outdir ./output --nav-selector "aside nav"

# 限制爬取深度
python wiki_crawler.py <url> --outdir ./output --max-depth 3

# 断点续爬
python wiki_crawler.py <url> --outdir ./output --resume

# 只重试失败页面
python wiki_crawler.py <url> --outdir ./output --retry-failed

# 完整性校验
python wiki_crawler.py --verify --outdir ./output
```

## 输出结构

```
output/
├── README.md                    ← 自动生成的目录索引
├── assets/images/<domain>/      ← 去重下载的图片
├── 01-getting-started/
│   ├── 01-installation__install.md
│   └── 02-quick-start__quickstart.md
├── manifest.json                ← URL、文件路径、SHA-256 校验和
└── failed.json                  ← 失败页面记录
```

每个 `.md` 文件包含 YAML frontmatter：

```markdown
---
title: Installation
source_url: https://docs.example.com/docs/install
crawled_at: 2026-06-14T10:23:45
---
```

## 登录墙处理

脚本使用 Playwright Chromium 有头浏览器，遇到需要登录的站点会弹出真实浏览器窗口，手动登录后爬取自动继续（复用你的登录态）。

## 文件结构

```
wiki-crawler/
├── SKILL.md              # Skill 主体
├── README.md             # 本文件
└── scripts/
    └── wiki_crawler.py   # 爬取脚本
```

## 适用版本

- Claude Code 任意版本
- Python 3.8+，Playwright 最新版
