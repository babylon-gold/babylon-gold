# -*- coding: utf-8 -*-
"""
Babylon AI Gold Intelligence — فاحص جودة البيانات v2 (واعٍ بعطلات السوق)
=======================================================================
يقرأ ملفات data/xauusd_*.csv المحفوظة مسبقًا ويعيد فحصها بقواعد أدق:

- يميّز إغلاقات العطلات الرسمية (الكريسماس، رأس السنة، الجمعة العظيمة،
  عيد الشكر، عطلات أمريكية أخرى) عن الفجوات غير المبررة فعلًا.
- يحسب تواريخ العطلات المتحركة رياضيًا (الجمعة العظيمة، عيد الشكر...).
- يكتشف شموع عطلة نهاية الأسبوع (السبت/نهار الأحد UTC) — تسعير قد يكون
  راكدًا أو اصطناعيًا ويشوّه المؤشرات، فيجب معرفته قبل الربط بالتحليل.

يعمل محليًا على الملفات فقط: بلا إنترنت، بلا مفتاح API، بلا أي طلب من حصتك.

التشغيل (من مجلد المشروع الذي يحتوي مجلد data):
    python recheck_data.py

المخرجات:
    data/validation_report_v2_ar.md + ملخص في الشاشة
"""

import csv
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"

FILES = {"5min": 5, "15min": 15, "1h": 60, "4h": 240}

SHORT_GAP_MAX_MIN = 150          # ≤ ساعتين ونصف: صيانة يومية / سيولة منخفضة
WEEKEND_GAP_MAX_MIN = 72 * 60    # فجوة جمعة→أحد الاعتيادية
HOLIDAY_GAP_MAX_MIN = 5 * 24 * 60
ANOMALOUS_TOLERANCE = 2          # يُسمح بفجوتين غير مبررتين كحد أقصى


# ---------------------------------------------------------------- العطلات

