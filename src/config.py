"""
Configuration settings for the Pokemon Monitor
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

load_dotenv()

# Target configuration
TARGET_URL = "https://www.pokemoncenter.com/search/destined-rivals-etb"
TARGET_EMAIL = "adamdand@telus.net"
PRODUCT_ID = "100-10653"
PRODUCT_NAME = "Pokémon TCG: Scarlet & Violet-Destined Rivals Pokémon Center Elite Trainer Box"

# Email configuration
SMTP_SERVERS = {
    "gmail": {"server": "smtp.gmail.com", "port": 587},
    "outlook": {"server": "smtp-mail.outlook.com", "port": 587},
    "yahoo": {"server": "smtp.mail.yahoo.com", "port": 587},
}

# Get email settings from environment
FROM_EMAIL: Optional[str] = os.getenv("FROM_EMAIL")
EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "gmail").lower()

# Get SMTP settings based on provider
SMTP_CONFIG = SMTP_SERVERS.get(EMAIL_PROVIDER, SMTP_SERVERS["gmail"])
SMTP_SERVER = SMTP_CONFIG["server"]
SMTP_PORT = SMTP_CONFIG["port"]

# Request settings
REQUEST_TIMEOUT = 30
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Logging configuration
LOG_FILE = LOGS_DIR / "pokemon_monitor.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Schedule settings
CHECK_TIME = "00:00"  # Midnight