import requests
from bs4 import BeautifulSoup
import schedule
import time
import logging
import sys
from datetime import datetime
from typing import Tuple
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    PRODUCT_ID,
    PRODUCT_NAME,
    REQUEST_TIMEOUT,
    REQUEST_HEADERS,
    CHECK_TIME,
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL,
)
from email_sender import EmailSender

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
    """Main class for monitoring Pokemon Center stock using Selenium"""

    def __init__(self):
        self.driver = None
        self.email_sender = EmailSender()
        logger.info("Pokemon Stock Monitor initialized")

    def setup_driver(self):
        """Set up Chrome driver with appropriate options for Chrome Driver 137"""
        try:
            chrome_options = Options()
            
            # Enhanced anti-detection measures for Incapsula/Imperva
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Additional stealth options
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')  # Faster loading
            chrome_options.add_argument('--disable-javascript')  # May help with some detection
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            
            # Set realistic window size
            chrome_options.add_argument('--window-size=1366,768')
            
            # Optional: Run in headless mode (uncomment if you don't want to see the browser)
            # chrome_options.add_argument('--headless')
            
            # Use a more common user agent string
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Disable logging to reduce noise
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--log-level=3')
            
            # Add proxy rotation capability (optional - you can add your own proxy here)
            # chrome_options.add_argument('--proxy-server=your-proxy-server:port')
            
            logger.info("Setting up ChromeDriver 137...")
            
            try:
                # Clear webdriver-manager cache first to ensure we get the latest driver
                import os
                import shutil
                cache_dir = os.path.expanduser('~/.wdm')
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                    logger.info("Cleared webdriver-manager cache")
            except Exception as e:
                logger.warning(f"Could not clear cache: {e}")
            
            try:
                # Force download ChromeDriver 137 using webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                
                # Specify Chrome version 137 explicitly
                driver_path = ChromeDriverManager(version="137.0.6738.0").install()
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info(f"Successfully set up ChromeDriver 137 from webdriver-manager: {driver_path}")
                
            except Exception as e:
                logger.warning(f"Automatic ChromeDriver 137 setup failed: {e}")
                logger.info("Attempting manual ChromeDriver 137 setup...")
                
                # Manual setup instructions for Chrome Driver 137
                logger.info("Manual setup required:")
                logger.info("1. Go to: https://googlechromelabs.github.io/chrome-for-testing/#stable")
                logger.info("2. Download ChromeDriver 137.x.x.x for your platform")
                logger.info("3. Extract chromedriver to one of the following locations:")
                
                # Try manual paths as fallback
                manual_paths = [
                    r'C:\chromedriver\chromedriver.exe',  # Windows
                    r'C:\Program Files\chromedriver\chromedriver.exe',  # Windows alternative
                    r'./chromedriver.exe',  # Current directory Windows
                    '/usr/local/bin/chromedriver',  # Linux/Mac
                    '/usr/bin/chromedriver',  # Linux alternative
                    './chromedriver'  # Current directory Unix
                ]
                
                for path in manual_paths:
                    logger.info(f"   - {path}")
                    if os.path.exists(path):
                        logger.info(f"Found ChromeDriver at: {path}")
                        service = Service(path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        logger.info("Successfully set up ChromeDriver 137 with manual path")
                        break
                else:
                    # Try to use system PATH
                    try:
                        service = Service()  # Will use chromedriver from PATH
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        logger.info("Successfully set up ChromeDriver 137 from system PATH")
                    except Exception as path_error:
                        logger.error(f"All ChromeDriver setup methods failed. Last error: {path_error}")
                        raise e
            
            # Execute multiple scripts to hide webdriver properties
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("delete navigator.__proto__.webdriver")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            # Set additional navigator properties to appear more human-like
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});
                Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            """)
            
            # Verify driver version
            try:
                capabilities = self.driver.capabilities
                browser_version = capabilities.get('browserVersion', 'Unknown')
                driver_version = capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown')
                logger.info(f"Chrome version: {browser_version}")
                logger.info(f"ChromeDriver version: {driver_version}")
            except Exception as e:
                logger.warning(f"Could not retrieve version info: {e}")
            
            logger.info("Chrome driver 137 set up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set up Chrome driver 137: {e}")
            logger.error("Please ensure you have Chrome 137+ installed and ChromeDriver 137 available")
            return False

    def close_driver(self):
        """Close the Chrome driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome driver closed")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")

    def handle_security_challenge(self) -> bool:
        """
        Handle Incapsula/Imperva security challenges
        """
        try:
            # Check if we're on a security challenge page
            page_source = self.driver.page_source.lower()
            
            # Look for Incapsula indicators
            incapsula_indicators = [
                'incapsula',
                'imperva', 
                'incident id',
                'request unsuccessful',
                'additional security check',
                'main-iframe'
            ]
            
            is_security_page = any(indicator in page_source for indicator in incapsula_indicators)
            
            if is_security_page:
                logger.warning("Detected security challenge page (Incapsula/Imperva)")
                
                # Try waiting for the page to resolve automatically
                logger.info("Waiting for security challenge to resolve...")
                
                max_wait_time = 30  # seconds
                wait_interval = 2   # seconds
                waited = 0
                
                while waited < max_wait_time:
                    time.sleep(wait_interval)
                    waited += wait_interval
                    
                    # Check if we've been redirected to the actual page
                    current_url = self.driver.current_url
                    new_page_source = self.driver.page_source.lower()
                    
                    # If we're no longer on a security page, we're good
                    if not any(indicator in new_page_source for indicator in incapsula_indicators):
                        logger.info(f"Security challenge resolved after {waited} seconds")
                        return True
                    
                    # Look for iframe and try to handle it
                    try:
                        iframe = self.driver.find_element(By.ID, "main-iframe")
                        if iframe:
                            logger.info("Found main iframe, switching to it...")
                            self.driver.switch_to.frame(iframe)
                            time.sleep(2)
                            # Switch back to main content
                            self.driver.switch_to.default_content()
                    except:
                        pass
                    
                    logger.info(f"Still on security page... waited {waited}/{max_wait_time} seconds")
                
                logger.warning(f"Security challenge did not resolve after {max_wait_time} seconds")
                return False
            
            return True  # No security challenge detected
            
        except Exception as e:
            logger.error(f"Error handling security challenge: {e}")
            return False

    def navigate_with_retry(self, url: str, max_retries: int = 3) -> bool:
        """
        Navigate to URL with retry logic, random delays, and security challenge handling
        """
        for attempt in range(max_retries):
            try:
                # Random delay between requests (longer delays to appear more human)
                if attempt > 0:
                    delay = random.uniform(10, 20)  # Increased delay
                    logger.info(f"Retrying after {delay:.1f} seconds...")
                    time.sleep(delay)
                
                logger.info(f"Navigating to {url} (attempt {attempt + 1})")
                self.driver.get(url)
                
                # Wait for initial page load
                WebDriverWait(self.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                # Handle security challenges
                if not self.handle_security_challenge():
                    logger.warning(f"Failed to handle security challenge on attempt {attempt + 1}")
                    continue
                
                # Additional wait for dynamic content
                time.sleep(random.uniform(3, 6))
                
                # Check if we got a valid page
                current_page = self.driver.page_source
                if len(current_page) > 1000 and "pokemon" in current_page.lower():
                    logger.info(f"Successfully loaded Pokemon page: {self.driver.title}")
                    return True
                else:
                    logger.warning(f"Page may not have loaded properly or still blocked")
                    
            except TimeoutException:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except WebDriverException as e:
                logger.warning(f"WebDriver exception on attempt {attempt + 1}: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")
                
            if attempt == max_retries - 1:
                logger.error(f"Failed to load page after {max_retries} attempts")
                return False
        
        return False

    def check_stock_status(self) -> Tuple[bool, str]:
        """
        Check if the Elite Trainer Box is in stock using Selenium
        
        Returns:
            Tuple[bool, str]: (is_available, status_message)
        """
        try:
            # Set up driver if not already done
            if not self.driver:
                if not self.setup_driver():
                    return False, "Failed to set up browser"
            
            # First, try visiting the main site to establish a session
            logger.info("Establishing session with main site...")
            try:
                self.driver.get("https://www.pokemoncenter.com")
                time.sleep(random.uniform(5, 8))
                
                # Handle any security challenges on main page
                self.handle_security_challenge()
            except Exception as e:
                logger.warning(f"Could not establish session with main site: {e}")
            
            # Navigate to the product page
            target_url = f"https://www.pokemoncenter.com/product/{PRODUCT_ID}/pokemon-tcg-scarlet-and-violet-destined-rivals-pokemon-center-elite-trainer-box"
            
            if not self.navigate_with_retry(target_url):
                return False, "Failed to load product page"
            
            # Add a longer delay to let dynamic content load
            time.sleep(random.uniform(5, 8))
            
            # Save page source for debugging
            debug_file = LOG_FILE.parent / "debug_page_selenium.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info(f"Page source saved to {debug_file}")
            
            # Check if we're still on a security/blocked page
            page_source_lower = self.driver.page_source.lower()
            blocked_indicators = [
                'incapsula',
                'imperva',
                'incident id',
                'request unsuccessful',
                'additional security check',
                'security challenge',
                'blocked'
            ]
            
            if any(indicator in page_source_lower for indicator in blocked_indicators):
                logger.error("Still blocked by security system after navigation attempts")
                return False, "BLOCKED BY SECURITY"
            
            # Check if we actually reached the product page
            if not any(term in page_source_lower for term in ['pokemon', 'elite trainer', 'add to cart', 'product']):
                logger.error("Did not reach actual product page")
                return False, "FAILED TO REACH PRODUCT PAGE"
            
            # Now proceed with stock checking methods...
            # Method 1: Look for the "Unavailable" button
            try:
                unavailable_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Unavailable') or contains(@aria-label, 'Unavailable')]"))
                )
                if unavailable_button:
                    logger.info("Found 'Unavailable' button - Product is SOLD OUT")
                    return False, "SOLD OUT"
            except TimeoutException:
                logger.info("No 'Unavailable' button found")
            
            # Method 2: Look for disabled add-to-cart button
            try:
                disabled_button = self.driver.find_element(By.XPATH, "//button[@disabled and (contains(text(), 'Add') or contains(@class, 'add-to-cart'))]")
                if disabled_button:
                    button_text = disabled_button.text.strip()
                    logger.info(f"Found disabled add-to-cart button: '{button_text}' - Product is SOLD OUT")
                    return False, "SOLD OUT"
            except:
                logger.info("No disabled add-to-cart button found")
            
            # Method 3: Look for enabled add-to-cart button
            try:
                add_to_cart_selectors = [
                    "//button[contains(@class, 'add-to-cart') and not(@disabled)]",
                    "//button[contains(text(), 'Add to Cart') and not(@disabled)]",
                    "//button[contains(text(), 'Add to Bag') and not(@disabled)]",
                    "//button[@data-testid='add-to-cart-button' and not(@disabled)]"
                ]
                
                for selector in add_to_cart_selectors:
                    try:
                        add_to_cart_button = self.driver.find_element(By.XPATH, selector)
                        if add_to_cart_button and add_to_cart_button.is_enabled():
                            button_text = add_to_cart_button.text.strip()
                            logger.info(f"Found enabled add-to-cart button: '{button_text}' - Product appears to be IN STOCK")
                            return True, "IN STOCK"
                    except:
                        continue
                        
            except:
                logger.info("No enabled add-to-cart button found")
            
            # Method 4: Check for out-of-stock text indicators
            out_of_stock_indicators = [
                "out of stock",
                "sold out", 
                "unavailable",
                "notify me when available",
                "email me when back in stock"
            ]
            
            for indicator in out_of_stock_indicators:
                if indicator in page_source_lower:
                    logger.info(f"Found out-of-stock indicator in page text: '{indicator}' - Product is SOLD OUT")
                    return False, "SOLD OUT"
            
            # Method 5: Look for specific product availability elements
            try:
                # Check for any availability indicators
                availability_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'availability') or contains(@class, 'stock') or contains(@data-testid, 'stock')]")
                for element in availability_elements:
                    element_text = element.text.lower()
                    if any(indicator in element_text for indicator in out_of_stock_indicators):
                        logger.info(f"Found stock indicator element: '{element_text}' - Product is SOLD OUT")
                        return False, "SOLD OUT"
            except:
                pass
            
            # Log all buttons found for debugging
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                logger.info(f"Found {len(all_buttons)} buttons on page")
                for i, button in enumerate(all_buttons[:10]):  # Log first 10 buttons
                    try:
                        button_text = button.text.strip()
                        button_classes = button.get_attribute("class")
                        is_disabled = not button.is_enabled()
                        logger.info(f"Button {i+1}: '{button_text}' (classes: {button_classes}, disabled: {is_disabled})")
                    except:
                        continue
            except:
                pass
            
            # If we reach here and haven't found clear out-of-stock indicators, assume it's available
            logger.info("No clear out-of-stock indicators found - assuming product is IN STOCK")
            return True, "Status unclear - assumed IN STOCK"

        except Exception as e:
            logger.error(f"Unexpected error during stock check: {e}")
            return False, f"Error checking stock: {e}"

    def check_alternative_method(self) -> Tuple[bool, str]:
        """
        Alternative method using different selectors or approaches
        """
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False, "Failed to set up browser"
            
            # Try a different approach - look for specific Pokemon Center elements
            product_url = f"https://www.pokemoncenter.com/product/{PRODUCT_ID}/pokemon-tcg-scarlet-and-violet-destined-rivals-pokemon-center-elite-trainer-box"
            
            if not self.navigate_with_retry(product_url):
                return False, "Failed to load product page"
                
            # Wait for dynamic content
            time.sleep(3)
            
            # Try to find the product container
            try:
                product_container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='product-details']"))
                )
                logger.info("Found product details container")
            except TimeoutException:
                logger.warning("Could not find product details container")
            
            # Look for purchase options
            try:
                purchase_section = self.driver.find_element(By.CSS_SELECTOR, "[class*='product-add'], [class*='purchase'], [class*='buy-box']")
                if purchase_section:
                    # Check if there's an enabled add to cart button in this section
                    add_button = purchase_section.find_element(By.TAG_NAME, "button")
                    if add_button and add_button.is_enabled() and "add" in add_button.text.lower():
                        logger.info("Found enabled add to cart button in purchase section - IN STOCK")
                        return True, "IN STOCK" 
                    elif not add_button.is_enabled():
                        logger.info("Found disabled button in purchase section - SOLD OUT")
                        return False, "SOLD OUT"
            except:
                logger.info("Could not find purchase section")
            
            # Default assumption
            logger.info("Alternative method could not determine stock status clearly")
            return True, "Status unknown - assumed IN STOCK"
            
        except Exception as e:
            logger.error(f"Alternative method failed: {e}")
            return False, f"Error with alternative method: {e}"

    def run_daily_check(self):
        """Run the daily stock check and send notification"""
        logger.info("=" * 50)
        logger.info("Starting daily Pokemon Center stock check with Selenium (ChromeDriver 137)")

        try:
            # Try primary method first
            is_available, status_message = self.check_stock_status()
            
            # Send email notification
            email_sent = self.email_sender.send_notification(is_available, status_message)

            if email_sent:
                logger.info("Daily check completed successfully")
            else:
                logger.error("Daily check completed but email failed to send")
                
        except Exception as e:
            logger.error(f"Error during daily check: {e}")
            # Try to send error notification
            self.email_sender.send_notification(False, f"Error during check: {e}")
        
        finally:
            # Always close the driver after each check to free resources
            self.close_driver()
            self.driver = None

        logger.info("=" * 50)

    def run_test_check(self):
        """Run a single test check without scheduling"""
        logger.info("Running test stock check with Selenium (ChromeDriver 137)...")
        
        try:
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
                
        except Exception as e:
            logger.error(f"Error during test check: {e}")
            return False
        finally:
            # Always close the driver
            self.close_driver()

    def start_scheduler(self):
        """Start the daily scheduler"""
        if not self.email_sender.is_configured():
            logger.error("Email credentials not configured!")
            logger.error("Please set FROM_EMAIL and EMAIL_PASSWORD environment variables")
            return False

        # Schedule daily check
        schedule.every().day.at(CHECK_TIME).do(self.run_daily_check)
        
        logger.info(f"Scheduler set up - will check daily at {CHECK_TIME} using ChromeDriver 137")
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
            self.close_driver()
            return True


def main():
    """Main entry point for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pokemon Center Stock Monitor (ChromeDriver 137)")
    parser.add_argument("--test", action="store_true", help="Run a single test check")
    args = parser.parse_args()
    
    monitor = PokemonStockMonitor()
    
    try:
        if args.test:
            success = monitor.run_test_check()
            sys.exit(0 if success else 1)
        else:
            monitor.start_scheduler()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        monitor.close_driver()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        monitor.close_driver()
        sys.exit(1)


if __name__ == "__main__":
    main()