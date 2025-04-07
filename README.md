# Real-Time Stock Price Analysis Using Heap Data Structures

This project implements a real-time stock analysis system that uses heap data structures (priority queues) to efficiently track and analyze stock performance. The application provides live updates, interactive visualizations, and automated alerts to help users make informed trading decisions.

## Key Features

- **Real-Time Data Access**: Connects to Yahoo Finance API to fetch current and historical stock price data
- **Efficient Stock Tracking**: Uses min-heaps and max-heaps to keep track of the best and worst performing stocks
- **Sliding Window Analysis**: Analyzes stock trends over customizable time frames to detect patterns and momentum shifts
- **Automated Alerts**: Configurable price and percentage change alerts for important stock movements
- **Interactive Visualizations**: Real-time updating charts and metrics for comprehensive market analysis

## System Architecture

The system is built with a modular architecture consisting of these main components:

1. **Data Structures Module**: Custom min-heap and max-heap implementations for efficient stock ranking
2. **API Module**: Interface with Yahoo Finance for real-time stock data
3. **Analysis Module**: Sliding window and trend analysis algorithms
4. **Alert Module**: Configurable alert system for price thresholds and percentage changes
5. **Visualization Module**: Interactive charts and dashboards using Plotly and Dash

## Technical Implementation

### Heap Data Structures

The project leverages two heap implementations:
- `StockMaxHeap`: Tracks top-performing stocks (gainers)
- `StockMinHeap`: Tracks worst-performing stocks (losers)

These heap structures allow O(log n) updates and O(1) access to the top/bottom performing stocks.

### Sliding Window Analysis

The sliding window implementation maintains a fixed-size window of recent stock data points and calculates various metrics:
- Price changes over different time periods
- Volatility measurements
- Momentum indicators
- Breakout detection

### Real-Time Alerts

The alert system allows users to:
- Create custom price and percentage change alerts
- Monitor multiple stocks simultaneously
- Receive notifications when conditions are met

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/stock-analysis.git
cd stock-analysis
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. (Optional) Set up environment variables:
Create a `.env` file with:
```
API_KEY=your_api_key_if_needed
WEB_PORT=8050
DEBUG_MODE=False
```

### Running the Application

Run the main application:
```
python main.py
```

This will start the web dashboard on http://localhost:8050 (or your configured port).

## Usage

1. **View Market Overview**: The dashboard shows top gainers and losers automatically
2. **Analyze Individual Stocks**: Select a stock to view detailed price charts and metrics
3. **Set up Alerts**: Configure alerts for important price thresholds
4. **Track Performance**: Monitor stock performance with automatically updating visualizations

## How the Heap Data Structure Helps

Heaps are particularly suited for this application because:

1. They maintain a sorted order with efficient updates (O(log n) time)
2. They allow fast access to the highest/lowest values (O(1) time)
3. They can be modified to track multiple metrics simultaneously
4. They're memory efficient compared to keeping all data sorted

Using heaps ensures our application can track hundreds of stocks while maintaining fast response times for identifying the best and worst performers.

## Future Enhancements

- Machine learning models for price prediction
- More advanced technical indicators
- Portfolio management features
- Social sentiment analysis integration
- Mobile application support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Yahoo Finance API for stock data
- Plotly and Dash for visualization capabilities
- Python heapq module for heap implementation
