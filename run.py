#!/usr/bin/env python3
"""
Main entry point for the Pokemon Center Stock Monitor
"""
import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from {env_file}")
    else:
        print(f"⚠️  No .env file found at {env_file}")
        print("Create a .env file based on .env.example for configuration")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# Import and run the monitor
try:
    from pokemon_monitor import main
    
    if __name__ == "__main__":
        print("🎮 Pokemon Center Stock Monitor")
        print("=" * 50)
        main()
        
except ImportError as e:
    print(f"❌ Error importing pokemon_monitor: {e}")
    print("Make sure you've installed all dependencies with: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error running monitor: {e}")
    sys.exit(1)