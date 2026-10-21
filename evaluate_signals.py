# -*- coding: utf-8 -*-
"""
Babylon AI Gold Intelligence — مُقيِّم الإشارات (التكاليف + تقطيع الأداء)
========================================================================
يعيد مسح الإشارات ثم يجيب عن ثلاثة أسئلة علمية:

  1. كم يتبقى من التوقع (R) بعد خصم السبريد والانزلاق لكل صفقة؟
  2. كيف يتوزع الأداء حسب: حالة السوق (Regime) • الجلسة • الاتجاه • السنة؟
  3. ما شكل منحنى الأداء التراكمي وأقصى انخفاض وأطول سلسلة خسائر؟

⚠ تحذير منهجي إلزامي — خطر تعدد المقارنات:
  عندما نقطّع النتائج إلى شرائح كثيرة، ستبدو بعض الشرائح "رابحة" بمحض
  الصدفة. أي شريحة واعدة هنا هي *فرضية* تحتاج إثباتًا على بيانات لم
  تدخل هذا التحليل (Walk-Forward)، وليست استراتيجية جاهزة للتداول.

يعمل محليًا بالكامل: بلا إنترنت، بلا مفتاح، بلا أي طلب من حصتك.

التشغيل (من مجلد المشروع، بجانب analyze_gold.py وsignal_engine.py):
    python evaluate_signals.py

المخرجات:
    data/signals_evaluated.csv  +  data/evaluation_report_ar.md
"""

import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from analyze_gold import detect_regime
    from signal_engine import (load_frame, run_scan, Frame,  # noqa: F401
                               STRAT_AR, DIR_AR, TARGET_R)
except ImportError as e:
    print("أحتاج analyze_gold.py وsignal_engine.py بجانب هذا السكربت في نفس المجلد.")
    print(f"({e})")
    sys.exit(1)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DATA_DIR = SCRIPT_DIR / "data"

# -------- نموذج التكاليف (قيم افتراضية متحفظة قابلة للضبط حسب وسيطك) --------
SPREAD_USD = 0.35       # سبريد ذهاب-إياب تقريبي على XAU/USD بالدولار
SLIPPAGE_USD = 0.10     # انزلاق تقديري للدخول والخروج معًا
COST_USD = SPREAD_USD + SLIPPAGE_USD

PROMISING_MIN_N = 30    # أقل عدد صفقات لاعتبار الشريحة قابلة للنقاش أصلًا
PROMISING_MIN_NET = 0.05


# ---------------------------------------------------------------- تصنيفات

def regime_at(f: Frame, i: int) -> str:
    atr_hist = [x for x in f.atr[max(0, i - 500):i + 1] if x is not None]
    label, _, _ = detect_regime(f.c[i], f.ema50[i], f.ema200[i],
                                f.adx[i], atr_hist, f.atr[i] or 0.0)
    return label.split(" +")[0]   # الحالة الأساسية بلا لاحقة التقلب


def session_of(dt: datetime) -> str:
    h = dt.hour
    if 7 <= h < 13:
        return "لندن (07–13 UTC)"
    if 13 <= h < 21:
        return "نيويورك (13–21 UTC)"
    return "آسيوية/هادئة (21–07 UTC)"


# ---------------------------------------------------------------- التقييم

def evaluate(f1h: Frame, f15: Frame):
    scenarios, blocked = run_scan(f1h, f15)
    idx_of = {dt: i for i, dt in enumerate(f1h.dt)}
    confirmed = []
    for s in scenarios:
        i = idx_of.get(s["created"])
        s["regime"] = regime_at(f1h, i) if i is not None else "غير محدد"
        s["session"] = session_of(s["created"])
        s["year"] = s["created"].year
        if s["state"] != "CONFIRMED":
            continue
        risk = abs(s["entry"] - s["invalidation"])
        cost_r = (COST_USD / risk) if risk else 0.0
        s["risk_usd"] = round(risk, 2)
        s["cost_r"] = round(cost_r, 3)
        s["net_r"] = round((s["r"] or 0.0) - cost_r, 3)
        confirmed.append(s)
    confirmed.sort(key=lambda s: s["confirmed"])
    return scenarios, confirmed, blocked


def agg(rows):
    n = len(rows)
    wins = sum(1 for s in rows if s["result"] == "WIN")
    losses = sum(1 for s in rows if s["result"] == "LOSS")
    resolved = wins + losses
    gross = sum(s["r"] for s in rows) / n if n else 0.0
    net = sum(s["net_r"] for s in rows) / n if n else 0.0
    wr = (wins / resolved * 100) if resolved else None
    return dict(n=n, wins=wins, losses=losses, wr=wr, gross=gross, net=net)


