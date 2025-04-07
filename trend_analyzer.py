import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from heap import StockMinHeap, StockMaxHeap
from sliding_window import SlidingWindow

class TrendAnalyzer:
    """
    Analyzes stock trends using heap data structures and sliding windows.
    """
    
    def __init__(self, max_size=10, window_size=60, stock_api=None):
        """
        Initialize the trend analyzer.
        
        Args:
            max_size (int): Maximum number of stocks to track in each heap
            window_size (int): Size of the sliding window for analysis
            stock_api (StockAPI): Stock API instance for data fetching
        """
        # Heaps for tracking top gainers and losers
        self.gainers_heap = StockMaxHeap(max_size=max_size)
        self.losers_heap = StockMinHeap(max_size=max_size)
        
        # Heaps for different timeframes
        self.timeframe_heaps = {
            'day': {
                'gainers': StockMaxHeap(max_size=max_size),
                'losers': StockMinHeap(max_size=max_size),
                'last_update': None
            },
            'week': {
                'gainers': StockMaxHeap(max_size=max_size),
                'losers': StockMinHeap(max_size=max_size),
                'last_update': None
            }
        }
        
        # Store reference to the stock API
        self.stock_api = stock_api
        
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
        
        # Update main heaps
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
        
        # Update time-based comparisons if stock API is available
        if self.stock_api:
            self._update_timeframe_comparisons(symbol, current_price, timestamp)
        
        self.last_update = timestamp
    
    def _update_timeframe_comparisons(self, symbol, current_price, timestamp):
        """
        Update the timeframe-based comparisons for a symbol using data from the stock API.
        
        Args:
            symbol (str): Stock symbol
            current_price (float): Current stock price
            timestamp (int): Timestamp of the data point
        """
        # Get timeframe data from the stock API
        for timeframe in ['day', 'week']:
            timeframe_data = self.stock_api.get_timeframe_data(timeframe)
            
            if timeframe_data and symbol in timeframe_data:
                # Get historical price for this timeframe
                historical_data = timeframe_data[symbol]
                historical_price = historical_data.get('price')
                
                if historical_price and historical_price > 0:
                    # Calculate percentage change
                    pct_change = ((current_price - historical_price) / historical_price) * 100
                    
                    # Update heaps for this timeframe
                    self.timeframe_heaps[timeframe]['gainers'].push(symbol, pct_change, timestamp)
                    self.timeframe_heaps[timeframe]['losers'].push(symbol, pct_change, timestamp)
                    self.timeframe_heaps[timeframe]['last_update'] = timestamp
    
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
    
    def get_top_gainers(self, n=None, timeframe=None):
        """
        Get the top gaining stocks.
        
        Args:
            n (int): Number of top gainers to return
            timeframe (str): Timeframe for comparison ('day', 'week', or None for default)
            
        Returns:
            list: List of top gainers
        """
        if timeframe and timeframe in self.timeframe_heaps:
            return self.timeframe_heaps[timeframe]['gainers'].get_top(n)
        return self.gainers_heap.get_top(n)
    
    def get_top_losers(self, n=None, timeframe=None):
        """
        Get the top losing stocks.
        
        Args:
            n (int): Number of top losers to return
            timeframe (str): Timeframe for comparison ('day', 'week', or None for default)
            
        Returns:
            list: List of top losers
        """
        if timeframe and timeframe in self.timeframe_heaps:
            return self.timeframe_heaps[timeframe]['losers'].get_top(n)
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
    
    def generate_summary_report(self, timeframe=None):
        """
        Generate a summary report of current market trends.
        
        Args:
            timeframe (str): Timeframe for comparison ('day', 'week', or None for default)
            
        Returns:
            dict: Summary report
        """
        top_gainers = self.get_top_gainers(5, timeframe)
        top_losers = self.get_top_losers(5, timeframe)
        momentum_stocks = self.get_momentum_stocks(5)
        volatile_stocks = self.get_highest_volatility(5)
        breakouts = self.detect_breakouts()
        
        # Determine the appropriate title based on timeframe
        timeframe_title = ""
        if timeframe == 'day':
            timeframe_title = "1 Day Comparison"
        elif timeframe == 'week':
            timeframe_title = "1 Week Comparison"
        
        return {
            'timestamp': self.last_update or int(time.time()),
            'datetime': datetime.fromtimestamp(self.last_update or time.time()).strftime('%Y-%m-%d %H:%M:%S'),
            'timeframe': timeframe,
            'timeframe_title': timeframe_title,
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'momentum_stocks': momentum_stocks,
            'volatile_stocks': volatile_stocks,
            'breakouts': breakouts[:5] if len(breakouts) > 5 else breakouts
        }
