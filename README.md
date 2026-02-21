# Pokemon Center Stock Monitor

Automated monitoring system for Pokemon Center Elite Trainer Box availability with email notifications.

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

# to run:
python src/pokemon_monitor.py
```
