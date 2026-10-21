# -*- coding: utf-8 -*-
"""
Babylon AI Gold Intelligence — محرك المؤشرات والتحليل الفني v1
==============================================================
يقرأ شموع XAU/USD الحقيقية من data/xauusd_*.csv ويحسب عليها:

  EMA 20/50/200 • RSI 14 • ATR 14 • ADX 14 (مع +DI/−DI)
  حالة السوق (Market Regime) • بنية السوق (HH/HL/LH/LL)
  أقرب دعم ومقاومة من نقاط الارتكاز

ثم يكتب تقريرًا عربيًا وملفات شموع "مُثراة" بأعمدة المؤشرات تصلح
لواجهة التطبيق لاحقًا.

- يرشّح تلقائيًا شموع عطلة نهاية الأسبوع (السبت + نهار الأحد قبل 21:00 UTC)
  لأنها تسعير غير سوقي يشوّه ATR والتقلب.
- حسابات محلية بالكامل: بلا إنترنت، بلا مفتاح، بلا أي طلب من حصتك.
- تحليل وصفي لآخر شمعة مغلقة في الملف — ليس توصية تداول ولا تنبؤًا.

التشغيل (من مجلد المشروع الذي يحتوي مجلد data):
    python analyze_gold.py

المخرجات:
    data/analysis_report_ar.md
    data/enriched/xauusd_<frame>_indicators.csv
"""

import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
ENRICHED_DIR = DATA_DIR / "enriched"

FRAMES = ["5min", "15min", "1h", "4h"]
PIVOT_WING = 3            # شمعات يمين ويسار نقطة الارتكاز
SR_LOOKBACK = 250         # عمق البحث عن الدعم والمقاومة (بالشموع)
MIN_BARS = 220            # أقل عدد شموع يسمح بتحليل كامل (EMA200 + إحماء)


# ---------------------------------------------------------------- القراءة والترشيح

def load_candles(path: Path):
    rows, seen = [], set()
    dup = bad = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            try:
                dt = datetime.strptime(r["datetime_utc"], "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=timezone.utc)
                o, h, l, c = (float(r["open"]), float(r["high"]),
                              float(r["low"]), float(r["close"]))
            except (KeyError, TypeError, ValueError):
                bad += 1
                continue
            if dt in seen:
                dup += 1
                continue
            seen.add(dt)
            rows.append((dt, o, h, l, c))
    rows.sort(key=lambda x: x[0])
    return rows, dup, bad


def is_offmarket(dt: datetime) -> bool:
    """السبت كاملًا + نهار الأحد قبل افتتاح الذهب (~21:00 UTC)."""
    return dt.weekday() == 5 or (dt.weekday() == 6 and dt.hour < 21)


def filter_weekend(rows):
    kept = [r for r in rows if not is_offmarket(r[0])]
    return kept, len(rows) - len(kept)


# ---------------------------------------------------------------- المؤشرات

def ema_series(values, n):
    out = [None] * len(values)
    if len(values) < n:
        return out
    out[n - 1] = sum(values[:n]) / n
    k = 2.0 / (n + 1)
    for i in range(n, len(values)):
        out[i] = values[i] * k + out[i - 1] * (1 - k)
    return out


def rsi_series(closes, n=14):
    out = [None] * len(closes)
    if len(closes) < n + 1:
        return out
    gains = [max(closes[i] - closes[i - 1], 0.0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0.0) for i in range(1, len(closes))]
    ag, al = sum(gains[:n]) / n, sum(losses[:n]) / n

    def to_rsi(g, s):
        if s == 0:
            return 100.0
        return 100.0 - 100.0 / (1.0 + g / s)

    out[n] = to_rsi(ag, al)
    for i in range(n + 1, len(closes)):
        ag = (ag * (n - 1) + gains[i - 1]) / n
        al = (al * (n - 1) + losses[i - 1]) / n
        out[i] = to_rsi(ag, al)
    return out


def true_ranges(h, l, c):
    tr = [h[0] - l[0]]
    for i in range(1, len(c)):
        tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
    return tr


def atr_series(h, l, c, n=14):
    out = [None] * len(c)
    if len(c) < n:
        return out
    tr = true_ranges(h, l, c)
    a = sum(tr[:n]) / n
    out[n - 1] = a
    for i in range(n, len(c)):
        a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def adx_series(h, l, c, n=14):
    """ADX بطريقة Wilder، مع +DI و−DI."""
    L = len(c)
    adx = [None] * L
    pdi = [None] * L
    mdi = [None] * L
    if L < 2 * n + 1:
        return adx, pdi, mdi

    tr = [0.0] * L
    pdm = [0.0] * L
    mdm = [0.0] * L
    for i in range(1, L):
        up = h[i] - h[i - 1]
        dn = l[i - 1] - l[i]
        pdm[i] = up if (up > dn and up > 0) else 0.0
        mdm[i] = dn if (dn > up and dn > 0) else 0.0
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))

    def rma(x):
        out = [None] * L
        out[n] = sum(x[1:n + 1]) / n
        for i in range(n + 1, L):
            out[i] = (out[i - 1] * (n - 1) + x[i]) / n
        return out

    atr_s, pdm_s, mdm_s = rma(tr), rma(pdm), rma(mdm)
    dx = [None] * L
    for i in range(n, L):
        a = atr_s[i]
        p = 100.0 * pdm_s[i] / a if a else 0.0
        m = 100.0 * mdm_s[i] / a if a else 0.0
        pdi[i], mdi[i] = p, m
        s = p + m
        dx[i] = 100.0 * abs(p - m) / s if s else 0.0

    adx[2 * n - 1] = sum(dx[n:2 * n]) / n
    for i in range(2 * n, L):
        adx[i] = (adx[i - 1] * (n - 1) + dx[i]) / n
    return adx, pdi, mdi


