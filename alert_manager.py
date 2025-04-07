import time
from datetime import datetime

class AlertCondition:
    """Class representing a stock alert condition."""
    
    # Alert types
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_CHANGE_ABOVE = "percent_change_above"
    PERCENT_CHANGE_BELOW = "percent_change_below"
    VOLUME_ABOVE = "volume_above"
    BREAKOUT = "breakout"
    
    def __init__(self, symbol, alert_type, threshold, name=None, expiry=None):
        """
        Initialize an alert condition.
        
        Args:
            symbol (str): Stock symbol to monitor
            alert_type (str): Type of alert condition
            threshold (float): Threshold value to trigger the alert
            name (str): Optional name for the alert
            expiry (int): Optional timestamp when this alert expires
        """
        self.symbol = symbol
        self.alert_type = alert_type
        self.threshold = threshold
        self.name = name or f"{symbol} {alert_type} {threshold}"
        self.expiry = expiry
        self.created_at = int(time.time())
        self.triggered = False
        self.last_triggered = None
        self.id = f"{symbol}_{alert_type}_{int(time.time())}"
    
    def check(self, stock_data):
        """
        Check if the alert condition is met.
        
        Args:
            stock_data (dict): Stock data to check against
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        if self.triggered and not self._can_retrigger():
            return False
            
        if self.is_expired():
            return False
            
        current_price = stock_data.get('price') or stock_data.get('current_price')
        previous_price = stock_data.get('previous_price')
        percent_change = stock_data.get('pct_change')
        volume = stock_data.get('volume')
        
        triggered = False
        
        if self.alert_type == self.PRICE_ABOVE and current_price is not None:
            triggered = current_price > self.threshold
            
        elif self.alert_type == self.PRICE_BELOW and current_price is not None:
            triggered = current_price < self.threshold
            
        elif self.alert_type == self.PERCENT_CHANGE_ABOVE and percent_change is not None:
            triggered = percent_change > self.threshold
            
        elif self.alert_type == self.PERCENT_CHANGE_BELOW and percent_change is not None:
            triggered = percent_change < self.threshold
            
        elif self.alert_type == self.VOLUME_ABOVE and volume is not None:
            triggered = volume > self.threshold
            
        elif self.alert_type == self.BREAKOUT:
            breakout_pct = stock_data.get('breakout_pct')
            if breakout_pct is not None:
                triggered = abs(breakout_pct) > self.threshold
        
        if triggered:
            self.triggered = True
            self.last_triggered = int(time.time())
            
        return triggered
    
    def is_expired(self):
        """Check if the alert has expired."""
        if self.expiry is None:
            return False
        return int(time.time()) > self.expiry
    
    def _can_retrigger(self):
        """Check if the alert can be triggered again."""
        # By default, don't retrigger within 1 hour
        return self.last_triggered is None or (int(time.time()) - self.last_triggered) > 3600
    
    def to_dict(self):
        """Convert alert to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'alert_type': self.alert_type,
            'threshold': self.threshold,
            'name': self.name,
            'expiry': self.expiry,
            'created_at': self.created_at,
            'triggered': self.triggered,
            'last_triggered': self.last_triggered
        }


class AlertManager:
    """
    Manages stock price alerts and notifications.
    """
    
    def __init__(self):
        """Initialize the alert manager."""
        self.alerts = {}  # Map of alert IDs to AlertCondition objects
        self.triggered_alerts = []  # List of recently triggered alerts
        self.max_triggered_history = 100  # Maximum number of triggered alerts to keep
    
    def add_alert(self, symbol, alert_type, threshold, name=None, expiry=None):
        """
        Add a new alert.
        
        Args:
            symbol (str): Stock symbol to monitor
            alert_type (str): Type of alert condition
            threshold (float): Threshold value to trigger the alert
            name (str): Optional name for the alert
            expiry (int): Optional timestamp when this alert expires
            
        Returns:
            str: ID of the new alert
        """
        alert = AlertCondition(symbol, alert_type, threshold, name, expiry)
        self.alerts[alert.id] = alert
        return alert.id
    
    def remove_alert(self, alert_id):
        """
        Remove an alert.
        
        Args:
            alert_id (str): ID of the alert to remove
            
        Returns:
            bool: True if alert was removed, False otherwise
        """
        if alert_id in self.alerts:
            alert = self.alerts.pop(alert_id)
            return True
        return False
    
    def check_alerts(self, stocks_data):
        """
        Check all alerts against current stock data.
        
        Args:
            stocks_data (dict): Map of stock symbols to their current data
            
        Returns:
            list: List of triggered alerts
        """
        triggered = []
        current_time = int(time.time())
        
        # Remove expired alerts
        expired_ids = [aid for aid, alert in self.alerts.items() if alert.is_expired()]
        for aid in expired_ids:
            del self.alerts[aid]
        
        # Check each alert
        for alert_id, alert in list(self.alerts.items()):
            stock_data = stocks_data.get(alert.symbol)
            if stock_data:
                if alert.check(stock_data):
                    triggered_info = {
                        'alert': alert.to_dict(),
                        'timestamp': current_time,
                        'datetime': datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S'),
                        'stock_data': stock_data
                    }
                    triggered.append(triggered_info)
                    self.triggered_alerts.append(triggered_info)
        
        # Trim triggered alerts history
        if len(self.triggered_alerts) > self.max_triggered_history:
            self.triggered_alerts = self.triggered_alerts[-self.max_triggered_history:]
        
        return triggered
    
    def get_alerts_for_symbol(self, symbol):
        """
        Get all alerts for a specific symbol.
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            list: List of alerts for the given symbol
        """
        return [alert for alert in self.alerts.values() if alert.symbol == symbol]
    
    def get_alert(self, alert_id):
        """
        Get an alert by ID.
        
        Args:
            alert_id (str): Alert ID
            
        Returns:
            AlertCondition: Alert object if found, None otherwise
        """
        return self.alerts.get(alert_id)
    
    def get_all_alerts(self):
        """
        Get all active alerts.
        
        Returns:
            list: List of all active alerts
        """
        return list(self.alerts.values())
    
    def get_triggered_alerts(self, limit=10):
        """
        Get recently triggered alerts.
        
        Args:
            limit (int): Maximum number of alerts to return
            
        Returns:
            list: List of recently triggered alerts
        """
        return self.triggered_alerts[-limit:] if self.triggered_alerts else []
