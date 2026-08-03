#!/usr/bin/env python3
"""
HAR Analyzer v2 — 抓包分析 + 去广告/爆破会员辅助工具

v2 新增（基于 46+ QuantumX/Surge/Loon 仓库研究）:
  - 自动识别 VIP 字段模式（70+ 关键词）
  - 自动识别广告请求
  - 自动识别破解写法类型
  - 生成 QX/Surge/Loon 脚本模板
  - RevenueCat 通用破解模板
  - 正则替换模式自动检测
  - 支持对比正常/VIP两个HAR包差异
"""

import json
import sys
import os
import re
import csv
import io
import base64
from collections import defaultdict, Counter
from urllib.parse import urlparse
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


# ============================================================
# 知识库：从 46+ 仓库学到的 VIP 字段模式
# ============================================================

VIP_PATTERNS = {
    # 布尔标记
    "bool_flags": [
        "is_vip", "vip", "vip_flag", "isVip", "isPro", "isPremium",
        "is_premium", "isSubscribed", "is_member", "is_trial", "isTrial",
        "has_ad", "ad_free", "is_unlimited", "isUnlimited",
        "is_super", "isYearUser", "isVIPMAutoPay",
    ],
    # 状态值
    "status_values": [
        "vip_status", "vipStatus", "vipType", "vip_level", "vipLevel",
        "premium_status", "premiumStatus", "status", "account_type",
        "user_type", "role", "grade", "level", "access_level",
        "subscription_status",
    ],
    # 到期时间
    "expire_time": [
        "expire_time", "expires_date", "expired_at", "expiry", "end_time",
        "vipEndDate", "vipExpire", "vip_expire_time", "expiration",
        "valid_until", "expire_date", "expire_time_stamp",
        "membership_expiry_date", "membership_expire",
    ],
    # 订阅/权益
    "subscription": [
        "entitlements", "subscriptions", "subscription", "entitlement",
        "product_id", "product_identifier", "membership",
        "planTier", "planType", "subscriptionProduct",
        "subscriptionTier", "planId",
    ],
    # 会员类型
    "member_info": [
        "vip_info", "vipInfo", "member_type", "memberid",
        "privilege", "privileges", "vipLuxuryExpire",
        "vipOverSeasExpire", "vipmExpire", "vip3Expire",
    ],
    # 破解后常用值
    "crack_values": [
        ("status", "1"),
        ("is_vip", "true"),
        ("vip_status", "1"),
        ("is_premium", "true"),
        ("premium_status", "ACTIVE"),
        ("has_ad", "0"),
        ("vip_type", "1"),
        ("level", "99"),
        ("is_unlimited", "true"),
    ],
}

# 广告域名模式
AD_PATTERNS = [
    r'ad\.', r'ads\.', r'adservice', r'doubleclick', r'googlesyndication',
    r'google-analytics', r'analytics\.', r'tracking\.', r'track\.',
    r'log\.', r'promotion', r'sponsor', r'banner', r'commercial',
    r'admob', r'applovin', r'vungle', r'unityads', r'ironsrc',
    r'flutter\.io', r'amazon-adsystem', r'adnxs', r'criteo',
    r'smaato', r'tapjoy', r'inmobi', r'chartboost',
    r'facebook\.com/tr', r'pixel\.', r'umeng', r'baidumob',
    r'bytedance\.com.*ad', r'tencent.*ad', r'gdt\.',
    r'toutiaoapi.*ad', r'pangolin-sdk', r'sigmob',
]

