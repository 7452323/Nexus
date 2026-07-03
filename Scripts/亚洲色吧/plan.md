# 听书白屏修复

## 根因分析

1. Navigation.present 被 setTimeout(0) 包裹
2. 模块级播放器被改为局部 AVPlayer
3. 音频URL含中文未编码

## 已应用的修复

| # | 修复项 |
|---|--------|
| 1 | 模块级播放器扩展为完整全局状态 |
| 2 | AudioPlayerView 挂载时复用 |
| 3 | 移除 setTimeout(0) |
| 4 | resolveAudioUrl 编码非ASCII字符 |
