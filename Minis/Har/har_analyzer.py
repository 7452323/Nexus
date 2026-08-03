#!/usr/bin/env python3
"""
HAR Analyzer - 综合 HAR 文件分析工具
用于抓包分析、会员爆破、去广告场景

功能：
- 解析 HAR 1.2 格式
- 请求过滤（域名/方法/状态码/内容类型/关键词）
- 请求统计（按类型/域名/状态码）
- 响应体提取（JSON/Text）
- 导出过滤后的请求为 JSON/CSV
- 对比两个 HAR 文件差异

灵感来源：
- harparser: HAR 1.2 规范解析
- purewater-har: 过滤/搜索/详情展示
- hara: 按资源类型统计
"""

import json
import sys
import os
import re
import csv
import io
from collections import defaultdict, Counter
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable


class HAREntry:
    """单条 HAR 请求记录"""
    
    def __init__(self, data: dict):
        self._raw = data
        self.started = data.get('startedDateTime', '')
        self.time = data.get('time', 0)
        self.timings = data.get('timings', {})
        
        req = data.get('request', {})
        self.method = req.get('method', 'GET')
        self.url = req.get('url', '')
        self.http_version = req.get('httpVersion', '')
        self.headers = {h['name'].lower(): h['value'] for h in req.get('headers', [])}
        self.query_params = {q['name']: q['value'] for q in req.get('queryString', [])}
        self.post_data = req.get('postData', {})
        self.req_headers_size = req.get('headersSize', 0)
        self.req_body_size = req.get('bodySize', 0)
        
        resp = data.get('response', {})
        self.status = resp.get('status', 0)
        self.status_text = resp.get('statusText', '')
        self.content_type = self._extract_content_type(resp)
        self.resp_headers = {h['name'].lower(): h['value'] for h in resp.get('headers', [])}
        self.content = resp.get('content', {})
        self.resp_body_size = resp.get('bodySize', 0)
        self.redirect_url = resp.get('redirectURL', '')
        
        # 解析 URL
        parsed = urlparse(self.url)
        self.scheme = parsed.scheme
        self.hostname = parsed.hostname or ''
        self.path = parsed.path
        self.query = parsed.query
        self.port = parsed.port
        
        # 资源类型（从 response content mimeType 推断）
        self.resource_type = self._classify_resource()
    
    def _extract_content_type(self, resp: dict) -> str:
        """提取内容类型"""
        # 从 headers 里找
        for h in resp.get('headers', []):
            if h['name'].lower() == 'content-type':
                return h['value'].split(';')[0].strip()
        # 从 content 里找
        return resp.get('content', {}).get('mimeType', '').split(';')[0].strip()
    
    def _classify_resource(self) -> str:
        """按内容类型分类资源"""
        ct = self.content_type.lower()
        if 'html' in ct:
            return 'document'
        elif 'json' in ct:
            return 'json'
        elif 'javascript' in ct or 'js' in ct:
            return 'script'
        elif 'css' in ct:
            return 'stylesheet'
        elif 'image' in ct:
            return 'image'
        elif 'font' in ct:
            return 'font'
        elif 'audio' in ct or 'video' in ct:
            return 'media'
        elif 'text/plain' in ct:
            return 'text'
        else:
            return 'other'
    
    @property
    def response_text(self) -> str:
        """获取响应体文本"""
        text = self.content.get('text', '')
        if text:
            return text
        # 尝试从 base64 解码
        encoding = self.content.get('encoding', '')
        if encoding == 'base64' and text:
            import base64
            try:
                return base64.b64decode(text).decode('utf-8', errors='replace')
            except:
                pass
        return ''
    
    @property
    def response_json(self) -> Optional[dict]:
        """尝试解析 JSON 响应"""
        text = self.response_text
        if text:
            try:
                return json.loads(text)
            except:
                pass
        return None
    
    @property
    def post_text(self) -> str:
        """获取 POST 数据文本"""
        if isinstance(self.post_data, dict):
            return self.post_data.get('text', '')
        return str(self.post_data)
    
    @property
    def post_params(self) -> Dict[str, str]:
        """解析 POST 参数"""
        if isinstance(self.post_data, dict):
            params = {}
            for p in self.post_data.get('params', []):
                params[p.get('name', '')] = p.get('value', '')
            if params:
                return params
        # 尝试从 text 解析 JSON
        text = self.post_text
        if text:
            try:
                return json.loads(text)
            except:
                pass
        return {}
    
    def matches(self, **filters) -> bool:
        """检查是否匹配过滤条件"""
        if 'method' in filters and self.method.upper() != filters['method'].upper():
            return False
        if 'status' in filters:
            s = filters['status']
            if isinstance(s, int) and self.status != s:
                return False
            elif isinstance(s, str):
                # 支持 "2xx", "3xx" 等
                if not re.match(f'^{s[0]}\\d\\d$', str(self.status)):
                    return False
        if 'domain' in filters and filters['domain'] not in self.hostname:
            return False
        if 'url_contains' in filters and filters['url_contains'] not in self.url:
            return False
        if 'path_contains' in filters and filters['path_contains'] not in self.path:
            return False
        if 'content_type' in filters and filters['content_type'] not in self.content_type:
            return False
        if 'resource_type' in filters and self.resource_type != filters['resource_type']:
            return False
        if 'min_size' in filters and self.resp_body_size < filters['min_size']:
            return False
        if 'max_size' in filters and self.resp_body_size > filters['max_size']:
            return False
        if 'min_time' in filters and self.time < filters['min_time']:
            return False
        if 'max_time' in filters and self.time > filters['max_time']:
            return False
        if 'header_contains' in filters:
            target = filters['header_contains'].lower()
            found = False
            for k, v in {**self.headers, **self.resp_headers}.items():
                if target in k or target in v.lower():
                    found = True
                    break
            if not found:
                return False
        if 'response_contains' in filters:
            if filters['response_contains'] not in self.response_text:
                return False
        if 'request_contains' in filters:
            if filters['request_contains'] not in self.post_text:
                return False
        return True
    
    def to_dict(self) -> dict:
        """导出为字典"""
        return {
            'started': self.started,
            'method': self.method,
            'url': self.url,
            'status': self.status,
            'content_type': self.content_type,
            'resource_type': self.resource_type,
            'hostname': self.hostname,
            'path': self.path,
            'time_ms': self.time,
            'resp_size': self.resp_body_size,
            'query_params': self.query_params,
            'request_headers': self.headers,
            'response_headers': self.resp_headers,
            'response_body': self.response_text[:10000],  # 截断
            'post_data': self.post_text[:5000],  # 截断
        }
    
    def __repr__(self):
        return f'<HAREntry {self.method} {self.status} {self.hostname}{self.path[:60]}>'