# 破解脚本模板类型
CRACK_TEMPLATES = {
    "json_replace": {
        "desc": "完全替换响应 JSON",
        "qx": """// {app_name} 解锁
var obj = JSON.parse($response.body);
// TODO: 根据抓包分析替换关键字段
// obj.data.vipExpire = "2099-01-01";
// obj.data.is_vip = true;
$done({{body: JSON.stringify(obj)}});
""",
        "surge": """// {app_name} 解锁
let obj = JSON.parse($response.body);
$done({{body: JSON.stringify(obj)}});
""",
    },
    "regex_replace": {
        "desc": "正则替换字段值",
        "qx": """// {app_name} 解锁 (正则替换)
var body = $response.body
    .replace(/{pattern}/g, '{replacement}');
$done({{body}});
""",
    },
    "revenuecat": {
        "desc": "RevenueCat 通用解锁",
        "qx": """// {app_name} RevenueCat 解锁
const obj = JSON.parse($response.body);
if (obj && obj.subscriber) {{
    obj.subscriber.subscriptions = obj.subscriber.subscriptions || {{}};
    obj.subscriber.entitlements = obj.subscriber.entitlements || {{}};
    const data = {{
        "expires_date": "2099-01-01T00:00:00Z",
        "original_purchase_date": "2024-01-01T00:00:00Z",
        "purchase_date": "2024-01-01T00:00:00Z",
        "ownership_type": "PURCHASED",
        "store": "app_store"
    }};
    // TODO: 填入 Product ID 和 Entitlement name
    obj.subscriber.subscriptions["TODO_product_id"] = data;
    obj.subscriber.entitlements["TODO_entitlement_name"] = JSON.parse(JSON.stringify(data));
    obj.subscriber.entitlements["TODO_entitlement_name"].product_identifier = "TODO_product_id";
}}
$done({{body: JSON.stringify(obj)}});
""",
    },
}

# 代理配置模板
PROXY_CONFIG = {
    "qx": """[rewrite_local]
{rewrite_rules}

[mitm]
hostname = {hostnames}
""",
    "surge": """[Script]
{script_rules}

[MITM]
hostname = {hostnames}
""",
    "loon": """[Script]
{script_rules}

[MITM]
hostname = {hostnames}
""",
}


# ============================================================
# 数据模型
# ============================================================

