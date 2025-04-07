import os


#from dotenv import load_dotenv
#load_dotenv()
#API_KEY = os.getenv('API_KEY', '')
#WEB_PORT = int(os.getenv('WEB_PORT', 8050))
#DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

#API_KEY=''
WEB_PORT=8050
DEBUG_MODE=False



DEFAULT_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 
    'TSLA', 'NVDA', 'JPM', 'V', 'WMT',
    'PG', 'JNJ', 'MA', 'DIS', 'NFLX'
]

# Heap Configuration
MAX_HEAP_SIZE = 10

# Sliding Window Configuration
DEFAULT_WINDOW_SIZE = 60  # Number of data points in sliding window
SHORT_WINDOW_SIZE = 20
MEDIUM_WINDOW_SIZE = 60
LONG_WINDOW_SIZE = 120

# Update intervals (in seconds)
UPDATE_INTERVAL = 60  # 1 minute

# Alert Configuration
MAX_ALERTS_HISTORY = 100
DEFAULT_ALERT_EXPIRY = 24 * 60 * 60  # 24 hours in seconds

# Chart Configuration
CHART_THEME = 'plotly_white'
DEFAULT_CHART_HEIGHT = 600