def easter_sunday(year: int) -> date:
    """خوارزمية Butcher لحساب عيد الفصح الغربي."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """التكرار n ليوم أسبوع معين داخل شهر (weekday: الاثنين=0)."""
    d = date(year, month, 1)
    offset = (weekday - d.weekday()) % 7
    return d + timedelta(days=offset + 7 * (n - 1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    nxt = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    d = nxt - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def market_holidays(years) -> dict:
    """تواريخ تُغلق فيها أسواق المعادن الأمريكية أو تعمل بساعات مختصرة."""
    hol = {}
    for y in years:
        gf = easter_sunday(y) - timedelta(days=2)
        hol[gf] = "الجمعة العظيمة"
        tg = nth_weekday(y, 11, 3, 4)                     # الخميس الرابع من نوفمبر
        hol[tg] = "عيد الشكر"
        hol[tg + timedelta(days=1)] = "ما بعد عيد الشكر (دوام مختصر)"
        for d_ in (24, 25, 26):
            hol[date(y, 12, d_)] = "عيد الميلاد"
        hol[date(y, 12, 31)] = "ليلة رأس السنة"
        hol[date(y, 1, 1)] = "رأس السنة"
        hol[nth_weekday(y, 1, 0, 3)] = "يوم مارتن لوثر كينغ"
        hol[nth_weekday(y, 2, 0, 3)] = "يوم الرؤساء"
        hol[last_weekday(y, 5, 0)] = "يوم الذكرى الأمريكي"
        hol[date(y, 6, 19)] = "يوم Juneteenth"
        hol[date(y, 7, 3)] = "عشية الاستقلال (دوام مختصر)"
        hol[date(y, 7, 4)] = "عيد الاستقلال الأمريكي"
        hol[nth_weekday(y, 9, 0, 1)] = "عيد العمال الأمريكي"
    return hol


def holiday_in_span(a: datetime, b: datetime, hol: dict):
    d = a.date()
    end = b.date()
    while d <= end:
        if d in hol:
            return hol[d]
        d += timedelta(days=1)
    return None


# ---------------------------------------------------------------- القراءة

def load_csv(path: Path):
    rows, dup_count, bad_rows = [], 0, 0
    seen = set()
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                dt = datetime.strptime(r["datetime_utc"], "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=timezone.utc)
                o, h, l, c = (float(r["open"]), float(r["high"]),
                              float(r["low"]), float(r["close"]))
            except (KeyError, TypeError, ValueError):
                bad_rows += 1
                continue
            if dt in seen:
                dup_count += 1
                continue
            seen.add(dt)
            rows.append((dt, o, h, l, c))
    rows.sort(key=lambda x: x[0])
    return rows, dup_count, bad_rows


# ---------------------------------------------------------------- الفحص v2

def analyze(interval: str, rows, dup_count: int, bad_rows: int, hol: dict) -> dict:
    expected = FILES[interval]
    n = len(rows)
    st = {
        "interval": interval, "count": n,
        "first": rows[0][0] if n else None, "last": rows[-1][0] if n else None,
        "duplicates": dup_count, "bad_rows": bad_rows,
        "ohlc_violations": 0, "nonpositive": 0,
        "weekend_gaps": 0, "short_gaps": 0,
        "holiday_gaps": [], "anomalous_gaps": [],
        "sat_bars": 0, "sun_day_bars": 0,
    }
    prev = None
    for dt, o, h, l, c in rows:
        if min(o, h, l, c) <= 0:
            st["nonpositive"] += 1
        if h < l or h < max(o, c) or l > min(o, c):
            st["ohlc_violations"] += 1
        if dt.weekday() == 5:
            st["sat_bars"] += 1
        elif dt.weekday() == 6 and dt.hour < 20:
            st["sun_day_bars"] += 1
        if prev is not None:
            delta = (dt - prev).total_seconds() / 60.0
            if delta <= expected * 1.5:
                pass
            elif (prev.weekday() == 4 and dt.weekday() in (6, 0)
                  and delta <= WEEKEND_GAP_MAX_MIN):
                st["weekend_gaps"] += 1
            else:
                name = (holiday_in_span(prev, dt, hol)
                        if delta <= HOLIDAY_GAP_MAX_MIN else None)
                if name:
                    st["holiday_gaps"].append((prev, dt, delta, name))
                elif delta <= SHORT_GAP_MAX_MIN:
                    st["short_gaps"] += 1
                else:
                    st["anomalous_gaps"].append((prev, dt, delta))
        prev = dt

    ok = (n > 0 and st["ohlc_violations"] == 0 and st["nonpositive"] == 0
          and len(st["anomalous_gaps"]) <= ANOMALOUS_TOLERANCE)
    st["verdict"] = "جاهز للربط بمحرك التحليل" if ok else "يحتاج مراجعة قبل الاستخدام"
    return st


# ---------------------------------------------------------------- التقرير

def fmt_gap(a, b, delta, name=None):
    base = f"من {a:%Y-%m-%d %H:%M} إلى {b:%Y-%m-%d %H:%M} UTC (≈ {delta/60:.1f} ساعة)"
    return f"{base} — {name}" if name else base


def build_report(all_stats):
    now_utc = datetime.now(timezone.utc)
    now_bgd = now_utc + timedelta(hours=3)
    lines = [
        "# تقرير التحقق v2 — شموع XAU/USD (فاحص واعٍ بعطلات السوق)",
        "",
        f"- وقت الإنشاء: {now_utc:%Y-%m-%d %H:%M} UTC ({now_bgd:%Y-%m-%d %H:%M} بتوقيت بغداد)",
        "- الفحص محلي بالكامل: لم يُرسل أي طلب إلى المزود.",
        "",
        "| الإطار | الشموع | من | إلى | عطلات نهاية الأسبوع | عطلات رسمية | فجوات قصيرة | غير مبررة | مخالفات OHLC | شموع السبت | الحكم النهائي |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in all_stats:
        first = f"{s['first']:%Y-%m-%d}" if s["first"] else "—"
        last = f"{s['last']:%Y-%m-%d}" if s["last"] else "—"
        lines.append(
            f"| {s['interval']} | {s['count']} | {first} | {last} "
            f"| {s['weekend_gaps']} | {len(s['holiday_gaps'])} | {s['short_gaps']} "
            f"| {len(s['anomalous_gaps'])} | {s['ohlc_violations']} "
            f"| {s['sat_bars']} | {s['verdict']} |"
        )
    for s in all_stats:
        if s["holiday_gaps"]:
            lines += ["", f"## إغلاقات عطلات رسمية في إطار {s['interval']} (طبيعية)"]
            for a, b, d, name in s["holiday_gaps"][:8]:
                lines.append(f"- {fmt_gap(a, b, d, name)}")
            if len(s["holiday_gaps"]) > 8:
                lines.append(f"- ... و{len(s['holiday_gaps']) - 8} أخرى")
        if s["anomalous_gaps"]:
            lines += ["", f"## فجوات غير مبررة متبقية في إطار {s['interval']}"]
            for a, b, d in s["anomalous_gaps"][:10]:
                lines.append(f"- {fmt_gap(a, b, d)}")
        if s["sat_bars"] or s["sun_day_bars"]:
            lines += ["", f"## شموع عطلة نهاية الأسبوع في إطار {s['interval']}"]
            lines.append(
                f"- شموع يوم السبت: {s['sat_bars']} | شموع نهار الأحد قبل 20:00 UTC: {s['sun_day_bars']}."
            )
            lines.append(
                "- سوق الذهب الفوري مغلق في هذه الأوقات، فهذه الشموع غالبًا تسعير راكد أو"
                " مجمّع من مصدر آخر. يُنصح بترشيحها (استبعاد السبت ونهار الأحد) قبل حساب"
                " المؤشرات حتى لا تنكمش قيم ATR والتقلب اصطناعيًا."
            )
    lines += [
        "",
        "ملاحظة: فجوات نهاية الأسبوع والعطلات الرسمية إغلاقات سوق طبيعية وليست خللًا في البيانات.",
        "",
        "هذه بيانات تحليلية تاريخية، وليست أسعار تنفيذ من وسيط، ولا تشكل توصية تداول.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------- التشغيل

def main():
    print("=" * 62)
    print("Babylon AI — فاحص جودة شموع XAU/USD (v2 واعٍ بالعطلات)")
    print("=" * 62)

    if not DATA_DIR.exists():
        print(f"لم أجد مجلد البيانات: {DATA_DIR}")
        print("شغّل هذا السكربت من نفس المجلد الذي يحتوي data\\ (مجلد المشروع).")
        sys.exit(1)

    all_stats = []
    years = set()
    loaded = {}
    for interval in FILES:
        path = DATA_DIR / f"xauusd_{interval}.csv"
        if not path.exists():
            print(f"  - {interval:<6}: الملف غير موجود — تجاوزته.")
            continue
        rows, dups, bad = load_csv(path)
        loaded[interval] = (rows, dups, bad)
        if rows:
            years.update(range(rows[0][0].year, rows[-1][0].year + 2))

    if not loaded:
        print("لا توجد ملفات شموع في data\\ — شغّل twelvedata_downloader.py أولًا.")
        sys.exit(1)

    hol = market_holidays(sorted(years))

    for interval, (rows, dups, bad) in loaded.items():
        s = analyze(interval, rows, dups, bad, hol)
        all_stats.append(s)
        print(f"\n■ {interval} — {s['count']} شمعة "
              f"({s['first']:%Y-%m-%d} → {s['last']:%Y-%m-%d})" if s["count"]
              else f"\n■ {interval} — ملف فارغ")
        if not s["count"]:
            continue
        print(f"  عطلات نهاية الأسبوع: {s['weekend_gaps']} | "
              f"عطلات رسمية: {len(s['holiday_gaps'])} | "
              f"فجوات قصيرة: {s['short_gaps']} | "
              f"غير مبررة: {len(s['anomalous_gaps'])}")
        print(f"  مخالفات OHLC: {s['ohlc_violations']} | أسعار صفرية/سالبة: {s['nonpositive']} | "
              f"مكررات: {s['duplicates']} | صفوف تالفة: {s['bad_rows']}")
        print(f"  شموع السبت: {s['sat_bars']} | شموع نهار الأحد (<20:00 UTC): {s['sun_day_bars']}")
        for a, b, d, name in s["holiday_gaps"][:4]:
            print(f"    عطلة: {fmt_gap(a, b, d, name)}")
        if len(s["holiday_gaps"]) > 4:
            print(f"    ... و{len(s['holiday_gaps']) - 4} عطلة أخرى (كاملة في التقرير)")
        for a, b, d in s["anomalous_gaps"][:6]:
            print(f"    ⚠ غير مبررة: {fmt_gap(a, b, d)}")
        print(f"  ← الحكم النهائي: {s['verdict']}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    report_path = DATA_DIR / "validation_report_v2_ar.md"
    report_path.write_text(build_report(all_stats), encoding="utf-8")
    print(f"\nالتقرير الكامل: {report_path}")

    ready = sum(1 for s in all_stats if s["verdict"].startswith("جاهز"))
    print(f"الخلاصة: {ready} من {len(all_stats)} أطر جاهزة للربط بمحرك التحليل.")
    if any(s["sat_bars"] for s in all_stats):
        print("تنبيه: توجد شموع نهاية أسبوع في بعض الأطر — راجع قسمها في التقرير قبل حساب المؤشرات.")


if __name__ == "__main__":
    main()