@dataclass
class HAREntry:
    """单条 HAR 请求记录"""
    method: str = "GET"
    url: str = ""
    status: int = 0
    status_text: str = ""
    content_type: str = ""
    resource_type: str = "other"
    hostname: str = ""
    path: str = ""
    time: int = 0
    started: str = ""
    req_headers: dict = field(default_factory=dict)
    resp_headers: dict = field(default_factory=dict)
    query_params: dict = field(default_factory=dict)
    post_data: Optional[dict] = None
    post_text: str = ""
    resp_body_size: int = 0
    resp_text: str = ""
    resp_json: Optional[dict] = None
    
    @classmethod
    def from_har(cls, entry: dict) -> 'HAREntry':
        req = entry.get('request', {})
        resp = entry.get('response', {})
        timing = entry.get('timings', {})
        
        # 提取 Content-Type
        ct = ""
        for h in resp.get('headers', []):
            if h.get('name', '').lower() == 'content-type':
                ct = h['value'].split(';')[0].strip()
                break
        
        # 提取响应体
        content = resp.get('content', {})
        resp_text = content.get('text', '')
        resp_encoding = content.get('encoding', '')
        if resp_text and resp_encoding == 'base64':
            try:
                resp_text = base64.b64decode(resp_text).decode('utf-8', errors='replace')
            except:
                pass
        
        # 提取 POST 数据
        post = req.get('postData', {})
        post_text = post.get('text', '') if isinstance(post, dict) else str(post)
        
        # 解析 JSON 响应
        resp_json = None
        if resp_text and ('json' in ct.lower() or resp_text.strip().startswith('{')):
            try:
                resp_json = json.loads(resp_text)
            except:
                pass
        
        # 计算 totals
        total_time = sum(v for v in timing.values() if isinstance(v, (int, float)) and v > 0)
        
        parsed = urlparse(req.get('url', ''))
        
        return cls(
            method=req.get('method', 'GET'),
            url=req.get('url', ''),
            status=resp.get('status', 0),
            status_text=resp.get('statusText', ''),
            content_type=ct,
            resource_type=cls._classify(ct),
            hostname=parsed.hostname or '',
            path=parsed.path or '',
            time=int(total_time),
            started=entry.get('startedDateTime', ''),
            req_headers={h['name'].lower(): h['value'] for h in req.get('headers', [])},
            resp_headers={h['name'].lower(): h['value'] for h in resp.get('headers', [])},
            query_params={q['name']: q['value'] for q in req.get('queryString', [])},
            post_data=post if isinstance(post, dict) else {},
            post_text=post_text,
            resp_body_size=resp.get('bodySize', 0) or len(resp_text),
            resp_text=resp_text,
            resp_json=resp_json,
        )
    
    @staticmethod
    def _classify(ct: str) -> str:
        ct_lower = ct.lower()
        if 'html' in ct_lower: return 'document'
        if 'json' in ct_lower: return 'json'
        if 'javascript' in ct_lower: return 'script'
        if 'css' in ct_lower: return 'stylesheet'
        if 'image' in ct_lower: return 'image'
        if 'font' in ct_lower: return 'font'
        if 'audio' in ct_lower or 'video' in ct_lower: return 'media'
        if 'text/plain' in ct_lower: return 'text'
        if 'xml' in ct_lower: return 'xml'
        return 'other'
    
    def matches_filter(self, **filters) -> bool:
        for k, v in filters.items():
            if k == 'method' and self.method.upper() != v.upper():
                return False
            if k == 'status_min' and self.status < v: return False
            if k == 'status_max' and self.status > v: return False
            if k == 'domain' and v not in self.hostname: return False
            if k == 'url_contains' and v not in self.url: return False
            if k == 'path_contains' and v not in self.path: return False
            if k == 'content_type' and v not in self.content_type: return False
            if k == 'resource_type' and v != self.resource_type: return False
            if k == 'min_body_size' and self.resp_body_size < v: return False
            if k == 'has_response_body' and not self.resp_text: return False
        return True


# ============================================================
# VIP 字段检测器
# ============================================================

class VIPFieldDetector:
    """检测响应 JSON 中的 VIP 相关字段"""
    
    @staticmethod
    def detect_json_fields(json_obj, prefix=""):
        """递归检测 JSON 中的所有 VIP 相关字段"""
        results = []
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                # 匹配 VIP 模式
                for cat, patterns in VIP_PATTERNS.items():
                    if cat == "crack_values":
                        continue
                    for pat in patterns:
                        if pat.lower() in key.lower():
                            results.append({
                                "field": full_key,
                                "value": value,
                                "category": cat,
                                "matched_pattern": pat,
                            })
                # 递归
                if isinstance(value, (dict, list)):
                    results.extend(VIPFieldDetector.detect_json_fields(value, full_key))
        elif isinstance(json_obj, list):
            for i, item in enumerate(json_obj):
                if isinstance(item, (dict, list)):
                    results.extend(VIPFieldDetector.detect_json_fields(item, f"{prefix}[{i}]"))
        return results
    
    @staticmethod
    def detect_in_text(text: str) -> List[Dict]:
        """在纯文本中检测 VIP 关键词"""
        results = []
        text_lower = text.lower()
        for cat, patterns in VIP_PATTERNS.items():
            if cat == "crack_values":
                continue
            for pat in patterns:
                if pat.lower() in text_lower:
                    # 找上下文
                    idx = text_lower.find(pat.lower())
                    start = max(0, idx - 30)
                    end = min(len(text), idx + len(pat) + 30)
                    results.append({
                        "pattern": pat,
                        "category": cat,
                        "context": text[start:end].replace('\n', '\\n'),
                    })
        return results


# ============================================================
# 脚本生成器
# ============================================================

