# -*- coding: utf-8 -*-
"""
Babylon AI Gold Intelligence — محرك الإشارات v1 (قواعد قابلة للاختبار)
=====================================================================
يطبّق استراتيجيتين على شموع XAU/USD الحقيقية:

  Strategy A — Trend Pullback:
      اتجاه قوي على إطار الساعة (EMA50/EMA200 + ADX) ← تراجع يلامس
      منطقة EMA20–EMA50 ← تأكيد بإغلاق شمعة 15 دقيقة.

  Strategy B — Breakout & Retest:
      اختراق مستوى مقاومة/دعم مُجرَّب (3 لمسات فأكثر) على الساعة ←
      انتظار إعادة الاختبار والثبات قبل التأكيد.

حالات السيناريو: WATCH ← CONFIRMED أو INVALIDATED أو EXPIRED،
مع RISK_BLOCK عند التقلب الشاذ.

يمسح التاريخ كله بلا نظر للمستقبل (كل قرار يستخدم شموعًا مغلقة قبله فقط)،
ويقيس نتيجة كل سيناريو مؤكد: هل بلغ السعر هدف 1.5R قبل مستوى الإلغاء؟

⚠ النتائج التاريخية هنا استكشافية أولية: قبل خصم السبريد والانزلاق
والتكاليف، وبأوزان هندسية غير مُثبتة، وبلا طبقة الأخبار — ليست إثباتًا
لصلاحية الاستراتيجية. التحقق الكامل (Walk-Forward + التكاليف) مرحلة لاحقة.

التشغيل (من مجلد المشروع، بعد twelvedata_downloader.py):
    python signal_engine.py

المخرجات:
    data/signals_history.csv  +  data/signal_report_ar.md
"""

import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from analyze_gold import (load_candles, filter_weekend, ema_series,
                              rsi_series, atr_series, adx_series,
                              pivot_points, percentile_rank, PIVOT_WING)
except ImportError:
    print("لم أجد analyze_gold.py بجانب هذا السكربت — ضع الملفين في نفس المجلد.")
    sys.exit(1)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DATA_DIR = SCRIPT_DIR / "data"

# -------- معايير قابلة للضبط (افتراضات هندسية أولية، ليست نتائج اختبار) --------
ADX_TREND_MIN = 25          # أدنى ADX لاعتبار اتجاه الساعة قويًا
CONFIRM_WINDOW_H = 12       # نافذة تأكيد 15m بعد لمسة التراجع (بالساعات)
RETEST_WINDOW_BARS = 10     # نافذة إعادة الاختبار لاستراتيجية B (شموع ساعة)
MIN_LEVEL_TOUCHES = 3       # أدنى لمسات لاعتبار المستوى مُجرَّبًا
INVALIDATION_ATR = 0.3      # بُعد مستوى الإلغاء عن المرجع (× ATR)
RETEST_TOL_ATR = 0.25       # سماحية ملامسة المستوى عند إعادة الاختبار (× ATR)
TARGET_R = 1.5              # الهدف بوحدات المخاطرة
OUTCOME_HORIZON_15M = 64    # أفق قياس النتيجة لاستراتيجية A (شموع 15m = 16 ساعة)
OUTCOME_HORIZON_1H = 48     # أفق قياس النتيجة لاستراتيجية B (شموع ساعة)
VOL_BLOCK_RANK = 0.95       # ترتيب ATR الذي يفعّل RISK_BLOCK
SR_LOOKBACK = 250
COOLDOWN_BARS_B = 20


# ---------------------------------------------------------------- تجهيز الإطارات

