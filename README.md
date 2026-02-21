# Pokemon Center Stock Monitor

# # Automated monitoring system for Pokemon Center Elite Trainer Box availability with email notifications.

You will need to change out the email for yours, see /src/config.py for these changable properties:
TARGET_URL = "https://www.pokemoncenter.com/search/destined-rivals-etb"
TARGET_EMAIL = "Your email here"
PRODUCT_ID = "100-10653"
PRODUCT_NAME = "Pokémon TCG: Scarlet & Violet-Destined Rivals Pokémon Center Elite Trainer Box"

Also need an .env file with the following properties to send the auto emails.
FROM_EMAIL=.....
EMAIL_PASSWORD=....
EMAIL_PROVIDER=.....

# # Learnings:

1. Had to open the url slowly, or else already got flagged as bot
2. Had to slow down speed of crawling to not appear as a bot
3. Had to automatically click "I am not a robot.."
4. Started solving the picture recapchas, But then my IP address

## Features

- 🔍 **Automated Stock Monitoring** - Checks daily at midnight
- 📧 **Email Notifications** - Instant alerts when stock status changes
- 🛡️ **Robust Error Handling** - Handles network issues gracefully
- 📊 **Detailed Logging** - Complete activity tracking
- 🧪 **Test Mode** - Verify setup before going live
- ⚙️ **VS Code Integration** - Full development environment setup

## Quick Start

### 1. Clone and Setup

```bash
# Create project directory
mkdir pokemon-stock-monitor
cd pokemon-stock-monitor

# Copy all the files from this setup into the directory
# Set up virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install selenium
pip install webdriver-manager

# to run:
python src/pokemon_monitor.py
```
