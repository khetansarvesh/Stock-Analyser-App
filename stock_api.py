import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

class StockAPI:
    """Class to handle interactions with stock market APIs."""
    
    def __init__(self, default_symbols=None):
        """
        Initialize the Stock API client.
        
        Args:
            default_symbols (list): List of default stock symbols to track
        """
        if default_symbols is None:
            self.default_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT']
        else:
            self.default_symbols = default_symbols
        
        self.cache = {}  # Cache to store recent data
        self.cache_expiry = 60  # Cache expiry in seconds
    
    def get_current_prices(self, symbols=None):
        """
        Get the current prices for a list of stock symbols.
        
        Args:
            symbols (list): List of stock symbols to fetch data for
        
        Returns:
            dict: Dictionary mapping symbols to their current prices
        """
        symbols = symbols or self.default_symbols
        
        try:
            tickers = yf.Tickers(" ".join(symbols))
            current_data = {}
            
            for symbol in symbols:
                ticker = tickers.tickers[symbol]
                # Get the last traded price
                current_data[symbol] = {
                    'price': ticker.info.get('regularMarketPrice', None),
                    'timestamp': int(time.time()),
                    'symbol': symbol
                }
            
            return current_data
        except Exception as e:
            return {}
    
    def get_historical_data(self, symbols=None, period="1d", interval="1m"):
        """
        Get historical price data for a list of stock symbols.
        
        Args:
            symbols (list): List of stock symbols to fetch data for
            period (str): Period of data to fetch (e.g., 1d, 5d, 1mo, 3mo, 1y)
            interval (str): Data point interval (e.g., 1m, 2m, 5m, 15m, 30m, 60m, 1d)
        
        Returns:
            dict: Dictionary mapping symbols to pandas DataFrames with historical data
        """
        symbols = symbols or self.default_symbols
        cache_key = f"{','.join(sorted(symbols))}-{period}-{interval}"
        
        # Check if data is in cache and not expired
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_expiry:
                return cache_data
        
        try:
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, interval=interval)
                
                if not hist.empty:
                    # Calculate percentage change
                    hist['change_pct'] = hist['Close'].pct_change() * 100
                    hist['symbol'] = symbol
                    data[symbol] = hist
            
            # Store in cache
            self.cache[cache_key] = (time.time(), data)
            return data
        except Exception as e:
            return {}
    
    def get_price_changes(self, symbols=None, period="1d"):
        """
        Calculate price changes over a period for a list of stock symbols.
        
        Args:
            symbols (list): List of stock symbols to fetch data for
            period (str): Period for calculating changes (e.g., 1d, 5d, 1mo)
        
        Returns:
            dict: Dictionary mapping symbols to their percentage changes
        """
        symbols = symbols or self.default_symbols
        
        try:
            data = self.get_historical_data(symbols, period=period)
            changes = {}
            
            for symbol, hist in data.items():
                if not hist.empty:
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    pct_change = ((end_price - start_price) / start_price) * 100
                    
                    changes[symbol] = {
                        'symbol': symbol,
                        'change_pct': pct_change,
                        'start_price': start_price,
                        'end_price': end_price,
                        'timestamp': int(time.time())
                    }
            
            return changes
        except Exception as e:
            return {}
    
    def search_stocks(self, query):
        """
        Search for stocks by name or symbol.
        
        Args:
            query (str): Search query
        
        Returns:
            list: List of matching stock symbols
        """
        try:
            # This is a simplified approach - a real implementation would use an API that supports search
            # For now, we'll just filter our default symbols
            return [symbol for symbol in self.default_symbols if query.upper() in symbol]
        except Exception as e:
            return []
