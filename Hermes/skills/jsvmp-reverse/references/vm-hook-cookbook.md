# VM Hook 注入技术手册: 7 种通用注入技术

本文档从瑞数逆向实战中提炼 7 种 VM 注入技术，通用化后适用于所有 JSVMP/VMP 场景。所有代码均经过实际验证。

---

## 1. Dispatcher Hook — 拦截操作码执行

**注入点**: VM dispatcher 函数 (while/for 循环 + switch-case)

**用途**: 追踪 VM 执行流、记录 opcode 序列、理解控制流

### 通用实现

```javascript
// 定位 VM dispatcher (通常是包含 while(true) + 大量 case 的函数)
// 方法: 搜索最长的函数 / 搜索 while(true) + switch 结构

const originalDispatcher = vmInterpreter; // 替换为实际函数引用

// 方案 A: 包装整个 dispatcher
const hookedDispatcher = function() {
    const opcode = bigArray[pc]; // 替换为实际的 PC/操作码获取方式
    console.log('[DISPATCHER] pc=' + pc + ' opcode=' + opcode);
    return originalDispatcher.apply(this, arguments);
};

// 方案 B: 在 switch-case 前插入日志 (需要修改代码文本)
// 原始: switch(bigArray[pc++]) {
// 修改: var __op=bigArray[pc++]; console.log('[OP]',__op); switch(__op) {
```

### eval/vm.runInContext 拦截 (适用于 eval 加载的 VM)

```javascript
const vm = require('vm');
const originalRunInContext = vm.runInContext;

vm.runInContext = function(code, context, options) {
    // 捕获 VM 初始化脚本
    if (code.includes('$_ts') || code.includes('initConfig')) {
        fs.writeFileSync('vm_init.js', code);
        console.log('[HOOK] VM init script captured, length:', code.length);
    }

    // 捕获核心业务代码 (通常体积最大)
    if (code.length > 250000) {
        fs.writeFileSync('vm_core.js', code);
        console.log('[HOOK] VM core code captured, length:', code.length);
    }

    // 可在此处修改 code 后再执行
    // code = injectDispatcherHook(code);

    return originalRunInContext.call(this, code, context, options);
};
```

### 关键点

- eval/vm.runInContext 是最前置的拦截点，可捕获 VM 加载的所有代码
- 按代码长度和特征内容区分不同脚本
- 可在执行前修改代码，注入后续 hook

---

## 2. Memory Hook — 追踪数据流

**注入点**: VM 内存读写函数

**用途**: 追踪 VM 内部数据流、定位数据来源、理解 TLV 结构

### 通用实现

```javascript
// 拦截数组操作 — VM 通常用数组模拟内存
const originalArrayPush = Array.prototype.push;
let __phase = 0; // Phase 控制，减少噪声

Array.prototype.push = function() {
    // 只在关键阶段采集，且只关注大数组 (可能是 TLV 结构)
    if (__phase === 1 && this.length > 100) {
        console.log('[MEMORY] push to array, len=' + this.length,
            'newItems=' + Array.from(arguments).slice(0, 5));
    }
    return originalArrayPush.apply(this, arguments);
};

// 拦截对象属性读写
function hookObjectProperty(obj, prop, tag) {
    let value = obj[prop];
    Object.defineProperty(obj, prop, {
        get() {
            console.log('[MEM_READ]', tag, prop);
            return value;
        },
        set(v) {
            console.log('[MEM_WRITE]', tag, prop, typeof v);
            value = v;
        },
        configurable: true
    });
}
```

### Cookie 劫持 (Memory Hook 特化)

```javascript
let cookieCache = '';

Object.defineProperty(Document.prototype, 'cookie', {
    get: function() { return cookieCache; },
    set: function(val) {
        // 捕获目标 Cookie 写入
        const name = val.split('=')[0];
        console.log('[COOKIE_WRITE]', name, 'value=' + val.split(';')[0].substring(name.length + 1));

        // 维护 cookie 缓存 (模拟浏览器行为)
        const cookies = cookieCache.split('; ').filter(c => c && !c.startsWith(name + '='));
        if (!val.includes('max-age=0')) {
            cookies.push(val.split(';')[0]);
        }
        cookieCache = cookies.join('; ');
    },
    configurable: true
});
```

### 关键点

