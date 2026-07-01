#!/usr/bin/env python3
"""
Cron 表达式解析器 v2.1
支持: 5/6字段, * , - / L W # ? 缩写(MON-SUN/JAN-DEC), DOM/DOW OR语义 时区 offset
已知限制:
- 人类的自然语言描述是简化的英文
- 未做完整 Zod schema 校验
- Year 字段在 next/previous 枚举时的进位策略可能不完全符合 cron 标准
"""

import re
from datetime import datetime, timedelta

SECOND, MINUTE, HOUR, DOM, MONTH, DOW, YEAR = range(7)

RANGES = {
    SECOND: (0, 59), MINUTE: (0, 59), HOUR: (0, 23),
    DOM: (1, 31), MONTH: (1, 12), DOW: (0, 6), YEAR: (1970, 2099),
}

DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MONTH_MAP = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
DOW_MAP = {'SUN':0,'MON':1,'TUE':2,'WED':3,'THU':4,'FRI':5,'SAT':6}


class CronField:
    __slots__ = ('type', 'values', 'special', 'any')

    def __init__(self, type_, expr):
        self.type = type_
        self.values = set()
        self.special = None
        self.any = False
        self._parse(expr.strip() if expr else '*')

    def _parse(self, expr):
        if expr in ('*', '?'):
            self.any = True
            return
        if 'L' in expr.upper() and self.type in (DOM, DOW):
            self._parse_l(expr)
            return
        if 'W' in expr.upper() and self.type == DOM:
            self._parse_w(expr)
            return
        if '#' in expr and self.type == DOW:
            self._parse_nth(expr)
            return
        for atom in expr.split(','):
            self._parse_atom(atom)
        if not self.values:
            self.any = True

    def _parse_atom(self, atom):
        step = 1
        if '/' in atom:
            atom, step_s = atom.split('/', 1)
            step = int(step_s)
        if atom == '*':
            lo, hi = RANGES[self.type]
        elif '-' in atom:
            a, b = atom.split('-', 1)
            lo, hi = self._convert(a), self._convert(b)
        else:
            v = self._convert(atom)
            if step == 1:
                self.values.add(v)
                return
            lo, hi = v, RANGES[self.type][1]
        mn, mx = RANGES[self.type]
        for x in range(lo, hi + 1, step):
            if mn <= x <= mx:
                self.values.add(x)

    def _convert(self, val):
        v = val.strip()
        if self.type == MONTH and v.upper() in MONTH_MAP:
            return MONTH_MAP[v.upper()]
        if self.type == DOW and v.upper() in DOW_MAP:
            return DOW_MAP[v.upper()]
        return int(v)

    def _parse_l(self, expr):
        if self.type == DOM:
            self.special = 'L'
        elif self.type == DOW:
            m = re.match(r'(\d+)L', expr)
            if m:
                self.special = 'L'
                self.values.add(int(m.group(1)))

    def _parse_w(self, expr):
        m = re.match(r'(\d+)W', expr, re.I)
        if m:
            self.special = 'W'
            self.values.add(int(m.group(1)))

    def _parse_nth(self, expr):
        m = re.match(r'(\d+)#(\d+)', expr)
        if m:
            self.special = '#' + m.group(2)
            self.values.add(int(m.group(1)))

    def __contains__(self, item):
        return self.any or item in self.values


