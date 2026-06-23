# a-stock-data · A股全栈数据工具包

> 版本 V3.2.2 · 2026-06 验证可用 · 27 个端点  
> 来源：[github.com/simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data)

---

## 七层数据架构

| Layer | 分类 | 数据源 | 典型用途 |
|-------|------|--------|---------|
| **1** | 行情层 | mootdx · 腾讯 · 百度 | K线、实时报价、PE/PB/市值、五档盘口 |
| **2** | 研报层 | 东财 · 同花顺 · iwencai | 研报列表/PDF下载、一致预期EPS、语义搜索 |
| **3** | 信号层 | 同花顺 · 东财 | 热点题材、北向资金、龙虎榜、解禁日历、行业排名 |
| **4** | 资金面/筹码层 | 东财 | 融资融券、大宗交易、股东户数、分红、120日资金流 |
| **5** | 新闻层 | 东财 | 个股新闻、全球资讯（7×24） |
| **6** | 基础数据层 | mootdx · 东财 · 新浪 | 财务快照、F10、三张报表（资产负债/利润/现金流） |
| **7** | 公告层 | 巨潮 · mootdx | 正式公告全文、F10公告摘要 |

---

## 数据源优先级（重要）

**原则：能用通达信/腾讯，就别用东财。**

| 数据源 | 特点 | 优先使用场景 |
|--------|------|------------|
| **mootdx（通达信）** | 不封 IP，稳定 | K线、财务快照、F10、公告摘要 |
| **腾讯财经** | 不封 IP，字段丰富 | PE/PB/市值/换手/涨跌停/指数/ETF |
| **东财** | 封 IP 风险高，有独家数据 | 研报、资金流、龙虎榜、新闻（唯一来源才用） |
| **同花顺** | 热点/北向独家 | 当日强势股题材、北向资金分钟级 |
| **新浪** | 三张报表 | 财务报表历史数据 |
| **巨潮（cninfo）** | 官方公告 | 完整公告全文，动态查 orgId |
| **iwencai** | 语义搜索研报（唯一） | 自然语言检索研报，需 API Key |

!!! warning "东财防封铁律"
    - 所有东财请求走统一节流入口 `em_get()`，已内置串行限流（间隔 ≥1s + 随机抖动）
    - 东财风控阈值（社区实测）：每秒 >5 次 / 单 IP 并发 ≥10 / 1 分钟 ≥200 次 → 临时封 IP
    - 部分大陆住宅 IP 被东财间歇风控（HTTP 000/空），属正常现象，加重试或换网络

---

## 各层主要端点

### Layer 1 · 行情层

| 端点 | 来源 | 返回字段 |
|------|------|---------|
| K线数据 | mootdx | open/close/high/low/vol/amount/datetime |
| 实时报价（46字段） | mootdx | price/open/high/low/bid1~5/ask1~5/vol/amount |
| 逐笔成交 | mootdx | time/price/vol/buyorsell（0买/1卖/2中性） |
| PE/PB/市值/换手 | 腾讯财经 | pe/pb/market_cap/turnover/涨跌停标志 |
| 带MA均线的K线 | 百度股市通 | ma5/ma10/ma20avgprice |

### Layer 2 · 研报层

| 端点 | 来源 | 说明 |
|------|------|------|
| 研报列表 + PDF 下载 | 东财 | 按股票/日期/机构筛选，返回 PDF 直链 |
| 一致预期 EPS | 同花顺 | 分析师盈利预测，机构数 <3 需谨慎 |
| 语义搜索研报 | iwencai | 自然语言查研报，**需 API Key**，申请见 iwencai.com |

### Layer 3 · 信号层

| 端点 | 来源 | 说明 |
|------|------|------|
| 当日强势股 + 题材归因 | 同花顺热点 | 独家 reason tags，词频统计题材热度 |
| 北向资金分钟流向 | 同花顺 hsgtApi | 实时 + 本地自缓存历史 |
| 个股板块/概念归属 | 东财 slist | 行业/概念/地域 + BK码 + 龙头股 |
| 个股资金流向（分钟级） | 东财 push2 | 超大单/大单/中单/小单净流入 |
| 龙虎榜席位 + 机构动向 | 东财 | 上榜记录 + 买卖席位 TOP5 |
| 限售解禁日历 | 东财 | 历史解禁 + 未来 90 天待解禁 |
| 行业板块排名 | 东财 | 今日涨幅排名（同花顺已加反爬，改用东财） |
| 全市场龙虎榜 | 东财 | 按净买入金额筛选 |