class Frame:
    def __init__(self, name, rows):
        self.name = name
        self.dt = [r[0] for r in rows]
        self.o = [r[1] for r in rows]
        self.h = [r[2] for r in rows]
        self.l = [r[3] for r in rows]
        self.c = [r[4] for r in rows]
        self.ema20 = ema_series(self.c, 20)
        self.ema50 = ema_series(self.c, 50)
        self.ema200 = ema_series(self.c, 200)
        self.rsi = rsi_series(self.c, 14)
        self.atr = atr_series(self.h, self.l, self.c, 14)
        self.adx, self.pdi, self.mdi = adx_series(self.h, self.l, self.c, 14)
        self.ph, self.pl = pivot_points(self.h, self.l)   # نقاط الارتكاز (كل التاريخ)

    def __len__(self):
        return len(self.c)


def load_frame(name):
    path = DATA_DIR / f"xauusd_{name}.csv"
    if not path.exists():
        return None
    rows, _, _ = load_candles(path)
    rows, _ = filter_weekend(rows)
    return Frame(name, rows) if len(rows) >= 220 else None


def atr_rank(f: Frame, i: int) -> float:
    window = [x for x in f.atr[max(0, i - 500):i + 1] if x is not None]
    return percentile_rank(window, f.atr[i] or 0.0)


# ---------------------------------------------------------------- مستويات مُجرَّبة
# المستويات تُبنى من نقاط ارتكاز مؤكدة قبل اللحظة i فقط (idx <= i - PIVOT_WING)،
# فلا يتسرب أي "نظر للمستقبل".

def known_clusters(f: Frame, i: int):
    cutoff = i - PIVOT_WING
    start = max(0, i - SR_LOOKBACK)
    levels = [v for j, v in f.ph if start <= j <= cutoff]
    levels += [v for j, v in f.pl if start <= j <= cutoff]
    if not levels:
        return []
    levels.sort()
    atr = f.atr[i] or (f.c[i] * 0.002)
    tol = max(atr * 0.5, f.c[i] * 1e-4)
    clusters = []
    for v in levels:
        if clusters and v - clusters[-1][-1] <= tol:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    return [(sum(cl) / len(cl), len(cl)) for cl in clusters]


# ---------------------------------------------------------------- السيناريوهات

def new_scenario(strategy, direction, created, note):
    return {
        "strategy": strategy, "direction": direction,   # +1 صعود / -1 هبوط
        "created": created, "state": "WATCH", "note": note,
        "level": None, "invalidation": None,
        "entry": None, "confirmed": None, "target": None,
        "result": "", "r": None,
    }


def close_scenario(s, state, result="", r=None):
    s["state"] = state
    s["result"] = result
    s["r"] = r


def outcome_walk(f: Frame, start_idx, direction, entry, inval, target, horizon):
    """قياس النتيجة: أي المستويين يُلمس أولًا؟ (الشمعة التي تلمس الاثنين = خسارة تحفظًا)"""
    end = min(len(f), start_idx + horizon)
    for j in range(start_idx, end):
        hit_inval = f.l[j] <= inval if direction > 0 else f.h[j] >= inval
        hit_target = f.h[j] >= target if direction > 0 else f.l[j] <= target
        if hit_inval:
            return "LOSS", -1.0
        if hit_target:
            return "WIN", TARGET_R
        # ملاحظة: hit_inval يُفحص أولًا، فالشمعة التي تلمس الاثنين تُحسب خسارة
    if end <= start_idx:
        return "TIMEOUT", 0.0
    risk = abs(entry - inval)
    r = (f.c[end - 1] - entry) / risk * (1 if direction > 0 else -1) if risk else 0.0
    return "TIMEOUT", round(r, 2)


# ---------------------------------------------------------------- Strategy A

def trend_context(f1h: Frame, i: int):
    e50, e200, adx, c = f1h.ema50[i], f1h.ema200[i], f1h.adx[i], f1h.c[i]
    if None in (e50, e200, adx):
        return 0
    if adx >= ADX_TREND_MIN and e50 > e200 and c > e50:
        return +1
    if adx >= ADX_TREND_MIN and e50 < e200 and c < e50:
        return -1
    return 0