- Array.prototype.push 是捕获 TLV 结构组装的有效入口
- Cookie 劫持需要正确维护缓存，否则后续逻辑读取 cookie 会异常
- 用 Phase 控制 (见技术 5) 减少日志噪声

---

## 3. Register Hook — 追踪计算过程

**注入点**: VM 寄存器操作 (栈顶/累加器/专用寄存器)

**用途**: 分析寄存器式 VM 指令集、追踪计算中间值

### 通用实现

```javascript
// 栈式 VM: 追踪栈操作
const originalStack = vmState.stack;
const stackProxy = new Proxy(originalStack, {
    get(target, prop) {
        if (prop === 'push') {
            return function(...args) {
                if (__phase === 1) {
                    console.log('[REG_PUSH]', args[0], 'depth=' + target.length);
                }
                return target.push(...args);
            };
        }
        if (prop === 'pop') {
            return function() {
                const val = target.pop();
                if (__phase === 1) {
                    console.log('[REG_POP]', val, 'depth=' + target.length);
                }
                return val;
            };
        }
        return target[prop];
    }
});
vmState.stack = stackProxy;

// 寄存器式 VM: 追踪寄存器赋值
function hookRegister(vmState, regName) {
    let value = vmState[regName];
    Object.defineProperty(vmState, regName, {
        get() { return value; },
        set(v) {
            if (__phase === 1) {
                console.log('[REG_SET]', regName, '=', v);
            }
            value = v;
        },
        configurable: true
    });
}
```

### 逗号表达式注入 (Register Hook 的零侵入变体)

```javascript
// 原始代码
result = targetFunction(arg1, arg2);

// 注入后 (不改变控制流和返回值)
result = (console.log('[TRACE] targetFunction called:', arg1, arg2), targetFunction(arg1, arg2));
```

### 关键点

- Proxy 是追踪栈操作的最干净方式，但可能有性能开销
- 逗号表达式是零侵入的，不改变控制流和返回值
- 适合在 AST 改写中批量注入到关键调用点

---

## 4. Call Hook — 追踪外部调用

**注入点**: VM 函数调用指令 (call/apply 调用)

**用途**: 追踪 VM 调用外部函数、理解 VM 与宿主的交互

### 通用实现

```javascript
// 方案 A: Hook Function.prototype.apply/call
const originalApply = Function.prototype.apply;
Function.prototype.apply = function(thisArg, args) {
    // 过滤高频调用 (只记录关键函数)
    if (this.name && !['forEach', 'map', 'filter'].includes(this.name)) {
        console.log('[CALL]', this.name || 'anonymous',
            'args=' + (args ? Array.from(args).length : 0));
    }
    return originalApply.call(this, thisArg, args);
};

// 方案 B: 在 VM 字节码的 CALL opcode 处注入
// 当 opcode 对应 "函数调用" 操作时:
// 原始: handlers[opcode](state);
// 注入: (console.log('[VM_CALL]', opcode, 'argc=' + state.stack.length), handlers[opcode](state));
```

### XHR/Fetch 拦截 (Call Hook 特化)

```javascript
// 拦截 XHR — 适用于 VM 内部发起网络请求
const originalXHROpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(method, url) {
    console.log('[XHR_OPEN]', method, url);
    this.__hookUrl = url;
    return originalXHROpen.apply(this, arguments);
};

const originalXHRSend = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.send = function(body) {
    console.log('[XHR_SEND]', this.__hookUrl, 'bodyLen=' + (body ? body.length : 0));
    return originalXHRSend.apply(this, arguments);
};
```

### 关键点

- apply/call hook 范围最广但噪声也大，需要配合过滤
- XHR/Fetch 拦截可定位 VM 的网络交互模式
- 注意不要 hook 到自身 hook 的调用，避免无限递归

---

## 5. Return Hook — 捕获加密结果

**注入点**: VM 函数返回值

**用途**: 捕获加密结果、定位 VM 输出点、验证中间数据

### 通用实现

```javascript
// 方案 A: 函数体替换 — 对已知签名的函数包装
function hookFunctionReturn(originalFunc, tag) {
    return function() {
        const result = originalFunc.apply(this, arguments);
        if (__phase === 1) {
            console.log('[RETURN]', tag,
                'args=' + Array.from(arguments).map(a => typeof a).join(','),
                'result_type=' + typeof result,
                'result_len=' + (result ? (result.length || 'N/A') : 'null'));
        }
        return result;
    };
}

// 方案 B: 在目标函数的 return 语句前插入日志
// AST 改写: 在 ReturnStatement 前插入 console.log
```

