"""Notification system for trading signals and events."""
import logging
import httpx
from datetime import datetime, timezone
from typing import Optional, List
import os

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram bot notification service."""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token (from BotFather)
            chat_id: Telegram chat/channel ID to send messages to
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.enabled = bool(self.bot_token and self.chat_id)

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send a text message to Telegram.

        Args:
            text: Message text
            parse_mode: HTML or Markdown for formatting

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Telegram notifications not configured")
            return False

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{self.api_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": text,
                        "parse_mode": parse_mode,
                    },
                )

                if response.status_code == 200:
                    logger.info("✅ Telegram message sent successfully")
                    return True
                else:
                    logger.error(f"❌ Telegram error: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
            return False

    def send_signal_notification(
        self,
        symbol: str,
        timeframe: str,
        direction: str,
        state: str,
        confidence: float,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        risk_reward: Optional[float] = None,
    ) -> bool:
        """
        Send a trading signal notification.

        Args:
            symbol: Trading pair (XAU/USD)
            timeframe: Chart timeframe (5min, 15min, 1h, 4h)
            direction: BUY, SELL, or NEUTRAL
            state: WATCH, CONFIRMED, INVALIDATED, RISK_BLOCK
            confidence: Confidence level (0-1)
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            risk_reward: Risk/reward ratio

        Returns:
            True if sent successfully, False otherwise
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Direction emoji
        direction_emoji = "📈 صاعد" if direction == "BUY" else "📉 هابط" if direction == "SELL" else "➡️ محايد"

        # State emoji
        state_emoji = "🟢" if state == "CONFIRMED" else "🔵" if state == "WATCH" else "🔴" if state == "INVALIDATED" else "⚠️"

        message = f"""
{state_emoji} <b>إشارة تداول جديدة</b>

<b>الزوج:</b> {symbol}
<b>الإطار الزمني:</b> {timeframe}
<b>الاتجاه:</b> {direction_emoji}
<b>الحالة:</b> {state}
<b>مستوى الثقة:</b> {confidence*100:.1f}%

"""

        if entry_price:
            message += f"<b>سعر الدخول:</b> {entry_price:.2f}\n"
        if stop_loss:
            message += f"<b>وقف الخسارة:</b> {stop_loss:.2f}\n"
        if take_profit:
            message += f"<b>الهدف:</b> {take_profit:.2f}\n"
        if risk_reward:
            message += f"<b>نسبة المخاطرة/العائد:</b> 1:{risk_reward:.2f}\n"

        message += f"\n<i>{timestamp}</i>"

        return self.send_message(message)

    def send_analysis_summary(
        self,
        timeframe: str,
        current_price: float,
        ema_20: Optional[float] = None,
        ema_50: Optional[float] = None,
        ema_200: Optional[float] = None,
        rsi: Optional[float] = None,
        market_regime: Optional[str] = None,
    ) -> bool:
        """Send market analysis summary."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        message = f"""
📊 <b>تحديث تحليل السوق</b>

<b>الزوج:</b> XAU/USD
<b>الإطار:</b> {timeframe}
<b>السعر الحالي:</b> ${current_price:.2f}

"""

        if ema_20:
            message += f"<b>EMA 20:</b> {ema_20:.2f}\n"
        if ema_50:
            message += f"<b>EMA 50:</b> {ema_50:.2f}\n"
        if ema_200:
            message += f"<b>EMA 200:</b> {ema_200:.2f}\n"
        if rsi:
            rsi_status = "🔴 مرتفع جدًا" if rsi > 70 else "🟢 منخفض جدًا" if rsi < 30 else "⚪ محايد"
            message += f"<b>RSI 14:</b> {rsi:.1f} {rsi_status}\n"
        if market_regime:
            message += f"<b>نظام السوق:</b> {market_regime}\n"

        message += f"\n<i>{timestamp}</i>"

        return self.send_message(message)

    def send_risk_alert(
        self,
        timeframe: str,
        reason: str,
        account_risk_pct: float,
        recommendation: str,
    ) -> bool:
        """Send risk management alert."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        message = f"""
⚠️ <b>تنبيه إدارة المخاطر</b>

<b>الإطار:</b> {timeframe}
<b>السبب:</b> {reason}
<b>مخاطر الحساب:</b> {account_risk_pct:.2f}%
<b>التوصية:</b> {recommendation}

<i>{timestamp}</i>
"""

        return self.send_message(message)

    def send_system_status(
        self,
        status: str,
        data_age_hours: Optional[float] = None,
        scheduler_running: Optional[bool] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Send system status notification."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        status_emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"

        message = f"""
{status_emoji} <b>حالة النظام</b>

<b>الحالة:</b> {status}
"""

        if data_age_hours is not None:
            message += f"<b>عمر البيانات:</b> {data_age_hours:.1f} ساعات\n"
        if scheduler_running is not None:
            scheduler_status = "🟢 مشغل" if scheduler_running else "🔴 موقف"
            message += f"<b>المجدول:</b> {scheduler_status}\n"
        if error_message:
            message += f"<b>الخطأ:</b> {error_message}\n"

        message += f"\n<i>{timestamp}</i>"

        return self.send_message(message)


class NotificationManager:
    """Manages notification preferences and delivery."""

    def __init__(self):
        """Initialize notification manager."""
        self.telegram = TelegramNotifier()
        self.notifications_enabled = {
            "signals": True,
            "analysis": False,
            "risks": True,
            "system": False,
        }

    def set_enabled(self, notification_type: str, enabled: bool):
        """Enable or disable a notification type."""
        if notification_type in self.notifications_enabled:
            self.notifications_enabled[notification_type] = enabled
            logger.info(f"Notification '{notification_type}' set to {enabled}")

    def notify_signal(
        self,
        symbol: str,
        timeframe: str,
        direction: str,
        state: str,
        confidence: float,
        **kwargs,
    ) -> bool:
        """Send signal notification if enabled."""
        if not self.notifications_enabled["signals"]:
            return False

        return self.telegram.send_signal_notification(
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            state=state,
            confidence=confidence,
            **kwargs,
        )

    def notify_analysis(
        self,
        timeframe: str,
        current_price: float,
        **kwargs,
    ) -> bool:
        """Send analysis notification if enabled."""
        if not self.notifications_enabled["analysis"]:
            return False

        return self.telegram.send_analysis_summary(
            timeframe=timeframe,
            current_price=current_price,
            **kwargs,
        )

    def notify_risk(
        self,
        timeframe: str,
        reason: str,
        account_risk_pct: float,
        recommendation: str,
    ) -> bool:
        """Send risk alert if enabled."""
        if not self.notifications_enabled["risks"]:
            return False

        return self.telegram.send_risk_alert(
            timeframe=timeframe,
            reason=reason,
            account_risk_pct=account_risk_pct,
            recommendation=recommendation,
        )

    def notify_system(self, **kwargs) -> bool:
        """Send system status if enabled."""
        if not self.notifications_enabled["system"]:
            return False

        return self.telegram.send_system_status(**kwargs)

    def get_status(self) -> dict:
        """Get notification system status."""
        return {
            "telegram_enabled": self.telegram.enabled,
            "telegram_configured": bool(self.telegram.bot_token and self.telegram.chat_id),
            "notifications_enabled": self.notifications_enabled,
            "setup_guide": "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars",
        }


# Global instance
notification_manager = NotificationManager()