def pullback_touch(f1h: Frame, i: int, d: int) -> bool:
    e20, e50 = f1h.ema20[i], f1h.ema50[i]
    if None in (e20, e50):
        return False
    if d > 0:
        return f1h.l[i] <= e20 and f1h.c[i] > e50
    return f1h.h[i] >= e20 and f1h.c[i] < e50


def scan_strategy_a(f1h: Frame, f15: Frame, scenarios, blocked):
    open_dir = {+1: None, -1: None}
    k = 0  # مؤشر متقدم على شموع 15m
    for i in range(220, len(f1h)):
        d = trend_context(f1h, i)
        for direction in (+1, -1):
            if open_dir[direction] is not None:
                continue
            if d != direction or not pullback_touch(f1h, i, direction):
                continue
            if atr_rank(f1h, i) >= VOL_BLOCK_RANK:
                blocked.append((f1h.dt[i], "A", direction, "تقلب شاذ"))
                continue
            atr = f1h.atr[i] or 0.0
            ref_ema20 = f1h.ema20[i]
            if direction > 0:
                inval = min(f1h.l[i], f1h.ema50[i]) - INVALIDATION_ATR * atr
            else:
                inval = max(f1h.h[i], f1h.ema50[i]) + INVALIDATION_ATR * atr
            s = new_scenario("A", direction, f1h.dt[i],
                             "تراجع داخل اتجاه الساعة لمس منطقة EMA20")
            s["level"] = round(ref_ema20, 2)
            s["invalidation"] = round(inval, 2)
            scenarios.append(s)
            open_dir[direction] = (s, i, ref_ema20, inval)

        # معالجة السيناريوهات المفتوحة على شموع 15m المغلقة حتى إغلاق شمعة الساعة i
        bar_close = f1h.dt[i] + timedelta(hours=1)
        while k < len(f15) and f15.dt[k] + timedelta(minutes=15) <= bar_close:
            for direction in (+1, -1):
                slot = open_dir[direction]
                if slot is None:
                    continue
                s, i0, ref, inval = slot
                t15 = f15.dt[k]
                if t15 < f1h.dt[i0] + timedelta(hours=1):
                    continue  # لم تبدأ نافذة التأكيد بعد
                if t15 >= f1h.dt[i0] + timedelta(hours=1 + CONFIRM_WINDOW_H):
                    close_scenario(s, "EXPIRED", "انتهت نافذة التأكيد دون إغلاق مؤكد")
                    open_dir[direction] = None
                    continue
                c15, o15, e20_15 = f15.c[k], f15.o[k], f15.ema20[k]
                breached = c15 <= inval if direction > 0 else c15 >= inval
                if breached:
                    close_scenario(s, "INVALIDATED", "كسر مستوى الإلغاء قبل التأكيد")
                    open_dir[direction] = None
                    continue
                if e20_15 is None:
                    continue
                confirmed = (c15 > ref and c15 > e20_15 and c15 > o15) if direction > 0 \
                    else (c15 < ref and c15 < e20_15 and c15 < o15)
                if confirmed:
                    entry = c15
                    risk = abs(entry - inval)
                    target = entry + direction * TARGET_R * risk
                    s.update(entry=round(entry, 2), confirmed=t15,
                             target=round(target, 2))
                    res, r = outcome_walk(f15, k + 1, direction, entry,
                                          inval, target, OUTCOME_HORIZON_15M)
                    close_scenario(s, "CONFIRMED", res, r)
                    open_dir[direction] = None
            k += 1
    for direction in (+1, -1):
        if open_dir[direction]:
            open_dir[direction][0]["note"] += " — سيناريو لا يزال مفتوحًا"


# ---------------------------------------------------------------- Strategy B