def breakdown(confirmed, key_fn):
    buckets = {}
    for s in confirmed:
        buckets.setdefault(key_fn(s), []).append(s)
    return {k: agg(v) for k, v in sorted(buckets.items(), key=lambda kv: str(kv[0]))}


def equity_stats(net_rs):
    cum = peak = maxdd = 0.0
    streak = max_streak = 0
    for r in net_rs:
        cum += r
        peak = max(peak, cum)
        maxdd = max(maxdd, peak - cum)
        streak = streak + 1 if r < 0 else 0
        max_streak = max(max_streak, streak)
    return round(cum, 1), round(maxdd, 1), max_streak


# ---------------------------------------------------------------- العرض

def fmt_row(label, a):
    wr = f"{a['wr']:.0f}%" if a["wr"] is not None else "—"
    return (f"| {label} | {a['n']} | {wr} | {a['gross']:+.2f}R | {a['net']:+.2f}R |")


def table(title, data, flags):
    lines = [f"### {title}", "",
             "| الشريحة | الصفقات | نسبة الربح | التوقع الخام | التوقع الصافي |",
             "|---|---|---|---|---|"]
    for k, a in data.items():
        lines.append(fmt_row(str(k), a))
        if a["n"] >= PROMISING_MIN_N and a["net"] > PROMISING_MIN_NET:
            flags.append((title, str(k), a))
    lines.append("")
    return lines


def build_report(scenarios, confirmed, blocked, f1h):
    now_utc = datetime.now(timezone.utc)
    now_bgd = now_utc + timedelta(hours=3)
    lines = [
        "# تقييم إشارات Babylon AI — التكاليف وتقطيع الأداء",
        "",
        f"- وقت الإنشاء: {now_utc:%Y-%m-%d %H:%M} UTC ({now_bgd:%Y-%m-%d %H:%M} بتوقيت بغداد)",
        f"- فترة البيانات: {f1h.dt[0]:%Y-%m-%d} → {f1h.dt[-1]:%Y-%m-%d}",
        f"- نموذج التكاليف: سبريد {SPREAD_USD}$ + انزلاق {SLIPPAGE_USD}$ لكل صفقة "
        "(يُحوَّل إلى R حسب مخاطرة كل صفقة على حدة) — عدّل القيم أعلى الملف حسب وسيطك.",
        f"- إجمالي السيناريوهات: {len(scenarios)} | المؤكدة المقاسة: {len(confirmed)} "
        f"| المحجوبة (تقلب شاذ): {len(blocked)}",
        "",
    ]
    flags = []
    for key in ("A", "B"):
        rows = [s for s in confirmed if s["strategy"] == key]
        if not rows:
            continue
        a = agg(rows)
        cum, maxdd, streak = equity_stats([s["net_r"] for s in rows])
        avg_cost = sum(s["cost_r"] for s in rows) / len(rows)
        lines += [
            f"## {STRAT_AR[key]} — الخلاصة",
            "",
            f"- صفقات مقاسة: {a['n']} | نسبة الربح: "
            f"{a['wr']:.0f}% (التعادل عند هدف {TARGET_R}R = 40%)" if a["wr"] is not None
            else f"- صفقات مقاسة: {a['n']}",
            f"- التوقع الخام: {a['gross']:+.2f}R ← متوسط كلفة الصفقة: −{avg_cost:.2f}R "
            f"← **التوقع الصافي: {a['net']:+.2f}R**",
            f"- الحصيلة التراكمية الصافية: {cum:+.1f}R | أقصى انخفاض: {maxdd:.1f}R "
            f"| أطول سلسلة خسائر: {streak}",
            "",
        ]
        lines += table(f"{STRAT_AR[key]} حسب حالة السوق عند ظهور الإشارة",
                       breakdown(rows, lambda s: s["regime"]), flags)
        lines += table(f"{STRAT_AR[key]} حسب الاتجاه",
                       breakdown(rows, lambda s: DIR_AR[s["direction"]]), flags)
        lines += table(f"{STRAT_AR[key]} حسب الجلسة",
                       breakdown(rows, lambda s: s["session"]), flags)
        lines += table(f"{STRAT_AR[key]} حسب السنة",
                       breakdown(rows, lambda s: s["year"]), flags)

    lines += ["## الشرائح المرشحة للفحص الأعمق", ""]
    if flags:
        for title, k, a in flags:
            lines.append(f"- {title} ← **{k}**: {a['n']} صفقة، صافي {a['net']:+.2f}R")
        lines += [
            "",
            "⚠ **هذه فرضيات وليست نتائج.** مع هذا العدد من الشرائح، ظهور بعضها "
            "موجبًا متوقع بمحض الصدفة (تعدد المقارنات). الطريق الصحيح: اختيار فرضية "
            "واحدة ذات منطق سوقي، تثبيت قاعدتها مسبقًا، ثم اختبارها على فترة لم "
            "تدخل هذا التحليل (Walk-Forward) قبل أي ثقة.",
        ]
    else:
        lines.append("لا توجد شريحة تجاوزت عتبة الترشيح "
                     f"(≥{PROMISING_MIN_N} صفقة وصافي > +{PROMISING_MIN_NET}R).")
    lines += [
        "", "---", "",
        "**ما لا يجوز فعله بهذا التقرير:** اختيار أفضل شريحة والتداول عليها غدًا. "
        "التقطيع بأثر رجعي يجد أنماطًا صدفية حتمًا.",
        "",
        "هذه نتائج تاريخية استكشافية بمعايير أولية — ليست توصية تداول ولا وعدًا بأي نتيجة.",
    ]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "evaluation_report_ar.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path, flags


