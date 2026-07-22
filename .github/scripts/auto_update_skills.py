#!/usr/bin/env python3
"""
GitHub Actions 自动更新脚本
搜索最新逆向/解密工具并更新技能文件
"""

import requests
import re
import os
from datetime import datetime

# GitHub API 配置
GITHUB_API = "https://api.github.com/search/repositories"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 搜索查询 - 解密/反混淆
DECRYPT_QUERIES = [
    "javascript deobfuscation",
    "js deobfuscator",
    "code obfuscation decrypt",
    "steganography analysis",
    "frida anti-detection",
    "jsjiami decode",
    "obfuscator.io deobfuscate",
    "wasm deobfuscation",
    "webcrack javascript",
    # 验证码/Cloudflare
    "captcha bypass solver",
    "cloudflare bypass",
    "flaresolverr",
    "cloudscraper",
    "anti-bot detection bypass",
    "puppeteer stealth",
    "playwright anti-detection",
]

# 搜索查询 - 逆向工程
REVERSE_QUERIES = [
    "reverse engineering tool",
    "binary analysis decompiler",
    "protocol reverse engineering",
    "VM devirtualization",
    "mobile reverse engineering",
    "iOS reverse engineering Android",
    "IDA Pro plugin Ghidra",
    "frida hooking script",
    "binary diffing bindiff",
    "malware analysis tool",
    "x64dbg debugger",
    "decompiler ilspy dnSPy",
    "firmware analysis embedded",
    "packet decryption network",
    "cryptographic analysis tool",
    "unpacker unpacking UPX",
    "anti-debug bypass",
    # 验证码绕过
    "captcha bypass solver",
    "reCAPTCHA v2 v3 solver",
    "hcaptcha bypass solver",
    "slider captcha bypass",
    "image captcha ocr",
    "anti-bot captcha",
    # Cloudflare 绕过
    "cloudflare bypass",
    "cloudflare turnstile solver",
    "cf-clearance scraper",
    "flaresolverr",
    "cloudscraper python",
    "bypass cloudflare 5 seconds",
]

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

def search_github(query, sort="stars", order="desc", per_page=5):
    """搜索 GitHub 仓库"""
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": per_page,
    }
    try:
        resp = requests.get(GITHUB_API, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json().get("items", [])
    except Exception as e:
        print(f"[ERROR] Search failed for '{query}': {e}")
        return []

def get_skill_content(repo_name):
    """读取技能文件内容"""
    paths = [
        f"Minis/SKILL/{repo_name}/SKILL.md",
        f"skills/{repo_name}/SKILL.md",
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read(), path
    return None, None

def check_repo_in_content(content, owner, name):
    """检查仓库是否已在技能文件中"""
    patterns = [
        f"{owner}/{name}",
        f"github.com/{owner}/{name}",
    ]
    for p in patterns:
        if p in content:
            return True
    return False

def find_section_end(content, section_title):
    """找到章节结束位置"""
    lines = content.split("\n")
    start_idx = None
    next_section_idx = None
    
    for i, line in enumerate(lines):
        if section_title in line:
            start_idx = i
        elif start_idx and line.startswith("# ") and i > start_idx + 1:
            next_section_idx = i
            break
    
    return next_section_idx or len(lines)

def update_decrypt_skill(new_repos):
    """更新解密技能文件"""
    content, path = get_skill_content("解密")
    if not content:
        print("[WARN] 解密技能文件未找到")
        return False
    
    # 过滤已存在的仓库
    unique_repos = []
    for repo in new_repos:
        if not check_repo_in_content(content, repo["owner"], repo["name"]):
            unique_repos.append(repo)
    
    if not unique_repos:
        print("[*] 解密技能无新仓库需要添加")
        return False
    
    # 生成新内容
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_section = f"\n\n<!-- 自动发现 {date_str} -->\n"
    new_section += "## 自动发现的新工具\n\n"
    new_section += "| 仓库 | Stars | 最近更新 | 描述 |\n"
    new_section += "|------|-------|---------|------|\n"
    
    for repo in unique_repos[:8]:  # 最多8个
        new_section += f"| [{repo['owner']}/{repo['name']}]({repo['url']}) | {repo['stars']}⭐ | {repo.get('updated','')} | {repo['desc'][:60]} |\n"
    
    # 在 minis_url 之前插入
    if "minis_url:" in content:
        content = content.replace("minis_url:", new_section + "\nminis_url:")
    else:
        content += new_section
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[+] 解密技能已更新 {len(unique_repos)} 个新仓库")
    return True

def update_reverse_skill(new_repos):
    """更新逆向技能文件"""
    content, path = get_skill_content("逆向")
    if not content:
        print("[WARN] 逆向技能文件未找到")
        return False
    
    unique_repos = []
    for repo in new_repos:
        if not check_repo_in_content(content, repo["owner"], repo["name"]):
            unique_repos.append(repo)
    
    if not unique_repos:
        print("[*] 逆向技能无新仓库需要添加")
        return False
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_section = f"\n\n<!-- 自动发现 {date_str} -->\n"
    new_section += "## 自动发现的新工具\n\n"
    new_section += "| 仓库 | Stars | 最近更新 | 描述 |\n"
    new_section += "|------|-------|---------|------|\n"
    
    for repo in unique_repos[:15]:
        new_section += f"| [{repo['owner']}/{repo['name']}]({repo['url']}) | {repo['stars']}⭐ | {repo.get('updated','')} | {repo['desc'][:60]} |\n"
    
    if "minis_url:" in content:
        content = content.replace("minis_url:", new_section + "\nminis_url:")
    else:
        content += new_section
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[+] 逆向技能已更新 {len(unique_repos)} 个新仓库")
    return True

def main():
    print(f"=== 技能自动更新 {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    
    all_repos = []
    
    # 按 Stars 搜索（唯一排序方式，减少 API 调用）
    print("[*] 按 Stars 排序搜索...")
    for query in DECRYPT_QUERIES + REVERSE_QUERIES:
        items = search_github(query, sort="stars", per_page=5)
        for item in items:
            repo_info = {
                "owner": item["owner"]["login"],
                "name": item["name"],
                "url": item["html_url"],
                "stars": item["stargazers_count"],
                "updated": item.get("updated_at", "")[:10],
                "desc": (item.get("description") or "")[:200],
            }
            all_repos.append(repo_info)
    
    # 去重
    seen = set()
    unique = []
    for r in all_repos:
        key = f"{r['owner']}/{r['name']}"
        if key not in seen:
            seen.add(key)
            unique.append(r)
    
    # 按 Stars 排序
    unique.sort(key=lambda x: x["stars"], reverse=True)
    
    print(f"[+] 共找到 {len(unique)} 个唯一仓库")
    
    # 分别更新两个技能
    decrypt_updated = update_decrypt_skill(unique[:20])
    reverse_updated = update_reverse_skill(unique[:30])
    
    if decrypt_updated or reverse_updated:
        print("[+] 技能已更新，等待提交")
    else:
        print("[*] 无更新")
    
    print("=== 完成 ===")

if __name__ == "__main__":
    main()