def scan_strategy_b(f1h: Frame, scenarios, blocked):
    pending = None      # (s, level, direction, created_idx)
    last_trigger = {}   # direction -> (idx, level) لمنع تكرار نفس الاختراق
    for i in range(220, len(f1h)):
        atr = f1h.atr[i] or 0.0

        # متابعة سيناريو اختراق بانتظار إعادة الاختبار
        if pending is not None:
            s, level, d, i0, inval = pending   # مستوى الإلغاء مُثبَّت منذ لحظة WATCH
            fail = f1h.c[i] < inval if d > 0 else f1h.c[i] > inval
            touched = (f1h.l[i] <= level + RETEST_TOL_ATR * atr) if d > 0 \
                else (f1h.h[i] >= level - RETEST_TOL_ATR * atr)
            held = f1h.c[i] > level if d > 0 else f1h.c[i] < level
            if fail:
                close_scenario(s, "INVALIDATED", "عاد السعر خلف المستوى قبل التأكيد")
                pending = None
            elif touched and held:
                entry = f1h.c[i]
                risk = abs(entry - inval)
                target = entry + d * TARGET_R * risk
                s.update(entry=round(entry, 2), confirmed=f1h.dt[i],
                         target=round(target, 2))
                res, r = outcome_walk(f1h, i + 1, d, entry, inval,
                                      target, OUTCOME_HORIZON_1H)
                close_scenario(s, "CONFIRMED", res, r)
                pending = None
            elif i - i0 >= RETEST_WINDOW_BARS:
                close_scenario(s, "EXPIRED", "انتهت نافذة إعادة الاختبار")
                pending = None
            if pending is not None:
                continue  # لا نفتح اختراقًا جديدًا وسيناريو قائم

        # البحث عن اختراق مستوى مُجرَّب (المستويات معروفة قبل هذه الشمعة)
        clusters = known_clusters(f1h, i - 1) if i > 0 else []
        prev_c = f1h.c[i - 1]
        for d in (+1, -1):
            if pending is not None:
                break
            if d > 0:
                cands = [(lv, t) for lv, t in clusters
                         if t >= MIN_LEVEL_TOUCHES and lv > prev_c]
                if not cands:
                    continue
                level, touches = min(cands, key=lambda x: x[0])
                broke = f1h.c[i] > level + 0.1 * atr
            else:
                cands = [(lv, t) for lv, t in clusters
                         if t >= MIN_LEVEL_TOUCHES and lv < prev_c]
                if not cands:
                    continue
                level, touches = max(cands, key=lambda x: x[0])
                broke = f1h.c[i] < level - 0.1 * atr
            if not broke:
                continue
            lt = last_trigger.get(d)
            if lt and i - lt[0] < COOLDOWN_BARS_B and abs(level - lt[1]) < 0.5 * atr:
                continue
            if atr_rank(f1h, i) >= VOL_BLOCK_RANK:
                blocked.append((f1h.dt[i], "B", d, "تقلب شاذ"))
                last_trigger[d] = (i, level)
                continue
            s = new_scenario("B", d, f1h.dt[i],
                             f"اختراق مستوى مُجرَّب ({touches} لمسات) بانتظار إعادة الاختبار")
            inval0 = round(level - d * INVALIDATION_ATR * atr, 2)
            s["level"] = round(level, 2)
            s["invalidation"] = inval0
            scenarios.append(s)
            pending = (s, level, d, i, inval0)
            last_trigger[d] = (i, level)
    if pending is not None:
        pending[0]["note"] += " — سيناريو لا يزال مفتوحًا"


# ---------------------------------------------------------------- التلخيص والتقارير

DIR_AR = {+1: "صاعد", -1: "هابط"}
STRAT_AR = {"A": "Trend Pullback", "B": "Breakout & Retest"}