### Layer 4 · 资金面/筹码层

| 端点 | 说明 |
|------|------|
| 融资融券明细 | 余额变化趋势 |
| 大宗交易 | 折溢价、买卖方席位 |
| 股东户数变化 | 筹码集中度判断 |
| 分红送转历史 | 历史分红记录 |
| 120日日级资金流 | 长周期资金趋势 |

### Layer 5 · 新闻层

| 端点 | 说明 |
|------|------|
| 东财个股新闻 | 公司相关新闻，直连 search-api-web |
| 东财全球资讯（7×24） | 替代已下线的财联社快讯 |

!!! note "财联社快讯已下线"
    cls.cn 旧 API 已全面 404（V3.2 标注弃用），改用东财全球资讯。

### Layer 6 · 基础数据层

| 端点 | 来源 | 说明 |
|------|------|------|
| 财务快照（37字段） | mootdx | 季报数据，含营收/净利/ROE等 |
| F10 公司文本资料 | mootdx | 公司简介、主营业务 |
| 个股基本面 | 东财 push2 | 实时财务指标 |
| 三张报表 | 新浪 | 资产负债表/利润表/现金流量表，按报告期展开 |

### Layer 7 · 公告层

| 端点 | 来源 | 说明 |
|------|------|------|
| 巨潮公告全文 | cninfo.com.cn | 动态查 orgId（含 6198 只股映射表），支持按类型/日期筛选 |
| F10 公告摘要 | mootdx | 轻量摘要，无需 orgId |

---

## 前置依赖

```bash
pip install mootdx requests
```

iwencai 语义搜索（可选）：

```bash
# 申请地址: https://www.iwencai.com/skillhub
# 注册后安装 SkillHub CLI → 安装 report-search 技能 → 获得 Key
export IWENCAI_API_KEY="your_key_here"
```

---

## 代码示例

### 获取实时报价

```python
from mootdx.quotes import Quotes
client = Quotes.factory(market='std')

# 单只股票实时报价（返回 46 个字段）
data = client.quotes(security='600519')  # 茅台
print(data['price'], data['vol'])
```

### 查询研报列表

```python
import requests, json

def eastmoney_reports(code, count=10):
    url = "https://reportapi.eastmoney.com/report/list"
    params = {
        "industryCode": "*", "pageSize": count,
        "industry": "*", "rating": "*",
        "ratingChange": "*", "beginTime": "2024-01-01",
        "endTime": "", "pageNo": 1, "fields": "",
        "qType": 0, "orgCode": "", "code": code,
        "rcode": "", "_": 1700000000000
    }
    r = requests.get(url, params=params, timeout=10)
    return r.json()["data"]["list"]
```

### 查询巨潮公告

```python
import requests

def cninfo_announcements(code, count=10):
    # 动态获取 orgId
    orgid_url = f"http://www.cninfo.com.cn/new/hisAnnouncement/query"
    # ... 详见 SKILL.md §7.1
    pass
```

---

## 证券场景典型用法

| 场景 | 推荐端点组合 |
|------|------------|
| 个股估值分析 | Layer1（PE/PB/市值）+ Layer6（三张报表）+ Layer2（研报EPS） |
| 题材归因 | Layer3（热点题材）+ Layer3（北向资金）+ Layer3（行业排名） |
| 解禁预警 | Layer3（解禁日历）+ Layer4（股东户数）|
| 投后跟踪 | Layer7（巨潮公告）+ Layer5（东财新闻）|
| 合规尽调 | Layer6（F10基本面）+ Layer7（公告全文）+ Layer2（研报）|

---

## Ticker 格式说明

```
沪市：sh600519（茅台）、sh000001（上证指数）
深市：sz000858（五粮液）、sz399006（创业板指）
ETF：sh510050（上证50）、sh510300（沪深300）

# mootdx 内部用 market + code
# market=1 上海，market=0 深圳
```
