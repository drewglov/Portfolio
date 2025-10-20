# Day Trading Simulator

A comprehensive day trading simulation system that tests multiple trading strategies with realistic market data and detailed performance tracking.

## Features

- **Real-time Market Data**: Uses yfinance for live market data
- **Multiple Trading Strategies**: 
  - Momentum Trading
  - Mean Reversion (Reversal)
  - Breakout Trading
  - Scalping
  - Gap Trading
- **Risk Management**: Position sizing, stop losses, daily risk limits
- **Portfolio Management**: $100k starting capital with realistic constraints
- **Excel Logging**: Comprehensive trade tracking with all requested fields
- **Performance Analytics**: Win rates, profit factors, drawdown tracking

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Setup Instructions

1. **Create Project Directory**
   ```bash
   mkdir day_trading_simulator
   cd day_trading_simulator
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   python main_simulator.py
   ```

## Project Structure

```
day_trading_simulator/
├── main_simulator.py          # Main simulator engine
├── config.py                  # Configuration settings
├── data_feed.py              # Market data feed (yfinance)
├── trading_strategies.py     # All trading strategies
├── portfolio_manager.py      # Portfolio and risk management
├── excel_logger.py          # Excel logging system
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── data/                   # Market data cache (auto-created)
├── logs/                   # Log files (auto-created)
└── trading_log.xlsx       # Excel output file (auto-created)
```

## Usage

### Starting the Simulator

1. **Run the main script**:
   ```bash
   python main_simulator.py
   ```

2. **Use the interactive commands**:
   - `start` - Start the trading simulation
   - `stop` - Stop the simulation
   - `status` - Show current portfolio status
   - `close` - Force close all positions
   - `exit` - Exit the program

### Example Session

```
Day Trading Simulator
====================
Commands:
  start - Start simulation
  stop - Stop simulation
  status - Show current status
  close - Force close all positions
  exit - Exit program

Enter command: start
Simulation started. Press Ctrl+C to stop or enter 'stop' command.

Enter command: status

Current Status:
  Running: True
  Market Open: True
  Current Capital: $98,450.00
  Open Positions: 3
  Total Trades: 15
  Win Rate: 60.0%
  Net Profit: $1,450.00
```

## Trading Strategies

### 1. Momentum Strategy
- **Entry**: Strong price momentum with high volume
- **Exit**: 6% profit target or 2% stop loss
- **Hold Time**: Up to 2 hours

### 2. Reversal Strategy
- **Entry**: RSI oversold/overbought with Bollinger Band confirmation
- **Exit**: 4% profit target or 3% stop loss
- **Hold Time**: Up to 3 hours

### 3. Breakout Strategy
- **Entry**: Price breaks above resistance or below support with volume
- **Exit**: 2:1 risk/reward ratio or 2% stop loss
- **Hold Time**: Up to 4 hours

### 4. Scalping Strategy
- **Entry**: Quick momentum signals (0.2%+ in 1 minute)
- **Exit**: 1% profit target or 0.5% stop loss
- **Hold Time**: Up to 30 minutes

### 5. Gap Strategy
- **Entry**: Significant opening gaps (>2%)
- **Exit**: 3% profit target or 3% stop loss
- **Hold Time**: Up to 2 hours

## Risk Management

- **Position Size**: Maximum 2% of portfolio per trade
- **Daily Risk**: Maximum 6% of portfolio risk per day
- **Stop Losses**: Automatic stop loss on all positions
- **Maximum Positions**: 10 concurrent positions
- **Sector Limits**: Maximum 3 positions in same sector

## Excel Output

The system automatically creates and updates `trading_log.xlsx` with the following sheets:

### Trading Log Sheet
Contains all trade data with these columns:
- Date, Ticker, Market Direction, Strategy
- Entry/Exit Times and Prices
- Stop Loss, Shares, Total Price
- Account Size, Risk Amount, Portfolio Risk %
- Gross P/L, Return %, R Multiple
- Trade Duration, Win/Loss, Setup Quality
- Order ID, Commission, Slippage
- ATR at Entry, Entry/Exit Signals
- Notes, Closing Notes, Cumulative P/L

### Summary Sheet
Key performance metrics:
- Total Trades, Win Rate, Profit Factor
- Average Win/Loss, Max Drawdown
- Sharpe Ratio, Last Updated

### Performance Sheet
Daily performance tracking:
- Daily P/L, Cumulative P/L, Drawdown
- Trades by Strategy

## Configuration

Edit `config.py` to customize:

```python
# Portfolio Settings
INITIAL_PORTFOLIO_VALUE = 100000  # Starting capital
MAX_POSITION_SIZE = 0.02         # 2% per trade
MAX_DAILY_RISK = 0.06           # 6% daily risk

# Trading Settings
STRATEGIES_PER_DAY = 2          # Trades per strategy per day
STOP_LOSS_PERCENTAGE = 0.02     # 2% stop loss

# Market Data
DEFAULT_TICKERS = [             # Tickers to trade
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"
]
```

## Logging

The system creates detailed logs in the `logs/` directory:
- `simulator.log` - Main application log
- Logs include trade executions, errors, and system status

## Performance Analysis

After running the simulator for several weeks/months:

1. **Open `trading_log.xlsx`**
2. **Analyze the Summary sheet** for overall performance
3. **Compare strategies** using the Performance sheet
4. **Identify winning patterns** from individual trades
5. **Adjust strategy parameters** in `config.py`

## Troubleshooting

### Common Issues

1. **"No module named 'yfinance'"**
   ```bash
   pip install yfinance
   ```

2. **"Permission denied" on Excel file**
   - Close Excel if it's open
   - Check file permissions

3. **"Market data not updating"**
   - Check internet connection
   - Verify market hours (9:30 AM - 4:00 PM EST)

4. **"No trading opportunities found"**
   - This is normal during low volatility periods
   - Strategies only trade high-confidence signals

### Performance Tips

1. **Run during market hours** for best results
2. **Monitor logs** for any errors
3. **Check Excel file** regularly for data
4. **Adjust strategy parameters** based on results

## Safety Features

- **Paper Trading Only**: No real money at risk
- **Automatic Stop Losses**: All positions protected
- **Risk Limits**: Multiple safety checks
- **Force Close**: Emergency exit option
- **Detailed Logging**: Full audit trail

## Legal Disclaimer

This is a simulation tool for educational purposes only. It does not provide financial advice and should not be used for real trading without proper risk management and professional guidance.

## Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Review the configuration in `config.py`
3. Ensure all dependencies are installed
4. Verify market data connectivity

## Future Enhancements

Potential improvements:
- Additional trading strategies
- Machine learning integration
- Real-time alerts
- Web dashboard
- Backtesting capabilities
- Options trading support
