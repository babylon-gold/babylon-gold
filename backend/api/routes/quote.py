"""Live Gold API spot quote endpoint."""
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from core.config import settings
from core.models import GoldQuote

router = APIRouter()


def _quote_path() -> Path:
    return Path(settings.LIVE_DATA_DIR) / "XAUUSD_latest_quote.json"


@router.get("/quote", response_model=GoldQuote)
async def get_quote() -> GoldQuote:
    """Return the latest validated Gold API spot reference quote."""
    path = _quote_path()
    if not path.exists():
        raise HTTPException(status_code=404, detail="Live quote is not available")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        quote = GoldQuote.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=f"Live quote is invalid: {exc}") from exc

    if quote.symbol.upper() != "XAU" or quote.currency.upper() != "USD":
        raise HTTPException(status_code=503, detail="Live quote has an unexpected instrument")

    if quote.stale or quote.age_seconds > settings.QUOTE_STALE_SECONDS:
        raise HTTPException(status_code=503, detail="Live quote is stale")

    return quote
