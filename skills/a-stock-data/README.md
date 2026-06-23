# a-stock-data · A股全栈数据工具包

A 股全栈数据 Claude Code Skill，七层数据架构、27 个端点，覆盖行情、研报、信号、资金面、新闻、基础数据、公告，内嵌全部调用代码，自包含零外部依赖文件。

> 原作者：Simon 林 · [github.com/simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data)  
> 版本：V3.2.2 · 2026-06 验证可用

## 功能

| Layer | 数据类型 | 主要数据源 |
|-------|---------|-----------|
| 1 · 行情 | K线、实时报价、PE/PB/市值、五档盘口 | mootdx · 腾讯（不封 IP） |
| 2 · 研报 | 研报列表/PDF、一致预期 EPS、语义搜索 | 东财 · 同花顺 · iwencai |
| 3 · 信号 | 热点题材、北向资金、龙虎榜、解禁日历 | 同花顺 · 东财 |
| 4 · 资金面 | 融资融券、大宗交易、股东户数、120日资金流 | 东财 |
| 5 · 新闻 | 个股新闻、全球资讯（7×24） | 东财 |
| 6 · 基础数据 | 财务快照、三张报表、F10 | mootdx · 新浪 |
| 7 · 公告 | 完整公告全文 + 摘要 | 巨潮 · mootdx |

## 安装

**前提条件**：已安装 [Claude Code](https://claude.ai/code) CLI 及 Python 3.8+

```bash
# 1. 克隆仓库
git clone git@github.com:timoxue/ADP_Training.git

# 2. 复制到 Claude Code skills 目录
# macOS / Linux
cp -r ADP_Training/skills/a-stock-data ~/.claude/skills/

# Windows（Git Bash）
cp -r ADP_Training/skills/a-stock-data "$USERPROFILE/.claude/skills/"

# 3. 安装 Python 依赖
pip install mootdx requests
```

**可选**：iwencai 语义搜索研报需要 API Key

```bash
# 申请：https://www.iwencai.com/skillhub
export IWENCAI_API_KEY="your_key_here"
```

## 触发方式

```
查一下宁德时代最新的 PE 和市值
```
```
拉茅台今日龙虎榜数据
```
```
搜索光伏行业最新研报，返回 PDF 链接
```
```
查平安银行最近 10 条公告
```
```
获取宁德时代近三年三张财务报表
```

## 防封说明

东财接口有风控（>5次/秒即封 IP），Skill 内已内置统一节流入口 `em_get()`，所有东财请求自动串行限流 + 随机抖动，直接调用即安全。mootdx / 腾讯接口不封 IP，优先使用。

## 文件结构

```
a-stock-data/
├── SKILL.md      # Skill 主体（含全部调用代码）
└── README.md     # 本文件
```

## 适用版本

- Claude Code 任意版本
- Python 3.8+，mootdx 最新版
- 接口状态：2026-06 验证，27 个端点可用