def write_eval_csv(confirmed):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "signals_evaluated.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["strategy", "direction", "created_utc", "confirmed_utc",
                    "regime", "session", "year", "risk_usd",
                    "result", "gross_r", "cost_r", "net_r"])
        for s in confirmed:
            w.writerow([s["strategy"], DIR_AR[s["direction"]],
                        s["created"].strftime("%Y-%m-%d %H:%M"),
                        s["confirmed"].strftime("%Y-%m-%d %H:%M"),
                        s["regime"], s["session"], s["year"], s["risk_usd"],
                        s["result"], s["r"], s["cost_r"], s["net_r"]])
    return path


# ---------------------------------------------------------------- التشغيل

def main():
    print("=" * 62)
    print("Babylon AI — تقييم الإشارات: التكاليف + تقطيع الأداء")
    print("=" * 62)

    f1h = load_frame("1h")
    f15 = load_frame("15min")
    if f1h is None or f15 is None:
        print("أحتاج ملفَي xauusd_1h.csv وxauusd_15min.csv في data\\ أولًا.")
        sys.exit(1)

    scenarios, confirmed, blocked = evaluate(f1h, f15)
    if not confirmed:
        print("لا توجد صفقات مؤكدة لتقييمها.")
        sys.exit(0)

    for key in ("A", "B"):
        rows = [s for s in confirmed if s["strategy"] == key]
        if not rows:
            continue
        a = agg(rows)
        cum, maxdd, streak = equity_stats([s["net_r"] for s in rows])
        avg_cost = sum(s["cost_r"] for s in rows) / len(rows)
        wr = f"{a['wr']:.0f}%" if a["wr"] is not None else "—"
        print(f"\n■ {STRAT_AR[key]} — {a['n']} صفقة مقاسة")
        print(f"  نسبة الربح {wr} | خام {a['gross']:+.2f}R − تكاليف {avg_cost:.2f}R "
              f"= صافي {a['net']:+.2f}R")
        print(f"  تراكمي صافي {cum:+.1f}R | أقصى انخفاض {maxdd:.1f}R "
              f"| أطول سلسلة خسائر {streak}")
        reg = breakdown(rows, lambda s: s["regime"])
        for k, b in reg.items():
            wr2 = f"{b['wr']:.0f}%" if b["wr"] is not None else "—"
            print(f"    • {k}: {b['n']} صفقة | ربح {wr2} | صافي {b['net']:+.2f}R")

    report, flags = build_report(scenarios, confirmed, blocked, f1h)
    csv_path = write_eval_csv(confirmed)
    print(f"\nالشرائح المرشحة للفحص الأعمق: {len(flags)} "
          "(تفاصيلها وتحذير تعدد المقارنات في التقرير)")
    print(f"سجل الصفقات المُقيَّمة: {csv_path}")
    print(f"التقرير العربي الكامل: {report}")
    print("\n⚠ شريحة موجبة ≠ استراتيجية صالحة: أي فرضية تحتاج Walk-Forward على "
          "بيانات لم تدخل هذا التحليل. ليست توصية تداول.")


if __name__ == "__main__":
    main()