def summarize(scenarios):
    out = {}
    for s in scenarios:
        key = s["strategy"]
        d = out.setdefault(key, dict(watch=0, confirmed=0, invalid=0, expired=0,
                                     win=0, loss=0, timeout=0, rs=[]))
        if s["state"] == "WATCH":
            d["watch"] += 1
        elif s["state"] == "INVALIDATED":
            d["invalid"] += 1
        elif s["state"] == "EXPIRED":
            d["expired"] += 1
        elif s["state"] == "CONFIRMED":
            d["confirmed"] += 1
            if s["result"] == "WIN":
                d["win"] += 1
            elif s["result"] == "LOSS":
                d["loss"] += 1
            else:
                d["timeout"] += 1
            if s["r"] is not None:
                d["rs"].append(s["r"])
    for d in out.values():
        resolved = d["win"] + d["loss"]
        d["win_rate"] = (d["win"] / resolved * 100) if resolved else None
        d["expectancy"] = (sum(d["rs"]) / len(d["rs"])) if d["rs"] else None
    return out


def write_csv_log(scenarios):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "signals_history.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["signal_id", "strategy", "direction", "created_utc", "state",
                    "level", "invalidation", "confirmed_utc", "entry", "target",
                    "result", "r_multiple", "notes"])
        for s in scenarios:
            sid = f"{s['strategy']}{'+' if s['direction'] > 0 else '-'}-{s['created']:%Y%m%d%H%M}"
            w.writerow([sid, s["strategy"], DIR_AR[s["direction"]],
                        s["created"].strftime("%Y-%m-%d %H:%M"), s["state"],
                        s["level"], s["invalidation"],
                        s["confirmed"].strftime("%Y-%m-%d %H:%M") if s["confirmed"] else "",
                        s["entry"] if s["entry"] is not None else "",
                        s["target"] if s["target"] is not None else "",
                        s["result"], s["r"] if s["r"] is not None else "", s["note"]])
    return path


def current_state_lines(scenarios, f1h: Frame):
    open_s = [s for s in scenarios if s["state"] == "WATCH"]
    last_dt = f1h.dt[-1] + timedelta(hours=1)
    lines = [f"## الوضع الحالي (حتى إغلاق {f1h.dt[-1]:%Y-%m-%d %H:%M} UTC)", ""]
    if not open_s:
        lines.append("لا يوجد سيناريو نشط الآن — النظام في وضع **الانتظار**، "
                     "وهذا قرار مشروع ضمن التصميم (لا صفقة أفضل من صفقة ضعيفة).")
        return lines, None
    s = open_s[-1]
    lines += [
        f"سيناريو **{STRAT_AR[s['strategy']]} {DIR_AR[s['direction']]}** "
        f"بحالة **WATCH** منذ {s['created']:%Y-%m-%d %H:%M} UTC:",
        "",
        f"- المستوى المرجعي: {s['level']:,.2f}$",
        f"- إلغاء السيناريو: {s['invalidation']:,.2f}$",
        f"- {s['note']}",
        "",
        "درجة الأدلة المتاحة (من 65): تُحتسب الاتجاه والبنية والزخم فقط — "
        "35 نقطة معلّقة (السيولة 10، الأخبار 15، النموذج الإحصائي 10) حتى تُربط مصادرها.",
    ]
    return lines, s


