# Live Telegram Notifications Setup

**Status**: ✅ Complete  
**Requires**: Telegram Bot Token + Chat ID (5 minute setup)

---

## 🚀 Quick Start

### **Step 1: Create Telegram Bot (2 minutes)**

1. Open Telegram and search for `@BotFather`
2. Send `/start` then `/newbot`
3. Choose a name (e.g., "Babylon AI Gold")
4. Choose a username (e.g., "babylon_gold_bot")
5. **Copy the token** → You'll need this

**Example token**: `123456789:ABCDEFGHijklmnopqrstuvwxyz_1234567`

### **Step 2: Get Your Chat ID (2 minutes)**

**Option A: Private Messages**
1. Message your bot
2. Search for `@userinfobot` 
3. Send `/start`
4. It shows your ID (e.g., `123456789`)

**Option B: Group/Channel**
1. Add bot to your group
2. Send `@userinfobot` the message `/start`
3. Get the chat ID (negative for channels: `-1001234567890`)

### **Step 3: Set Environment Variables (1 minute)**

**Windows PowerShell** (as Administrator):
```powershell
$env:TELEGRAM_BOT_TOKEN = "123456789:ABCDEFGHijklmnopqrstuvwxyz_1234567"
$env:TELEGRAM_CHAT_ID = "your_chat_id"
```

**Windows CMD** (as Administrator):
```cmd
setx TELEGRAM_BOT_TOKEN "123456789:ABCDEFGHijklmnopqrstuvwxyz_1234567"
setx TELEGRAM_CHAT_ID "your_chat_id"
```

**Linux/Mac**:
```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCDEFGHijklmnopqrstuvwxyz_1234567"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### **Step 4: Restart Backend**
```powershell
cd D:\BabylonAI_GoldIntelligence\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

### **Step 5: Test (in browser or API)**
```
GET http://localhost:8000/api/v1/notifications/status
POST http://localhost:8000/api/v1/notifications/test-signal
```

✅ **You should receive a test message on Telegram!**

---

## 🎮 Admin Panel

**Access**: `http://localhost:3000/notifications`

### **Features**
- ✅ **Status indicator** — Shows if Telegram is connected
- ✅ **Toggle notifications** — Enable/disable each type individually
- ✅ **Test notifications** — Send samples to verify setup
- ✅ **Setup guide** — Integrated instructions

### **Notification Types**
1. **Signals** (🎯) — New trading signals
2. **Analysis** (📊) — Market analysis updates
3. **Risks** (⚠️) — Risk management alerts
4. **System** (⚙️) — System health status

---

## 📡 API Endpoints

### **Notification Status**
```
GET /api/v1/notifications/status
```
**Response**:
```json
{
  "timestamp": "2026-10-21T01:55:00Z",
  "status": {
    "telegram_enabled": true,
    "telegram_configured": true,
    "notifications_enabled": {
      "signals": true,
      "analysis": false,
      "risks": true,
      "system": false
    }
  }
}
```

### **Get Preferences**
```
GET /api/v1/notifications/preferences
```

### **Update Preferences**
```
POST /api/v1/notifications/preferences
Content-Type: application/json

{
  "signals": true,
  "analysis": true,
  "risks": true,
  "system": false
}
```

### **Test Notifications**
```
POST /api/v1/notifications/test-signal
POST /api/v1/notifications/test-analysis
POST /api/v1/notifications/test-risk
POST /api/v1/notifications/test-system
```

### **Setup Guide**
```
GET /api/v1/notifications/telegram-setup-guide
```

---

## 📝 Signal Notification Example

```
🟢 إشارة تداول جديدة

الزوج: XAU/USD
الإطار الزمني: 15min
الاتجاه: 📈 صاعد
الحالة: CONFIRMED
مستوى الثقة: 75.0%

سعر الدخول: 4120.50
وقف الخسارة: 4115.00
الهدف: 4130.00
نسبة المخاطرة/العائد: 1:2.00

2026-10-21 01:55:00 UTC
```

---

## 🏗️ Architecture

### **Notification Classes**

**TelegramNotifier** (`core/notifications.py`)
```python
# Send raw messages
telegram.send_message(text)

# Send formatted signals
telegram.send_signal_notification(
    symbol="XAU/USD",
    timeframe="15min",
    direction="BUY",
    state="CONFIRMED",
    confidence=0.75,
    entry_price=4120.50,
    stop_loss=4115.00,
    take_profit=4130.00,
    risk_reward=2.0
)

# Send analysis updates
telegram.send_analysis_summary(
    timeframe="1h",
    current_price=4120.01,
    ema_20=4121.85,
    rsi=65.5,
    market_regime="اتجاه صاعد"
)
```

**NotificationManager** (`core/notifications.py`)
```python
# Respects user preferences
manager.notify_signal(...)  # Only sends if enabled

# Get status
manager.get_status()

# Toggle types
manager.set_enabled("signals", True)
```

---

## 🔧 Configuration