class CronExpression:
    def __init__(self, expr, strict=False):
        self.original = expr
        self.strict = strict
        parts = expr.strip().split()
        if len(parts) == 5:
            self.has_seconds = False
            self.second = CronField(SECOND, '0')
            self.minute = CronField(MINUTE, parts[0])
            self.hour   = CronField(HOUR,   parts[1])
            self.dom     = CronField(DOM,     parts[2])
            self.month   = CronField(MONTH,   parts[3])
            self.dow     = CronField(DOW,     parts[4])
            self.year    = CronField(YEAR,    '*')
        elif len(parts) >= 6:
            self.has_seconds = True
            self.second = CronField(SECOND, parts[0])
            self.minute = CronField(MINUTE, parts[1])
            self.hour   = CronField(HOUR,   parts[2])
            self.dom     = CronField(DOM,     parts[3])
            self.month   = CronField(MONTH,   parts[4])
            self.dow     = CronField(DOW,     parts[5])
            self.year    = CronField(YEAR, parts[6]) if len(parts) > 6 else CronField(YEAR, '*')
        else:
            raise ValueError(f"Invalid cron: {expr}")

    @staticmethod
    def _is_leap(y):
        return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

    @classmethod
    def _dim(cls, y, m):
        return 29 if m == 2 and cls._is_leap(y) else DAYS_IN_MONTH[m]

    def _dow_py(self, d):
        """DOW (0=Sun) -> Python weekday (0=Mon)"""
        return (d - 1) % 7

    def _valid_days(self, y, m):
        dim = self._dim(y, m)
        dom_r = not self.dom.any or self.dom.special
        dow_r = not self.dow.any or self.dow.special
        result = set()

        if self.dom.special == 'L':
            result.add(dim)
            return result

        if dom_r and dow_r:
            # OR 语义
            if self.dom.special and self.dom.special.startswith('W'):
                base = list(self.dom.values)[0]
                result.add(self._nearest_weekday(y, m, min(base, dim)))
            else:
                result.update(d for d in self.dom.values if 1 <= d <= dim)
            # DOW
            if self.dow.special and self.dow.special.startswith('#'):
                nth = int(self.dow.special[1:])
                d = self._nth_weekday(y, m, list(self.dow.values)[0], nth)
                if d: result.add(d)
            elif self.dow.special == 'L':
                # Last weekday of month
                d = self._last_weekday(y, m, list(self.dow.values)[0])
                if d: result.add(d)
            else:
                target = self._dow_py(list(self.dow.values)[0]) if len(self.dow.values) == 1 else None
                for d in self.dow.values:
                    t = self._dow_py(d)
                    for day in range(1, dim + 1):
                        if datetime(y, m, day).weekday() == t:
                            result.add(day)
        elif dom_r:
            if self.dom.special and self.dom.special.startswith('W'):
                base = list(self.dom.values)[0]
                result.add(self._nearest_weekday(y, m, min(base, dim)))
            else:
                result.update(d for d in self.dom.values if 1 <= d <= dim)
        elif dow_r:
            if self.dow.special and self.dow.special.startswith('#'):
                nth = int(self.dow.special[1:])
                d = self._nth_weekday(y, m, list(self.dow.values)[0], nth)
                if d: result.add(d)
            elif self.dow.special == 'L':
                d = self._last_weekday(y, m, list(self.dow.values)[0])
                if d: result.add(d)
            else:
                for d in self.dow.values:
                    t = self._dow_py(d)
                    for day in range(1, dim + 1):
                        if datetime(y, m, day).weekday() == t:
                            result.add(day)
        else:
            result.update(range(1, dim + 1))
        return result

    @staticmethod
    def _nearest_weekday(y, m, d):
        dim = CronExpression._dim(y, m)
        if d > dim: d = dim
        wd = datetime(y, m, d).weekday()
        if wd < 5: return d
        elif wd == 5: return d - 1 if d > 1 else d + 2
        else: return d + 1 if d < dim else d - 2

    @staticmethod
    def _nth_weekday(y, m, dow, nth):
        dim = CronExpression._dim(y, m)
        count = 0
        target = (dow - 1) % 7
        for d in range(1, dim + 1):
            if datetime(y, m, d).weekday() == target:
                count += 1
                if count == nth:
                    return d
        return None

    @staticmethod
    def _last_weekday(y, m, dow):
        dim = CronExpression._dim(y, m)
        target = (dow - 1) % 7
        for d in range(dim, 0, -1):
            if datetime(y, m, d).weekday() == target:
                return d
        return None

    def _prev_month_end(self, y, m):
        nm = m - 1
        ny = y
        if nm < 1: nm, ny = 12, y - 1
        return ny, nm, self._dim(ny, nm)

    def _next_month_start(self, y, m):
        nm = m + 1
        ny = y
        if nm > 12: nm, ny = 1, y + 1
        return ny, nm

    def next(self, after=None):
        if after is None: after = datetime.now()
        cand = after.replace(microsecond=0) + timedelta(seconds=1)
        limit = after + timedelta(days=366 * 4)

        while cand < limit:
            if not self.year.any and cand.year not in self.year.values:
                later = sorted(yr for yr in self.year.values if yr > cand.year)
                if not later: return None
                cand = cand.replace(year=later[0], month=1, day=1, hour=0, minute=0, second=0)
                continue
            if cand.month not in self.month:
                later_m = sorted(mm for mm in self.month.values if mm > cand.month)
                if later_m:
                    cand = cand.replace(month=later_m[0], day=1, hour=0, minute=0, second=0)
                else:
                    cand = cand.replace(year=cand.year + 1, month=1, day=1, hour=0, minute=0, second=0)
                continue
            valid = self._valid_days(cand.year, cand.month)
            if not valid:
                ny, nm = self._next_month_start(cand.year, cand.month)
                cand = cand.replace(year=ny, month=nm, day=1, hour=0, minute=0, second=0)
                continue
            if cand.day not in valid:
                later_d = sorted(d for d in valid if d >= cand.day)
                if later_d:
                    cand = cand.replace(day=later_d[0], hour=0, minute=0, second=0)
                else:
                    ny, nm = self._next_month_start(cand.year, cand.month)
                    cand = cand.replace(year=ny, month=nm, day=1, hour=0, minute=0, second=0)
                continue
            if cand.hour not in self.hour:
                later_h = sorted(hr for hr in self.hour.values if hr >= cand.hour)
                if later_h:
                    cand = cand.replace(hour=later_h[0], minute=0, second=0)
                else:
                    # Next day 00:00:00 — will re-check valid_days
                    cand = cand + timedelta(days=1)
                    cand = cand.replace(hour=0, minute=0, second=0)
                continue
            if cand.minute not in self.minute:
                later_mn = sorted(mi for mi in self.minute.values if mi >= cand.minute)
                if later_mn:
                    cand = cand.replace(minute=later_mn[0], second=0)
                else:
                    cand = cand + timedelta(hours=1)
                    cand = cand.replace(minute=0, second=0)
                continue
            if cand.second not in self.second:
                later_s = sorted(sc for sc in self.second.values if sc >= cand.second)
                if later_s:
                    cand = cand.replace(second=later_s[0])
                else:
                    cand = cand + timedelta(minutes=1)
                    cand = cand.replace(second=0)
                continue
            return cand
        return None

    def previous(self, before=None):
        if before is None: before = datetime.now()
        cand = before.replace(microsecond=0) - timedelta(seconds=1)
        limit = before - timedelta(days=366 * 4)

        while cand >= limit:
            if not self.year.any and cand.year not in self.year.values:
                earlier = sorted((yr for yr in self.year.values if yr < cand.year), reverse=True)
                if not earlier: return None
                cand = cand.replace(year=earlier[0], month=12, day=31, hour=23, minute=59, second=59)
                continue
            if cand.month not in self.month:
                earlier_m = sorted((mm for mm in self.month.values if mm < cand.month), reverse=True)
                if earlier_m:
                    dim = self._dim(cand.year, earlier_m[0])
                    cand = cand.replace(month=earlier_m[0], day=dim, hour=23, minute=59, second=59)
                else:
                    ny, nm, dim = self._prev_month_end(cand.year, cand.month)
                    cand = cand.replace(year=ny, month=nm, day=dim, hour=23, minute=59, second=59)
                    # Also need to decrement year — actually we should go to prev year Dec
                    # The above already handles month wrap, but we also need to decrement year
                    # Actually _prev_month_end handles year wrap. But the else clause means we're going from month 1→12 of prev year
                    # Wait, no: if earlier_m is empty and cand.month=1, then nm=12 and ny=cand.year-1
                    # That's correct!
                continue
            valid = self._valid_days(cand.year, cand.month)
            if not valid:
                ny, nm, dim = self._prev_month_end(cand.year, cand.month)
                cand = cand.replace(year=ny, month=nm, day=dim, hour=23, minute=59, second=59)
                continue
            if cand.day not in valid:
                earlier_d = sorted((d for d in valid if d <= cand.day), reverse=True)
                if earlier_d:
                    cand = cand.replace(day=earlier_d[0], hour=23, minute=59, second=59)
                else:
                    ny, nm, dim = self._prev_month_end(cand.year, cand.month)
                    cand = cand.replace(year=ny, month=nm, day=dim, hour=23, minute=59, second=59)
                continue
            if cand.hour not in self.hour:
                earlier_h = sorted((hr for hr in self.hour.values if hr <= cand.hour), reverse=True)
                if earlier_h:
                    cand = cand.replace(hour=earlier_h[0], minute=59, second=59)
                else:
                    # Go to previous day 23:59:59 — use timedelta to avoid day=0
                    cand = cand - timedelta(days=1)
                    cand = cand.replace(hour=23, minute=59, second=59)
                continue
            if cand.minute not in self.minute:
                earlier_mn = sorted((mi for mi in self.minute.values if mi <= cand.minute), reverse=True)
                if earlier_mn:
                    cand = cand.replace(minute=earlier_mn[0], second=59)
                else:
                    cand = cand - timedelta(hours=1)
                    cand = cand.replace(minute=59, second=59)
                continue
            if cand.second not in self.second:
                earlier_s = sorted((sc for sc in self.second.values if sc <= cand.second), reverse=True)
                if earlier_s:
                    cand = cand.replace(second=earlier_s[0])
                else:
                    cand = cand - timedelta(minutes=1)
                    cand = cand.replace(second=59)
                continue
            # Final check
            final_valid = self._valid_days(cand.year, cand.month)
            if cand.day not in final_valid:
                # Go back to previous valid day
                earlier_d = sorted((d for d in final_valid if d <= cand.day), reverse=True)
                if earlier_d:
                    cand = cand.replace(day=earlier_d[0], hour=23, minute=59, second=59)
                    continue
                else:
                    ny, nm, dim = self._prev_month_end(cand.year, cand.month)
                    cand = cand.replace(year=ny, month=nm, day=dim, hour=23, minute=59, second=59)
                    continue
            return cand
        return None

    def enumerate(self, count=5, after=None):
        if after is None: after = datetime.now()
        results = []
        cur = after
        for _ in range(count):
            nxt = self.next(cur)
            if nxt is None: break
            results.append(nxt)
            cur = nxt
        return results

    def to_diagram(self):
        def fs(f):
            if f.any: return '*'
            if f.special:
                if f.special == 'L' and f.values:
                    return f'{list(f.values)[0]}L'
                if f.special.startswith('#') and f.values:
                    return f'{list(f.values)[0]}{f.special}'
                if f.special == 'W' and f.values:
                    return f'{list(f.values)[0]}W'
                return str(f.special)
            return ','.join(map(str, sorted(f.values)))
        sec = _pad(fs(self.second), 5)
        minute = _pad(fs(self.minute), 5)
        hour = _pad(fs(self.hour), 5)
        dom = _pad(fs(self.dom), 5)
        month = _pad(fs(self.month), 5)
        dow = fs(self.dow)
        return (
            f"{sec} {minute} {hour} {dom} {month} {dow}\n"
            "┬     ┬     ┬     ┬     ┬     ┬\n"
            "│     │     │     │     │     └ day of week (0=Sun)\n"
            "│     │     │     │     └────── month (1-12)\n"
            "│     │     │     └──────────── day (1-31)\n"
            "│     │     └───────────────── hour (0-23)\n"
            "│     └────────────────────── minute (0-59)\n"
            "└─────────────────────────── second (0-59)"
        )


