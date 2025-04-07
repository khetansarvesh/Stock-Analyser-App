import pandas as pd
import numpy as np
from collections import deque
import time

class SlidingWindow:
    """
    A sliding window implementation for time-series stock data analysis.
    This class maintains a fixed-size window of recent stock data points 
    and can compute various metrics over this window.
    """
    
    def __init__(self, window_size=60, symbols=None):
        """
        Initialize a sliding window for stock analysis.
        
        Args:
            window_size (int): Size of the sliding window in data points
            symbols (list): List of stock symbols to track
        """
        self.window_size = window_size
        self.symbols = symbols or []
        self.windows = {}  # Maps symbol to its data window
        
        # Initialize windows for each symbol
        for symbol in self.symbols:
            self.windows[symbol] = deque(maxlen=window_size)
    
    def add_symbol(self, symbol):
        """Add a new symbol to track."""
        if symbol not in self.windows:
            self.windows[symbol] = deque(maxlen=self.window_size)
            self.symbols.append(symbol)
    
    def remove_symbol(self, symbol):
        """Remove a symbol from tracking."""
        if symbol in self.windows:
            del self.windows[symbol]
            self.symbols.remove(symbol)
    
    def update(self, symbol, price, timestamp=None):
        """
        Add a new data point to the window for a given symbol.
        
        Args:
            symbol (str): Stock symbol
            price (float): Current price
            timestamp (int/float): Timestamp of the data point
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        if symbol not in self.windows:
            self.add_symbol(symbol)
        
        # Add data point to the window
        self.windows[symbol].append({
            'price': price,
            'timestamp': timestamp
        })
    
    def update_batch(self, data_dict):
        """
        Update multiple symbols with new data points.
        
        Args:
            data_dict (dict): Dictionary mapping symbols to {price, timestamp} dicts
        """
        for symbol, data in data_dict.items():
            self.update(symbol, data['price'], data.get('timestamp'))
    
    def get_window(self, symbol):
        """
        Get the current window data for a symbol.
        
        Args:
            symbol (str): Stock symbol
        
        Returns:
            list: List of data points in the window
        """
        if symbol in self.windows:
            return list(self.windows[symbol])
        return []
    
    def calculate_metrics(self, symbol):
        """
        Calculate various metrics for a symbol based on its window data.
        
        Args:
            symbol (str): Stock symbol
        
        Returns:
            dict: Dictionary containing calculated metrics
        """
        if symbol not in self.windows or not self.windows[symbol]:
            return {}
        
        window = list(self.windows[symbol])
        prices = [point['price'] for point in window]
        
        if not prices or len(prices) < 2:
            return {'symbol': symbol, 'window_size': len(prices), 'insufficient_data': True}
        
        # Calculate metrics
        current_price = prices[-1]
        start_price = prices[0]
        max_price = max(prices)
        min_price = min(prices)
        avg_price = sum(prices) / len(prices)
        
        # Percentage change over the window
        pct_change = ((current_price - start_price) / start_price) * 100
        
        # Calculate volatility (standard deviation)
        volatility = np.std(prices)
        
        # Calculate simple momentum (rate of change)
        if len(prices) >= 5:
            momentum = ((prices[-1] - prices[-5]) / prices[-5]) * 100
        else:
            momentum = 0
        
        return {
            'symbol': symbol,
            'window_size': len(prices),
            'current_price': current_price,
            'start_price': start_price,
            'max_price': max_price,
            'min_price': min_price,
            'avg_price': avg_price,
            'pct_change': pct_change,
            'volatility': volatility,
            'momentum': momentum,
            'timestamp': window[-1]['timestamp']
        }
    
    def calculate_all_metrics(self):
        """
        Calculate metrics for all symbols.
        
        Returns:
            dict: Dictionary mapping symbols to their metrics
        """
        metrics = {}
        for symbol in self.symbols:
            metrics[symbol] = self.calculate_metrics(symbol)
        return metrics
    
    def get_top_performers(self, n=5, metric='pct_change'):
        """
        Get the top performing stocks based on a specified metric.
        
        Args:
            n (int): Number of top performers to return
            metric (str): Metric to sort by (e.g., 'pct_change', 'momentum')
        
        Returns:
            list: List of top performing stocks and their metrics
        """
        metrics = self.calculate_all_metrics()
        
        # Filter out insufficient data and sort
        valid_metrics = {k: v for k, v in metrics.items() 
                         if v and not v.get('insufficient_data', False)}
        
        # Sort by the specified metric in descending order
        sorted_symbols = sorted(valid_metrics.keys(), 
                              key=lambda s: valid_metrics[s].get(metric, 0), 
                              reverse=True)
        
        # Return the top n
        top_symbols = sorted_symbols[:n]
        return [valid_metrics[s] for s in top_symbols]
    
    def get_bottom_performers(self, n=5, metric='pct_change'):
        """
        Get the bottom performing stocks based on a specified metric.
        
        Args:
            n (int): Number of bottom performers to return
            metric (str): Metric to sort by (e.g., 'pct_change', 'momentum')
        
        Returns:
            list: List of bottom performing stocks and their metrics
        """
        metrics = self.calculate_all_metrics()
        
        # Filter out insufficient data and sort
        valid_metrics = {k: v for k, v in metrics.items() 
                         if v and not v.get('insufficient_data', False)}
        
        # Sort by the specified metric in ascending order
        sorted_symbols = sorted(valid_metrics.keys(), 
                              key=lambda s: valid_metrics[s].get(metric, 0))
        
        # Return the bottom n
        bottom_symbols = sorted_symbols[:n]
        return [valid_metrics[s] for s in bottom_symbols]
