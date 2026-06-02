# 数据集收集方法取证分析

> 当用户问"这个数据集/GitHub仓库是怎么收集到这些数据的？他们逆向了什么？"
> 时使用此方法。不是逆向API协议本身，而是**从数据特征推断收集方法**。

## 适用场景

- 分析 GitHub 仓库的数据来源（如 fmz200/global-testflight-link）
- 判断数据集是爬虫、暴力枚举、API逆向还是人工收集
- 评估自己能否复现相同数据收集

## 5步取证流程

### Step 1: 仓库结构扫描

```bash
# 获取仓库元数据
curl -s "https://api.github.com/repos/{owner}/{repo}" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k in ['description','language','size','created_at','updated_at','stargazers_count']:
    print(f'{k}: {d.get(k)}')"

# 列出根目录
curl -s "https://api.github.com/repos/{owner}/{repo}/contents/" | python3 -c "
import sys, json
for item in json.load(sys.stdin):
    print(f'{item[\"type\"]:4s} {item[\"size\"]:>6d} {item[\"name\"]}')"

# 重点看: scripts/ .github/workflows/ data/ db/ 目录
```

### Step 2: 数据库/数据文件格式分析

如果存在 SQLite DB / JSON / CSV：
- **下载并分析 schema**：表结构、字段类型、主键
- **统计分布**：状态值分布、时间分布、平台分布
- **关键字段**：ID格式、charset、长度

```python
import sqlite3
from collections import Counter

conn = sqlite3.connect('data.db')
cur = conn.cursor()

# 1. Schema
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
# 2. 每张表: PRAGMA table_info, COUNT, 样本行
# 3. 状态/分类分布: SELECT status, COUNT(*) GROUP BY status
# 4. ID格式: 长度分布、charset分析
```

### Step 3: 时间戳聚类（判断是一次性还是持续积累）

```python
# 关键查询：按日期统计创建量
cur.execute('SELECT date(create_time), COUNT(*) FROM table GROUP BY date(create_time) ORDER BY date(create_time)')

# 判断标准：
# - 全部集中在1-2天 → 一次性批量扫描/导入
# - 均匀分布 → 持续积累/社区贡献
# - 有几个spike → 间歇性批量导入
```

### Step 4: ID/Key 空间分析（判断暴力枚举 vs 定向收集）

```python
# ID charset分析
charset = set()
for id in all_ids:
    charset.update(id)
# 如果charset = [0-9A-Za-z] → base62编码
# 如果charset = [0-9a-f] → hex/md5

# 长度分布
# 如果全部固定长度 → 可能是暴力枚举的目标keyspace

# Keyspace计算
charset_size = len(charset)  # e.g. 62
id_length = len(all_ids[0])  # e.g. 8
keyspace = charset_size ** id_length  # e.g. 62^8 = 218万亿

# 前缀覆盖率（2-char, 3-char）
# 2-char覆盖率接近100% → 系统性扫描
# 2-char覆盖率低 → 定向收集
prefix2_dist = {}
for id in all_ids:
    prefix2_dist[id[:2]] = prefix2_dist.get(id[:2], 0) + 1
coverage = len(prefix2_dist) / (charset_size ** 2) * 100
```

### Step 5: 源码审查（脚本/工作流）

```bash
# 下载关键脚本
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/{script_path}"

# 下载 GitHub Actions 工作流
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/.github/workflows/{workflow}.yml"

# 看什么：
# - 请求了什么URL/API？→ 数据来源
# - 用了什么认证？→ 是否需要API key/token
# - 解析了什么内容？→ HTML关键词？JSON字段？
# - 并发/速率控制？→ 扫描规模和策略
# - cron schedule？→ 更新频率
```

## 判断矩阵

| 证据 | 暴力枚举 | API逆向 | 爬虫/扫描 | 社区贡献 |
|------|---------|---------|----------|---------|
| 全部记录同一天创建 | ✅ | 可能 | 可能 | ❌ |
| ID覆盖整个keyspace前缀 | ✅ | ❌ | ❌ | ❌ |
| 大量状态Unknown | ✅ | ❌ | ❌ | ❌ |
| 有GitHub Actions添加入口 | ❌ | ❌ | ❌ | ✅ |
| 脚本中有私有API URL | ❌ | ✅ | ❌ | ❌ |
| 脚本只解析HTML关键词 | ❌ | ❌ | ✅ | ❌ |
| 数据量>1万 | ✅ | 可能 | ✅ | 可能 |
| app_name填充率<50% | ✅ | ❌ | 可能 | ❌ |
| 有workflow_dispatch输入表单 | ❌ | ❌ | ❌ | ✅ |

## 实战案例：TestFlight链接收集

### fmz200/global-testflight-link（暴力枚举）
- 26202条全部在 2025-08-17 同一天创建
- TF ID 固定8位base62，2-char前缀覆盖99.8%
- 52%状态Unknown，80%无app_name
- 结论：穷举 `https://testflight.apple.com/join/{8位base62}`

### pluwen/awesome-testflight-link（社区贡献）
- 843条，跨6年积累
- GitHub Actions手动添加链接，每日定时检测状态
- 状态判断纯靠HTML关键词匹配（满/不可加入/404/可加入）
- 结论：用户提交 + `GET /join/{id}` 页面解析

### 共同点：都没有逆向任何私有API
- 唯一数据源：`GET https://testflight.apple.com/join/{id}`
- 状态判断：HTML关键词匹配
- app_name提取：HTML title正则
