import requests
import pandas as pd
import ta



def get_stock_data(symbol, api_key):
    """
    Fetches fundamental and technical data for a given stock symbol.
    
    Parameters:
    - symbol: The stock symbol (e.g., "AAPL" for Apple)
    - api_key: Your Alpha Vantage API key
    
    Returns:
    - dict: Dictionary containing the stock's metrics
    """
    base_url = "https://www.alphavantage.co/query"
    
    # Fetch fundamental data
    fundamentals_url = f"{base_url}?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
    fundamentals_response = requests.get(fundamentals_url).json()
    
    # Fetch technical data (Daily prices)
    technicals_url = f"{base_url}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    technicals_response = requests.get(technicals_url).json()
    
    # Parse fundamental data
    fundamental_data = {
        'ROA': float(fundamentals_response.get('ReturnOnAssetsTTM', 0)),
        'ROE': float(fundamentals_response.get('ReturnOnEquityTTM', 0)),
        'ROI': float(fundamentals_response.get('ReturnOnInvestmentTTM', 0)),
        'P/E': float(fundamentals_response.get('PERatio', 0)),
        'D/E': float(fundamentals_response.get('DebtToEquity', 0)),
        'Current Ratio': float(fundamentals_response.get('CurrentRatio', 0)),
        'EPS Growth': float(fundamentals_response.get('EPSGrowth5Y', 0))
    }
    
    # Parse technical data (RSI calculation)
    technical_data = pd.DataFrame.from_dict(technicals_response['Time Series (Daily)'], orient='index')
    technical_data = technical_data.astype(float)
    technical_data['RSI'] = ta.momentum.RSIIndicator(close=technical_data['4. close'], window=90).rsi()
    
    # Recent performance
    recent_performance = (technical_data['4. close'].iloc[-1] - technical_data['4. close'].iloc[-30]) / technical_data['4. close'].iloc[-30] * 100
    
    # Latest RSI value
    latest_rsi = technical_data['RSI'].iloc[-1]
    
    return {**fundamental_data, 'RSI': latest_rsi, 'Recent Performance': recent_performance}

def is_good_time_to_buy_stock(symbol, api_key):
    """
    Determines if it is a good time to buy a stock based on various metrics.
    
    Parameters:
    - symbol: The stock symbol (e.g., "AAPL" for Apple)
    - api_key: Your Alpha Vantage API key
    
    Returns:
    - bool: True if it is a good time to buy, False otherwise
    - dict: Dictionary containing the stock's metrics
    """
    
    stock_data = get_stock_data(symbol, api_key)
    
    # Define thresholds for decision-making
    roa_threshold = 5.0
    roe_threshold = 10.0
    roi_threshold = 7.0
    rsi_oversold = 30
    pe_threshold = 20
    de_threshold = 1.0
    current_ratio_threshold = 1.5
    eps_growth_threshold = 5.0
    recent_performance_threshold = -5.0  # stock underperformed the market by 5%
    
    # Check fundamental indicators
    fundamental_conditions = (
        stock_data['ROA'] >= roa_threshold and
        stock_data['ROE'] >= roe_threshold and
        stock_data['ROI'] >= roi_threshold and
        stock_data['P/E'] < pe_threshold and
        stock_data['D/E'] <= de_threshold and
        stock_data['Current Ratio'] >= current_ratio_threshold and stock_data['EPS Growth'] >= eps_growth_threshold
    )
    
    # Check technical indicators
    technical_conditions = (
        stock_data['RSI'] < rsi_oversold and
        stock_data['Recent Performance'] < recent_performance_threshold
    )
    
    # Determine if it's a good time to buy
    is_good_time = fundamental_conditions and technical_conditions
    return is_good_time, stock_data


# Example usage:
api_key = "1JDSQ58C13IVWU48"
symbol = "NVDA"
is_good_time, stock_data = is_good_time_to_buy_stock(symbol, api_key)
print(f"Is it a good time to buy {symbol}? {'Yes' if is_good_time else 'No'}")
print("Stock Data:", stock_data)