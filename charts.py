import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class StockVisualizer:
    """
    Class for creating interactive stock visualizations.
    """
    
    def __init__(self, theme='plotly_white'):
        """
        Initialize the visualizer.
        
        Args:
            theme (str): Plotly theme to use for charts
        """
        self.theme = theme
    
    def create_price_chart(self, historical_data, title=None):
        """
        Create a candlestick chart for a stock's price history.
        
        Args:
            historical_data (pd.DataFrame): DataFrame with historical price data
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        if historical_data.empty:
            return None
        
        # Create figure
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=historical_data.index,
                open=historical_data['Open'],
                high=historical_data['High'],
                low=historical_data['Low'],
                close=historical_data['Close'],
                name="Price"
            )
        )
        
        # Add volume as bar chart on secondary y-axis if available
        if 'Volume' in historical_data.columns:
            fig.add_trace(
                go.Bar(
                    x=historical_data.index,
                    y=historical_data['Volume'],
                    name="Volume",
                    marker_color='rgba(0, 150, 255, 0.3)',
                    opacity=0.3,
                    yaxis="y2"
                )
            )
            
            # Add secondary y-axis for volume
            fig.update_layout(
                yaxis2=dict(
                    title="Volume",
                    overlaying="y",
                    side="right",
                    showgrid=False
                )
            )
        
        # Customize layout
        fig.update_layout(
            title=title or f"Price Chart for {historical_data['symbol'].iloc[0] if 'symbol' in historical_data.columns else 'Stock'}",
            xaxis_title="Date",
            yaxis_title="Price",
            template=self.theme,
            xaxis_rangeslider_visible=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=600
        )
        
        # Add buttons for time range selection
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    buttons=list([
                        dict(
                            args=[{"xaxis.rangeslider.visible": True}],
                            label="Show Range Slider",
                            method="relayout"
                        ),
                        dict(
                            args=[{"xaxis.rangeslider.visible": False}],
                            label="Hide Range Slider",
                            method="relayout"
                        )
                    ]),
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                )
            ]
        )
        
        return fig
    
    def create_comparison_chart(self, stocks_data, metric='Close', title=None):
        """
        Create a comparison chart for multiple stocks.
        
        Args:
            stocks_data (dict): Dictionary of stock symbols to their historical data
            metric (str): Metric to compare ('Close', 'pct_change', etc.)
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        if not stocks_data:
            return None
        
        fig = go.Figure()
        
        # Normalize data to compare different price ranges
        normalized_data = {}
        for symbol, data in stocks_data.items():
            if data.empty or metric not in data.columns:
                continue
                
            # Normalize to first value = 100
            base_value = data[metric].iloc[0]
            if base_value != 0:
                normalized_data[symbol] = data[metric] / base_value * 100
        
        # Add a line for each stock
        for symbol, values in normalized_data.items():
            fig.add_trace(
                go.Scatter(
                    x=values.index,
                    y=values,
                    mode='lines',
                    name=symbol
                )
            )
        
        # Customize layout
        fig.update_layout(
            title=title or f"Stock Comparison ({metric})",
            xaxis_title="Date",
            yaxis_title=f"Normalized {metric} (%)",
            template=self.theme,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=500
        )
        
        return fig
    
    def create_heatmap(self, correlation_matrix, title=None):
        """
        Create a correlation heatmap for multiple stocks.
        
        Args:
            correlation_matrix (pd.DataFrame): Correlation matrix for stocks
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        if correlation_matrix.empty:
            return None
        
        fig = px.imshow(
            correlation_matrix,
            text_auto=True,
            color_continuous_scale='RdBu_r',
            labels=dict(x="Stock", y="Stock", color="Correlation")
        )
        
        # Customize layout
        fig.update_layout(
            title=title or "Stock Correlation Heatmap",
            template=self.theme,
            height=600,
            width=700
        )
        
        return fig
    
    def create_gainers_losers_chart(self, gainers, losers, title=None):
        """
        Create a bar chart showing top gainers and losers.
        
        Args:
            gainers (list): List of top gaining stocks with their data
            losers (list): List of top losing stocks with their data
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        # Extract data
        gainer_symbols = [g[1] for g in gainers]  # (value, symbol, timestamp)
        gainer_values = [g[0] for g in gainers]
        
        loser_symbols = [l[1] for l in losers]
        loser_values = [l[0] for l in losers]
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Top Gainers", "Top Losers"),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Add gainers
        fig.add_trace(
            go.Bar(
                x=gainer_symbols,
                y=gainer_values,
                marker_color='green',
                name="Gainers"
            ),
            row=1, col=1
        )
        
        # Add losers
        fig.add_trace(
            go.Bar(
                x=loser_symbols,
                y=loser_values,
                marker_color='red',
                name="Losers"
            ),
            row=1, col=2
        )
        
        # Customize layout
        fig.update_layout(
            title=title or "Top Gainers and Losers",
            yaxis_title="% Change",
            template=self.theme,
            showlegend=False,
            height=400
        )
        
        return fig
    
    def create_distribution_chart(self, stocks_data, metric='pct_change', title=None):
        """
        Create a histogram showing the distribution of a metric across stocks.
        
        Args:
            stocks_data (dict): Dictionary of stock symbols to their metrics
            metric (str): Metric to visualize distribution for
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly figure object
        """
        # Extract values
        values = []
        for symbol, data in stocks_data.items():
            if isinstance(data, dict) and metric in data:
                values.append(data[metric])
        
        if not values:
            return None
        
        # Create histogram
        fig = go.Figure(
            data=[go.Histogram(
                x=values,
                nbinsx=20,
                marker_color='rgba(0, 128, 255, 0.7)',
                opacity=0.8
            )]
        )
        
        # Add mean line
        mean_value = np.mean(values)
        fig.add_vline(
            x=mean_value, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"Mean: {mean_value:.2f}%",
            annotation_position="top right"
        )
        
        # Customize layout
        fig.update_layout(
            title=title or f"Distribution of {metric}",
            xaxis_title=metric,
            yaxis_title="Count",
            template=self.theme,
            height=400
        )
        
        return fig
