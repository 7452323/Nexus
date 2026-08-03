# Har - HAR 文件分析工具集

> 抓包分析 → 去广告 / 爆破会员

## 灵感与研究

深入分析以下开源项目后，取其精华整合而成：

### 1. [JustusW/harparser](https://github.com/JustusW/harparser) (Python, 17⭐)
- **最近更新**: 2026-07-20
- **核心设计**: 完整实现 HAR 1.2 规范
  - `HAREncodable` 基类基于 `MutableMapping`，支持递归 HAR 结构
  - `_HAR` 类把 spec 映射为动态子类（`type()` 生成）
  - 自动类型转换（str/int/bool/dict/list）
- **借鉴点**: HAR 数据模型的规范化解析思路

### 2. [PureWaterSun/har-analyzer](https://github.com/PureWaterSun/har-analyzer) (JS, 6⭐)
- **最近更新**: 2026-05-24
- **核心功能**:
  - 拖拽上传 HAR
  - 多维度过滤（method / statusCode / contentType）
  - 搜索高亮
  - 请求列表 + 4-tab 详情面板（General / Request / Response / Timing）
  - 键盘导航 + 滚动同步
- **借鉴点**: 过滤/搜索 UI 逻辑 → 转为 CLI 过滤参数

### 3. [kevinfarrugia/hara](https://github.com/kevinfarrugia/hara) (Node.js CLI, 9⭐)
- **最近更新**: 2026-02-04
- **分支**: main / csv-output / wpt-format / linting
- **核心能力**:
  - 按资源类型分类统计（document/font/image/stylesheet/script/xhr/other）
  - 计算中位数 / 95th 百分位
  - `csv-output` 分支: CSV 表格导出
  - `wpt-format` 分支: WebPageTest HAR 兼容
- **借鉴点**: 请求分类统计 + 多格式导出

### 4. [mfoulks3200/har-analyzer](https://github.com/mfoulks3200/har-analyzer) (VS Code, 13⭐)
- **最近更新**: 2026-02-27
- **核心**: VS Code Webview 面板 + 消息传递机制
- **借鉴点**: 大文件处理策略（>5MB 用 URL 加载）

## 工具清单

| 文件 | 说明 |
|------|------|
| `har_analyzer.py` | 综合 HAR 分析脚本（命令行） |
| `harparser/` | 参考: 完整 HAR 1.2 规范解析 |
| `purewater-har/` | 参考: 前端 HAR 分析器 |
| `hara/` | 参考: 性能统计 + CSV 导出 |
| `vscode-har/` | 参考: VS Code 扩展 |

## 使用方法

```bash
# 查看摘要统计
python3 har_analyzer.py sample.har -s

# 搜索 VIP 相关请求（爆破会员）
python3 har_analyzer.py sample.har --find-vip

# 查找广告请求（去广告）
python3 har_analyzer.py sample.har --find-ads

# 搜索关键词
python3 har_analyzer.py sample.har --search "vip_level"

# 按域名过滤
python3 har_analyzer.py sample.har --domain "api.example.com"

# 按方法+状态码过滤
python3 har_analyzer.py sample.har --method POST --status 200

# 导出过滤结果为 JSON
python3 har_analyzer.py sample.har --find-vip --export-json vips.json

# 导出为 CSV
python3 har_analyzer.py sample.har -s --export-csv report.csv

# URL 包含 + 响应体包含
python3 har_analyzer.py sample.har --url-contains "/api/" --response-contains "is_vip"
```

## 在代码中使用

```python
from har_analyzer import HARAnalyzer

analyzer = HARAnalyzer('capture.har')

# VIP 相关请求
vip_reqs = analyzer.find_vip_related()
for req in vip_reqs:
    print(req.url)
    print(req.response_json)  # 自动解析 JSON

# 自定义过滤
ads = analyzer.filter(
    domain='adservice',
    method='GET',
    resource_type='image'
)

# 搜索关键词
results = analyzer.search('vip_level', in_response=True)

# 按域名统计
stats = analyzer.get_statistics()
for domain, count in stats['by_domain'].items():
    print(f'{domain}: {count}')
```

## 工作流（爆破会员/去广告）

```
1. 抓包导出 HAR
       ↓
2. python3 har_analyzer.py capture.har --find-vip --export-json vip_apis.json
       ↓
3. 分析响应体，定位关键字段（vip_level / is_vip / expire_time）
       ↓
4. 写 QX/Surge/Loon 脚本:
   - script-response-body 改响应体
   - hostname=.reject 去广告
       ↓
5. 验证
```

## 参考项目更新时间表

| 项目 | 最近更新 | Stars |
|------|----------|-------|
| JustusW/harparser | 2026-07-20 | 17 |
| PureWaterSun/har-analyzer | 2026-05-24 | 6 |
| kevinfarrugia/hara | 2026-02-04 | 9 |
| mfoulks3200/har-analyzer | 2026-02-27 | 13 |
