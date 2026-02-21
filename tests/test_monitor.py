"""
Tests for the Pokemon Monitor
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from src.pokemon_monitor import PokemonStockMonitor
from src.email_sender import EmailSender


class TestPokemonStockMonitor:
    """Test cases for PokemonStockMonitor"""

    def setup_method(self):
        """Set up test fixtures"""
        self.monitor = PokemonStockMonitor()

    @patch('src.pokemon_monitor.requests.Session.get')
    def test_check_stock_status_sold_out(self, mock_get):
        """Test checking stock status when product is sold out"""
        # Mock HTML response with sold out product
        mock_response = Mock()
        mock_response.content = '''
        <html>
            <a href="/product/100-10653/pokemon-tcg-scarlet-and-violet-destined-rivals-pokemon-center-elite-trainer-box">
                <div class="product-image-oos--Lae0t">SOLD OUT</div>
            </a>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        is_available, status = self.monitor.check_stock_status()
        
        assert not is_available
        assert status == "SOLD OUT"

    @patch('src.pokemon_monitor.requests.Session.get')
    def test_check_stock_status_in_stock(self, mock_get):
        """Test checking stock status when product is in stock"""
        # Mock HTML response without sold out div
        mock_response = Mock()
        mock_response.content = '''
        <html>
            <a href="/product/100-10653/pokemon-tcg-scarlet-and-violet-destined-rivals-pokemon-center-elite-trainer-box">
                <div class="product-image">Product Image</div>
            </a>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        is_available, status = self.monitor.check_stock_status()
        
        assert is_available
        assert status == "IN STOCK"

    @patch('src.pokemon_monitor.requests.Session.get')
    def test_check_stock_status_product_not_found(self, mock_get):
        """Test checking stock status when product is not found"""
        mock_response = Mock()
        mock_response.content = '<html><body>No products found</body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        is_available, status = self.monitor.check_stock_status()
        
        assert not is_available
        assert status == "Product not found on page"

    @patch('src.pokemon_monitor.requests.Session.get')
    def test_check_stock_status_network_error(self, mock_get):
        """Test handling of network errors"""
        mock_get.side_effect = requests.RequestException("Network error")

        is_available, status = self.monitor.check_stock_status()
        
        assert not is_available
        assert "Error checking stock" in status


class TestEmailSender:
    """Test cases for EmailSender"""

    def setup_method(self):
        """Set up test fixtures"""
        self.email_sender = EmailSender()

    @patch('src.email_sender.FROM_EMAIL', 'test@example.com')
    @patch('src.email_sender.EMAIL_PASSWORD', 'password123')
    def test_is_configured_true(self):
        """Test email configuration check when properly configured"""
        sender = EmailSender()
        assert sender.is_configured()

    @patch('src.email_sender.FROM_EMAIL', None)
    @patch('src.email_sender.EMAIL_PASSWORD', None)
    def test_is_configured_false(self):
        """Test email configuration check when not configured"""
        sender = EmailSender()
        assert not sender.is_configured()

    @patch('src.email_sender.smtplib.SMTP')
    @patch('src.email_sender.FROM_EMAIL', 'test@example.com')
    @patch('src.email_sender.EMAIL_PASSWORD', 'password123')
    def test_send_notification_success(self, mock_smtp):
        """Test successful email notification"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        sender = EmailSender()
        result = sender.send_notification(True, "IN STOCK")
        
        assert result is True
        mock_server.send_message.assert_called_once()

    def test_send_notification_not_configured(self):
        """Test email notification when not configured"""
        sender = EmailSender()
        sender.from_email = None
        sender.password = None
        
        result = sender.send_notification(True, "IN STOCK")
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])