# ---------------------------------------------------------------- البنية والدعم والمقاومة

def pivot_points(h, l, wing=PIVOT_WING):
    """نقاط ارتكاز: قمة/قاع محلي ضمن نافذة wing يمينًا ويسارًا."""
    highs, lows = [], []
    for i in range(wing, len(h) - wing):
        win_h = h[i - wing:i] + h[i + 1:i + wing + 1]
        win_l = l[i - wing:i] + l[i + 1:i + wing + 1]
        if h[i] > max(win_h):
            highs.append((i, h[i]))
        if l[i] < min(win_l):
            lows.append((i, l[i]))
    return highs, lows


def market_structure(highs, lows):
    if len(highs) < 2 or len(lows) < 2:
        return "بنية غير محسومة (نقاط ارتكاز غير كافية)"
    hh = highs[-1][1] > highs[-2][1]
    hl = lows[-1][1] > lows[-2][1]
    if hh and hl:
        return "قمم وقيعان صاعدة (HH/HL)"
    if (not hh) and (not hl):
        return "قمم وقيعان هابطة (LH/LL)"
    return "بنية متذبذبة (قمم وقيعان متعارضة)"


def support_resistance(highs, lows, close, atr, lookback_start):
    """تجميع مستويات الارتكاز الحديثة إلى عناقيد، ثم أقرب دعم ومقاومة."""
    levels = [v for i, v in highs if i >= lookback_start]
    levels += [v for i, v in lows if i >= lookback_start]
    if not levels or not atr:
        return None, None
    levels.sort()
    tol = max(atr * 0.5, close * 1e-4)
    clusters = []
    for v in levels:
        if clusters and v - clusters[-1][-1] <= tol:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    merged = [(sum(c) / len(c), len(c)) for c in clusters]
    res = [(lv, k) for lv, k in merged if lv > close]
    sup = [(lv, k) for lv, k in merged if lv < close]
    nearest_res = min(res, key=lambda x: x[0]) if res else None
    nearest_sup = max(sup, key=lambda x: x[0]) if sup else None
    return nearest_sup, nearest_res


# ---------------------------------------------------------------- حالة السوق

def percentile_rank(window, value):
    if not window:
        return 0.0
    below = sum(1 for x in window if x <= value)
    return below / len(window)


