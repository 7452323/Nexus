#!/usr/bin/env python3
"""
lzlukvca.cc (黄豆短剧) - 金币播放破解脚本生成器
基于 main.dart.js 静态逆向

来源: https://github.com/lzlukvca.cc
分析样本: 2026-08-04
- main.dart.js (6.7MB) 内嵌 API 路径和字段定义
- API base: hdmgdj.com / hddj05.com / hddj06.com / hddj07.com / fsbd.yskkkkb.me
- 核心金币字段: coin_consume_amount, coin_balance_before/after, coin_quantity
- 播放接口: POST /api/drama/play
- 锁定字段: is_free, is_coin, need_coin, cost_gold
"""

import os

CRACK_JS = '''// ========================================================
// 黄豆短剧 (lzlukvca.cc) 金币播放破解
// 基于 main.dart.js 静态逆向 (2026-08-04)
// 作者: Minis
// ========================================================

// [rewrite_local]
// ^https?://[a-z0-9-]+\\.[a-z]+/api/drama/play url script-response-body <this_script.js>
// ^https?://[a-z0-9-]+\\.[a-z]+/api/drama/detail url script-response-body <this_script.js>
//
// [mitm]
// hostname = *.hddj05.com, *.hddj06.com, *.hddj07.com, *.hdmgdj.com, *.fsbd.yskkkkb.me

(function() {
    'use strict';

    let body;
    try {
        body = JSON.parse($response.body);
    } catch (e) {
        $done({});
        return;
    }

    if (!body || typeof body !== 'object') {
        $done({});
        return;
    }

    // ========================================================
    // 金币破解核心 - 递归修改所有金币相关字段
    // ========================================================
    function unlock(obj) {
        if (!obj || typeof obj !== 'object') return;

        if (Array.isArray(obj)) {
            obj.forEach(unlock);
            return;
        }

        // 扣币字段清零
        if ('coin_consume_amount' in obj) obj.coin_consume_amount = 0;
        if ('cost_gold' in obj) obj.cost_gold = 0;
        if ('consume_amount' in obj) obj.consume_amount = 0;
        if ('amount' in obj) obj.amount = 0;

        // 余额字段设大
        if ('coin_balance_before' in obj) obj.coin_balance_before = 999999;
        if ('coin_balance_after' in obj) obj.coin_balance_after = 999999;
        if ('coin_quantity' in obj) obj.coin_quantity = 999999;
        if ('today_coin' in obj) obj.today_coin = 999999;
        if ('total_coin' in obj) obj.total_coin = 999999;
        if ('gold_balance' in obj) obj.gold_balance = 999999;
        if ('min_price_coin' in obj) obj.min_price_coin = 0;
        if ('max_reward_coin' in obj) obj.max_reward_coin = 999999;
        if ('pending_coin' in obj) obj.pending_coin = 0;

        // 解锁标记
        if ('is_free' in obj) obj.is_free = 1;
        if ('is_coin' in obj) obj.is_coin = 0;
        if ('need_coin' in obj) obj.need_coin = 0;
        if ('is_locked' in obj) obj.is_locked = 0;
        if ('locked' in obj) obj.locked = false;
        if ('need_pay' in obj) obj.need_pay = false;
        if ('is_pay' in obj) obj.is_pay = 1;
        if ('is_vip' in obj) obj.is_vip = true;
        if ('vip' in obj) obj.vip = true;

        // 递归子对象
        for (var key in obj) {
            if (obj[key] && typeof obj[key] === 'object') {
                unlock(obj[key]);
            }
        }
    }

    unlock(body);

    $done({body: JSON.stringify(body)});
})();
'''


QX_CONFIG = '''[rewrite_local]
^https?://[a-z0-9-]+\\.[a-z]+/api/drama/play url script-response-body https://raw.githubusercontent.com/your-repo/main/lzlukvca.js
^https?://[a-z0-9-]+\\.[a-z]+/api/drama/detail url script-response-body https://raw.githubusercontent.com/your-repo/main/lzlukvca.js

[mitm]
hostname = *.hddj05.com, *.hddj06.com, *.hddj07.com, *.hdmgdj.com, *.fsbd.yskkkkb.me
'''

SURGE_CONFIG = '''[Script]
黄豆短剧 = type=http-response,pattern=^https?://[^/]+/api/drama/(play|detail),requires-body=1,max-size=-1,script-path=https://raw.githubusercontent.com/your-repo/main/lzlukvca.js

[MITM]
hostname = *.hddj05.com, *.hddj06.com, *.hddj07.com, *.hdmgdj.com, *.fsbd.yskkkkb.me
'''

LOON_CONFIG = '''#!name = 黄豆短剧破解
#!desc = 拦截扣币改为0金币播放
#!author = Minis
#!date = 2026-08-04

[Rule]
DOMAIN, hddj05.com, REJECT
DOMAIN, hddj06.com, REJECT
DOMAIN, hddj07.com, REJECT

[Rewrite]
^https?://[^/]+/api/drama/play$ script-response-body https://raw.githubusercontent.com/your-repo/main/lzlukvca.js
^https?://[^/]+/api/drama/detail$ script-response-body https://raw.githubusercontent.com/your-repo/main/lzlukvca.js

[MitM]
hostname = hddj05.com, hddj06.com, hddj07.com, hdmgdj.com, fsbd.yskkkkb.me
'''


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lzlukvca')
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'lzlukvca.js'), 'w', encoding='utf-8') as f:
        f.write(CRACK_JS)
    print(f"[+] lzlukvca.js written")

    with open(os.path.join(out_dir, 'qx.conf'), 'w', encoding='utf-8') as f:
        f.write(QX_CONFIG)
    print(f"[+] qx.conf written")

    with open(os.path.join(out_dir, 'surge.conf'), 'w', encoding='utf-8') as f:
        f.write(SURGE_CONFIG)
    print(f"[+] surge.conf written")

    with open(os.path.join(out_dir, 'loon.plugin'), 'w', encoding='utf-8') as f:
        f.write(LOON_CONFIG)
    print(f"[+] loon.plugin written")

    print(f"\n=== 使用方法 ===")
    print(f"1. 上传 lzlukvca.js 到 GitHub raw URL")
    print(f"2. 替换 conf 文件中的 <your-repo>")
    print(f"3. QX: 粘贴 qx.conf 内容")
    print(f"4. Surge: 粘贴 surge.conf 内容")
    print(f"5. Loon: 安装 loon.plugin 文件")
    print(f"6. 开启 MITM 并信任证书")
    print(f"\n=== 注意 ===")
    print(f"⚠️ Cloudflare 风控严格，需要保持登录状态")
    print(f"⚠️ token 来自 Flutter localStorage 'app_token_info'")


if __name__ == '__main__':
    main()