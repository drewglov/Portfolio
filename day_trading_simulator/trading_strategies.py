"""
Day Trading Strategies Implementation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from abc import ABC, abstractmethod
from config import *
from data_feed import MarketDataFeed

logger = logging.getLogger(__name__)

class TradingSignal:
    def __init__(self, action: str, price: float, confidence: float, 
                 stop_loss: float, target_price: float, reason: str):
        self.action = action  # 'BUY', 'SELL', 'HOLD'
        self.price = price
        self.confidence = confidence  # 0-1 scale
        self.stop_loss = stop_loss
        self.target_price = target_price
        self.reason = reason
        self.timestamp = datetime.now()

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.data_feed = None
        
    def set_data_feed(self, data_feed: MarketDataFeed):
        self.data_feed = data_feed
    
    @abstractmethod
    def generate_signal(self, ticker: str) -> Optional[TradingSignal]:
        """Generate trading signal for given ticker"""
        pass
    
    @abstractmethod
    def should_exit(self, ticker: str, entry_price: float, 
                   entry_time: datetime, current_price: float) -> bool:
        """Determine if position should be exited"""
        pass

class MomentumStrategy(BaseStrategy):
    """Momentum trading strategy based on price and volume"""
    
    def __init__(self):
        super().__init__("Momentum", "1.0")
    
    def generate_signal(self, ticker: str) -> Optional[TradingSignal]:
        try:
            hist_data = self.data_feed.get_historical_data(ticker, "30d")
            if len(hist_data) < MOMENTUM_LOOKBACK:
                return None
            
            current_price = self.data_feed.get_current_price(ticker)
            if not current_price:
                return None
            
            # Calculate momentum indicators
            price_change = (hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-MOMENTUM_LOOKBACK]) / hist_data['Close'].iloc[-MOMENTUM_LOOKBACK]
            volume_avg = hist_data['Volume'].rolling(window=MOMENTUM_LOOKBACK).mean().iloc[-1]
            current_volume = hist_data['Volume'].iloc[-1]
            volume_ratio = current_volume / volume_avg if volume_avg > 0 else 1
            
            # RSI momentum
            rsi = hist_data['RSI'].iloc[-1]
            
            # MACD momentum
            macd = hist_data['MACD'].iloc[-1]
            macd_signal = hist_data['MACD_Signal'].iloc[-1]
            macd_histogram = macd - macd_signal
            
            # Generate signals
            if (price_change > 0.03 and  # 3% price increase
                volume_ratio > 1.5 and  # 50% above average volume
                rsi > 50 and rsi < 70 and  # RSI in momentum zone
                macd_histogram > 0):  # MACD bullish
                
                stop_loss = current_price * (1 - STOP_LOSS_PERCENTAGE)
                target_price = current_price * 1.06  # 6% target
                confidence = min(0.9, (price_change * 10 + volume_ratio - 1 + (rsi - 50) / 20) / 3)
                
                return TradingSignal(
                    action="BUY",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Momentum: Price +{price_change:.2%}, Volume {volume_ratio:.1f}x, RSI {rsi:.1f}"
                )
            
            elif (price_change < -0.03 and  # 3% price decrease
                  volume_ratio > 1.5 and  # High volume
                  rsi < 50 and rsi > 30 and  # RSI in bearish momentum
                  macd_histogram < 0):  # MACD bearish
                
                stop_loss = current_price * (1 + STOP_LOSS_PERCENTAGE)
                target_price = current_price * 0.94  # 6% target
                confidence = min(0.9, (abs(price_change) * 10 + volume_ratio - 1 + (50 - rsi) / 20) / 3)
                
                return TradingSignal(
                    action="SELL",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Momentum: Price {price_change:.2%}, Volume {volume_ratio:.1f}x, RSI {rsi:.1f}"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in MomentumStrategy for {ticker}: {e}")
            return None
    
    def should_exit(self, ticker: str, entry_price: float, 
                   entry_time: datetime, current_price: float) -> bool:
        # Exit if position has been held for more than 2 hours
        if datetime.now() - entry_time > timedelta(hours=2):
            return True
        
        # Exit if profit target reached
        profit_pct = (current_price - entry_price) / entry_price
        if profit_pct > 0.06:  # 6% profit target
            return True
        
        # Exit if stop loss hit
        if profit_pct < -STOP_LOSS_PERCENTAGE:
            return True
        
        return False

class ReversalStrategy(BaseStrategy):
    """Mean reversion strategy based on RSI and Bollinger Bands"""
    
    def __init__(self):
        super().__init__("Reversal", "1.0")
    
    def generate_signal(self, ticker: str) -> Optional[TradingSignal]:
        try:
            hist_data = self.data_feed.get_historical_data(ticker, "30d")
            if len(hist_data) < REVERSAL_LOOKBACK:
                return None
            
            current_price = self.data_feed.get_current_price(ticker)
            if not current_price:
                return None
            
            rsi = hist_data['RSI'].iloc[-1]
            bb_upper = hist_data['BB_Upper'].iloc[-1]
            bb_lower = hist_data['BB_Lower'].iloc[-1]
            bb_middle = hist_data['BB_Middle'].iloc[-1]
            
            # Oversold reversal (buy signal)
            if (rsi < RSI_OVERSOLD and 
                current_price <= bb_lower and
                current_price < bb_middle):
                
                stop_loss = current_price * (1 - STOP_LOSS_PERCENTAGE * 1.5)  # Wider stop for reversal
                target_price = bb_middle  # Target middle band
                confidence = min(0.85, (RSI_OVERSOLD - rsi) / RSI_OVERSOLD + 0.3)
                
                return TradingSignal(
                    action="BUY",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Reversal: RSI {rsi:.1f} oversold, Price at BB Lower {current_price:.2f}"
                )
            
            # Overbought reversal (sell signal)
            elif (rsi > RSI_OVERBOUGHT and 
                  current_price >= bb_upper and
                  current_price > bb_middle):
                
                stop_loss = current_price * (1 + STOP_LOSS_PERCENTAGE * 1.5)  # Wider stop for reversal
                target_price = bb_middle  # Target middle band
                confidence = min(0.85, (rsi - RSI_OVERBOUGHT) / (100 - RSI_OVERBOUGHT) + 0.3)
                
                return TradingSignal(
                    action="SELL",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Reversal: RSI {rsi:.1f} overbought, Price at BB Upper {current_price:.2f}"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in ReversalStrategy for {ticker}: {e}")
            return None
    
    def should_exit(self, ticker: str, entry_price: float, 
                   entry_time: datetime, current_price: float) -> bool:
        # Exit if position has been held for more than 3 hours
        if datetime.now() - entry_time > timedelta(hours=3):
            return True
        
        # Exit if mean reversion target reached
        profit_pct = (current_price - entry_price) / entry_price
        if profit_pct > 0.04:  # 4% profit target for reversal
            return True
        
        # Exit if stop loss hit
        if profit_pct < -STOP_LOSS_PERCENTAGE * 1.5:
            return True
        
        return False

class BreakoutStrategy(BaseStrategy):
    """Breakout strategy based on support/resistance levels"""
    
    def __init__(self):
        super().__init__("Breakout", "1.0")
    
    def generate_signal(self, ticker: str) -> Optional[TradingSignal]:
        try:
            hist_data = self.data_feed.get_historical_data(ticker, "30d")
            if len(hist_data) < BREAKOUT_LOOKBACK:
                return None
            
            current_price = self.data_feed.get_current_price(ticker)
            if not current_price:
                return None
            
            # Calculate support and resistance levels
            recent_highs = hist_data['High'].rolling(window=5).max()
            recent_lows = hist_data['Low'].rolling(window=5).min()
            
            resistance = recent_highs.iloc[-BREAKOUT_LOOKBACK:].max()
            support = recent_lows.iloc[-BREAKOUT_LOOKBACK:].min()
            
            # Volume confirmation
            volume_avg = hist_data['Volume'].rolling(window=BREAKOUT_LOOKBACK).mean().iloc[-1]
            current_volume = hist_data['Volume'].iloc[-1]
            volume_ratio = current_volume / volume_avg if volume_avg > 0 else 1
            
            # Breakout above resistance (buy signal)
            if (current_price > resistance * 1.001 and  # 0.1% above resistance
                volume_ratio > 1.3):  # 30% above average volume
                
                stop_loss = resistance * 0.998  # Just below resistance
                target_price = current_price + (current_price - resistance) * 2  # 2:1 risk/reward
                confidence = min(0.9, volume_ratio / 2 + 0.4)
                
                return TradingSignal(
                    action="BUY",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Breakout: Price {current_price:.2f} > Resistance {resistance:.2f}, Volume {volume_ratio:.1f}x"
                )
            
            # Breakdown below support (sell signal)
            elif (current_price < support * 0.999 and  # 0.1% below support
                  volume_ratio > 1.3):  # 30% above average volume
                
                stop_loss = support * 1.002  # Just above support
                target_price = current_price - (support - current_price) * 2  # 2:1 risk/reward
                confidence = min(0.9, volume_ratio / 2 + 0.4)
                
                return TradingSignal(
                    action="SELL",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Breakdown: Price {current_price:.2f} < Support {support:.2f}, Volume {volume_ratio:.1f}x"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in BreakoutStrategy for {ticker}: {e}")
            return None
    
    def should_exit(self, ticker: str, entry_price: float, 
                   entry_time: datetime, current_price: float) -> bool:
        # Exit if position has been held for more than 4 hours
        if datetime.now() - entry_time > timedelta(hours=4):
            return True
        
        # Exit if profit target reached (2:1 risk/reward)
        profit_pct = (current_price - entry_price) / entry_price
        if profit_pct > 0.08:  # 8% profit target
            return True
        
        # Exit if stop loss hit
        if profit_pct < -STOP_LOSS_PERCENTAGE:
            return True
        
        return False

class ScalpingStrategy(BaseStrategy):
    """Scalping strategy for quick profits on small price movements"""
    
    def __init__(self):
        super().__init__("Scalping", "1.0")
    
    def generate_signal(self, ticker: str) -> Optional[TradingSignal]:
        try:
            hist_data = self.data_feed.get_historical_data(ticker, "5d")
            if len(hist_data) < SCALPING_LOOKBACK:
                return None
            
            current_price = self.data_feed.get_current_price(ticker)
            if not current_price:
                return None
            
            # Use shorter timeframes for scalping
            sma_5 = hist_data['Close'].rolling(window=5).mean().iloc[-1]
            sma_10 = hist_data['Close'].rolling(window=10).mean().iloc[-1]
            
            # Quick momentum signals
            price_change_1min = (current_price - hist_data['Close'].iloc[-2]) / hist_data['Close'].iloc[-2]
            price_change_5min = (current_price - hist_data['Close'].iloc[-6]) / hist_data['Close'].iloc[-6]
            
            # Buy signal: quick upward momentum
            if (price_change_1min > 0.002 and  # 0.2% in 1 minute
                price_change_5min > 0.005 and  # 0.5% in 5 minutes
                current_price > sma_5 > sma_10):
                
                stop_loss = current_price * (1 - 0.005)  # 0.5% stop loss
                target_price = current_price * 1.01  # 1% target
                confidence = min(0.8, price_change_1min * 100 + price_change_5min * 50)
                
                return TradingSignal(
                    action="BUY",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Scalp: +{price_change_1min:.2%} 1min, +{price_change_5min:.2%} 5min"
                )
            
            # Sell signal: quick downward momentum
            elif (price_change_1min < -0.002 and  # 0.2% down in 1 minute
                  price_change_5min < -0.005 and  # 0.5% down in 5 minutes
                  current_price < sma_5 < sma_10):
                
                stop_loss = current_price * (1 + 0.005)  # 0.5% stop loss
                target_price = current_price * 0.99  # 1% target
                confidence = min(0.8, abs(price_change_1min) * 100 + abs(price_change_5min) * 50)
                
                return TradingSignal(
                    action="SELL",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Scalp: {price_change_1min:.2%} 1min, {price_change_5min:.2%} 5min"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in ScalpingStrategy for {ticker}: {e}")
            return None
    
    def should_exit(self, ticker: str, entry_price: float, 
                   entry_time: datetime, current_price: float) -> bool:
        # Exit if position has been held for more than 30 minutes
        if datetime.now() - entry_time > timedelta(minutes=30):
            return True
        
        # Exit if profit target reached
        profit_pct = (current_price - entry_price) / entry_price
        if profit_pct > 0.01:  # 1% profit target
            return True
        
        # Exit if stop loss hit
        if profit_pct < -0.005:  # 0.5% stop loss
            return True
        
        return False

class GapStrategy(BaseStrategy):
    """Gap trading strategy for opening gaps"""
    
    def __init__(self):
        super().__init__("Gap", "1.0")
    
    def generate_signal(self, ticker: str) -> Optional[TradingSignal]:
        try:
            hist_data = self.data_feed.get_historical_data(ticker, "5d")
            if len(hist_data) < 2:
                return None
            
            current_price = self.data_feed.get_current_price(ticker)
            if not current_price:
                return None
            
            # Calculate gap
            prev_close = hist_data['Close'].iloc[-2]  # Previous day close
            gap_size = (current_price - prev_close) / prev_close
            
            # Only trade significant gaps (>2%)
            if abs(gap_size) < 0.02:
                return None
            
            # Gap up (buy signal)
            if gap_size > 0.02:  # 2% gap up
                stop_loss = prev_close  # Stop at previous close
                target_price = current_price * 1.03  # 3% target from gap open
                confidence = min(0.9, gap_size * 20)
                
                return TradingSignal(
                    action="BUY",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Gap Up: {gap_size:.2%} gap from {prev_close:.2f} to {current_price:.2f}"
                )
            
            # Gap down (sell signal)
            elif gap_size < -0.02:  # 2% gap down
                stop_loss = prev_close  # Stop at previous close
                target_price = current_price * 0.97  # 3% target from gap open
                confidence = min(0.9, abs(gap_size) * 20)
                
                return TradingSignal(
                    action="SELL",
                    price=current_price,
                    confidence=confidence,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    reason=f"Gap Down: {gap_size:.2%} gap from {prev_close:.2f} to {current_price:.2f}"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in GapStrategy for {ticker}: {e}")
            return None
    
    def should_exit(self, ticker: str, entry_price: float, 
                   entry_time: datetime, current_price: float) -> bool:
        # Exit if position has been held for more than 2 hours
        if datetime.now() - entry_time > timedelta(hours=2):
            return True
        
        # Exit if profit target reached
        profit_pct = (current_price - entry_price) / entry_price
        if profit_pct > 0.03:  # 3% profit target
            return True
        
        # Exit if stop loss hit
        if profit_pct < -0.03:  # 3% stop loss for gaps
            return True
        
        return False

class StrategyManager:
    """Manages all trading strategies"""
    
    def __init__(self, data_feed: MarketDataFeed):
        self.data_feed = data_feed
        self.strategies = {
            "Momentum": MomentumStrategy(),
            "Reversal": ReversalStrategy(),
            "Breakout": BreakoutStrategy(),
            "Scalping": ScalpingStrategy(),
            "Gap": GapStrategy()
        }
        
        # Set data feed for all strategies
        for strategy in self.strategies.values():
            strategy.set_data_feed(data_feed)
    
    def get_all_signals(self, ticker: str) -> Dict[str, TradingSignal]:
        """Get signals from all strategies for a ticker"""
        signals = {}
        for name, strategy in self.strategies.items():
            try:
                signal = strategy.generate_signal(ticker)
                if signal and signal.confidence > 0.6:  # Only high-confidence signals
                    signals[name] = signal
            except Exception as e:
                logger.error(f"Error getting signal from {name} for {ticker}: {e}")
        
        return signals
    
    def get_best_signal(self, ticker: str) -> Optional[Tuple[str, TradingSignal]]:
        """Get the best signal (highest confidence) for a ticker"""
        signals = self.get_all_signals(ticker)
        if not signals:
            return None
        
        best_strategy = max(signals.keys(), key=lambda x: signals[x].confidence)
        return best_strategy, signals[best_strategy]
    
    def should_exit_position(self, ticker: str, strategy_name: str, 
                           entry_price: float, entry_time: datetime, 
                           current_price: float) -> bool:
        """Check if position should be exited based on strategy"""
        if strategy_name in self.strategies:
            return self.strategies[strategy_name].should_exit(
                ticker, entry_price, entry_time, current_price
            )
        return False
