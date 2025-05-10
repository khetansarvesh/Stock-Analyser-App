import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

class StockAPI:
    
    def __init__(self, default_symbols=None):
        
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

    def get_current_prices(self, target_datetime, symbols=None):
        current_data = {}
        for symbol in self.default_symbols:
            ticker = yf.Ticker(symbol)

            # current data
            hist = ticker.history(start=target_datetime - timedelta(minutes=1), 
                                    end=target_datetime, 
                                    interval="1m")
            current_data[symbol] = {
                                        "symbol": symbol,
                                        "price": hist.iloc[0,3],
                                        "timestamp": target_datetime
                                    }


            # one week old data
            hist = ticker.history(start = target_datetime - timedelta(days=7), 
                                    end = target_datetime - timedelta(days=6))                
            self.timeframe_data['one_week'][symbol] = {'price': hist['Close'].iloc[0],
                            'timestamp': int((target_datetime - timedelta(days=7)).timestamp()),
                            'symbol': symbol}


            # two week old data
            hist = ticker.history(start = target_datetime - timedelta(days=14), 
                                    end = target_datetime - timedelta(days=13))                
            self.timeframe_data['two_week'][symbol] = {'price': hist['Close'].iloc[0],
                            'timestamp': int((target_datetime - timedelta(days=14)).timestamp()),
                            'symbol': symbol}


        return current_data        
    
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
        
        data = self.get_historical_data(self.default_symbols, period=period)
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
    
    def get_timeframe_data(self, timeframe):
        return self.timeframe_data[timeframe]