class ScriptGenerator:
    """根据 HAR 分析结果生成破解脚本"""
    
    @staticmethod
    def suggest_crack_type(entry: HAREntry) -> str:
        """根据请求特征建议破解类型"""
        url_lower = entry.url.lower()
        
        if 'revenuecat' in url_lower:
            return "revenuecat"
        if 'verifyReceipt' in url_lower or 'itunes.apple.com' in url_lower:
            return "itunes"
        if 'login' in url_lower or 'auth' in url_lower:
            return None  # 登录接口通常不改
        
        # JSON 接口
        if entry.resp_json:
            # 有明确的 VIP 字段 → JSON 修改
            vip_fields = VIPFieldDetector.detect_json_fields(entry.resp_json)
            if vip_fields:
                return "json_replace"
            # 可以正则替换
            if any(kw in entry.resp_text.lower() for kw in ['vip', 'premium', 'member', 'ad']):
                return "regex_replace"
        
        return "json_replace" if entry.resp_json else None
    
    @staticmethod
    def generate_qx_rewrite(hostname: str, path_pattern: str, script_url: str, is_reject: bool = False) -> str:
        """生成 QX rewrite_local 规则"""
        if is_reject:
            return f"^{re.escape(hostname)}\\b url reject"
        
        # 转义路径
        path_escaped = re.escape(path_pattern).replace(r'\*', '.*')
        full = f"^https?:\\/\\/{re.escape(hostname)}{path_escaped}"
        return f"{full} url script-response-body {script_url}"
    
    @staticmethod
    def generate_surge_script(hostname: str, path_pattern: str, script_url: str) -> str:
        """生成 Surge Script 规则"""
        path_escaped = re.escape(path_pattern).replace(r'\*', '.*')
        full = f"^https?:\\/\\/{re.escape(hostname)}{path_escaped}"
        return f"http-response {full} requires-body=1,max-size=-1,script-path={script_url}"
    
    @staticmethod
    def generate_crack_script(entries: List[HAREntry], app_name: str = "App") -> str:
        """根据多个请求生成综合破解脚本"""
        if not entries:
            return "// 未找到相关请求"
        
        lines = [f"/* {app_name} 破解脚本 */", "// 分析日期: " + datetime.now().strftime("%Y-%m-%d"), ""]
        
        for i, entry in enumerate(entries[:5]):
            hostname = entry.hostname
            path = entry.path
            crack_type = ScriptGenerator.suggest_crack_type(entry)
            
            if not crack_type:
                continue
            
            lines.append(f"// === 请求 {i+1}: {entry.method} {hostname}{path} ===")
            
            # 显示检测到的 VIP 字段
            if entry.resp_json:
                vip_fields = VIPFieldDetector.detect_json_fields(entry.resp_json)
                if vip_fields:
                    lines.append("// 检测到的 VIP 字段:")
                    for vf in vip_fields[:10]:
                        lines.append(f"//   {vf['field']} = {vf['value']} [{vf['category']}]")
            
            # 生成模板代码
            if crack_type == "json_replace":
                lines.append("var obj = JSON.parse($response.body);")
                lines.append("// 修改关键字段:")
                if entry.resp_json:
                    for vf in vip_fields[:5]:
                        if vf['category'] == 'bool_flags':
                            lines.append(f"// obj.{vf['field'].split('.')[-1]} = true;")
                        elif vf['category'] == 'expire_time':
                            lines.append(f"// obj.{vf['field'].split('.')[-1]} = 1879685290000;")
                        elif vf['category'] == 'status_values':
                            lines.append(f"// obj.{vf['field'].split('.')[-1]} = 1;")
                lines.append("$done({body: JSON.stringify(obj)});")
            
            elif crack_type == "regex_replace":
                lines.append("var body = $response.body")
                for vf in vip_fields[:3]:
                    if vf['category'] == 'bool_flags':
                        field_name = vf['field'].split('.')[-1]
                        lines.append(f'  .replace(/{field_name}":\\w+/g, \'{field_name}":true\')')
                lines.append("$done({body});")
            
            elif crack_type == "revenuecat":
                lines.append(CRACK_TEMPLATES["revenuecat"]["qx"])
            
            lines.append("")
        
        # 生成配置
        hostnames = set()
        rewrites = []
        scripts = []
        for e in entries[:5]:
            if e.hostname:
                hostnames.add(e.hostname)
                rewrites.append(ScriptGenerator.generate_qx_rewrite(e.hostname, e.path, "TODO_SCRIPT_URL"))
                scripts.append(ScriptGenerator.generate_surge_script(e.hostname, e.path, "TODO_SCRIPT_URL"))
        
        lines.append("// === 代理配置 ===")
        lines.append("// Quantumult X:")
        lines.append("[rewrite_local]")
        for r in rewrites:
            lines.append(r)
        lines.append("")
        lines.append("[mitm]")
        lines.append(f"hostname = {', '.join(hostnames)}")
        lines.append("")
        lines.append("// Surge:")
        lines.append("[Script]")
        for s in scripts:
            lines.append(s)
        lines.append("")
        lines.append("[MITM]")
        lines.append(f"hostname = %APPEND% {', '.join(hostnames)}")
        
        return '\n'.join(lines)


