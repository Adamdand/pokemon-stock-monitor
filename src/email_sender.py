"""
Email notification functionality
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Tuple

from config import (
    FROM_EMAIL,
    EMAIL_PASSWORD,
    TARGET_EMAIL,
    SMTP_SERVER,
    SMTP_PORT,
    PRODUCT_NAME,
    PRODUCT_ID,
)

logger = logging.getLogger(__name__)


class EmailSender:
    """Handles email notifications for stock status"""

    def __init__(self):
        self.from_email = FROM_EMAIL
        self.password = EMAIL_PASSWORD
        self.target_email = TARGET_EMAIL

    def is_configured(self) -> bool:
        """Check if email credentials are properly configured"""
        return bool(self.from_email and self.password)

    def send_notification(self, is_available: bool, status_message: str) -> bool:
        """
        Send email notification about stock status
        
        Args:
            is_available: Whether the product is in stock
            status_message: Status description
            
        Returns:
            bool: True if email was sent successfully
        """
        if not self.is_configured():
            logger.error("Email credentials not configured")
            return False

        try:
            msg = self._create_message(is_available, status_message)
            self._send_email(msg)
            logger.info(f"Email notification sent successfully to {self.target_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def _create_message(self, is_available: bool, status_message: str) -> MIMEMultipart:
        """Create email message"""
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = self.target_email
        msg["Subject"] = f"Pokemon Center ETB Stock Alert - {status_message}"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product_url = f"https://www.pokemoncenter.com/product/{PRODUCT_ID}/pokemon-tcg-scarlet-and-violet-destined-rivals-pokemon-center-elite-trainer-box"

        if is_available:
            body = self._create_in_stock_message(timestamp, product_url, status_message)
        else:
            body = self._create_out_of_stock_message(timestamp, product_url, status_message)

        msg.attach(MIMEText(body, "plain"))
        return msg

    def _create_in_stock_message(self, timestamp: str, product_url: str, status_message: str) -> str:
        """Create message for when product is in stock"""
        return f"""
🎉 GOOD NEWS! 🎉

The {PRODUCT_NAME} is currently IN STOCK!

✅ Status: {status_message}
🕒 Checked at: {timestamp}
🔗 Direct link: {product_url}

Hurry up and grab it before it sells out again!

---
Automated Pokemon Center Stock Monitor
        """.strip()

    def _create_out_of_stock_message(self, timestamp: str, product_url: str, status_message: str) -> str:
        """Create message for when product is out of stock"""
        return f"""
📦 Stock Update 📦

The {PRODUCT_NAME} status:

❌ Status: {status_message}
🕒 Checked at: {timestamp}
🔗 Product page: {product_url}

We'll keep monitoring and let you know when it's back in stock!

---
Automated Pokemon Center Stock Monitor
        """.strip()

    def _send_email(self, msg: MIMEMultipart) -> None:
        """Send the email message"""
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(self.from_email, self.password)
            server.send_message(msg)

    def send_test_email(self) -> bool:
        """Send a test email to verify configuration"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = self.target_email
            msg["Subject"] = "Pokemon Monitor - Test Email"

            body = f"""
🧪 Test Email 🧪

This is a test email from your Pokemon Center Stock Monitor.

If you're receiving this, your email configuration is working correctly!

Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
Pokemon Center Stock Monitor Setup Test
            """.strip()

            msg.attach(MIMEText(body, "plain"))
            self._send_email(msg)
            
            logger.info("Test email sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send test email: {e}")
            return False