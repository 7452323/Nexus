# Hermes 技能集合

## 技能列表

| 技能 | 说明 | 文件数 |
|------|------|--------|
| **reverse-engineering** | 逆向工程技能树索引。JS/Android/iOS/二进制/协议/EDR/MCP/Flutter/RN/WASM/脱壳全栈30+子领域 | 1 |
| **qx-script-master** | QX/Surge/Loon全能脚本。5大类型+18+实战模式+46项目索引+去广告三流派+模块转换 | 1 |
| **book-source-master** | Legado阅读3.0书源编写。6种模板+Key轮换+分页陷阱+反混淆实战 | 3 |
| **novel-writing** | 中文网文AI写作。三派方法论融合，6阶段全流程（选题→世界观→角色→大纲→创作→润色） | 12 |

## 结构

```
skills/
├── README.md                          ← 本文件
├── reverse-engineering/
│   └── SKILL.md                       ← 逆向工程技能树（30+子领域索引）
├── qx-script-master/
│   └── SKILL.md                       ← 代理脚本全能技能
├── book-source-master/
│   ├── SKILL.md                       ← 书源编写技能
│   ├── references/
│   │   └── obfuscation-patterns.md    ← 书源JS混淆与反防爬模式
│   └── examples/
│       ├── 69shu_book_source.json     ← 69书吧纯HTML书源示例
│       └── qidian_skybook.json        ← 起点中转型书源示例
└── novel-writing/
    ├── SKILL.md                       ← 网文写作技能总纲
    └── references/                    ← 10个写作参考文档
        ├── genre-frameworks.md        ← 题材框架（20种题材）
        ├── story-structure.md         ← 故事结构
        ├── character-design.md        ← 角色设计
        ├── world-building.md          ← 世界观构建
        ├── outline-generation.md      ← 大纲生成
        ├── writing-techniques.md      ← 写作技巧
        ├── anti-ai-writing.md         ← 去AI味指南
        ├── dialogue-mastery.md        ← 对话写作
        ├── emotional-curve.md         ← 情绪曲线
        ├── reversal-techniques.md     ← 反转设计
        └── quality-review.md          ← 质量审查
```

## 设计原则

1. **少即是多** — 每个技能一个 SKILL.md，内容精炼不注水
2. **代码优先** — 给命令给工具，不给废话教程
3. **表格化** — 速查表格式，快速定位
4. **实战导向** — 所有内容来自真实项目验证