# ============================================================
# HAR 分析器主类
# ============================================================

class HARAnalyzer:
    """HAR 文件分析器 v2"""
    
    def __init__(self, har_path: str = None, har_data: dict = None):
        self.entries: List[HAREntry] = []
        self.pages = []
        self.creator = {}
        self.version = ''
        
        if har_path:
            self.load(har_path)
        elif har_data:
            self.load_data(har_data)
    
    def load(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            self.load_data(json.load(f))
    
    def load_data(self, data: dict):
        log = data.get('log', data)
        self.version = log.get('version', '1.2')
        self.creator = log.get('creator', {})
        self.pages = log.get('pages', [])
        self.entries = [HAREntry.from_har(e) for e in log.get('entries', [])]
    
    # --- 过滤 ---
    def filter(self, **kwargs) -> List[HAREntry]:
        return [e for e in self.entries if e.matches_filter(**kwargs)]
    
    def json_apis(self) -> List[HAREntry]:
        return self.filter(resource_type='json')
    
    def by_domain(self, domain: str) -> List[HAREntry]:
        return self.filter(domain=domain)
    
    def by_hostnames(self, hostnames: List[str]) -> List[HAREntry]:
        result = []
        for hn in hostnames:
            result.extend(self.by_domain(hn))
        return result
    
    def by_url_keyword(self, keyword: str) -> List[HAREntry]:
        return self.filter(url_contains=keyword)
    
    # --- VIP 分析 ---
    def find_vip_related(self) -> List[HAREntry]:
        """查找 VIP/会员相关请求"""
        keywords = [
            'vip', 'member', 'premium', 'subscribe', 'subscription',
            'payment', 'order', 'purchase', 'unlock', 'privilege',
            'entitlement', 'verifyReceipt', 'profile', 'user/info',
            'account', 'revenuecat',
        ]
        results = []
        seen = set()
        for e in self.entries:
            url_lower = e.url.lower()
            for kw in keywords:
                if kw in url_lower:
                    results.append(e)
                    break
            if e.resp_json:
                # 深搜响应 JSON 中的 VIP 字段
                vip_fields = VIPFieldDetector.detect_json_fields(e.resp_json)
                if vip_fields and e.url not in seen:
                    seen.add(e.url)
                    results.append(e)
                    e._vip_fields = vip_fields
        return results
    
    def find_ad_related(self) -> List[HAREntry]:
        """查找广告相关请求"""
        results = []
        for e in self.entries:
            for pat in AD_PATTERNS:
                if re.search(pat, e.hostname, re.IGNORECASE):
                    results.append(e)
                    break
        return results
    
    def find_auth_related(self) -> List[HAREntry]:
        """查找认证/登录相关请求"""
        keywords = ['login', 'signin', 'auth', 'token', 'session', 'oauth']
        return [e for e in self.entries if any(kw in e.url.lower() for kw in keywords)]
    
    def find_config_related(self) -> List[HAREntry]:
        """查找配置初始化请求（含版本号、特性开关等）"""
        keywords = ['config', 'init', 'feature', 'settings', 'abtest', 'experiment']
        return [e for e in self.entries if any(kw in e.url.lower() for kw in keywords) and e.resource_type == 'json']
    
    # --- 对比分析 ---
    def diff(self, other: 'HARAnalyzer') -> Dict:
        """对比两个 HAR 包差异"""
        urls_self = {e.url for e in self.entries}
        urls_other = {e.url for e in other.entries}
        
        # 找出响应不同的相同 URL
        diff_entries = []
        self_map = {e.url: e for e in self.entries if e.resp_json}
        other_map = {e.url: e for e in other.entries if e.resp_json}
        
        for url in urls_self & urls_other:
            e1 = self_map.get(url)
            e2 = other_map.get(url)
            if e1 and e2:
                # 检测 JSON 差异
                vip1 = VIPFieldDetector.detect_json_fields(e1.resp_json) if e1.resp_json else []
                vip2 = VIPFieldDetector.detect_json_fields(e2.resp_json) if e2.resp_json else []
                if len(vip1) != len(vip2) or any(
                    v1.get('value') != v2.get('value') 
                    for v1, v2 in zip(vip1, vip2) if v1.get('field') == v2.get('field')
                ):
                    diff_entries.append({
                        'url': url,
                        'hostname': e1.hostname,
                        'path': e1.path,
                        'method': e1.method,
                        'before_vip_fields': [{'field': v['field'], 'value': v['value']} for v in vip1],
                        'after_vip_fields': [{'field': v['field'], 'value': v['value']} for v in vip2] if vip2 else None,
                    })
        
        return {
            'only_in_self': [e.url for e in self.entries if e.url in urls_self - urls_other],
            'only_in_other': [e.url for e in other.entries if e.url in urls_other - urls_self],
            'common_with_diff': diff_entries,
            'self_total': len(self.entries),
            'other_total': len(other.entries),
        }
    
    # --- 统计 ---
    def get_statistics(self) -> Dict:
        if not self.entries:
            return {}
        return {
            'total_requests': len(self.entries),
            'total_time_ms': sum(e.time for e in self.entries),
            'total_resp_size': sum(e.resp_body_size for e in self.entries),
            'avg_time_ms': int(sum(e.time for e in self.entries) / len(self.entries)) if self.entries else 0,
            'by_method': dict(Counter(e.method for e in self.entries)),
            'by_status': dict(Counter(f"{e.status // 100}xx" for e in self.entries)),
            'by_resource_type': dict(Counter(e.resource_type for e in self.entries)),
            'unique_hostnames': len(set(e.hostname for e in self.entries)),
            'top_hostnames': dict(Counter(e.hostname for e in self.entries).most_common(20)),
            'json_apis_count': sum(1 for e in self.entries if e.resource_type == 'json'),
            'revenuecat_count': sum(1 for e in self.entries if 'revenuecat' in e.url.lower()),
        }
    
    # --- 导出 ---
    def export_json(self, entries: List[HAREntry] = None, output_path: str = None) -> str:
        if entries is None:
            entries = self.entries
        data = [{
            'method': e.method, 'url': e.url, 'status': e.status,
            'content_type': e.content_type, 'resource_type': e.resource_type,
            'hostname': e.hostname, 'path': e.path, 'time_ms': e.time,
            'resp_size': e.resp_body_size,
            'response_body_preview': e.resp_text[:2000],
        } for e in entries]
        j = json.dumps(data, ensure_ascii=False, indent=2)
        if output_path:
            with open(output_path, 'w') as f:
                f.write(j)
        return j
    
    def export_csv(self, entries: List[HAREntry] = None, output_path: str = None) -> str:
        if entries is None:
            entries = self.entries
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['Method', 'URL', 'Status', 'Hostname', 'Path', 'Type', 'Size', 'Time(ms)', 'ResponsePreview'])
        for e in entries:
            w.writerow([e.method, e.url, e.status, e.hostname, e.path, e.resource_type, e.resp_body_size, e.time, e.resp_text[:200]])
        s = buf.getvalue()
        if output_path:
            with open(output_path, 'w') as f:
                f.write(s)
        return s
    
    # --- 显示 ---
    def summary(self):
        s = self.get_statistics()
        print(f"\n{'='*60}")
        print(f"  HAR Analysis v2")
        print(f"{'='*60}")
        print(f"  Creator: {self.creator.get('name', '?')} {self.creator.get('version', '')}")
        print(f"  Requests: {s.get('total_requests', 0)}")
        print(f"  JSON APIs: {s.get('json_apis_count', 0)}")
        print(f"  RevenueCat: {s.get('revenuecat_count', 0)}")
        print(f"  Domains: {s.get('unique_hostnames', 0)}")
        print(f"  Total time: {s.get('total_time_ms', 0):.0f}ms")
        print(f"  Total size: {self._fmt(s.get('total_resp_size', 0))}")
        print(f"\n  Methods: {s.get('by_method', {})}")
        print(f"  Status: {s.get('by_status', {})}")
        print(f"  Resource Types: {s.get('by_resource_type', {})}")
        print(f"\n  Top Hostnames:")
        for h, c in list(s.get('top_hostnames', {}).items())[:10]:
            print(f"    {h}: {c}")
        print(f"{'='*60}\n")
    
    def print_vip(self, entries: List[HAREntry] = None):
        if entries is None:
            entries = self.find_vip_related()
        
        print(f"\n--- VIP/Member Related Requests ({len(entries)}) ---")
        for i, e in enumerate(entries):
            print(f"\n[{i+1}] {e.method} {e.status} {e.hostname}{e.path}")
            print(f"    URL: {e.url[:120]}")
            print(f"    Type: {e.resource_type} | Size: {self._fmt(e.resp_body_size)}")
            
            if e.resp_json:
                fields = VIPFieldDetector.detect_json_fields(e.resp_json)
                if fields:
                    print(f"    VIP Fields ({len(fields)}):")
                    for f in fields[:15]:
                        print(f"      {f['field']} = {f['value']} [{f['category']}]")
            
            if e.resp_text and not e.resp_json:
                print(f"    Body preview: {e.resp_text[:200]}...")
    
    def print_ads(self, entries: List[HAREntry] = None):
        if entries is None:
            entries = self.find_ad_related()
        
        print(f"\n--- Ad-Related Requests ({len(entries)}) ---")
        for e in entries:
            print(f"  {e.method} {e.status} {e.hostname}{e.path[:60]}")
            print(f"  → {e.url[:120]}")
    
    @staticmethod
    def _fmt(size: int) -> str:
        for u in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{u}"
            size /= 1024
        return f"{size:.1f}TB"


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    
    p = argparse.ArgumentParser(description='HAR Analyzer v2 - 去广告/爆破会员辅助')
    p.add_argument('har_file', nargs='?', help='HAR 文件路径')
    p.add_argument('-s', '--summary', action='store_true', help='显示摘要')
    p.add_argument('--find-vip', action='store_true', help='查找 VIP 请求')
    p.add_argument('--find-ads', action='store_true', help='查找广告请求')
    p.add_argument('--find-auth', action='store_true', help='查找认证请求')
    p.add_argument('--find-config', action='store_true', help='查找配置请求')
    p.add_argument('--gen-script', action='store_true', help='生成破解脚本模板')
    p.add_argument('--diff', help='对比两个 HAR 文件 (--diff file2.har)')
    p.add_argument('--domain', help='按域名过滤')
    p.add_argument('--method', help='按方法过滤')
    p.add_argument('--url-contains', help='URL 包含关键词')
    p.add_argument('--resource-type', help='过滤资源类型 (json/document/image/script)')
    p.add_argument('--export-json', help='导出 JSON')
    p.add_argument('--export-csv', help='导出 CSV')
    p.add_argument('--app-name', default='App', help='脚本中的应用名')
    p.add_argument('--top', type=int, default=20, help='最多显示条数')
    p.add_argument('--no-body', action='store_true', help='不显示响应体')
    
    args = p.parse_args()
    
    if not args.har_file and not args.diff:
        p.print_help()
        return
    
    # 对比模式
    if args.diff:
        if not args.har_file:
            print("需要两个 HAR 文件: --diff free.har --har_file vip.har")
            return
        a1 = HARAnalyzer(args.har_file)
        a2 = HARAnalyzer(args.diff)
        d = a1.diff(a2)
        print(f"\n=== HAR Diff ===")
        print(f"  File1: {args.har_file} ({d['self_total']} requests)")
        print(f"  File2: {args.diff} ({d['other_total']} requests)")
        print(f"  Only in File1: {len(d['only_in_self'])}")
        print(f"  Only in File2: {len(d['only_in_other'])}")
        print(f"  Different responses: {len(d['common_with_diff'])}")
        
        if d['common_with_diff']:
            print(f"\n--- Key Differences (VIP fields) ---")
            for diff in d['common_with_diff']:
                print(f"\n  {diff['method']} {diff['hostname']}{diff['path']}")
                if diff.get('before_vip_fields'):
                    print(f"    File1 fields:")
                    for f in diff['before_vip_fields'][:5]:
                        print(f"      {f['field']} = {f['value']}")
                if diff.get('after_vip_fields') is not None:
                    print(f"    File2 fields:")
                    for f in diff['after_vip_fields'][:5]:
                        print(f"      {f['field']} = {f['value']}")
        return
    
    # 正常模式
    a = HARAnalyzer(args.har_file)
    
    if args.summary or not any([args.find_vip, args.find_ads, args.find_auth, 
                                 args.find_config, args.domain, args.method,
                                 args.url_contains, args.resource_type]):
        a.summary()
        return
    
    # 过滤
    entries = None
    title = ""
    
    if args.find_vip:
        entries = a.find_vip_related()
        title = "VIP/Member Related"
    elif args.find_ads:
        entries = a.find_ad_related()
        title = "Ad Related"
    elif args.find_auth:
        entries = a.find_auth_related()
        title = "Auth Related"
    elif args.find_config:
        entries = a.find_config_related()
        title = "Config Related"
    elif args.domain:
        entries = a.by_domain(args.domain)
        title = f"Domain: {args.domain}"
    elif args.method:
        entries = a.filter(method=args.method)
        title = f"Method: {args.method}"
    elif args.url_contains:
        entries = a.by_url_keyword(args.url_contains)
        title = f"URL contains: {args.url_contains}"
    
    if entries:
        entries = entries[:args.top]
        print(f"\n=== {title} ({len(entries)} results) ===")
        
        if args.no_body or args.find_ads:
            for i, e in enumerate(entries):
                print(f"  [{i+1}] {e.method} {e.status} {e.hostname}{e.path[:80]}")
                print(f"       {e.url[:150]}")
        else:
            a.print_vip(entries) if args.find_vip else None
        
        if args.gen_script:
            print("\n" + "="*60)
            print(ScriptGenerator.generate_crack_script(entries, args.app_name))
        
        if args.export_json:
            a.export_json(entries, args.export_json)
            print(f"\nJSON exported: {args.export_json}")
        if args.export_csv:
            a.export_csv(entries, args.export_csv)
            print(f"\nCSV exported: {args.export_csv}")


if __name__ == '__main__':
    main()
