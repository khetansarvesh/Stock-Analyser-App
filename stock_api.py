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
        
        # Historical snapshots for different timeframes
        self.timeframe_data = {
            'one_week': {},     # Snapshot from 1 week ago
            'two_week': {}      # Snapshot from 2 weeks ago
        }
        
        # Last update timestamps for each timeframe
        self.timeframe_last_update = {
            'one_week': 0,
            'two_week': 0
        }
    
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
            current_timestamp = int(time.time())
            
            for symbol in symbols:
                ticker = tickers.tickers[symbol]
                # Get the last traded price
                price = ticker.info.get('regularMarketPrice', None)
                
                if price is not None:
                    current_data[symbol] = {
                        'price': price,
                        'timestamp': current_timestamp,
                        'symbol': symbol
                    }
                    
                    # Update timeframe data if needed
                    self._update_timeframe_data(symbol, price, current_timestamp)
            
            return current_data
        except Exception as e:
            return {}
    
    def _update_timeframe_data(self, symbol, price, timestamp):
        """
        Update the historical snapshots for different timeframes.
        
        Args:
            symbol (str): Stock symbol
            price (float): Current price
            timestamp (int): Current timestamp
        """
        current_time = datetime.fromtimestamp(timestamp)
        
        # One week timeframe - capture every week (604800 seconds = 7 days)
        if timestamp - self.timeframe_last_update['one_week'] >= 604800:
            self.timeframe_data['one_week'] = self._fetch_one_week_timeframe_data(self.default_symbols)
            self.timeframe_last_update['one_week'] = timestamp
        
        # Two week timeframe - capture every two weeks (1209600 seconds = 14 days)
        if timestamp - self.timeframe_last_update['two_week'] >= 1209600:
            self.timeframe_data['two_week'] = self._fetch_two_week_timeframe_data(self.default_symbols)
            self.timeframe_last_update['two_week'] = timestamp
        
        # Store current data in each timeframe if the symbol doesn't exist yet
        for timeframe in ['one_week', 'two_week']:
            if timeframe not in self.timeframe_data or symbol not in self.timeframe_data[timeframe]:
                if timeframe not in self.timeframe_data:
                    self.timeframe_data[timeframe] = {}
                self.timeframe_data[timeframe][symbol] = {
                    'price': price,
                    'timestamp': timestamp,
                    'symbol': symbol
                }
    
    def _copy_timeframe_data(self, timeframe):
        """Create a copy of the current data for a timeframe snapshot."""
        return self.timeframe_data.get(timeframe, {}).copy()
    
    def _fetch_one_week_timeframe_data(self, symbols):
        """Fetch data from 1 week ago using yfinance."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=start_date + timedelta(days=1))
                
                if not hist.empty:
                    price = hist['Close'].iloc[0]
                    timestamp = int(start_date.timestamp())
                    data[symbol] = {
                        'price': price,
                        'timestamp': timestamp,
                        'symbol': symbol
                    }
            
            return data
        except Exception as e:
            return {}
    
    def _fetch_two_week_timeframe_data(self, symbols):
        """Fetch data from 2 weeks ago using yfinance."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=14)
            
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=start_date + timedelta(days=1))
                
                if not hist.empty:
                    price = hist['Close'].iloc[0]
                    timestamp = int(start_date.timestamp())
                    data[symbol] = {
                        'price': price,
                        'timestamp': timestamp,
                        'symbol': symbol
                    }
            
            return data
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
    
    def get_timeframe_data(self, timeframe):
        """
        Get stock data for a specific timeframe comparison.
        
        Args:
            timeframe (str): Timeframe to get data for ('one_week', 'two_week')
            
        Returns:
            dict: Historical data for the specified timeframe
        """
        if timeframe in self.timeframe_data:
            return self.timeframe_data[timeframe]
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
