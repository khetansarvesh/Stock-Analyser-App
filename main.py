import time
import threading
import schedule
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Import project modules
from stock_api import StockAPI
from trend_analyzer import TrendAnalyzer
from alert_manager import AlertManager
from charts import StockVisualizer
import config

class StockAnalysisApp:
    """
    Main application class for real-time stock analysis.
    """
    
    def __init__(self):
        """Initialize the stock analysis application."""
        # Initialize components
        self.api = StockAPI(default_symbols=config.DEFAULT_SYMBOLS)
        self.trend_analyzer = TrendAnalyzer(
            max_size=config.MAX_HEAP_SIZE, 
            window_size=config.DEFAULT_WINDOW_SIZE,
            stock_api=self.api
        )
        self.alert_manager = AlertManager()
        self.visualizer = StockVisualizer(theme=config.CHART_THEME)
        
        # Data storage
        self.current_data = {}
        self.previous_data = {}
        self.historical_data = {}
        
        # Last update timestamp
        self.last_update = None
        
        # Threading and scheduling
        self.update_thread = None
        self.is_running = False
        
        # Dash app for visualization
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        self.setup_dashboard()
    
    def update_data(self):
        """Fetch and update stock data."""
        try:
            # Store previous data
            self.previous_data = self.current_data.copy()
            date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
            time_str = (datetime.now() - timedelta(hours=5)).strftime('%H:%M')
            target_datetime = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")

            self.current_data = self.api.get_current_prices(target_datetime)
            print(self.current_data)
            # Update trend analyzer
            self.trend_analyzer.update_batch(self.current_data, self.previous_data)
            
            # Get historical data for charts
            self.historical_data = self.api.get_historical_data(period="1d")
            
            # Check for alerts
            triggered_alerts = self.alert_manager.check_alerts(self.current_data)
            
            self.last_update = int(time.time())
            
        except Exception as e:
            pass
    
    def scheduled_update(self):
        """Scheduled function to update data periodically."""
        while self.is_running:
            self.update_data()
            time.sleep(config.UPDATE_INTERVAL)
    
    def start(self):
        """Start the data update thread and run the dashboard."""
        if not self.is_running:
            self.is_running = True
            
            # Initial data update
            self.update_data()
            
            # Start update thread
            self.update_thread = threading.Thread(target=self.scheduled_update)
            self.update_thread.daemon = True
            self.update_thread.start()
            
            # Run the dashboard
            self.app.run(debug=config.DEBUG_MODE, port=config.WEB_PORT)
    
    def stop(self):
        """Stop the application."""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
    
    def setup_dashboard(self):
        """Set up the Dash dashboard."""
        # App layout
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Real-Time Stock Analysis", className="text-center my-4"),
                    html.P("Using Heap Data Structures for Efficient Analysis", 
                           className="text-center lead"),
                    dbc.Button("Refresh Data", id="refresh-button", color="primary", 
                               className="my-2")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            dbc.Row([
                                dbc.Col("Top Gainers & Losers", width=6),
                                dbc.Col([
                                    dbc.Select(
                                        id="timeframe-selector",
                                        options=[
                                            {"label": "Current", "value": "default"},
                                            {"label": "1 Week Ago", "value": "one_week"},
                                            {"label": "2 Weeks Ago", "value": "two_week"}
                                        ],
                                        value="one_week"
                                    )
                                ], width=6)
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="gainers-losers-chart")
                        ])
                    ], className="mb-4")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            dbc.Row([
                                dbc.Col("Stock Selection", width=6),
                                dbc.Col([
                                    dbc.Select(
                                        id="stock-selector",
                                        options=[
                                            {"label": symbol, "value": symbol}
                                            for symbol in config.DEFAULT_SYMBOLS
                                        ],
                                        value=config.DEFAULT_SYMBOLS[0]
                                    )
                                ], width=6)
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="stock-price-chart")
                        ])
                    ])
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Stock Metrics"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id="stock-metrics")
                                ])
                            ])
                        ])
                    ])
                ], width=12, className="my-4")
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Alert Settings"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Form([
                                        dbc.Label("Symbol"),
                                        dbc.Select(
                                            id="alert-symbol",
                                            options=[
                                                {"label": symbol, "value": symbol}
                                                for symbol in config.DEFAULT_SYMBOLS
                                            ],
                                            value=config.DEFAULT_SYMBOLS[0]
                                        )
                                    ])
                                ], width=3),
                                dbc.Col([
                                    dbc.Form([
                                        dbc.Label("Alert Type"),
                                        dbc.Select(
                                            id="alert-type",
                                            options=[
                                                {"label": "Price Above", "value": "price_above"},
                                                {"label": "Price Below", "value": "price_below"},
                                                {"label": "Percent Change Above", "value": "percent_change_above"},
                                                {"label": "Percent Change Below", "value": "percent_change_below"}
                                            ],
                                            value="price_above"
                                        )
                                    ])
                                ], width=3),
                                dbc.Col([
                                    dbc.Form([
                                        dbc.Label("Threshold"),
                                        dbc.Input(id="alert-threshold", type="number", value=0)
                                    ])
                                ], width=3),
                                dbc.Col([
                                    dbc.Button("Add Alert", id="add-alert-button", color="success", 
                                               className="mt-4")
                                ], width=3)
                            ]),
                            html.Div(id="alert-status", className="mt-3"),
                            html.Div(id="alerts-list", className="mt-3")
                        ])
                    ])
                ], width=12, className="my-4")
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Div(
                        f"Last updated: Never", 
                        id="last-update-time", 
                        className="text-right text-muted small"
                    )
                ], width=12, className="mb-4")
            ]),
            
            # Interval component for periodic updates
            dcc.Interval(
                id='interval-component',
                interval=10 * 1000,  # in milliseconds (10 seconds)
                n_intervals=0
            )
        ], fluid=True)
        
        # Callbacks
        self.app.callback(
            Output("gainers-losers-chart", "figure"),
            [Input("interval-component", "n_intervals"),
             Input("refresh-button", "n_clicks"),
             Input("timeframe-selector", "value")]
        )(self.update_gainers_losers_chart)
        
        self.app.callback(
            Output("stock-price-chart", "figure"),
            [Input("stock-selector", "value"),
             Input("interval-component", "n_intervals"),
             Input("refresh-button", "n_clicks")]
        )(self.update_stock_price_chart)
        
        self.app.callback(
            Output("stock-metrics", "children"),
            [Input("stock-selector", "value"),
             Input("interval-component", "n_intervals"),
             Input("refresh-button", "n_clicks")]
        )(self.update_stock_metrics)
        
        self.app.callback(
            [Output("alert-status", "children"),
             Output("alerts-list", "children")],
            [Input("add-alert-button", "n_clicks"),
             Input("interval-component", "n_intervals")],
            [State("alert-symbol", "value"),
             State("alert-type", "value"),
             State("alert-threshold", "value")]
        )(self.handle_alerts)
        
        self.app.callback(
            Output("last-update-time", "children"),
            [Input("interval-component", "n_intervals")]
        )(self.update_time_display)
    
    def update_gainers_losers_chart(self, n_intervals=None, n_clicks=None, timeframe="one_week"):
        """Update the gainers and losers chart."""
        if self.trend_analyzer.last_update is None:
            # No data yet
            return go.Figure().update_layout(title="No data available yet")
        
        # Get title based on timeframe
        title = "Top Gainers and Losers"
        if timeframe == "one_week":
            title = "Top Gainers and Losers - 1 Week Comparison"
        elif timeframe == "two_week":
            title = "Top Gainers and Losers - 2 Week Comparison"
        
        if timeframe == "default":
            top_gainers = self.trend_analyzer.get_top_gainers(5)
            top_losers = self.trend_analyzer.get_top_losers(5)
        else:
            top_gainers = self.trend_analyzer.get_top_gainers(5, timeframe)
            top_losers = self.trend_analyzer.get_top_losers(5, timeframe)
        
        return self.visualizer.create_gainers_losers_chart(
            top_gainers, 
            top_losers, 
            title
        )
    
    def update_stock_price_chart(self, symbol, n_intervals=None, n_clicks=None):
        """Update the stock price chart for the selected symbol."""
        if not symbol or symbol not in self.historical_data:
            return go.Figure().update_layout(title=f"No data available for {symbol}")
        
        return self.visualizer.create_price_chart(
            self.historical_data[symbol], 
            f"Price Chart - {symbol}"
        )
    
    def update_stock_metrics(self, symbol, n_intervals=None, n_clicks=None):
        """Update the stock metrics display."""
        if not symbol or symbol not in self.current_data:
            return "No data available"
        
        # Get current data
        current = self.current_data.get(symbol, {})
        
        # Get metrics from sliding window
        metrics = self.trend_analyzer.sliding_window.calculate_metrics(symbol)
        
        # Format metrics table
        table_rows = []
        
        if current:
            price = current.get('price')
            if price:
                table_rows.append(
                    html.Tr([
                        html.Td("Current Price"),
                        html.Td(f"${price:.2f}")
                    ])
                )
        
        if metrics:
            for key, value in metrics.items():
                if key not in ['symbol', 'window_size', 'timestamp', 'insufficient_data']:
                    if isinstance(value, float):
                        formatted_value = f"{value:.2f}"
                        if key in ['pct_change', 'momentum']:
                            formatted_value += '%'
                        elif key in ['volatility']:
                            formatted_value = f"${formatted_value}"
                        elif 'price' in key:
                            formatted_value = f"${formatted_value}"
                        
                        table_rows.append(
                            html.Tr([
                                html.Td(key.replace('_', ' ').title()),
                                html.Td(formatted_value)
                            ])
                        )
        
        # Return metrics table
        return dbc.Table(
            [html.Tbody(table_rows)],
            bordered=True,
            hover=True,
            responsive=True,
            size="sm"
        )
    
    def handle_alerts(self, n_clicks, n_intervals, symbol, alert_type, threshold):
        """Handle alert creation and display."""
        ctx = dash.callback_context
        alert_message = ""
        
        # Add alert if button was clicked
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'add-alert-button.n_clicks' and n_clicks:
            if symbol and alert_type and threshold is not None:
                alert_id = self.alert_manager.add_alert(symbol, alert_type, float(threshold))
                alert_message = dbc.Alert(
                    f"Alert added for {symbol} {alert_type} {threshold}",
                    color="success",
                    dismissable=True
                )
            else:
                alert_message = dbc.Alert(
                    "Please fill in all alert fields",
                    color="danger",
                    dismissable=True
                )
        
        # Get all active alerts
        alerts = self.alert_manager.get_all_alerts()
        triggered = self.alert_manager.get_triggered_alerts()
        
        # Format alerts list
        alerts_list = []
        
        if alerts:
            active_alerts = dbc.Card([
                dbc.CardHeader("Active Alerts"),
                dbc.CardBody([
                    dbc.ListGroup([
                        dbc.ListGroupItem(
                            f"{alert.symbol} - {alert.alert_type} - {alert.threshold}",
                            color="info"
                        ) for alert in alerts
                    ])
                ])
            ], className="mb-3")
            alerts_list.append(active_alerts)
        
        if triggered:
            triggered_alerts = dbc.Card([
                dbc.CardHeader("Recent Triggered Alerts"),
                dbc.CardBody([
                    dbc.ListGroup([
                        dbc.ListGroupItem(
                            [
                                html.Strong(f"{t['alert']['symbol']} - {t['alert']['alert_type']}"),
                                html.Div(f"Threshold: {t['alert']['threshold']}"),
                                html.Small(f"Triggered: {t['datetime']}", className="text-muted")
                            ],
                            color="warning"
                        ) for t in triggered[:5]
                    ])
                ])
            ])
            alerts_list.append(triggered_alerts)
        
        return alert_message, alerts_list
    
    def update_time_display(self, n_intervals):
        """Update the last update time display."""
        if self.last_update:
            time_str = datetime.fromtimestamp(self.last_update).strftime('%Y-%m-%d %H:%M:%S')
            return f"Last updated: {time_str}"
        return "Last updated: Never"


if __name__ == "__main__":
    app = StockAnalysisApp()
    app.start()