def write_report(scenarios, summary, blocked, f1h: Frame, f15: Frame):
    now_utc = datetime.now(timezone.utc)
    now_bgd = now_utc + timedelta(hours=3)
    lines = [
        "# محرك إشارات Babylon AI — المسح التاريخي والوضع الحالي",
        "",
        f"- وقت الإنشاء: {now_utc:%Y-%m-%d %H:%M} UTC ({now_bgd:%Y-%m-%d %H:%M} بتوقيت بغداد)",
        f"- فترة المسح: {f1h.dt[min(220, len(f1h) - 1)]:%Y-%m-%d} → {f1h.dt[-1]:%Y-%m-%d} "
        f"(شموع ساعة: {len(f1h)} | شموع 15 دقيقة: {len(f15)})",
        f"- سيناريوهات محجوبة بسبب التقلب الشاذ (RISK_BLOCK): {len(blocked)}",
        "",
        "| الاستراتيجية | ظهرت (WATCH) | تأكدت | أُلغيت | انتهت | ربح | خسارة | مهلة | نسبة الربح | التوقع (R) |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for key in ("A", "B"):
        d = summary.get(key)
        if not d:
            continue
        total = d["watch"] + d["confirmed"] + d["invalid"] + d["expired"]
        wr = f"{d['win_rate']:.0f}%" if d["win_rate"] is not None else "—"
        ex = f"{d['expectancy']:+.2f}R" if d["expectancy"] is not None else "—"
        lines.append(f"| {STRAT_AR[key]} | {total} | {d['confirmed']} | {d['invalid']} "
                     f"| {d['expired']} | {d['win']} | {d['loss']} | {d['timeout']} | {wr} | {ex} |")
    lines.append("")
    cur, _ = current_state_lines(scenarios, f1h)
    lines += cur
    lines += [
        "", "---", "",
        "**تحذيرات إلزامية قبل أي استنتاج:**",
        "- الأرقام قبل خصم السبريد والانزلاق والعمولات — النتائج الفعلية أسوأ حتمًا.",
        "- المعايير أعلاه افتراضات هندسية أولية لم تخضع لـ Walk-Forward بعد.",
        "- طبقة الأخبار والسيولة غير مفعّلة؛ إشارات وقت الأحداث الكبرى لم تُستبعد.",
        "- نسبة ربح تاريخية ليست وعدًا بأي نتيجة مستقبلية. هذا ليس توصية تداول.",
    ]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "signal_report_ar.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------- التشغيل

def run_scan(f1h: Frame, f15: Frame):
    scenarios, blocked = [], []
    scan_strategy_a(f1h, f15, scenarios, blocked)
    scan_strategy_b(f1h, scenarios, blocked)
    scenarios.sort(key=lambda s: s["created"])
    return scenarios, blocked


def main():
    print("=" * 62)
    print("Babylon AI — محرك الإشارات (Trend Pullback + Breakout & Retest)")
    print("=" * 62)

    f1h = load_frame("1h")
    f15 = load_frame("15min")
    if f1h is None or f15 is None:
        print("أحتاج ملفَي xauusd_1h.csv وxauusd_15min.csv في data\\ "
              "— شغّل twelvedata_downloader.py أولًا.")
        sys.exit(1)

    scenarios, blocked = run_scan(f1h, f15)
    summary = summarize(scenarios)

    for key in ("A", "B"):
        d = summary.get(key)
        if not d:
            print(f"\n■ {STRAT_AR[key]}: لم يظهر أي سيناريو في فترة المسح.")
            continue
        total = d["watch"] + d["confirmed"] + d["invalid"] + d["expired"]
        wr = f"{d['win_rate']:.0f}%" if d["win_rate"] is not None else "—"
        ex = f"{d['expectancy']:+.2f}R" if d["expectancy"] is not None else "—"
        print(f"\n■ {STRAT_AR[key]}: {total} سيناريو | تأكد {d['confirmed']} "
              f"| أُلغي {d['invalid']} | انتهى {d['expired']}")
        print(f"  النتائج: ربح {d['win']} / خسارة {d['loss']} / مهلة {d['timeout']} "
              f"| نسبة الربح {wr} | التوقع {ex} (قبل التكاليف!)")
    print(f"\nمحجوب بسبب التقلب الشاذ: {len(blocked)}")

    cur, _ = current_state_lines(scenarios, f1h)
    print()
    for line in cur:
        print(line.replace("**", "").replace("## ", ""))

    log = write_csv_log(scenarios)
    report = write_report(scenarios, summary, blocked, f1h, f15)
    print(f"\nسجل الإشارات: {log}")
    print(f"التقرير العربي: {report}")
    print("\n⚠ أرقام استكشافية قبل التكاليف وبلا طبقة أخبار — ليست توصية تداول "
          "ولا إثباتًا لصلاحية الاستراتيجية.")


if __name__ == "__main__":
    main()
