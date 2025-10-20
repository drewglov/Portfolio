"""
Configuration settings for the Day Trading Simulator
"""

import os
from datetime import datetime

# Portfolio Settings
INITIAL_PORTFOLIO_VALUE = 100000  # $100k starting capital
MAX_POSITION_SIZE = 0.02  # 2% of portfolio per trade
MAX_DAILY_RISK = 0.06  # 6% of portfolio risk per day
STOP_LOSS_PERCENTAGE = 0.02  # 2% stop loss
COMMISSION_PER_TRADE = 1.00  # $1 commission per trade

# Trading Hours (EST)
MARKET_OPEN = "09:30"
MARKET_CLOSE = "16:00"
TRADING_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Strategies Configuration
STRATEGIES_PER_DAY = 2  # Number of trades per strategy per day
MIN_TRADE_DURATION = 5  # Minimum minutes to hold a position
MAX_TRADE_DURATION = 240  # Maximum minutes to hold a position (4 hours)

# Risk Management
MAX_CORRELATED_POSITIONS = 3  # Max positions in same sector
MAX_TOTAL_POSITIONS = 10  # Maximum concurrent positions

# Data Settings
DATA_REFRESH_INTERVAL = 30  # seconds
HISTORICAL_DAYS = 30  # Days of historical data to load

# File Paths
DATA_DIR = "data"
LOGS_DIR = "logs"
EXCEL_FILE = "trading_log.xlsx"
CONFIG_FILE = "simulator_config.json"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Market Data
DEFAULT_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD", 
    "NFLX", "CRM", "ADBE", "ORCL", "INTC", "CSCO", "IBM"
]

# Strategy Parameters
MOMENTUM_LOOKBACK = 20
REVERSAL_LOOKBACK = 10
BREAKOUT_LOOKBACK = 15
SCALPING_LOOKBACK = 5
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
