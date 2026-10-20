# Babylon AI Gold Intelligence — حزمة مصادر بيانات الذهب XAU/USD

**الإصدار:** 1.0 — بداية التشغيل على Windows 10 / Windows 11

هذه الحزمة تساعدك في بناء قسم البيانات داخل مشروع Babylon AI Gold Intelligence. وهي **ليست روبوت تداول** ولا تفتح صفقات. لا تحتوي الحزمة على أي أسعار تاريخية حقيقية أو سعر حي محفوظ مسبقًا؛ البيانات التجريبية المرفقة اصطناعية وموسومة بوضوح.

## المحتويات

| الملف | الفائدة |
|---|---|
| `data/demo/XAUUSD_*_SYNTHETIC.csv` | بيانات تجريبية للاختبار البرمجي فقط (5min, 15min, 1h, 4h) |
| `scripts/fetch_live_goldapi.py` | تنزيل سعر الذهب الفوري الحالي **لحظة التشغيل**، ولا يحتاج API key |
| `scripts/fetch_history_twelvedata.py` | تنزيل شموع XAU/USD التاريخية الحقيقية عبر حساب Twelve Data |
| `scripts/validate_csv.py` | التحقق من بنية وجودة CSV |
| `RUN_DEMO_WINDOWS.bat` | تشغيل توليد بيانات تجريبية |
| `FETCH_LIVE_QUOTE_WINDOWS.bat` | جلب السعر الحالي مرة واحدة |
| `tests/test_data.py` | اختبارات آلية دون اتصال بالإنترنت |

## خطوات تشغيل بسيطة

1. فك الضغط في `D:\BabylonAI_GoldIntelligence\GoldDataStarter` أو في مجلد مناسب.
2. تأكد من توفر Python 3.10 أو أحدث: افتح PowerShell واكتب `py -3 --version`.
3. شغّل `RUN_DEMO_WINDOWS.bat` لتوليد أو إعادة إنشاء بيانات المحاكاة.
4. شغّل `FETCH_LIVE_QUOTE_WINDOWS.bat` لجلب **السعر الحالي الحقيقي** من Gold API، إذا كان الإنترنت متاحًا.
5. ابحث عن الناتج في `data\live\XAUUSD_latest_quote.json` وعن لقطات السعر في `data\live\XAUUSD_spot_snapshots.csv`.

### أوامر PowerShell — استيراد تاريخ حقيقي عبر Twelve Data

احصل أولًا على API key من https://twelvedata.com/ ثم نفّذ هذه الأوامر من جذر الحزمة:

```powershell
$env:TWELVEDATA_API_KEY = 'PASTE_YOUR_KEY_HERE'
py -3 scripts\fetch_history_twelvedata.py --interval 5min --count 1000
py -3 scripts\fetch_history_twelvedata.py --interval 15min --count 1000
py -3 scripts\fetch_history_twelvedata.py --interval 1h --count 1000
py -3 scripts\fetch_history_twelvedata.py --interval 4h --count 1000
py -3 scripts\validate_csv.py data\live\XAUUSD_15min_twelvedata.csv
```

**مهم:** الخطة المجانية ليست ضمانًا لإتاحة شموع XAU/USD على جميع الأطر. إذا ظهر رد `access denied`, `plan restriction` أو أي خطأ فلا تستخدم بيانات وهمية بدلها؛ تحقق من صلاحية الرمز والخطة ومصدر الأسعار. يمكن للمزود أيضًا تطبيق حدود عدد الطلبات. عند فشل أي طلب يحتفظ البرنامج بما حُفظ سابقًا ولا ينشئ تاريخًا زائفًا.

### جلب تاريخ أقدم على دفعات

```powershell
py -3 scripts\fetch_history_twelvedata.py --interval 15min --count 5000 --pages 8 --start 2026-09-01 --end 2026-10-19
```

**ملاحظة:** يطلب البرنامج دفعات تاريخية باتجاه الماضي؛ يتوقف عند الوصول إلى `--start` إن أمكن. يطبق مهلة 9 ثوانٍ بين الصفحات افتراضيًا، لكن حدود الاشتراك قد تتطلب الانتظار أو تقليل الطلبات. إذا انتهت `--pages` قبل الوصول إلى التاريخ المطلوب، فالملف الناتج **جزئي** ولا يمثل التاريخ كله.

### تحديث لقطة السعر الحية

```powershell
py -3 scripts\fetch_live_goldapi.py
```

وللتحديث كل 60 ثانية أثناء تشغيل النافذة:

```powershell
py -3 scripts\fetch_live_goldapi.py --watch --poll 60
```

يمكن إيقاف المراقبة بالضغط على `Ctrl+C`. ينصح المصدر بتخزين السعر مؤقتًا 30 ثانية. السعر هنا **سعر إرشادي** وليس أسعار Bid/Ask لوسيطك. ولا يحوّل البرنامج لقطات سعر متباعدة إلى شموع حقيقية.

## شكل البيانات

الأعمدة في ملف الشموع:

`timestamp_utc,open,high,low,close,volume,source,instrument,interval,bar_complete`

- `timestamp_utc`: وقت بداية الشمعة بتوقيت UTC بصيغة ISO 8601.
- `open/high/low/close`: أسعار OHLC بوحدة دولار أمريكي لكل أونصة تروي.
- `volume`: يُترك فارغًا إذا لم يوفر مصدر الذهب الفوري حجم تداول موثوقًا. **لا تعتبر الفراغ صفرًا.**
- `source`: اسم المزود أو الوسم `SYNTHETIC_DEMO_NOT_REAL`.
- `bar_complete`: إذا كان False، لا تُستخدم الشمعة في استراتيجيات إغلاق الشموع.

الملفات التجريبية تستخدم تقويمًا مبسطًا من الاثنين للجمعة، ولا تمثل ساعات التداول الحقيقية أو أسعار السوق أو التوزيع الحقيقي للتقلب. تُستخدم لفحص واجهة البرنامج فقط.

## اختبارات محلية

```powershell
py -3 -m unittest discover -s tests -v
```

## الاستخدام في Babylon AI Gold Intelligence

- `data/demo/*` تُظهرها الواجهة مع شريط **DEMO / SYNTHETIC** فقط.
- `data/live/XAUUSD_latest_quote.json` لوحة السعر الحالي وتوقيت التحديث؛ ليست OHLC ولا تستخدم للاختبار التاريخي.
- `data/live/XAUUSD_*_twelvedata.csv` مصدر رسم الشموع واختبار الاستراتيجيات بعد التأكد من الترخيص واكتمال البيانات وتوقيت كل شمعة.
- **ممنوع** استخدام بيانات تجريبية لحساب نسبة نجاح استراتيجية فعلية أو إصدار أوامر تداول.

## المراجع الرسمية

- Gold API docs: https://gold-api.com/docs
- Gold API integration reference: https://gold-api.com/llms.txt
- Twelve Data docs: https://twelvedata.com/docs
- Twelve Data historical prices: https://support.twelvedata.com/en/articles/5656039-how-to-get-historical-prices
- Twelve Data plans: https://twelvedata.com/pricing

راجع شروط استخدام وتوزيع بيانات كل مزود قبل نشر التطبيق تجاريًا. بعض بيانات الأسعار الحية والتاريخية محكومة بقيود ترخيص أو باشتراك خاص.
