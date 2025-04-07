import time
from datetime import datetime
import pandas as pd
import numpy as np

from heap import StockMinHeap, StockMaxHeap
from sliding_window import SlidingWindow

class TrendAnalyzer:
    """
    Analyzes stock trends using heap data structures and sliding windows.
    """
    
    def __init__(self, max_size=10, window_size=60):
        """
        Initialize the trend analyzer.
        
        Args:
            max_size (int): Maximum number of stocks to track in each heap
            window_size (int): Size of the sliding window for analysis
        """
        # Heaps for tracking top gainers and losers
        self.gainers_heap = StockMaxHeap(max_size=max_size)
        self.losers_heap = StockMinHeap(max_size=max_size)
        
        # Sliding window for time-based analysis
        self.sliding_window = SlidingWindow(window_size=window_size)
        
        # Time of last update
        self.last_update = None
        
        # Track current metrics
        self.current_metrics = {}
    
    def update(self, symbol, current_price, previous_price, timestamp=None):
        """
        Update the analyzer with new stock data.
        
        Args:
            symbol (str): Stock symbol
            current_price (float): Current stock price
            previous_price (float): Previous stock price for comparison
            timestamp (int): Timestamp of the data point
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        # Calculate percentage change
        if previous_price and previous_price > 0:
            pct_change = ((current_price - previous_price) / previous_price) * 100
        else:
            pct_change = 0
        
        # Update heaps
        self.gainers_heap.push(symbol, pct_change, timestamp)
        self.losers_heap.push(symbol, pct_change, timestamp)
        
        # Update sliding window
        self.sliding_window.update(symbol, current_price, timestamp)
        
        # Update metrics
        self.current_metrics[symbol] = {
            'symbol': symbol,
            'current_price': current_price,
            'previous_price': previous_price,
            'pct_change': pct_change,
            'timestamp': timestamp
        }
        
        self.last_update = timestamp
    
    def update_batch(self, price_data, previous_data=None):
        """
        Update multiple stocks at once.
        
        Args:
            price_data (dict): Current price data for multiple stocks 
                              {symbol: {'price': float, 'timestamp': int}}
            previous_data (dict): Previous price data for comparison
        """
        for symbol, data in price_data.items():
            current_price = data.get('price')
            timestamp = data.get('timestamp')
            
            if current_price is None:
                continue
                
            # Get previous price
            previous_price = None
            if previous_data and symbol in previous_data:
                previous_price = previous_data[symbol].get('price')
            
            # Update with new data
            self.update(symbol, current_price, previous_price, timestamp)
    
    def get_top_gainers(self, n=None):
        """
        Get the top gaining stocks.
        
        Args:
            n (int): Number of top gainers to return
            
        Returns:
            list: List of top gainers
        """
        return self.gainers_heap.get_top(n)
    
    def get_top_losers(self, n=None):
        """
        Get the top losing stocks.
        
        Args:
            n (int): Number of top losers to return
            
        Returns:
            list: List of top losers
        """
        return self.losers_heap.get_top(n)
    
    def get_momentum_stocks(self, n=5):
        """
        Get stocks with the highest momentum (rate of change).
        
        Args:
            n (int): Number of momentum stocks to return
            
        Returns:
            list: List of stocks with highest momentum
        """
        return self.sliding_window.get_top_performers(n, metric='momentum')
    
    def get_highest_volatility(self, n=5):
        """
        Get stocks with the highest volatility.
        
        Args:
            n (int): Number of volatile stocks to return
            
        Returns:
            list: List of stocks with highest volatility
        """
        return self.sliding_window.get_top_performers(n, metric='volatility')
    
    def detect_breakouts(self, threshold_pct=5):
        """
        Detect stocks breaking out (crossing a significant threshold).
        
        Args:
            threshold_pct (float): Percentage threshold for considering a breakout
            
        Returns:
            list: List of stocks in breakout
        """
        metrics = self.sliding_window.calculate_all_metrics()
        breakouts = []
        
        for symbol, data in metrics.items():
            if not data or data.get('insufficient_data', False):
                continue
                
            # Check if current price is significantly higher than the average
            if data['current_price'] > data['avg_price'] * (1 + threshold_pct/100):
                data['breakout_type'] = 'upward'
                data['breakout_pct'] = ((data['current_price'] - data['avg_price']) / data['avg_price']) * 100
                breakouts.append(data)
            
            # Check for downward breakout
            elif data['current_price'] < data['avg_price'] * (1 - threshold_pct/100):
                data['breakout_type'] = 'downward'
                data['breakout_pct'] = ((data['avg_price'] - data['current_price']) / data['avg_price']) * 100
                breakouts.append(data)
        
        return sorted(breakouts, key=lambda x: abs(x.get('breakout_pct', 0)), reverse=True)
    
    def generate_summary_report(self):
        """
        Generate a summary report of current market trends.
        
        Returns:
            dict: Summary report
        """
        top_gainers = self.get_top_gainers(5)
        top_losers = self.get_top_losers(5)
        momentum_stocks = self.get_momentum_stocks(5)
        volatile_stocks = self.get_highest_volatility(5)
        breakouts = self.detect_breakouts()
        
        return {
            'timestamp': self.last_update or int(time.time()),
            'datetime': datetime.fromtimestamp(self.last_update or time.time()).strftime('%Y-%m-%d %H:%M:%S'),
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'momentum_stocks': momentum_stocks,
            'volatile_stocks': volatile_stocks,
            'breakouts': breakouts[:5] if len(breakouts) > 5 else breakouts
        }