### Cookie 写入拦截 (Return Hook 特化)

```javascript
// 拦截 document.cookie 写入 — 这是加密结果的最终输出点
Object.defineProperty(Document.prototype, 'cookie', {
    set: function(val) {
        // 捕获目标 Cookie (加密结果)
        const name = val.split('=')[0];
        const value = val.split(';')[0].substring(name.length + 1);
        console.log('[COOKIE_RESULT]', name, 'len=' + value.length);
        // ... 保存到全局变量供外部读取
        cookieCache = updateCookieCache(cookieCache, val);
    },
    configurable: true
});
```

### 关键点

- Return Hook 通常与 Memory Hook 配合: Memory 追踪数据流，Return 捕获输出
- Cookie/Header 写入是最常见的 VM 输出点
- 函数体替换时绝对不能依赖函数名定位，必须用结构特征

---

## 6. Exception Hook — 调试 VM 错误

**注入点**: VM 异常处理 (try-catch / onerror)

**用途**: 捕获 VM 执行异常、理解 VM 错误处理机制、调试补环境问题

### 通用实现

```javascript
// 方案 A: 全局异常拦截
process.on('uncaughtException', (err) => {
    console.error('[VM_EXCEPTION]', err.message, err.stack);
});

// 方案 B: 包装 VM 执行入口
function runVMWithExceptionHook(vmCode) {
    try {
        return vm.runInContext(vmCode, context);
    } catch (e) {
        console.error('[VM_EXCEPTION]', e.message);
        console.error('  type:', e.constructor.name);
        console.error('  stack:', e.stack.split('\n').slice(0, 5).join('\n'));
        throw e; // 重新抛出
    }
}

// 方案 C: 在 VM 字节码的 ETRY/ECATCH opcode 处注入
// 当 opcode 对应 "进入 try" 或 "进入 catch" 时记录
```

### 补环境调试

```javascript
// 当 VM 访问未实现的环境对象时，抛出详细错误
const handler = {
    get(target, prop) {
        if (!(prop in target)) {
            const err = new Error('[ENV_MISS] ' + prop);
            console.error(err.stack);
            // 返回合理的默认值，避免 VM 崩溃
            return undefined;
        }
        return target[prop];
    }
};

window = new Proxy({}, handler);
document = new Proxy({}, handler);
navigator = new Proxy({}, handler);
```

### 关键点

- Proxy handler.get 是发现未实现环境对象的最佳方式
- 异常信息通常包含 VM 执行状态 (PC 值、栈内容)，有助于定位问题
- 补环境时应返回合理默认值而非 undefined，避免后续连锁错误

---

## 7. Custom Opcode / Phase 标记 — 扩展 VM 能力

**注入点**: 全局变量 + VM 代码修改

**用途**: 数据导出、Phase 控制、扩展 VM 能力

### Phase 标记

**目的**: 通过全局变量区分执行上下文，只在关键阶段采集数据。

```javascript
// 在全局作用域定义
globalThis.__phase = 0;
globalThis.__collectedData = {};

// Phase 0: 初始化阶段 (忽略)
// Phase 1: 目标生成阶段 (重点采集)
// Phase 2: 后续请求阶段 (按需采集)

// 在关键入口处设置
globalThis.__phase = 1; // 检测到目标函数开始执行

// 在数据采集 hook 中检查阶段
function logIfCritical(tag, data) {
    if (globalThis.__phase === 1) {
        console.log(tag, JSON.stringify(data));
    }
}
```

### console.log 侧信道导出

**目的**: 利用运行环境的 console 回调机制，将 VM 内部数据导出到外部。

```javascript
// 外部环境: 配置 console 回调
const collectedData = {};

const envConfig = {
    consoleConfig: {
        log: function() {
            const msg = arguments[0];
            if (typeof msg !== 'string') return;

            // 用约定前缀区分不同数据类型
            if (msg.startsWith('__KEYS__')) {
                collectedData.keys = JSON.parse(msg.substring(8));
                console.error('[COLLECT] keys captured, length:', collectedData.keys.length);
            }
            if (msg.startsWith('__RESULT__')) {
                collectedData.result = JSON.parse(msg.substring(10));
                console.error('[COLLECT] result captured');
            }
            if (msg.startsWith('__BASEARR__')) {
                collectedData.baseArr = JSON.parse(msg.substring(11));
                console.error('[COLLECT] baseArr captured, length:', collectedData.baseArr.length);
            }
        }
    }
};
```