def detect_regime(close, ema50, ema200, adx, atr_window, atr_last):
    vol_rank = percentile_rank(atr_window, atr_last)
    high_vol = vol_rank >= 0.85
    if adx is None or ema50 is None or ema200 is None:
        base = "غير محدد (بيانات غير كافية)"
    elif adx >= 25 and ema50 > ema200 and close > ema50:
        base = "اتجاه صاعد"
    elif adx >= 25 and ema50 < ema200 and close < ema50:
        base = "اتجاه هابط"
    elif adx < 20:
        base = "سوق عرضي"
    else:
        base = "انتقالي / غير محسوم"
    label = base + (" + تقلب مرتفع" if high_vol else "")
    return label, vol_rank, high_vol


# ---------------------------------------------------------------- تحليل إطار واحد

def analyze_frame(frame: str, rows):
    dts = [r[0] for r in rows]
    o = [r[1] for r in rows]
    h = [r[2] for r in rows]
    l = [r[3] for r in rows]
    c = [r[4] for r in rows]

    ema20 = ema_series(c, 20)
    ema50 = ema_series(c, 50)
    ema200 = ema_series(c, 200)
    rsi = rsi_series(c, 14)
    atr = atr_series(h, l, c, 14)
    adx, pdi, mdi = adx_series(h, l, c, 14)

    i = len(c) - 1
    atr_hist = [x for x in atr[max(0, i - 500):i + 1] if x is not None]
    regime, vol_rank, high_vol = detect_regime(
        c[i], ema50[i], ema200[i], adx[i], atr_hist, atr[i] or 0.0)

    highs, lows = pivot_points(h, l)
    structure = market_structure(highs, lows)
    sup, res = support_resistance(
        highs, lows, c[i], atr[i] or 0.0, max(0, len(c) - SR_LOOKBACK))

    return {
        "frame": frame, "last_dt": dts[i], "close": c[i],
        "ema20": ema20[i], "ema50": ema50[i], "ema200": ema200[i],
        "rsi": rsi[i], "atr": atr[i], "adx": adx[i],
        "pdi": pdi[i], "mdi": mdi[i],
        "regime": regime, "vol_rank": vol_rank, "high_vol": high_vol,
        "structure": structure, "support": sup, "resistance": res,
        "series": (dts, o, h, l, c, ema20, ema50, ema200, rsi, atr, adx),
    }


def write_enriched(frame: str, series):
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
    dts, o, h, l, c, e20, e50, e200, rsi, atr, adx = series
    path = ENRICHED_DIR / f"xauusd_{frame}_indicators.csv"

    def f(x):
        return f"{x:.4f}" if x is not None else ""

    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["datetime_utc", "open", "high", "low", "close",
                    "ema20", "ema50", "ema200", "rsi14", "atr14", "adx14"])
        for i in range(len(c)):
            w.writerow([dts[i].strftime("%Y-%m-%d %H:%M:%S"),
                        o[i], h[i], l[i], c[i],
                        f(e20[i]), f(e50[i]), f(e200[i]),
                        f(rsi[i]), f(atr[i]), f(adx[i])])
    return path


# ---------------------------------------------------------------- التقرير

def level_txt(level):
    if not level:
        return "—"
    lv, k = level
    return f"{lv:,.2f}$ (لمسات: {k})"


def frame_lines(s):
    return [
        f"## إطار {s['frame']} — آخر شمعة مغلقة: {s['last_dt']:%Y-%m-%d %H:%M} UTC",
        "",
        f"- الإغلاق: {s['close']:,.2f}$",
        f"- EMA20 / EMA50 / EMA200: {s['ema20']:,.2f} / {s['ema50']:,.2f} / {s['ema200']:,.2f}",
        f"- RSI14: {s['rsi']:.1f} | ATR14: {s['atr']:.2f}$ | "
        f"ADX14: {s['adx']:.1f} (+DI {s['pdi']:.1f} / −DI {s['mdi']:.1f})",
        f"- حالة السوق: **{s['regime']}** (ترتيب التقلب التاريخي: {s['vol_rank']*100:.0f}%)",
        f"- بنية السوق: {s['structure']}",
        f"- أقرب دعم: {level_txt(s['support'])} | أقرب مقاومة: {level_txt(s['resistance'])}",
        "",
    ]


