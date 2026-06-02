# Task Artifact 目录与文件模板

## 目录结构

```
artifacts/tasks/<taskId>/
├── task.json                    # 任务元数据
├── network.jsonl                # 网络请求证据
├── scripts.jsonl                # 脚本证据
├── runtime-evidence.jsonl       # 运行时证据
├── env/
│   ├── env.js                   # 基础宿主对象
│   ├── polyfills.js             # 代理诊断层
│   ├── entry.js                 # 运行时入口
│   └── capture.json             # 页面证据快照
├── run/
│   ├── exported-runtime.js      # 便携运行时（阶段 2 产物）
│   ├── pure-*.js               # 纯算法实现（阶段 3 产物）
│   ├── pure_*.py               # Python 移植（可选）
│   └── fixtures.json           # 固定夹具
├── replay/
│   └── actions.json            # 页面动作复放
└── report.md                    # 结果报告
```

## 文件职责

### 必备文件（缺少会影响续做）

| 文件 | 职责 |
|------|------|
| `task.json` | 任务元数据：目标参数、URL、触发动作、验收条件 |
| `network.jsonl` | 网络请求证据：目标请求的 URL/headers/body/响应 |
| `scripts.jsonl` | 脚本证据：参与参数生成的脚本定位信息 |
| `runtime-evidence.jsonl` | 运行时证据：Hook 命中记录、函数调用序列 |
| `env/entry.js` | 运行时入口：加载 env→polyfills→capture→目标脚本 |
| `env/env.js` | 基础宿主：window/document/navigator/storage/crypto |
| `env/polyfills.js` | 代理诊断：watch/safeFunction/makeFunction |
| `env/capture.json` | 页面证据快照：cookies/storage/请求样本 |
| `report.md` | 结果报告：状态、签名链、环境依赖、验收结果 |

### 可选文件（按任务需要补充）

| 文件 | 职责 |
|------|------|
| `timeline.jsonl` | 时间线事件记录 |
| `cookies.json` | Cookie 数据 |
| `replay/actions.json` | 页面动作复放序列 |
| `run/exported-runtime.js` | 便携运行时（execjs/quickjs 可调用） |
| `run/pure-*.js` | 纯算法实现（无环境依赖） |
| `run/pure_*.py` | Python 等效实现 |
| `run/fixtures.json` | 固定输入/输出夹具 |

## 读取优先级

1. 先复用已存在的 `artifacts/tasks/<taskId>/` 全链路数据
2. 若不存在，再参考 `scripts/cases/*` 抽象 case
3. 仍不足时，按参数方法论模板新建任务目录并执行

## 安全边界

- 公开索引：`scripts/cases/README.md`
- 正式规则/模板/契约：`docs/reference/`
- 本地私有任务产物：`artifacts/tasks/<taskId>/`
- 真实 task artifact 默认本地保留，共享前先做脱敏审查
- Git 只跟踪 `_TEMPLATE/`，不跟踪真实 task 目录

## 关于 Python execjs 等外部宿主

推荐产出两类不同文件：

1. **local rebuild 文件**：用于补环境、调试、读取代理 env log、定位 first divergence
   - 典型文件：`env/env.js`、`env/polyfills.js`、`env/entry.js`

2. **portable runtime 文件**：用于外部宿主直接调用
   - 典型文件：`run/exported-runtime.js`

建议流程：

1. 先在 Node local rebuild 中跑通链路
2. 先依据代理 env log 和 first divergence 完成最小因果单元补丁
3. 再把最小依赖提纯到 `run/exported-runtime.js`
4. 最后让 Python execjs、quickjs 或其他宿主调用导出函数

**不要反过来直接在 execjs 里做补环境**，这会让调试和定位缺口变得更困难。

## 关于 pure algorithm 产物

进入条件：env rebuild 已通过且服务端验收通过。

建议在 task-local `run/` 下补齐：

- `run/pure-*.js`：可读纯算实现
- 可选 `run/pure_*.py`：外部语言实现
- `run/fixtures.json`：固定输入、固定 runtimeContext、固定输出
- `report.md` 中的 Pure Runtime 验收记录

注意：pure algorithm 文件仍是 task-local 产物，不属于仓库公开 case。
