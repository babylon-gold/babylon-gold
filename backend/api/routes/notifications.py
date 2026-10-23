"""Notification management endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from core.notifications import notification_manager
from core.auth import verify_admin_token

router = APIRouter()


class NotificationPreferences(BaseModel):
    """Notification preference settings."""
    signals: bool
    analysis: bool
    risks: bool
    system: bool


class TestNotification(BaseModel):
    """Test notification request."""
    notification_type: str  # signal, analysis, risk, system
    timeframe: Optional[str] = "15min"
    message: Optional[str] = None


@router.get("/status")
async def get_notification_status():
    """Get notification system status and configuration."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": notification_manager.get_status(),
    }


@router.get("/preferences")
async def get_notification_preferences():
    """Get current notification preferences."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "preferences": notification_manager.notifications_enabled,
    }


@router.post("/preferences")
async def set_notification_preferences(
    preferences: NotificationPreferences,
    admin_token: str = Depends(verify_admin_token),
):
    """Update notification preferences - Requires admin authentication."""
    notification_manager.set_enabled("signals", preferences.signals)
    notification_manager.set_enabled("analysis", preferences.analysis)
    notification_manager.set_enabled("risks", preferences.risks)
    notification_manager.set_enabled("system", preferences.system)

    return {
        "message": "Preferences updated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "preferences": notification_manager.notifications_enabled,
    }


@router.post("/test-signal")
async def send_test_signal(admin_token: str = Depends(verify_admin_token)):
    """Send a test trading signal notification - Requires admin authentication."""
    if not notification_manager.telegram.enabled:
        raise HTTPException(
            status_code=400,
            detail="Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID",
        )

    success = notification_manager.notify_signal(
        symbol="XAU/USD",
        timeframe="15min",
        direction="BUY",
        state="CONFIRMED",
        confidence=0.75,
        entry_price=4120.50,
        stop_loss=4115.00,
        take_profit=4130.00,
        risk_reward=2.0,
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send notification")

    return {
        "message": "Test signal notification sent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/test-analysis")
async def send_test_analysis(admin_token: str = Depends(verify_admin_token)):
    """Send a test market analysis notification - Requires admin authentication."""
    if not notification_manager.telegram.enabled:
        raise HTTPException(
            status_code=400,
            detail="Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID",
        )

    success = notification_manager.notify_analysis(
        timeframe="1h",
        current_price=4120.01,
        ema_20=4121.85,
        ema_50=4118.50,
        ema_200=4100.25,
        rsi=65.5,
        market_regime="اتجاه صاعد",
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send notification")

    return {
        "message": "Test analysis notification sent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/test-risk")
async def send_test_risk(admin_token: str = Depends(verify_admin_token)):
    """Send a test risk alert notification - Requires admin authentication."""
    if not notification_manager.telegram.enabled:
        raise HTTPException(
            status_code=400,
            detail="Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID",
        )

    success = notification_manager.notify_risk(
        timeframe="15min",
        reason="Account risk exceeds maximum",
        account_risk_pct=3.5,
        recommendation="WAIT",
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send notification")

    return {
        "message": "Test risk alert notification sent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/test-system")
async def send_test_system(admin_token: str = Depends(verify_admin_token)):
    """Send a test system status notification - Requires admin authentication."""
    if not notification_manager.telegram.enabled:
        raise HTTPException(
            status_code=400,
            detail="Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID",
        )

    success = notification_manager.notify_system(
        status="healthy",
        data_age_hours=0.5,
        scheduler_running=True,
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send notification")

    return {
        "message": "Test system status notification sent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/custom")
async def send_custom_notification(
    message: str,
    admin_token: str = Depends(verify_admin_token),
):
    """Send a custom notification message - Requires admin authentication."""
    if not notification_manager.telegram.enabled:
        raise HTTPException(
            status_code=400,
            detail="Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID",
        )

    success = notification_manager.telegram.send_message(message)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send notification")

    return {
        "message": "Custom notification sent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/telegram-setup-guide")
async def get_telegram_setup():
    """Get Telegram bot setup instructions."""
    return {
        "step_1": "Create a Telegram bot via @BotFather",
        "step_1_url": "https://t.me/BotFather",
        "step_2": "Get your Chat ID via @userinfobot or by sending a message to your bot",
        "step_2_url": "https://t.me/userinfobot",
        "step_3": "Set environment variables",
        "step_3_windows": "setx TELEGRAM_BOT_TOKEN your_bot_token\nsetx TELEGRAM_CHAT_ID your_chat_id",
        "step_3_linux": "export TELEGRAM_BOT_TOKEN=your_bot_token\nexport TELEGRAM_CHAT_ID=your_chat_id",
        "step_4": "Restart backend to load new environment variables",
        "step_5": "Send test notifications via /api/v1/notifications/test-signal",
        "note": "Chat ID can be negative (for channels) or positive (for private messages)",
    }
