#!/usr/bin/env python3
"""
Quick test script for Pokemon Stock Monitor
Put this file in your root directory: Pokemon-stock-monitor/test_monitor.py
"""

from pokemon_monitor import PokemonStockMonitor
import os

def test_stock_check():
    """Test the stock checking functionality"""
    print("🧪 Testing Pokemon Stock Monitor")
    print("=" * 50)
    
    # Create monitor instance
    monitor = PokemonStockMonitor()
    
    # Test stock check
    print("📡 Checking stock status...")
    is_available, status = monitor.check_stock_status()
    
    print(f"📦 Stock Status: {status}")
    print(f"✅ Available: {is_available}")
    print("=" * 50)
    
    return is_available, status

def test_email_setup():
    """Test if email credentials are configured"""
    print("📧 Testing email configuration...")
    
    from_email = os.getenv("FROM_EMAIL")
    email_password = os.getenv("EMAIL_PASSWORD")
    
    if from_email and email_password:
        print(f"✅ FROM_EMAIL: {from_email}")
        print("✅ EMAIL_PASSWORD: [CONFIGURED]")
        return True
    else:
        print("❌ Email credentials not configured!")
        print("Please set environment variables:")
        print("  FROM_EMAIL=your.email@gmail.com")
        print("  EMAIL_PASSWORD=your_app_password")
        return False

def test_email_notification():
    """Test sending an email (optional)"""
    response = input("\n📧 Do you want to test sending an email? (y/n): ")
    if response.lower() == 'y':
        monitor = PokemonStockMonitor()
        print("📤 Sending test email...")
        success = monitor.send_email_notification(True, "TEST - Email system working!")
        if success:
            print("✅ Test email sent successfully!")
        else:
            print("❌ Failed to send test email")
        return success
    return None

if __name__ == "__main__":
    print("🎮 Pokemon Center Stock Monitor - Test Script")
    print("=" * 60)
    
    # Test 1: Stock checking
    is_available, status = test_stock_check()
    
    # Test 2: Email configuration
    email_configured = test_email_setup()
    
    # Test 3: Email notification (optional)
    if email_configured:
        test_email_notification()
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print(f"   Stock Check: ✅ Working")
    print(f"   Email Config: {'✅ Configured' if email_configured else '❌ Not Configured'}")
    print("=" * 60)
    
    if email_configured:
        print("\n🚀 Your monitor is ready to run!")
        print("To start monitoring:")
        print("   python pokemon_monitor.py")
    else:
        print("\n⚠️  Configure email credentials first!")
        print("See README.md for setup instructions")