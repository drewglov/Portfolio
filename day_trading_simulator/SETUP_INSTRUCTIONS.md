# Day Trading Simulator - Setup Instructions

## Quick Start Guide

### 1. Folder Structure
Save all files in a folder called `day_trading_simulator` with this structure:

```
day_trading_simulator/
├── main_simulator.py          # Main simulator (interactive)
├── run_simulator.py          # Simple auto-run version
├── config.py                 # Configuration settings
├── data_feed.py             # Market data feed
├── trading_strategies.py    # All 5 trading strategies
├── portfolio_manager.py     # Portfolio & risk management
├── excel_logger.py          # Excel logging system
├── analyze_results.py       # Results analysis tool
├── setup.py                # Setup helper script
├── requirements.txt        # Python dependencies
├── README.md              # Detailed documentation
└── SETUP_INSTRUCTIONS.md  # This file
```

### 2. Installation Steps

**Step 1: Create the folder**
```bash
mkdir day_trading_simulator
cd day_trading_simulator
```

**Step 2: Copy all files**
Copy all the Python files and requirements.txt into this folder.

**Step 3: Install dependencies**

**Option A: Use the improved installer**
```bash
python install_packages.py
```

**Option B: Use the original setup**
```bash
python setup.py
```

**Option C: Manual installation (if above fails)**
```bash
pip install yfinance pandas numpy openpyxl requests schedule matplotlib seaborn
```

**Option D: If you have conda**
```bash
conda install pandas numpy matplotlib seaborn
pip install yfinance openpyxl requests schedule
```

**Step 4: Run the simulator**
```bash
python main_simulator.py
```

### 3. Running Options

**Option A: Interactive Mode (Recommended)**
```bash
python main_simulator.py
```
Then use commands:
- `start` - Start simulation
- `status` - Check performance
- `stop` - Stop simulation

**Option B: Auto-Run Mode**
```bash
python run_simulator.py
```
Automatically starts and runs until you press Ctrl+C.

### 4. What the Simulator Does

**Trading Strategies (2 trades per day each):**
1. **Momentum** - Trades strong price moves with volume
2. **Reversal** - Trades oversold/overbought conditions
3. **Breakout** - Trades support/resistance breaks
4. **Scalping** - Quick trades for small profits
5. **Gap** - Trades opening gaps

**Risk Management:**
- $100,000 starting capital
- 2% maximum position size
- 6% maximum daily risk
- Automatic stop losses
- Maximum 10 concurrent positions

**Data Tracking:**
- All trades logged to Excel automatically
- Real-time market data from Yahoo Finance
- Comprehensive performance metrics
- Detailed trade records with all requested fields

### 5. Output Files

**Excel File: `trading_log.xlsx`**
- Trading Log sheet with all trade data
- Summary sheet with key metrics
- Performance sheet with daily tracking

**Log Files: `logs/simulator.log`**
- Detailed system logs
- Trade executions
- Error messages

### 6. Analysis

**View Results:**
1. Open `trading_log.xlsx` in Excel
2. Check the Summary sheet for overall performance
3. Analyze individual trades in the Trading Log sheet

**Advanced Analysis:**
```bash
python analyze_results.py
```
Generates detailed performance charts and statistics.

### 7. Configuration

Edit `config.py` to customize:
- Starting capital
- Risk parameters
- Trading tickers
- Strategy settings

### 8. Troubleshooting

**Common Issues:**

1. **"pip subprocess to install build dependencies did not run successfully"**
   - Try: `python install_packages.py` (new installer)
   - Or: `pip install --user yfinance pandas numpy openpyxl`
   - Or: Use conda if available

2. **"No module named 'yfinance'"**
   ```bash
   pip install yfinance
   ```

3. **Excel file locked**
   - Close Excel if it's open
   - Check file permissions

4. **No trades happening**
   - Normal during low volatility
   - Check market hours (9:30 AM - 4:00 PM EST)
   - Verify internet connection

5. **Permission errors**
   - Run as administrator (Windows)
   - Check folder permissions
   - Try: `pip install --user package_name`

### 9. Expected Results

**After 1 week:**
- 50+ trades across all strategies
- Performance data in Excel
- Strategy comparison data

**After 1 month:**
- 200+ trades
- Clear strategy performance patterns
- Sufficient data for analysis

**After 3 months:**
- 600+ trades
- Statistical significance
- Clear winning/losing strategies

### 10. Next Steps

1. **Run for several weeks** to gather data
2. **Analyze Excel results** to identify winning strategies
3. **Adjust parameters** in config.py based on results
4. **Focus on profitable strategies** for future runs
5. **Consider real trading** (with proper risk management)

## Important Notes

- **Paper Trading Only**: No real money at risk
- **Market Hours**: Best results during trading hours (9:30 AM - 4:00 PM EST)
- **Internet Required**: Needs connection for market data
- **Patience**: Let it run for weeks to get meaningful data
- **Analysis**: Regular review of results is important

## Support

If you encounter issues:
1. Check the logs in the `logs/` folder
2. Verify all dependencies are installed
3. Ensure market data connectivity
4. Review the configuration settings

The simulator is designed to be robust and will handle most market conditions automatically.