### **Environment Variables**
```
TELEGRAM_BOT_TOKEN=your_bot_token      # Required for notifications
TELEGRAM_CHAT_ID=your_chat_id           # Required for notifications
```

### **Fallback**
If not configured:
- ✅ System still works
- ✅ All features available
- ❌ Telegram notifications disabled
- 📌 Admin panel shows setup guide

---

## 🧪 Testing

### **Manual API Test**
```bash
# Check status
curl http://localhost:8000/api/v1/notifications/status

# Send test signal
curl -X POST http://localhost:8000/api/v1/notifications/test-signal

# Send test analysis
curl -X POST http://localhost:8000/api/v1/notifications/test-analysis
```

### **Via Admin Panel**
1. Go to `http://localhost:3000/notifications`
2. Click "Send test" buttons
3. Check Telegram for messages

---

## 📚 Usage Examples

### **Send Signal from Code**
```python
from core.notifications import notification_manager

notification_manager.notify_signal(
    symbol="XAU/USD",
    timeframe="15min",
    direction="BUY",
    state="CONFIRMED",
    confidence=0.82,
    entry_price=4120.50,
    stop_loss=4115.00,
    take_profit=4130.00,
)
```

### **Send Analysis Update**
```python
notification_manager.notify_analysis(
    timeframe="1h",
    current_price=4120.01,
    ema_20=4121.85,
    ema_50=4118.50,
    ema_200=4100.25,
    rsi=65.5,
    market_regime="اتجاه صاعد"
)
```

### **Send Risk Alert**
```python
notification_manager.notify_risk(
    timeframe="15min",
    reason="Account risk exceeds maximum",
    account_risk_pct=3.5,
    recommendation="WAIT"
)
```

---

## 🔐 Security Notes

- ✅ Bot token stored in environment variables (not in code)
- ✅ Chat ID can be for private messages or groups/channels
- ✅ No credentials stored in database
- ✅ Messages are read-only (no two-way interaction needed)
- ✅ Can disable notifications anytime in admin panel

---

## 🚀 Advanced: Auto-Notify on Signals

To automatically send notifications when signals are generated, integrate with signal routes:

```python
# In api/routes/signals.py
from core.notifications import notification_manager

@router.get("/generate/{interval}")
async def generate_signal(interval: str):
    # ... existing code ...
    signal = signal_engine.generate_signal(...)
    
    # Auto-notify if signal is CONFIRMED
    if signal.state == "CONFIRMED":
        notification_manager.notify_signal(
            symbol=signal.symbol,
            timeframe=interval,
            direction=signal.direction,
            state=signal.state,
            confidence=signal.confidence,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
        )
    
    return signal
```

---

## 📖 Notification Types

### **🎯 Trading Signals**
- **When**: New signal generated
- **Info**: Direction, confidence, entry/exit prices
- **Language**: العربية (Arabic)

### **📊 Market Analysis**
- **When**: Scheduled analysis or manual trigger
- **Info**: Current price, EMA levels, RSI, market regime
- **Frequency**: Configurable (optional)

### **⚠️ Risk Alerts**
- **When**: Risk threshold exceeded
- **Info**: Reason, account risk %, recommendation
- **Enabled**: Default ON (important)

### **⚙️ System Status**
- **When**: Health check or errors
- **Info**: System status, data age, scheduler state
- **Enabled**: Default OFF (optional)

---

## ⚙️ Setup Checklist

- [ ] Create Telegram bot via @BotFather
- [ ] Get bot token (copy safely)
- [ ] Get Chat ID from @userinfobot
- [ ] Set TELEGRAM_BOT_TOKEN environment variable
- [ ] Set TELEGRAM_CHAT_ID environment variable
- [ ] Restart backend
- [ ] Visit `/notifications` admin panel
- [ ] Send test notifications
- [ ] Verify messages arrive on Telegram
- [ ] Configure preferences (what to notify on)
- [ ] Done! 🎉

---

## 🆘 Troubleshooting

### **Status shows "Not Connected"**
- Check environment variables are set
- Restart backend (variables load on startup)
- Verify token is correct (no spaces, full string)

### **"Failed to send notification"**
- Verify Chat ID is correct
- Add bot to channel/group if using one
- Check bot token hasn't been revoked

### **Messages in wrong language**
- Check Telegram client language setting
- Messages are in Arabic (العربية) by default

### **No test messages appearing**
- Check admin panel shows Telegram as connected
- Verify Chat ID is YOUR Telegram ID/group
- Send manual test via API: `POST /test-signal`

---

## 📞 Support

**Telegram Issues?**
- BotFather docs: `t.me/BotFather?start=help`
- userinfobot: `t.me/userinfobot`

**Integration Issues?**
- Check backend logs: `POST /api/v1/notifications/test-signal`
- Status endpoint shows configuration: `GET /api/v1/notifications/status`

---

## 🎉 You're All Set!

Your platform now sends **instant Telegram notifications** for:
- ✅ New trading signals
- ✅ Market analysis updates
- ✅ Risk management alerts
- ✅ System status checks

All **configurable, secure, and in Arabic** (العربية)!