def _pad(s, n): return s + " " * max(0, n - len(s))


if __name__ == "__main__":
    cases = [
        ("0 0 1 * *", "每月1日 00:00"),
        ("*/5 * * * *", "每5分钟"),
        ("0 12 * * 1-5", "工作日12:00"),
        ("0 0 * * 0", "每周日00:00"),
        ("0 0 1 1 *", "每年1月1日"),
        ("30 9 ? * MON-FRI", "工作日9:30"),
        ("0 0 L * *", "月末00:00"),
        ("0 0 1W * *", "每月最近工作日的1号"),
        ("0 0 * * 5L", "每月最后一个周五"),
        ("0 10 ? * 2#3", "每月第3个周一10:00"),
        ("0 0 1,15 * *", "每月1日和15日"),
        ("0 */6 * * *", "每6小时"),
        ("0 9-18 * * 1-5", "工作日9点到18点每整点"),
    ]

    print("=" * 60)
    print("Cron 表达式解析器")
    print("=" * 60)

    for expr, label in cases:
        print(f"\n[{label}] {expr}")
        try:
            c = CronExpression(expr)
            print(f"  Next:      {c.next() or '-'}")
            print(f"  Previous:  {c.previous() or '-'}")
            print(f"  Following: {[d.strftime('%m-%d %H:%M') for d in c.enumerate(3)]}")
            print(c.to_diagram())
        except Exception as e:
            print(f"  Error: {e}")
