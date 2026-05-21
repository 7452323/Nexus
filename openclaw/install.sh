#!/bin/bash
# OpenClaw Patches — 一键安装
# 用法:
#   bash install.sh                  # 安装全部
#   bash install.sh --only skill1,skill2  # 只装指定的
#   bash install.sh --skip skill1,skill2  # 跳过指定的

set -e

REPO_URL="https://github.com/7452323/Nexus.git"
OPENCLAW_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}"
WORKSPACE_DIR="${OPENCLAW_WORKSPACE:-$OPENCLAW_DIR/workspace}"
SKILLS_DIR="$WORKSPACE_DIR/skills"
TEMP_DIR=$(mktemp -d)

# 解析参数
ONLY=""
SKIP=""
for arg in "$@"; do
    case $arg in
        --only=*) ONLY="${arg#*=}" ;;
        --skip=*) SKIP="${arg#*=}" ;;
        --help|-h)
            echo "用法: bash install.sh [选项]"
            echo "  --only=技能1,技能2  只安装指定技能"
            echo "  --skip=技能1,技能2  安装全部但跳过指定技能"
            echo "  不加参数            安装全部 16 个技能"
            echo ""
            echo "可用技能:"
            echo "  memory-enhancer    记忆增强"
            echo "  preflight-checker  工具预检"
            echo "  session-isolator   会话隔离"
            echo "  memory-backup-auto 自动备份"
            echo "  knowledge-archiver 知识归档"
            echo "  provider-failover  故障切换"
            echo "  context-optimizer  上下文优化"
            echo "  rate-limiter       频率控制"
            echo "  server-doctor      服务器诊断"
            echo "  skill-scaffold     技能脚手架"
            echo "  config-presets     配置预设"
            echo "  notification-bridge 通知桥梁"
            echo "  multi-instance     多实例管理"
            echo "  daily-digest       每日报告"
            echo "  usage-analytics    使用分析"
            echo "  book-source-master  书源大湿
  qx-script-master    QX 全能脚本"
            exit 0
            ;;
    esac
done

if [ ! -d "$OPENCLAW_DIR" ]; then
    echo "❌ 错误: 找不到 OpenClaw 目录"
    echo "   请设置 OPENCLAW_HOME 环境变量"
    exit 1
fi

echo "OpenClaw Patches Installer"
echo "  目标: $SKILLS_DIR"
echo ""

# 克隆仓库
echo "📥 下载..."
git clone --depth 1 "$REPO_URL" "$TEMP_DIR/patches" 2>/dev/null
echo ""

# 确定要安装的技能
ALL_SKILLS=$(ls "$TEMP_DIR/patches/skills/"*.skill.md 2>/dev/null | xargs -n1 basename | sed 's/\.skill\.md$//' | sort)
echo "📋 规划安装..."

INSTALL_LIST=""
if [ -n "$ONLY" ]; then
    # 只安装指定的
    IFS=',' read -ra SELECTED <<< "$ONLY"
    for skill in "${SELECTED[@]}"; do
        skill=$(echo "$skill" | xargs)  # 去空格
        if echo "$ALL_SKILLS" | grep -q "^$skill$"; then
            INSTALL_LIST="$INSTALL_LIST $skill"
        else
            echo "  ⚠️  未知技能: $skill（跳过）"
        fi
    done
elif [ -n "$SKIP" ]; then
    # 全部安装但跳过指定的
    INSTALL_LIST="$ALL_SKILLS"
    IFS=',' read -ra SKIP_LIST <<< "$SKIP"
    for skip in "${SKIP_LIST[@]}"; do
        skip=$(echo "$skip" | xargs)
        INSTALL_LIST=$(echo "$INSTALL_LIST" | tr ' ' '\n' | grep -v "^$skip$" | tr '\n' ' ')
    done
else
    # 全部安装
    INSTALL_LIST="$ALL_SKILLS"
fi

# 安装
echo "🔧 安装技能..."
mkdir -p "$SKILLS_DIR"
COUNT=0
for skill in $INSTALL_LIST; do
    src="$TEMP_DIR/patches/skills/$skill.skill.md"
    dst="$SKILLS_DIR/$skill/SKILL.md"
    if [ -f "$src" ]; then
        mkdir -p "$(dirname "$dst")"
        cp "$src" "$dst"
        COUNT=$((COUNT + 1))
        echo "  ✅ $skill"
    fi
done

# 清理
rm -rf "$TEMP_DIR"

echo ""
echo "✅ 安装完成！已安装 $COUNT 个技能。"
echo "   位置: $SKILLS_DIR"
echo ""
echo "💡 提示: 技能安装后需重启 OpenClaw Gateway 才能生效"
echo "   openclaw gateway restart"
