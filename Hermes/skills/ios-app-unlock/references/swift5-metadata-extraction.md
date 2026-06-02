# Swift5 反射元数据提取技术

从已编译的 Swift 二进制中提取类型结构（枚举 case、类属性、协议遵循），无需 Ghidra/IDA。

## 背景

Swift 编译器在 Mach-O 二进制中保留了 4 个元数据 section，用于运行时反射：

| Section | 内容 | 用途 |
|---------|------|------|
| `__constg_swiftt` | 类型描述符 | 类型名称、大小、字段偏移 |
| `__swift5_typeref` | 类型引用 | 泛型参数、协议见证表 |
| `__swift5_reflstr` | 反射字符串 | 属性名、枚举 case 名 |
| `__swift5_fieldmd` | 字段元数据 | 字段类型、偏移、数量 |
| `__swift5_builtin` | 内建类型 | Swift 标准类型映射 |

**最重要的 section 是 `__swift5_reflstr`** — 它包含所有属性名和枚举 case 名，以空字节分隔。

## 定位 Section 偏移

```bash
otool -l Binary | grep -A4 "swift5"
```

输出格式：
```
sectname __swift5_reflstr
   segname __TEXT
      addr 0x0000000100c5a4f0
      size 0x00000000000189ee
    offset 12952816
```

关键值：
- `offset` = 文件中的字节偏移
- `size` = section 大小

## 提取反射字符串

```python
with open('Binary', 'rb') as f:
    data = f.read()

reflstr = data[offset:offset+size]
strings = [s.decode('utf-8') for s in reflstr.split(b'\x00') if s]
```

字符串是**按类型分组**的，连续的字符串属于同一个类型。

## 模式识别

### 枚举模式

```
notSet              ← case 0
subscribed          ← case 1
notSubscribed       ← case 2
expired             ← case 3
inBillingRetryPeriod ← case 4
inGracePeriod       ← case 5
revoked             ← case 6
refunded            ← case 7
RawValue            ← 枚举结束标记（有 RawRepresentable）
```

**判断规则**：
- 连续短字符串 + 末尾有 `RawValue` = Int/String 枚举
- case 的 rawValue 从 0 递增
- `AllCases` = 遵循 CaseIterable

### 类/结构体属性模式

```
_subscriptionState    ← @Observable 存储属性
_wasRefunded          ← @Observable 存储属性
_renewalDate          ← @Observable 存储属性
_$observationRegistrar ← @Observable 宏生成
```

**判断规则**：
- `_` 前缀 = `@Observable` 宏生成的存储属性（Swift 5.9+）
- `_$observationRegistrar` 出现 = 类用了 `@Observable`
- `showing` / `isEnabled` / `CanBeEnabled` = 布尔门控
- `Body` 出现 = SwiftUI View 的 body 计算属性

### ProductPlan 枚举模式

```
universalYearly          ← String rawValue
universalYearlyUpToQ126
universalMonthly
universalMonthlyUpToQ126
lifetime
lifetimeFamily
lifetimeFamilyUpgrade
update                   ← 可能是方法名，不是 case
current                  ← 可能是方法名
AllCases                 ← CaseIterable 标记
RawValue                 ← 枚举结束
```

## 上下文分析法

打印关键词附近的字符串（前后各 N 个），识别所属类型：

```python
for i, s in enumerate(all_strings):
    if 'subscr' in s.lower():
        start = max(0, i-3)
        end = min(len(all_strings), i+10)
        for j in range(start, end):
            print(f'  [{"!!!" if j==i else "   "}] [{j}] {all_strings[j]}')
```

### 实战示例：Screens 5

```
=== Near [2293] _subscriptionState ===
  [2289] _currentTransaction
  [2290] _currentTransactions
  [2291] _currentProduct
  [2292] _products
>>> [2293] _subscriptionState
  [2294] _wasRefunded
  [2295] _renewalDate
  [2296] _willAutoRenew
  [2297] _uniqueUserID
  [2298] _isPurchasing
  [2299] _updateListenerTask
  [2300] _statusUpdatesTask
  [2301] _promotedPurchaseListenerTask
  [2302] _searchAdsAttributed
  [2303] _$observationRegistrar
```

→ 完整还原了 `SubsStore` 类的所有属性，确认是 `@Observable` 类。

## 字符串在二进制中的定位

用于后续 radare2/Ghidra 交叉引用：

```python
with open('Binary', 'rb') as f:
    data = f.read()

for pattern in [b'subscriptionState', b'curtainModeCanBeEnabled', b'showingPaywall']:
    count = data.count(pattern)
    idx = data.find(pattern)
    print(f'{pattern.decode()}: {count} occurrences, first at 0x{idx:x}')
```

## 局限性

1. **stripped 符号不影响 reflstr** — 即使 `nm` 无输出，reflstr 仍包含属性名
2. **内联函数不在此处** — 方法实现代码在 `__TEXT,__text`，不在元数据 section
3. **泛型特化不反映** — reflstr 只有泛型定义，不包含特化版本
4. **private 标记的属性仍然可见** — Swift access control 不影响反射字符串
5. **混淆后的 App 字符串可能被加密** — 但极少数 App 做了这个

## 与 nm/otool 的互补

| 方法 | 能发现 | 不能发现 |
|------|--------|---------|
| `nm` | 导出符号、外部引用 | stripped 内部符号 |
| `strings` | 任意字符串 | 类型归属 |
| `__swift5_reflstr` | 属性名+枚举case+类型分组 | 函数实现、代码逻辑 |
| `radare2/Ghidra` | 完整反编译 | 需要时间，Swift 反编译质量差 |

**最佳工作流**：`reflstr 提取类型结构` → `strings 侦察关键词` → `radare2 定位函数地址` → `lief Patch`
