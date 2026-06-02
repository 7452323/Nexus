# Screens 5 (Edovia) v5.8.6 — Subscription Unlock Case Study

> **状态**: 未完成。v7.1 dylib 已部署但未验证。核心问题仍未解决。

## App Architecture

- **Type**: iOS native Swift app (SwiftUI + @Observable)
- **IAP**: StoreKit 2 (async/await), no StoreKit 1
- **Subscription Model**: Monthly + Lifetime + Lifetime Family
- **Products**: `com.edovia.screen5.universalMonthly`, `com.edovia.screen5.lifetime`, `com.edovia.screen5.lifetimeFamily`, `com.edovia.screen5.lifetimeFamilyUpgrade`
- **Obfuscation**: None (binary is decrypted, cryptid=0)
- **Symbol Status**: All private Swift symbols stripped (`baseMethods → __mh_execute_header`), StoreKit imports retained
- **Framework**: SSHKit, Sentry, SupportKit, VNCKit

## Key Types (from __swift5_reflstr)

### SubscriptionState (Int8 enum, 8 cases)

```
notSet(0), subscribed(1), notSubscribed(2), expired(3),
inBillingRetryPeriod(4), inGracePeriod(5), revoked(6), pending(7)
```

⚠️ **rawValue 类型是 Int8**（1 字节），不是 Int（8 字节）。从 ObjC ivar metadata 的 `size=1` 确认。

### PaywallFeature (enum)

```
dictation, obscur, curtainMode, floatingToolbar, connect, shortcut, advanced, dragDrop, curtainModeIsEnabled
```

### SubsStore (_TtC7Screens9SubsStore, @Observable class)

ObjC ivar 布局（19 个 ivars，`class_copyIvarList` 可枚举）：

| # | Name | size | alignment | 实际类型 |
|---|------|------|-----------|---------|
| 0 | groupID | 16 | 3 | String |
| 1 | appID | 8 | 3 | String? |
| 2 | _lastCheck | 0 | 0 | Date? |
| 3 | networkMonitor | 8 | 3 | 对象 |
| 4 | _currentTransaction | 0 | 0 | Transaction? |
| 5 | _currentTransactions | 8 | 3 | [Transaction] |
| 6 | _currentProduct | 0 | 0 | Product? |
| 7 | _products | 8 | 3 | [Product] |
| **8** | **_subscriptionState** | **1** | **0** | **Int8** ← 核心解锁目标 |
| **9** | **_wasRefunded** | **1** | **0** | **Bool** ← 必须为 0 |
| 10 | _renewalDate | 0 | 0 | Date? |
| **11** | **_willAutoRenew** | **1** | **0** | **Bool** ← 必须为 1 |
| 12 | _uniqueUserID | 16 | 3 | String |
| **13** | **_isPurchasing** | **1** | **0** | **Bool** ← 必须为 0 |
| 14 | _updateListenerTask | 8 | 3 | Task? |
| 15 | _statusUpdatesTask | 8 | 3 | Task? |
| 16 | _promotedPurchaseListenerTask | 8 | 3 | Task? |
| **17** | **_searchAdsAttributed** | **1** | **0** | **Bool** |
| 18 | _$observationRegistrar | 0 | 0 | ObservationRegistrar |

> ObjC `size=0` 的 ivar 表示 Swift 引用类型（class/Optional），实际占 8 字节指针。`size=1` 表示 Int8/Bool。

### _showingPaywall

出现 **9 次**，在多个 SwiftUI View 类中（**不在 SubsStore 中**）：
```
0x100c5a6f3, 0x100c5b0ed, 0x100c5fabb, 0x100c6092d,
0x100c60c06, 0x100c62c53, 0x100c635b1, 0x100c63784, 0x100c63eb2
```

是 `@Observable` stored property，**不出现在 ObjC `class_copyIvarList` 中**（但 `_subsStore` 和 `_subscriptionState` 在 SubsStore 中出现）。

### _subsStore

出现 **17 次**，通过 SwiftUI `@Environment` 注入到各个 View。

## 版本迭代与失败分析

### ❌ v1: fishhook 3个 StoreKit + NSUserDefaults
- Hook `RenewalState.rawValue`, `willAutoRenew`, `Status.state`
- **失败原因**: Hook 函数签名错误（多了 `SEL _cmd` 参数），寄存器偏移读垃圾值

### ❌ v2: 二进制 Patch 3处 B.NE→NOP
- Patch 0x100039f24, 0x1003decac, 0x1003e0c40
- **不够**: 16MB 二进制有 4274 个 `CMP #1 + B.NE`，只 Patch 3 处远不够

### ❌ v3: Patch IPA + dylib 双重方案
- 同上问题叠加

### ❌ v4-v5: 运行时修改 SubsStore 实例
- SubsStore 实例未被成功捕获（init hook 可能无效）
- Hook 函数签名仍然错误（`int8_t` vs `int64_t` 返回值大小）
- `RenewalState` 是 `Int`（8字节），但 App 的 `SubscriptionState` 是 `Int8`（1字节）

### ❌ v6: 修复 Swift struct getter 签名
- 发现根本问题：大部分 StoreKit 调用被内联
- `rawValue` stub 只有 1 次 BL，`willAutoRenew` 0 次

