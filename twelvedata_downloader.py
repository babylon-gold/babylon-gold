# -*- coding: utf-8 -*-
"""
Babylon AI Gold Intelligence — Twelve Data Historical Downloader
================================================================
تنزيل شموع XAU/USD التاريخية (5min / 15min / 1h / 4h) من Twelve Data
على الخطة المجانية Basic، ثم التحقق من جودة البيانات وكتابة تقرير عربي.

- يقرأ مفتاح API من متغير البيئة TWELVEDATA_API_KEY أو من ملف api_key.txt بجانب السكربت.
- يحترم حدود الخطة المجانية: 8 طلبات/دقيقة، 800 طلب/يوم، 5000 شمعة لكل طلب.
- تنزيل بيانات وتحقق فقط — لا تداول، ولا اتصال بأي وسيط، ولا تنفيذ أوامر.

التشغيل:
    python twelvedata_downloader.py

المخرجات:
    data/xauusd_5min.csv , xauusd_15min.csv , xauusd_1h.csv , xauusd_4h.csv
    data/validation_report_ar.md
"""

import csv
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("مكتبة requests غير مثبتة. نفّذ أولًا:  pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------- الإعدادات

BASE_URL = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "data"

# العمق المستهدف لكل إطار زمني (بالأيام). عدّلها كما تشاء.
TARGETS = {
    "5min": 90,         # ~3 أشهر
    "15min": 365,       # سنة
    "1h": 365 * 3,      # 3 سنوات
    "4h": 365 * 5,      # 5 سنوات
}
INTERVAL_MINUTES = {"5min": 5, "15min": 15, "1h": 60, "4h": 240}

OUTPUTSIZE = 5000            # الحد الأقصى للشموع في الطلب الواحد (الخطة المجانية)
REQUEST_GAP_SECONDS = 8.5    # ~7 طلبات/دقيقة (الحد 8 — نترك هامش أمان)
DAILY_BUDGET_STOP = 780      # نتوقف قبل حد 800 طلب/يوم
MAX_429_RETRIES = 3

# ---------------------------------------------------------------- أدوات عامة

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


class ApiError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def explain_api_error(e: ApiError) -> str:
    msg = (e.message or "").lower()
    if e.code == 401 or "apikey" in msg or "api key" in msg:
        return "مفتاح API غير صحيح أو غير مفعّل. تأكد من نسخه كاملًا."
    if e.code == 403 or "plan" in msg or "upgrade" in msg or "grow" in msg:
        return ("هذا الرمز أو الإطار الزمني غير متاح في خطتك الحالية (Basic/Free). "
                "قد يتطلب XAU/USD خطة أعلى — راجع README للبدائل المجانية (MT5 التجريبي / Dukascopy).")
    if e.code == 404 or "not found" in msg or "symbol" in msg:
        return "الرمز غير معروف لدى المزود بهذه الصيغة."
    return f"خطأ من المزود (رمز {e.code}): {e.message}"


def load_api_key() -> str:
    key = os.environ.get("TWELVEDATA_API_KEY", "").strip()
    if not key:
        key_file = SCRIPT_DIR / "api_key.txt"
        if key_file.exists():
            key = key_file.read_text(encoding="utf-8").strip()
    if not key:
        print("لم يتم العثور على مفتاح API.")
        print("ضعه في متغير البيئة TWELVEDATA_API_KEY، أو في ملف api_key.txt بجانب هذا السكربت.")
        print("راجع README_TWELVEDATA_AR.md للخطوات. لا تشارك المفتاح مع أي أحد.")
        sys.exit(1)
    return key


# ---------------------------------------------------------------- طلبات الشبكة

_last_request_at = 0.0
_request_count = 0


def td_request(params: dict) -> dict:
    """طلب واحد إلى Twelve Data مع احترام حدود الخطة المجانية."""
    global _last_request_at, _request_count

    for _ in range(MAX_429_RETRIES + 1):
        if _request_count >= DAILY_BUDGET_STOP:
            raise RuntimeError(
                f"اقتربنا من حد 800 طلب/يوم (استُهلك {_request_count}). "
                "توقف السكربت حمايةً لحسابك — أعد التشغيل غدًا أو قلّل العمق المستهدف."
            )
        wait = REQUEST_GAP_SECONDS - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        _last_request_at = time.monotonic()
        _request_count += 1

        try:
            resp = requests.get(BASE_URL, params=params, timeout=30)
        except requests.RequestException as exc:
            raise RuntimeError(f"فشل الاتصال بالشبكة: {exc}") from exc

        try:
            data = resp.json()
        except ValueError:
            raise RuntimeError(f"استجابة غير متوقعة من المزود (HTTP {resp.status_code}).")

        if isinstance(data, dict) and data.get("status") == "error":
            code = int(data.get("code") or 0)
            message = str(data.get("message") or "")
            if code == 429:
                print("    بلغنا حد الطلبات مؤقتًا (429) — انتظار 65 ثانية ثم إعادة المحاولة...")
                time.sleep(65)
                continue
            raise ApiError(code, message)

        return data

    raise RuntimeError("تكرر خطأ 429 عدة مرات — أوقف السكربت وجرّب لاحقًا.")


def parse_dt(value: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"صيغة وقت غير معروفة: {value}")


# ---------------------------------------------------------------- فحص توفر الرمز

def probe_interval(interval: str, api_key: str):
    """فحص سريع: هل XAU/USD متاح بهذا الإطار على خطتك؟"""
    try:
        data = td_request({
            "symbol": SYMBOL, "interval": interval, "outputsize": 2,
            "timezone": "UTC", "apikey": api_key,
        })
    except ApiError as e:
        return False, explain_api_error(e)
    values = data.get("values") or []
    if not values:
        return False, "المزود أعاد استجابة بلا بيانات."
    return True, f"متاح — آخر شمعة: {values[0].get('datetime')} UTC"


# ---------------------------------------------------------------- التنزيل

def download_interval(interval: str, target_days: int, api_key: str):
    """ينزّل شموع إطار واحد حتى العمق المستهدف، دفعة 5000 شمعة في كل طلب."""
    start_cut = datetime.now(timezone.utc) - timedelta(days=target_days)
    rows = {}          # dt -> (open, high, low, close, volume)
    duplicates = 0
    parse_errors = 0
    end_date = None
    batch_no = 0

    while True:
        batch_no += 1
        params = {
            "symbol": SYMBOL,
            "interval": interval,
            "outputsize": OUTPUTSIZE,
            "timezone": "UTC",
            "apikey": api_key,
            "start_date": start_cut.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if end_date is not None:
            params["end_date"] = end_date.strftime("%Y-%m-%d %H:%M:%S")

        data = td_request(params)
        values = data.get("values") or []
        if not values:
            break

        oldest = None
        for v in values:
            try:
                dt = parse_dt(v["datetime"])
                o, h, l, c = (float(v["open"]), float(v["high"]),
                              float(v["low"]), float(v["close"]))
            except (KeyError, ValueError):
                parse_errors += 1
                continue
            vol = v.get("volume", "")
            if oldest is None or dt < oldest:
                oldest = dt
            if dt < start_cut:
                continue
            if dt in rows:
                duplicates += 1
            rows[dt] = (o, h, l, c, vol)

        reached = f"{oldest:%Y-%m-%d %H:%M} UTC" if oldest else "—"
        print(f"    الدفعة {batch_no}: وصلنا حتى {reached} (إجمالي الشموع: {len(rows)})")

        if oldest is None or oldest <= start_cut or len(values) < OUTPUTSIZE:
            break
        new_end = oldest - timedelta(seconds=1)
        if end_date is not None and new_end >= end_date:
            break  # حماية من حلقة لا نهائية
        end_date = new_end

    ordered = sorted(rows.items())
    return ordered, duplicates, parse_errors


def write_csv(interval: str, ordered_rows) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"xauusd_{interval}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["datetime_utc", "open", "high", "low", "close", "volume"])
        for dt, (o, h, l, c, vol) in ordered_rows:
            w.writerow([dt.strftime("%Y-%m-%d %H:%M:%S"), o, h, l, c, vol])
    return path


# ---------------------------------------------------------------- التحقق من الجودة

def is_weekend_gap(a: datetime, b: datetime, delta_min: float) -> bool:
    """الذهب يغلق مساء الجمعة ويفتح مساء الأحد (UTC) — فجوة طبيعية."""
    return a.weekday() == 4 and b.weekday() in (6, 0) and delta_min <= 72 * 60


def validate(interval: str, ordered_rows, duplicates: int, parse_errors: int) -> dict:
    expected = INTERVAL_MINUTES[interval]
    n = len(ordered_rows)
    stats = {
        "interval": interval, "count": n,
        "first": ordered_rows[0][0] if n else None,
        "last": ordered_rows[-1][0] if n else None,
        "duplicates": duplicates, "parse_errors": parse_errors,
        "ohlc_violations": 0, "nonpositive": 0,
        "weekend_gaps": 0, "short_gaps": 0, "anomalous_gaps": [],
    }
    prev_dt = None
    for dt, (o, h, l, c, _vol) in ordered_rows:
        if min(o, h, l, c) <= 0:
            stats["nonpositive"] += 1
        if h < l or h < max(o, c) or l > min(o, c):
            stats["ohlc_violations"] += 1
        if prev_dt is not None:
            delta_min = (dt - prev_dt).total_seconds() / 60.0
            if delta_min <= expected * 1.5:
                pass  # تسلسل طبيعي
            elif is_weekend_gap(prev_dt, dt, delta_min):
                stats["weekend_gaps"] += 1
            elif delta_min <= 150:
                stats["short_gaps"] += 1  # صيانة يومية / سيولة منخفضة
            else:
                stats["anomalous_gaps"].append((prev_dt, dt, delta_min))
        prev_dt = dt

    ok = (n > 0 and stats["ohlc_violations"] == 0 and stats["nonpositive"] == 0
          and len(stats["anomalous_gaps"]) <= 2)
    stats["verdict"] = "جاهز للربط بمحرك التحليل" if ok else "يحتاج مراجعة قبل الاستخدام"
    return stats


def write_report(all_stats: list, requests_used: int) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "validation_report_ar.md"
    now_utc = datetime.now(timezone.utc)
    now_bgd = now_utc + timedelta(hours=3)
    lines = [
        "# تقرير التحقق من شموع XAU/USD — Twelve Data (الخطة المجانية)",
        "",
        f"- وقت الإنشاء: {now_utc:%Y-%m-%d %H:%M} UTC ({now_bgd:%Y-%m-%d %H:%M} بتوقيت بغداد)",
        f"- الطلبات المستهلكة في هذا التشغيل: {requests_used} من حد 800 طلب/يوم",
        "- التوقيتات كلها UTC. حجم التداول غالبًا غير متوفر لأزواج المعادن الفورية،"
        " وسيُعوَّض لاحقًا ببيانات عقود GC كمؤشر منفصل.",
        "",
        "| الإطار | الشموع | من | إلى | فجوات نهاية الأسبوع | فجوات قصيرة | فجوات غير مبررة | مخالفات OHLC | مكررات | الحكم |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in all_stats:
        first = f"{s['first']:%Y-%m-%d}" if s["first"] else "—"
        last = f"{s['last']:%Y-%m-%d}" if s["last"] else "—"
        lines.append(
            f"| {s['interval']} | {s['count']} | {first} | {last} "
            f"| {s['weekend_gaps']} | {s['short_gaps']} | {len(s['anomalous_gaps'])} "
            f"| {s['ohlc_violations']} | {s['duplicates']} | {s['verdict']} |"
        )
    for s in all_stats:
        if s["anomalous_gaps"]:
            lines += ["", f"## فجوات غير مبررة في إطار {s['interval']} (أول 5)"]
            for a, b, d in s["anomalous_gaps"][:5]:
                lines.append(f"- من {a:%Y-%m-%d %H:%M} إلى {b:%Y-%m-%d %H:%M} UTC "
                             f"(≈ {d/60:.1f} ساعة)")
    lines += [
        "",
        "ملاحظة: فجوة نهاية الأسبوع (إغلاق الجمعة وفتح الأحد مساءً UTC) طبيعية في الذهب وليست خللًا. "
        "الفجوات القصيرة (≤ ساعتين ونصف) غالبًا فترة الصيانة اليومية أو عطلة جزئية.",
        "",
        "هذه بيانات تحليلية تاريخية، وليست أسعار تنفيذ من وسيط، ولا تشكل توصية تداول.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------- التشغيل

def main():
    print("=" * 62)
    print("Babylon AI Gold Intelligence — تنزيل شموع XAU/USD التاريخية")
    print("المزود: Twelve Data (الخطة المجانية Basic) — تحليل فقط، بلا تداول")
    print("=" * 62)

    api_key = load_api_key()

    # 1) فحص توفر الرمز والأطر على خطتك
    print("\n[1/3] فحص توفر XAU/USD على خطتك لكل إطار زمني:")
    available = []
    for interval in TARGETS:
        ok, note = probe_interval(interval, api_key)
        print(f"  - {interval:<6} : {'✅' if ok else '❌'} {note}")
        if ok:
            available.append(interval)

    if not available:
        print("\nلا يمكن الوصول إلى XAU/USD بأي إطار على هذه الخطة.")
        print("راجع README_TWELVEDATA_AR.md — البديلان المجانيان: MetaTrader 5 التجريبي أو Dukascopy.")
        sys.exit(2)

    # 2) التنزيل
    print(f"\n[2/3] التنزيل (مع احترام حد {int(60/REQUEST_GAP_SECONDS)} طلبات/دقيقة — قد يستغرق دقائق):")
    all_stats = []
    for interval in available:
        print(f"\n  ⏬ {interval} — العمق المستهدف: {TARGETS[interval]} يومًا")
        try:
            ordered, dups, perr = download_interval(interval, TARGETS[interval], api_key)
        except ApiError as e:
            print(f"    توقف إطار {interval}: {explain_api_error(e)}")
            continue
        if not ordered:
            print(f"    لم تصل أي شموع لإطار {interval}.")
            continue
        path = write_csv(interval, ordered)
        stats = validate(interval, ordered, dups, perr)
        all_stats.append(stats)
        print(f"    حُفظ: {path.name} ({stats['count']} شمعة، "
              f"{stats['first']:%Y-%m-%d} → {stats['last']:%Y-%m-%d}) — {stats['verdict']}")

    if not all_stats:
        print("\nلم يُنزَّل أي إطار بنجاح.")
        sys.exit(2)

    # 3) التقرير
    report = write_report(all_stats, _request_count)
    print(f"\n[3/3] تقرير التحقق: {report}")
    print(f"إجمالي الطلبات المستهلكة: {_request_count} من 800 متاحة يوميًا.")
    print("\nالخطوة التالية في Babylon AI: ربط ملفات CSV بمحرك المؤشرات "
          "(EMA/RSI/ATR/ADX وبنية السوق) بدل الشموع التجريبية.")


if __name__ == "__main__":
    main()
