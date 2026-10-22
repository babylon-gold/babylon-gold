"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List, Literal


class Settings(BaseSettings):
    """Application settings."""
    # App
    APP_NAME: str = "Babylon AI Gold Intelligence"
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://babylon-gold.vercel.app",
    ]

    # Data paths
    DATA_DIR: str = "../BabylonAI_Gold_Data_Starter/data"
    DEMO_DATA_DIR: str = "../BabylonAI_Gold_Data_Starter/data/demo"
    LIVE_DATA_DIR: str = "../BabylonAI_Gold_Data_Starter/data/live"
    QUOTE_STALE_SECONDS: int = 1800
    # Keep demo data as the safe default. Set DATA_MODE=live explicitly when
    # validated Twelve Data files should be loaded instead.
    DATA_MODE: Literal["demo", "live"] = "demo"

    # Signal configuration
    WATCH_THRESHOLD: float = 0.5  # Watch signal threshold
    CONFIRMED_THRESHOLD: float = 0.7  # Confirmed signal threshold
    RISK_BLOCK_THRESHOLD: float = 0.3  # Risk block threshold

    # Indicator periods (EMA, RSI, ATR, ADX)
    EMA_SHORT: int = 20
    EMA_MEDIUM: int = 50
    EMA_LONG: int = 200
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: float = 70.0
    RSI_OVERSOLD: float = 30.0
    ATR_PERIOD: int = 14
    ADX_PERIOD: int = 14
    ADX_STRONG: float = 25.0

    # Risk management
    MAX_POSITION_SIZE: float = 10.0  # % of account
    MAX_LOSS_PER_TRADE: float = 2.0  # % of account
    DEFAULT_STOP_LOSS_PIPS: float = 50.0  # pips
    DEFAULT_TAKE_PROFIT_PIPS: float = 100.0  # pips

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