### ❓ v7.1: 三路 alloc Hook + 定时器覆写（当前版本，未验证）
- Hook `swift_allocObject` + `objc_alloc` + `objc_allocWithZone`
- 定时器每 0.5s 强制 `_subscriptionState = 1`
- Swizzle `_showingPaywall` setter
- **未知**: SubsStore 实例是否被成功捕获

## 四个根因（为什么 dylib 方案反复失败）

### 根因 1: Swift struct getter 函数签名错误

StoreKit 的 `RenewalState.rawValue` 等是 **C 函数**，不是 ObjC 方法，**没有 SEL 参数**：
```
❌ int64_t hooked_rawValue(id self, SEL _cmd)     // SEL 多占8字节
✅ int64_t hooked_rawValue(const void *self)       // 正确
✅ int64_t hooked_expired(void *result)            // 静态getter，连self都没有
```

### 根因 2: 大部分 StoreKit 调用被内联

- `rawValue` stub: 仅 1 次 BL
- `willAutoRenew` stub: 0 次 BL
- fishhook 只能截获 GOT 间接调用，内联调用完全无效

### 根因 3: SubsStore 实例难以捕获

- 所有方法符号被 stripped
- Swift 类可能走 `swift_allocObject` 或 `objc_alloc`
- `@Observable` 的 init 可能不走标准 ObjC init

### 根因 4: @Observable 的 withMutation 覆写风险

直接修改 `_subscriptionState` 内存后，App 的 `withMutation` 可能在下次属性访问时覆写回去。定时器每 0.5s 强制写入可能不够快。

## 关键二进制地址

### SubscriptionState switch @ 0x100039ee8

```asm
0x100039ee8: CMP W9, #0          ; case .notSet
0x100039f20: CMP W9, #1          ; case .subscribed ← 核心检查
0x100039f24: B.NE 0x100039f30    ; 不是 subscribed 就跳走 [PATCH→NOP]
0x100039f3c: CMP W9, #3          ; case .expired
0x100039f40: B.LE 0x100039f88
0x100039f44: CMP W9, #4          ; case .inBillingRetryPeriod
0x100039f4c: CMP W9, #5          ; case .inGracePeriod
0x100039f54: CMP W9, #6          ; case .revoked
```

### StoreKit GOT/Stubs

| 符号 | Stub | GOT |
|------|------|-----|
| RenewalState.rawValue | 0x100af945c | 0x100d8e020 |
| Status.state | 0x100af94bc | 0x100d8e070 |
| willAutoRenew | 0x100af9408 | 0x100d8dfe0 |
| swift_allocObject | 0x100afd164 | 0x100d95518 |
| objc_alloc | 0x100afc984 | 0x100d8f1c8 |

### Paywall 相关字符串偏移

```
PaywalledViewModifier: 0x100b42bf0
curtainModeCanBeEnabled: 0x100c5d941, 0x100d0ec31
_showingPaywall: 9 处
_subsStore: 17 处
```

## 下一步方案

### 方案 A: Frida Gadget 注入（当前进行中）

**已完成**：
- FridaGadget.dylib v17.9.6 下载+签名 → `/Users/loh/Downloads/FridaGadget.dylib` (37MB, arm64+arm64e)
- Mac 端 frida 17.9.6 + frida-tools 14.8.2 安装完毕
- Frida 调试脚本 → `/Users/loh/Downloads/screens5_debug.js`
- `frida-ls-devices` CLI 有 asyncio bug，用 Python `import frida` API 替代

**Frida Gadget 注入步骤（TrollTools 方案）**：
1. 把 `/Users/loh/Downloads/FridaGadget.dylib` 传到 iPad（AirDrop/iCloud）
2. TrollTools → 选择 Screens 5 → 注入 FridaGadget.dylib
3. USB 连接 iPad 到 Mac
4. 启动 Screens 5（Gadget 会自动启动监听）
5. Mac 端运行 Python frida API 附加 → 运行调试脚本

**调试目标**：
- [ ] 确认 SubsStore 实例是否被 alloc Hook 捕获
- [ ] 获取 `_subscriptionState` 的运行时真实偏移（`ivar_getOffset`）
- [ ] 确认 `@Observable` 的 `withMutation` 是否会覆写直接内存修改
- [ ] 探查 `_showingPaywall` 在哪个 View 类中，如何修改
- [ ] 确认 dylib v7.1 是否成功加载（检查 `[Unlock]` 日志）

### 方案 B: 改进 dylib v8

1. Hook `ObservationRegistrar.withMutation` 拦截属性修改
2. 在 withMutation 回调中强制覆写
3. 确认 ivar 运行时偏移（用 Frida 验证）

### 方案 C: Frida 脚本直接解锁

打包为 Gadget 自动运行模式，不需要 Mac 端连接。

## 环境信息

- macOS 15.5 Sequoia arm64
- Xcode 16.4 at `/Users/loh/data/FileSystem/安装包/Xcode.app`
- iOS SDK: `iPhoneOS18.5.sdk`
- iPad 17.0 (TrollStore, 非越狱)
- Frida 17.9.6 + frida-tools 14.8.2 (Mac 端已安装)