```javascript
// VM 内部 (注入到代码中): 使用约定前缀发送数据
console.log('__KEYS__' + JSON.stringify(keysArray));
console.log('__RESULT__' + JSON.stringify(encryptedResult));
console.log('__BASEARR__' + JSON.stringify(baseArray));
```

### 正则批量函数发现

**目的**: 在混淆代码中通过结构特征批量定位目标函数。

```javascript
/**
 * 通过结构特征查找函数
 * @param {string} code - 完整的混淆代码
 * @param {RegExp} bodyPattern - 函数体内的特征正则
 * @returns {Array} 匹配的函数信息
 */
function findFunctionsByPattern(code, bodyPattern) {
    const results = [];
    const funcDeclRegex = /function\s+(\w+)\s*\(([^)]*)\)\s*\{/g;
    let match;

    while ((match = funcDeclRegex.exec(code)) !== null) {
        const funcStart = match.index;
        const bodyStart = match.index + match[0].length;
        const body = extractByBracketDepth(code, bodyStart - 1);

        if (body && bodyPattern.test(body)) {
            results.push({
                name: match[1],
                params: match[2],
                body: body,
                position: funcStart
            });
        }
    }
    return results;
}

/**
 * 括号深度追踪, 提取完整的 {} 块
 */
function extractByBracketDepth(code, openBracePos) {
    let depth = 0, inString = false, stringChar = '';

    for (let i = openBracePos; i < code.length; i++) {
        const ch = code[i];
        if (!inString && (ch === '"' || ch === "'")) {
            inString = true;
            stringChar = ch;
        } else if (inString && ch === stringChar && code[i - 1] !== '\\') {
            inString = false;
        }
        if (!inString) {
            if (ch === '{') depth++;
            if (ch === '}') depth--;
            if (depth === 0) return code.substring(openBracePos, i + 1);
        }
    }
    return null;
}
```

**常用特征模式**:

```javascript
// SHA-1
const sha1Pattern = /0x67452301|0xEFCDAB89|0x98BADCFE/;

// CRC32
const crc32Pattern = /0xEDB88320|>>>.*0xFF/;

// Base64
const base64Pattern = /ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/;

// XTEA
const xteaPattern = /2654435769|0x9E3779B9/;
```

### 关键点

- Phase 标记大幅减少日志噪声，只关注关键执行路径
- console.log 侧信道是从 VM 内部向外传递数据的可靠通道
- 前缀命名应唯一，避免与正常 console.log 冲突
- 正则发现是 AST 分析的轻量替代，适合快速定位候选函数

---

## 组合使用策略

### 快速定位 (数据驱动辅助)

```
1. Dispatcher Hook → 找到 VM 入口和操作码序列
2. Phase 标记 → 缩小采集范围
3. Return Hook → 捕获输出
4. console 侧信道 → 导出中间数据
```

### 深度分析 (AST 反编译辅助)

```
1. 正则发现 → 定位候选函数
2. Memory Hook → 追踪数据流
3. Register Hook → 理解计算过程
4. Call Hook → 追踪外部调用链
```

### 调试排错

```
1. Exception Hook → 捕获 VM 错误
2. Proxy handler → 发现缺失环境
3. 逗号表达式 → 零侵入追踪
4. Phase 标记 → 过滤噪声
```

---

## 通用注意事项

1. **变量名不可靠**: JSVMP 的变量名每次加载可能不同 (如瑞数的 nsd 洗牌)。Hook 定位必须用结构特征，不用变量名。
2. **性能开销**: 全量 Hook 有性能影响。始终用 Phase 控制 + 条件过滤。
3. **Hook 顺序**: 先 Dispatcher → 再 Memory/Register → 最后 Return。从外到内。
4. **可逆性**: 所有 Hook 应支持卸载 (configurable: true / 保存原始引用)。
5. **循环引用**: JSON.stringify 导出数据时注意循环引用，按需截断。
6. **编码安全**: 括号深度追踪必须处理字符串内的括号，否则会提前截断。
