#!/usr/bin/env python3
"""
init-reverse-task.py — 初始化逆向任务目录

用法:
    python init-reverse-task.py <taskId> [--target-param <param>] [--target-url <url>] [--output-dir <dir>]

功能:
    1. 创建标准 task artifact 目录结构
    2. 从模板复制 env.js / polyfills.js / entry.js / task.json / report.md
    3. 交互式填写 task.json 元数据
    4. 初始化空的 JSONL 证据文件
"""

import argparse
import json
import os
import shutil
import sys

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")

REQUIRED_SUBDIRS = ["env", "run", "replay"]

REQUIRED_JSONL = ["network.jsonl", "scripts.jsonl", "runtime-evidence.jsonl"]

TEMPLATE_FILES = {
    "env/env.js": "env.js",
    "env/polyfills.js": "polyfills.js",
    "env/entry.js": "entry.js",
    "task.json": "task.json",
    "report.md": "report.md",
}


def prompt_field(label, default=""):
    """交互式提示输入字段"""
    prompt = f"  {label}"
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    value = input(prompt).strip()
    return value or default


def init_task(task_id: str, target_param: str, target_url: str, output_dir: str, interactive: bool):
    """初始化逆向任务目录"""

    task_dir = os.path.join(output_dir, task_id)

    if os.path.exists(task_dir):
        print(f"[ERROR] 目录已存在: {task_dir}", file=sys.stderr)
        sys.exit(1)

    # 创建目录结构
    print(f"[INFO] 创建任务目录: {task_dir}")
    os.makedirs(task_dir, exist_ok=True)

    for subdir in REQUIRED_SUBDIRS:
        os.makedirs(os.path.join(task_dir, subdir), exist_ok=True)
        print(f"  创建子目录: {subdir}/")

    # 复制模板文件
    print("[INFO] 复制模板文件...")
    for dest_rel, template_name in TEMPLATE_FILES.items():
        src = os.path.join(TEMPLATE_DIR, template_name)
        dst = os.path.join(task_dir, dest_rel)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  复制: {template_name} -> {dest_rel}")
        else:
            print(f"  [WARN] 模板文件不存在: {src}", file=sys.stderr)

    # 初始化空的 JSONL 文件
    print("[INFO] 初始化证据文件...")
    for jsonl_file in REQUIRED_JSONL:
        filepath = os.path.join(task_dir, jsonl_file)
        with open(filepath, "w", encoding="utf-8") as f:
            pass  # 创建空文件
        print(f"  创建: {jsonl_file}")

    # 创建空的 capture.json
    capture_path = os.path.join(task_dir, "env", "capture.json")
    with open(capture_path, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2, ensure_ascii=False)
    print("  创建: env/capture.json")

    # 填写 task.json
    task_json_path = os.path.join(task_dir, "task.json")
    with open(task_json_path, "r", encoding="utf-8") as f:
        task_data = json.load(f)

    task_data["taskId"] = task_id

    if interactive:
        print("\n[交互] 填写任务元数据 (直接回车跳过):")
        task_data["targetParam"] = prompt_field("targetParam", target_param)
        task_data["targetUrl"] = prompt_field("targetUrl", target_url)
        task_data["targetAction"] = prompt_field("targetAction", "")
        task_data["signEntryHint"] = prompt_field("signEntryHint", "")
    else:
        task_data["targetParam"] = target_param
        task_data["targetUrl"] = target_url

    with open(task_json_path, "w", encoding="utf-8") as f:
        json.dump(task_data, f, indent=2, ensure_ascii=False)
    print(f"\n[INFO] task.json 已更新: taskId={task_id}")

    # 输出结果
    print(f"\n[DONE] 任务目录初始化完成: {task_dir}")
    print("\n目录结构:")
    for root, dirs, files in os.walk(task_dir):
        level = root.replace(task_dir, "").count(os.sep)
        indent = "  " * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = "  " * (level + 1)
        for file in files:
            print(f"{sub_indent}{file}")

    print(f"\n下一步:")
    print(f"  1. 在 env/capture.json 中填入页面证据快照")
    print(f"  2. 运行 node env/entry.js 查看 first divergence")
    print(f"  3. 按代理日志逐项补环境")


def main():
    parser = argparse.ArgumentParser(description="初始化逆向任务目录")
    parser.add_argument("taskId", help="任务 ID，如 param-xxxx-site")
    parser.add_argument("--target-param", "-p", default="<param_name>", help="目标参数名")
    parser.add_argument("--target-url", "-u", default="<url_pattern>", help="目标 URL 模式")
    parser.add_argument("--output-dir", "-o", default=".", help="输出目录（默认当前目录）")
    parser.add_argument("--non-interactive", "-n", action="store_true", help="非交互模式，使用默认值")

    args = parser.parse_args()
    interactive = not args.non_interactive

    init_task(
        task_id=args.taskId,
        target_param=args.target_param,
        target_url=args.target_url,
        output_dir=args.output_dir,
        interactive=interactive,
    )


if __name__ == "__main__":
    main()