def context_line(results):
    by = {s["frame"]: s for s in results}
    a, b = by.get("4h"), by.get("1h")
    if not a or not b:
        return "توافق الأطر: غير متاح (إطار ناقص)."
    ra, rb = a["regime"].split(" +")[0], b["regime"].split(" +")[0]
    if ra == rb and "اتجاه" in ra:
        return f"توافق الأطر: 4h و1h كلاهما «{ra}» — السياق العام متوافق."
    return f"توافق الأطر: 4h «{ra}» بينما 1h «{rb}» — سياق غير متوافق، يُفضَّل الانتظار حتى يتضح."


def write_report(results, meta):
    now_utc = datetime.now(timezone.utc)
    now_bgd = now_utc + timedelta(hours=3)
    lines = [
        "# التحليل الفني لشموع XAU/USD الحقيقية — Babylon AI",
        "",
        f"- وقت الإنشاء: {now_utc:%Y-%m-%d %H:%M} UTC ({now_bgd:%Y-%m-%d %H:%M} بتوقيت بغداد)",
        "- المصدر: ملفات data/xauusd_*.csv المنزّلة من Twelve Data (بيانات تاريخية).",
        f"- شموع عطلة نهاية الأسبوع المرشَّحة قبل الحساب: {meta['filtered_total']} "
        "(السبت + نهار الأحد قبل 21:00 UTC — تسعير غير سوقي).",
        "- هذا وصف لآخر شمعة مغلقة في الملفات؛ لتحديثه أعد تشغيل منزّل البيانات ثم هذا السكربت.",
        "",
    ]
    for s in results:
        lines += frame_lines(s)
    lines += [context_line(results), "",
              "---", "",
              "تحليل وصفي تعليمي مبني على بيانات تاريخية — ليس توصية تداول، "
              "ولا تنبؤًا، ولا يضمن أي نتيجة."]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "analysis_report_ar.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------- التشغيل

def main():
    print("=" * 62)
    print("Babylon AI — محرك المؤشرات على شموع XAU/USD الحقيقية")
    print("=" * 62)

    if not DATA_DIR.exists():
        print(f"لم أجد مجلد البيانات: {DATA_DIR}")
        print("شغّل السكربت من مجلد المشروع الذي يحتوي data (بعد تنزيل الشموع).")
        sys.exit(1)

    results = []
    filtered_total = 0
    for frame in FRAMES:
        path = DATA_DIR / f"xauusd_{frame}.csv"
        if not path.exists():
            print(f"\n■ {frame}: الملف غير موجود — تجاوزته.")
            continue
        rows, dup, bad = load_candles(path)
        rows, filtered = filter_weekend(rows)
        filtered_total += filtered
        print(f"\n■ {frame}: {len(rows)} شمعة سوقية "
              f"(رُشّحت {filtered} شمعة عطلة، مكررات {dup}، صفوف تالفة {bad})")
        if len(rows) < MIN_BARS:
            print(f"  أقل من {MIN_BARS} شمعة — لا يكفي لحساب EMA200 بثقة. تجاوزته.")
            continue
        s = analyze_frame(frame, rows)
        results.append(s)
        print(f"  آخر شمعة: {s['last_dt']:%Y-%m-%d %H:%M} UTC | إغلاق {s['close']:,.2f}$")
        print(f"  EMA 20/50/200: {s['ema20']:,.2f} / {s['ema50']:,.2f} / {s['ema200']:,.2f}")
        print(f"  RSI {s['rsi']:.1f} | ATR {s['atr']:.2f}$ | ADX {s['adx']:.1f} "
              f"(+DI {s['pdi']:.1f} / −DI {s['mdi']:.1f})")
        print(f"  حالة السوق: {s['regime']} | البنية: {s['structure']}")
        print(f"  دعم: {level_txt(s['support'])} | مقاومة: {level_txt(s['resistance'])}")
        enriched = write_enriched(frame, s.pop("series"))
        print(f"  شموع مُثراة بالمؤشرات: {enriched.relative_to(SCRIPT_DIR)}")

    if not results:
        print("\nلم يُحلَّل أي إطار — شغّل twelvedata_downloader.py أولًا.")
        sys.exit(1)

    report = write_report(results, {"filtered_total": filtered_total})
    print(f"\n{context_line(results)}")
    print(f"التقرير العربي: {report}")
    print("\nتذكير: تحليل وصفي لبيانات تاريخية — ليس توصية تداول ولا تنبؤًا.")


if __name__ == "__main__":
    main()
