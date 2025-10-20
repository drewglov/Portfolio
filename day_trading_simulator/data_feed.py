"""
Real-time market data feed using yfinance
"""

import yfinance as yf
import pandas as pd
import numpy as np
import time
import threading
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from config import *

logger = logging.getLogger(__name__)

class MarketDataFeed:
    def __init__(self, tickers: List[str] = None):
        self.tickers = tickers or DEFAULT_TICKERS
        self.data_cache = {}
        self.realtime_data = {}
        self.is_running = False
        self.thread = None
        
    def start_feed(self):
        """Start the real-time data feed in a separate thread"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._update_loop)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Market data feed started")
    
    def stop_feed(self):
        """Stop the real-time data feed"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info("Market data feed stopped")
    
    def _update_loop(self):
        """Main loop for updating market data"""
        while self.is_running:
            try:
                self._fetch_realtime_data()
                time.sleep(DATA_REFRESH_INTERVAL)
            except Exception as e:
                logger.error(f"Error in data feed loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _fetch_realtime_data(self):
        """Fetch real-time data for all tickers"""
        try:
            for ticker in self.tickers:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1d", interval="1m")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    volume = hist['Volume'].iloc[-1]
                    high = hist['High'].iloc[-1]
                    low = hist['Low'].iloc[-1]
                    
                    self.realtime_data[ticker] = {
                        'price': float(current_price),
                        'volume': int(volume),
                        'high': float(high),
                        'low': float(low),
                        'timestamp': datetime.now(),
                        'market_cap': info.get('marketCap', 0),
                        'sector': info.get('sector', 'Unknown'),
                        'industry': info.get('industry', 'Unknown')
                    }
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current price for a ticker"""
        if ticker in self.realtime_data:
            return self.realtime_data[ticker]['price']
        return None
    
    def get_historical_data(self, ticker: str, period: str = "30d") -> pd.DataFrame:
        """Get historical data for a ticker"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            # Calculate technical indicators
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['RSI'] = self._calculate_rsi(data['Close'])
            data['MACD'] = self._calculate_macd(data['Close'])
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            data['ATR'] = self._calculate_atr(data)
            data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = self._calculate_bollinger_bands(data['Close'])
            
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {e}")
            return pd.DataFrame()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # Fill NaN values with neutral RSI
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd.fillna(0)  # Fill NaN values with 0
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean()
        return atr.fillna(true_range.mean())  # Fill NaN with average true range
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> tuple:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        # Fill NaN values
        sma = sma.fillna(prices.mean())
        upper_band = upper_band.fillna(prices.mean() * (1 + std_dev * 0.1))
        lower_band = lower_band.fillna(prices.mean() * (1 - std_dev * 0.1))
        
        return upper_band, sma, lower_band
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A")
        
        return (current_day in TRADING_DAYS and 
                MARKET_OPEN <= current_time <= MARKET_CLOSE)
    
    def get_market_direction(self, ticker: str) -> str:
        """Determine market direction based on recent price action"""
        try:
            hist = self.get_historical_data(ticker, "5d")
            if len(hist) < 2:
                return "Neutral"
            
            recent_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
            
            if recent_change > 0.02:  # 2% gain
                return "Bullish"
            elif recent_change < -0.02:  # 2% loss
                return "Bearish"
            else:
                return "Neutral"
        except Exception as e:
            logger.error(f"Error determining market direction for {ticker}: {e}")
            return "Neutral"
    
    def get_ticker_info(self, ticker: str) -> Dict:
        """Get comprehensive ticker information"""
        if ticker in self.realtime_data:
            return self.realtime_data[ticker]
        return {}
