"""
Main Pokemon Center stock monitoring functionality
"""
import requests
from bs4 import BeautifulSoup
import schedule
import time
import logging
import sys
from datetime import datetime
from typing import Tuple

from config import ( # type: ignore
    TARGET_URL,
    PRODUCT_ID,
    PRODUCT_NAME,
    REQUEST_TIMEOUT,
    REQUEST_HEADERS,
    CHECK_TIME,
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL,
)
from email_sender import EmailSender # type: ignore

# Set up logging
def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)


class PokemonStockMonitor:
    """Main class for monitoring Pokemon Center stock"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        self.email_sender = EmailSender()
        
        logger.info("Pokemon Stock Monitor initialized")

    def check_stock_status(self) -> Tuple[bool, str]:
        """
        Check if the Elite Trainer Box is in stock
        
        Returns:
            Tuple[bool, str]: (is_available, status_message)
        """
        try:
            logger.info(f"Checking stock status at {TARGET_URL}")
            response = self.session.get(TARGET_URL, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Look for the specific product link
            product_link = soup.find(
                "a", 
                href=f"/product/{PRODUCT_ID}/pokemon-tcg-scarlet-and-violet-destined-rivals-pokemon-center-elite-trainer-box"
            )

            if not product_link:
                logger.warning("Product link not found on page")
                return False, "Product not found on page"

            # Check if there's a "SOLD OUT" div within the product link
            sold_out_div = product_link.find("div", class_="product-image-oos--Lae0t")

            if sold_out_div and "SOLD OUT" in sold_out_div.get_text():
                logger.info("Product is SOLD OUT")
                return False, "SOLD OUT"
            else:
                logger.info("Product appears to be IN STOCK")
                return True, "IN STOCK"

        except requests.RequestException as e:
            logger.error(f"Error fetching page: {e}")
            return False, f"Error checking stock: {e}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False, f"Unexpected error: {e}"

    def run_daily_check(self):
        """Run the daily stock check and send notification"""
        logger.info("=" * 50)
        logger.info("Starting daily Pokemon Center stock check")

        is_available, status_message = self.check_stock_status()
        email_sent = self.email_sender.send_notification(is_available, status_message)

        if email_sent:
            logger.info("Daily check completed successfully")
        else:
            logger.error("Daily check completed but email failed to send")

        logger.info("=" * 50)

    def run_test_check(self):
        """Run a single test check without scheduling"""
        logger.info("Running test stock check...")
        
        # Check email configuration first
        if not self.email_sender.is_configured():
            logger.error("Email not configured. Please set FROM_EMAIL and EMAIL_PASSWORD environment variables.")
            return False
        
        # Test email sending
        logger.info("Testing email configuration...")
        if self.email_sender.send_test_email():
            logger.info("✅ Email test successful")
        else:
            logger.error("❌ Email test failed")
            return False
        
        # Check stock status
        is_available, status_message = self.check_stock_status()
        logger.info(f"Stock Status: {status_message} (Available: {is_available})")
        
        # Send stock notification
        if self.email_sender.send_notification(is_available, status_message):
            logger.info("✅ Stock notification sent successfully")
            return True
        else:
            logger.error("❌ Failed to send stock notification")
            return False

    def start_scheduler(self):
        """Start the daily scheduler"""
        if not self.email_sender.is_configured():
            logger.error("Email credentials not configured!")
            logger.error("Please set FROM_EMAIL and EMAIL_PASSWORD environment variables")
            return False

        # Schedule daily check
        schedule.every().day.at(CHECK_TIME).do(self.run_daily_check)
        
        logger.info(f"Scheduler set up - will check daily at {CHECK_TIME}")
        logger.info("Press Ctrl+C to stop the monitor")

        # Run an initial check
        logger.info("Running initial stock check...")
        self.run_daily_check()

        # Keep the script running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled tasks
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
            return True


def main():
    """Main entry point for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pokemon Center Stock Monitor")
    parser.add_argument("--test", action="store_true", help="Run a single test check")
    args = parser.parse_args()
    
    monitor = PokemonStockMonitor()
    
    if args.test:
        success = monitor.run_test_check()
        sys.exit(0 if success else 1)
    else:
        monitor.start_scheduler()


if __name__ == "__main__":
    main()