class HARAnalyzer:
    """HAR 文件分析器"""
    
    def __init__(self, har_path: str = None, har_data: dict = None):
        self.entries: List[HAREntry] = []
        self.pages: List[dict] = []
        self.creator = {}
        self.browser = {}
        self.version = ''
        self.comments = []
        
        if har_path:
            self.load_file(har_path)
        elif har_data:
            self.load_data(har_data)
    
    def load_file(self, path: str):
        """从文件加载 HAR"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.load_data(data)
    
    def load_data(self, data: dict):
        """从字典加载 HAR"""
        log = data.get('log', data)  # 兼容直接传 log 或完整 HAR
        self.version = log.get('version', '1.2')
        self.creator = log.get('creator', {})
        self.browser = log.get('browser', {})
        self.pages = log.get('pages', [])
        self.comments = log.get('comment', [])
        
        entries = log.get('entries', [])
        self.entries = [HAREntry(e) for e in entries]
    
    def filter(self, **filters) -> List[HAREntry]:
        """过滤请求"""
        return [e for e in self.entries if e.matches(**filters)]
    
    def search(self, keyword: str, in_response: bool = True, in_request: bool = True, 
               in_url: bool = True) -> List[HAREntry]:
        """搜索关键词"""
        results = []
        kw = keyword.lower()
        for e in self.entries:
            matched = False
            if in_url and kw in e.url.lower():
                matched = True
            if in_response and kw in e.response_text.lower():
                matched = True
            if in_request and kw in e.post_text.lower():
                matched = True
            if matched:
                results.append(e)
        return results
    
    def find_json_api(self, key: str = None) -> List[HAREntry]:
        """查找 JSON API 请求"""
        results = []
        for e in self.entries:
            if e.resource_type == 'json':
                if key is None or key in e.url or key in e.response_text:
                    results.append(e)
        return results
    
    def find_by_domain(self, domain: str) -> List[HAREntry]:
        """按域名查找"""
        return [e for e in self.entries if domain in e.hostname]
    
    def find_login_related(self) -> List[HAREntry]:
        """查找登录/认证相关请求"""
        keywords = ['login', 'signin', 'auth', 'token', 'session', 'oauth', 'verify', 'captcha']
        results = []
        for e in self.entries:
            url_lower = e.url.lower()
            if any(kw in url_lower for kw in keywords):
                results.append(e)
        return results
    
    def find_ad_requests(self) -> List[HAREntry]:
        """查找广告相关请求"""
        ad_patterns = [
            'ad.', 'ads.', 'adservice', 'doubleclick', 'googlesyndication',
            'google-analytics', 'analytics', 'tracking', 'track.', 'log.',
            'promotion', 'sponsor', 'banner', 'commercial'
        ]
        results = []
        for e in self.entries:
            hostname_lower = e.hostname.lower()
            if any(pat in hostname_lower for pat in ad_patterns):
                results.append(e)
        return results
    
    def find_vip_related(self) -> List[HAREntry]:
        """查找 VIP/会员相关请求"""
        keywords = ['vip', 'member', 'premium', 'subscribe', 'subscription', 
                     'payment', 'order', 'purchase', 'unlock', 'privilege']
        results = []
        for e in self.entries:
            if any(kw in e.url.lower() for kw in keywords):
                results.append(e)
            elif any(kw in e.response_text.lower() for kw in keywords):
                results.append(e)
        return results
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        if not self.entries:
            return {}
        
        total_time = sum(e.time for e in self.entries)
        total_size = sum(e.resp_body_size for e in self.entries)
        
        return {
            'total_requests': len(self.entries),
            'total_time_ms': total_time,
            'total_resp_size': total_size,
            'avg_time_ms': total_time / len(self.entries) if self.entries else 0,
            'avg_resp_size': total_size / len(self.entries) if self.entries else 0,
            'by_method': dict(Counter(e.method for e in self.entries)),
            'by_status': dict(Counter(str(e.status) for e in self.entries)),
            'by_resource_type': dict(Counter(e.resource_type for e in self.entries)),
            'by_content_type': dict(Counter(e.content_type for e in self.entries)),
            'by_domain': dict(Counter(e.hostname for e in self.entries).most_common(20)),
            'domains_count': len(set(e.hostname for e in self.entries)),
        }
    
    def get_domain_summary(self) -> List[dict]:
        """按域名汇总"""
        domain_data = defaultdict(lambda: {
            'count': 0, 'total_time': 0, 'total_size': 0,
            'methods': Counter(), 'statuses': Counter()
        })
        
        for e in self.entries:
            d = domain_data[e.hostname]
            d['count'] += 1
            d['total_time'] += e.time
            d['total_size'] += e.resp_body_size
            d['methods'][e.method] += 1
            d['statuses'][str(e.status)] += 1
        
        result = []
        for domain, data in sorted(domain_data.items(), key=lambda x: x[1]['count'], reverse=True):
            result.append({
                'domain': domain,
                'requests': data['count'],
                'total_time_ms': data['total_time'],
                'total_size': data['total_size'],
                'methods': dict(data['methods']),
                'statuses': dict(data['statuses']),
            })
        return result
    
    def export_json(self, entries: List[HAREntry] = None, output_path: str = None) -> str:
        """导出为 JSON"""
        if entries is None:
            entries = self.entries
        data = [e.to_dict() for e in entries]
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        return json_str
    
    def export_csv(self, entries: List[HAREntry] = None, output_path: str = None) -> str:
        """导出为 CSV"""
        if entries is None:
            entries = self.entries
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Started', 'Method', 'URL', 'Status', 'Content-Type', 'Resource-Type',
            'Hostname', 'Path', 'Time(ms)', 'Resp-Size', 'Response-Body-Preview'
        ])
        
        for e in entries:
            writer.writerow([
                e.started, e.method, e.url, e.status, e.content_type,
                e.resource_type, e.hostname, e.path, e.time, e.resp_body_size,
                e.response_text[:500]
            ])
        
        csv_str = output.getvalue()
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(csv_str)
        return csv_str
    
    def diff(self, other: ' HARAnalyzer') -> dict:
        """对比两个 HAR 文件的差异"""
        urls_self = {e.url for e in self.entries}
        urls_other = {e.url for e in other.entries}
        
        return {
            'only_in_self': len(urls_self - urls_other),
            'only_in_other': len(urls_other - urls_self),
            'common': len(urls_self & urls_other),
            'self_total': len(self.entries),
            'other_total': len(other.entries),
        }
    
    def print_summary(self):
        """打印摘要"""
        stats = self.get_statistics()
        print(f"\n{'='*60}")
        print(f"  HAR Analysis Summary")
        print(f"{'='*60}")
        print(f"  Creator: {self.creator.get('name', 'unknown')} {self.creator.get('version', '')}")
        print(f"  Total Requests: {stats.get('total_requests', 0)}")
        print(f"  Total Time: {stats.get('total_time_ms', 0):.0f} ms")
        print(f"  Total Response Size: {self._format_bytes(stats.get('total_resp_size', 0))}")
        print(f"  Unique Domains: {stats.get('domains_count', 0)}")
        print(f"\n  By Method:")
        for method, count in sorted(stats.get('by_method', {}).items()):
            print(f"    {method}: {count}")
        print(f"\n  By Status:")
        for status, count in sorted(stats.get('by_status', {}).items()):
            print(f"    {status}: {count}")
        print(f"\n  By Resource Type:")
        for rtype, count in sorted(stats.get('by_resource_type', {}).items(), key=lambda x: -x[1]):
            print(f"    {rtype}: {count}")
        print(f"\n  Top Domains:")
        for domain, count in list(stats.get('by_domain', {}).items())[:10]:
            print(f"    {domain}: {count}")
        print(f"{'='*60}\n")
    
    def print_entries(self, entries: List[HAREntry] = None, max_body_len: int = 200):
        """打印请求详情"""
        if entries is None:
            entries = self.entries
        
        for i, e in enumerate(entries):
            print(f"\n--- [{i+1}/{len(entries)}] ---")
            print(f"  {e.method} {e.status} {e.url}")
            print(f"  Type: {e.resource_type} | Size: {self._format_bytes(e.resp_body_size)} | Time: {e.time:.0f}ms")
            
            # 打印响应体预览
            body = e.response_text
            if body:
                print(f"  Response ({len(body)} chars):")
                print(f"    {body[:max_body_len]}{'...' if len(body) > max_body_len else ''}")
            
            # 打印 POST 数据
            post = e.post_text
            if post:
                print(f"  POST Data ({len(post)} chars):")
                print(f"    {post[:max_body_len]}{'...' if len(post) > max_body_len else ''}")
    
    @staticmethod
    def _format_bytes(size: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HAR Analyzer - 抓包分析工具')
    parser.add_argument('har_file', help='HAR 文件路径')
    parser.add_argument('-s', '--summary', action='store_true', help='显示摘要统计')
    parser.add_argument('-f', '--filter', help='过滤条件，格式: key1=val1,key2=val2')
    parser.add_argument('--search', help='搜索关键词')
    parser.add_argument('--domain', help='按域名过滤')
    parser.add_argument('--method', help='按方法过滤 (GET/POST)')
    parser.add_argument('--status', help='按状态码过滤 (200, 2xx)')
    parser.add_argument('--url-contains', help='URL 包含')
    parser.add_argument('--response-contains', help='响应体包含')
    parser.add_argument('--find-vip', action='store_true', help='查找 VIP 相关请求')
    parser.add_argument('--find-ads', action='store_true', help='查找广告相关请求')
    parser.add_argument('--find-login', action='store_true', help='查找登录相关请求')
    parser.add_argument('--find-json', action='store_true', help='查找 JSON API')
    parser.add_argument('--export-json', help='导出为 JSON 文件')
    parser.add_argument('--export-csv', help='导出为 CSV 文件')
    parser.add_argument('--top', type=int, default=20, help='显示前 N 条')
    parser.add_argument('--no-body', action='store_true', help='不显示响应体')
    
    args = parser.parse_args()
    
    # 加载 HAR
    analyzer = HARAnalyzer(args.har_file)
    
    # 显示摘要
    if args.summary or not any([args.filter, args.search, args.domain, args.method,
                                 args.status, args.url_contains, args.response_contains,
                                 args.find_vip, args.find_ads, args.find_login, args.find_json]):
        analyzer.print_summary()
        return
    
    # 过滤
    entries = None
    
    if args.find_vip:
        entries = analyzer.find_vip_related()
        print(f"\n=== VIP/会员相关请求 ({len(entries)} 条) ===")
    elif args.find_ads:
        entries = analyzer.find_ad_requests()
        print(f"\n=== 广告相关请求 ({len(entries)} 条) ===")
    elif args.find_login:
        entries = analyzer.find_login_related()
        print(f"\n=== 登录相关请求 ({len(entries)} 条) ===")
    elif args.find_json:
        entries = analyzer.find_json_api()
        print(f"\n=== JSON API 请求 ({len(entries)} 条) ===")
    elif args.search:
        entries = analyzer.search(args.search)
        print(f"\n=== 搜索 '{args.search}' 结果 ({len(entries)} 条) ===")
    elif args.domain:
        entries = analyzer.find_by_domain(args.domain)
        print(f"\n=== 域名 '{args.domain}' 请求 ({len(entries)} 条) ===")
    elif args.filter:
        filters = {}
        for pair in args.filter.split(','):
            k, v = pair.split('=', 1)
            filters[k.strip()] = v.strip()
        entries = analyzer.filter(**filters)
        print(f"\n=== 过滤结果 ({len(entries)} 条) ===")
    
    # 显示结果
    if entries is not None:
        if args.top:
            entries = entries[:args.top]
        
        if args.no_body:
            for i, e in enumerate(entries):
                print(f"  [{i+1}] {e.method} {e.status} {e.url}")
                print(f"       Type: {e.resource_type} | Size: {HARAnalyzer._format_bytes(e.resp_body_size)} | Time: {e.time:.0f}ms")
        else:
            analyzer.print_entries(entries)
        
        # 导出
        if args.export_json:
            analyzer.export_json(entries, args.export_json)
            print(f"\n已导出 JSON: {args.export_json}")
        if args.export_csv:
            analyzer.export_csv(entries, args.export_csv)
            print(f"\n已导出 CSV: {args.export_csv}")


if __name__ == '__main__':
    main()
