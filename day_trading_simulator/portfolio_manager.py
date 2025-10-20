"""
Portfolio Management System with Risk Assessment
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from config import *
from data_feed import MarketDataFeed

logger = logging.getLogger(__name__)

@dataclass
class Position:
    ticker: str
    strategy: str
    action: str  # 'BUY' or 'SELL'
    shares: int
    entry_price: float
    entry_time: datetime
    stop_loss: float
    target_price: float
    order_id: str
    setup_quality: int = 3  # 1-5 scale
    notes: str = ""

@dataclass
class Trade:
    date: str
    ticker: str
    market_direction: str
    strategy: str
    strategy_version: str
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price_intended: float
    entry_fill_price: float
    exit_price_intended: Optional[float]
    exit_fill_price: Optional[float]
    stop_loss_price: float
    shares: int
    total_price: float
    account_size: float
    risk_amount: float
    portfolio_risk_pct: float
    gross_pl: Optional[float]
    return_pct: Optional[float]
    r_multiple: Optional[float]
    trade_duration_min: Optional[int]
    win_loss: Optional[str]
    setup_quality: int
    order_id: str
    commission: float
    slippage: float
    atr_at_entry: float
    entry_signal: str
    exit_signal: str
    notes: str
    closing_notes: str
    cumulative_pl: float

class PortfolioManager:
    def __init__(self, initial_capital: float = INITIAL_PORTFOLIO_VALUE):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # {order_id: Position}
        self.completed_trades = []
        self.daily_risk_used = 0.0
        self.last_reset_date = datetime.now().date()
        
        # Risk tracking
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        self.peak_capital = initial_capital
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        
    def reset_daily_risk(self):
        """Reset daily risk tracking at start of new day"""
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_risk_used = 0.0
            self.last_reset_date = current_date
            logger.info(f"Daily risk reset for {current_date}")
    
    def can_take_position(self, risk_amount: float, ticker: str) -> Tuple[bool, str]:
        """Check if we can take a new position based on risk limits"""
        self.reset_daily_risk()
        
        # Check daily risk limit
        if self.daily_risk_used + risk_amount > self.current_capital * MAX_DAILY_RISK:
            return False, f"Daily risk limit exceeded. Used: {self.daily_risk_used:.2f}, Attempting: {risk_amount:.2f}"
        
        # Check maximum positions
        if len(self.positions) >= MAX_TOTAL_POSITIONS:
            return False, f"Maximum positions reached: {len(self.positions)}"
        
        # Check position size limit
        position_value = risk_amount / (STOP_LOSS_PERCENTAGE / 100)  # Calculate position size
        if position_value > self.current_capital * MAX_POSITION_SIZE:
            return False, f"Position size too large: {position_value:.2f} > {self.current_capital * MAX_POSITION_SIZE:.2f}"
        
        # Check correlated positions (same sector)
        sector_positions = self._count_sector_positions(ticker)
        if sector_positions >= MAX_CORRELATED_POSITIONS:
            return False, f"Too many positions in same sector: {sector_positions}"
        
        return True, "OK"
    
    def _count_sector_positions(self, ticker: str) -> int:
        """Count positions in the same sector as the given ticker"""
        # This would need market data to determine sector
        # For now, we'll use a simple approach
        return len(self.positions)
    
    def calculate_position_size(self, ticker: str, entry_price: float, 
                              stop_loss: float, risk_per_trade: float) -> Tuple[int, float]:
        """Calculate optimal position size based on risk management"""
        try:
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            if risk_per_share <= 0:
                return 0, 0.0
            
            # Calculate shares based on risk amount
            shares = int(risk_per_trade / risk_per_share)
            
            # Apply position size limits
            max_shares_by_capital = int((self.current_capital * MAX_POSITION_SIZE) / entry_price)
            shares = min(shares, max_shares_by_capital)
            
            # Calculate actual risk amount
            actual_risk = shares * risk_per_share
            total_cost = shares * entry_price
            
            return shares, actual_risk
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0, 0.0
    
    def open_position(self, ticker: str, strategy: str, signal_action: str,
                     entry_price: float, stop_loss: float, target_price: float,
                     risk_amount: float, setup_quality: int = 3, 
                     notes: str = "") -> Optional[str]:
        """Open a new position"""
        try:
            # Check if we can take the position
            can_trade, reason = self.can_take_position(risk_amount, ticker)
            if not can_trade:
                logger.warning(f"Cannot open position in {ticker}: {reason}")
                return None
            
            # Calculate position size
            shares, actual_risk = self.calculate_position_size(
                ticker, entry_price, stop_loss, risk_amount
            )
            
            if shares <= 0:
                logger.warning(f"Invalid position size for {ticker}")
                return None
            
            # Create order ID
            order_id = f"{ticker}_{strategy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create position
            position = Position(
                ticker=ticker,
                strategy=strategy,
                action=signal_action,
                shares=shares,
                entry_price=entry_price,
                entry_time=datetime.now(),
                stop_loss=stop_loss,
                target_price=target_price,
                order_id=order_id,
                setup_quality=setup_quality,
                notes=notes
            )
            
            # Add to positions
            self.positions[order_id] = position
            
            # Update risk tracking
            self.daily_risk_used += actual_risk
            
            # Calculate costs
            total_cost = shares * entry_price
            commission = COMMISSION_PER_TRADE
            
            # Update capital (for short positions, we'd add to capital)
            if signal_action == "BUY":
                self.current_capital -= total_cost + commission
            else:  # SELL (short)
                self.current_capital += total_cost - commission
            
            logger.info(f"Opened {signal_action} position in {ticker}: {shares} shares @ ${entry_price:.2f}, Risk: ${actual_risk:.2f}")
            
            return order_id
            
        except Exception as e:
            logger.error(f"Error opening position: {e}")
            return None
    
    def close_position(self, order_id: str, exit_price: float, 
                      exit_reason: str = "Manual") -> Optional[Trade]:
        """Close an existing position and create trade record"""
        try:
            if order_id not in self.positions:
                logger.error(f"Position {order_id} not found")
                return None
            
            position = self.positions[order_id]
            exit_time = datetime.now()
            
            # Calculate trade metrics
            if position.action == "BUY":
                gross_pl = (exit_price - position.entry_price) * position.shares
                return_pct = (exit_price - position.entry_price) / position.entry_price
            else:  # SELL (short)
                gross_pl = (position.entry_price - exit_price) * position.shares
                return_pct = (position.entry_price - exit_price) / position.entry_price
            
            # Calculate additional metrics
            commission = COMMISSION_PER_TRADE
            slippage = abs(exit_price - position.target_price) if position.target_price else 0.0
            trade_duration = (exit_time - position.entry_time).total_seconds() / 60
            
            # Calculate R multiple
            risk_amount = abs(position.entry_price - position.stop_loss) * position.shares
            r_multiple = gross_pl / risk_amount if risk_amount > 0 else 0
            
            # Determine win/loss
            win_loss = "Win" if gross_pl > 0 else "Loss"
            
            # Update performance metrics
            self.total_trades += 1
            if gross_pl > 0:
                self.winning_trades += 1
                self.total_profit += gross_pl
            else:
                self.losing_trades += 1
                self.total_loss += abs(gross_pl)
            
            # Update capital
            if position.action == "BUY":
                self.current_capital += exit_price * position.shares - commission
            else:  # SELL (short)
                self.current_capital -= exit_price * position.shares + commission
            
            # Update drawdown tracking
            if self.current_capital > self.peak_capital:
                self.peak_capital = self.current_capital
                self.current_drawdown = 0.0
            else:
                self.current_drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
                self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
            
            # Create trade record
            trade = Trade(
                date=position.entry_time.strftime("%Y-%m-%d"),
                ticker=position.ticker,
                market_direction="",  # Will be filled by simulator
                strategy=position.strategy,
                strategy_version="1.0",
                entry_time=position.entry_time,
                exit_time=exit_time,
                entry_price_intended=position.entry_price,
                entry_fill_price=position.entry_price,  # Assuming no slippage on entry
                exit_price_intended=position.target_price,
                exit_fill_price=exit_price,
                stop_loss_price=position.stop_loss,
                shares=position.shares,
                total_price=position.entry_price * position.shares,
                account_size=self.current_capital,
                risk_amount=risk_amount,
                portfolio_risk_pct=(risk_amount / self.current_capital) * 100,
                gross_pl=gross_pl,
                return_pct=return_pct * 100,
                r_multiple=r_multiple,
                trade_duration_min=int(trade_duration),
                win_loss=win_loss,
                setup_quality=position.setup_quality,
                order_id=order_id,
                commission=commission,
                slippage=slippage,
                atr_at_entry=0.0,  # Will be filled by simulator
                entry_signal="",  # Will be filled by simulator
                exit_signal=exit_reason,
                notes=position.notes,
                closing_notes=f"Closed via {exit_reason}",
                cumulative_pl=self.total_profit - self.total_loss
            )
            
            # Remove position and add to completed trades
            del self.positions[order_id]
            self.completed_trades.append(trade)
            
            logger.info(f"Closed position {order_id}: {win_loss} ${gross_pl:.2f} ({return_pct:.2%})")
            
            return trade
            
        except Exception as e:
            logger.error(f"Error closing position {order_id}: {e}")
            return None
    
    def update_positions(self, data_feed: MarketDataFeed, strategy_manager) -> List[Trade]:
        """Update all open positions and close if necessary"""
        closed_trades = []
        
        for order_id, position in list(self.positions.items()):
            try:
                current_price = data_feed.get_current_price(position.ticker)
                if not current_price:
                    continue
                
                # Check if position should be closed
                should_close = False
                exit_reason = ""
                
                # Check stop loss
                if position.action == "BUY" and current_price <= position.stop_loss:
                    should_close = True
                    exit_reason = "Stop Loss"
                elif position.action == "SELL" and current_price >= position.stop_loss:
                    should_close = True
                    exit_reason = "Stop Loss"
                
                # Check target price
                elif position.action == "BUY" and current_price >= position.target_price:
                    should_close = True
                    exit_reason = "Target Hit"
                elif position.action == "SELL" and current_price <= position.target_price:
                    should_close = True
                    exit_reason = "Target Hit"
                
                # Check strategy exit conditions
                elif strategy_manager.should_exit_position(
                    position.ticker, position.strategy, position.entry_price,
                    position.entry_time, current_price
                ):
                    should_close = True
                    exit_reason = "Strategy Exit"
                
                # Close position if needed
                if should_close:
                    trade = self.close_position(order_id, current_price, exit_reason)
                    if trade:
                        closed_trades.append(trade)
                
            except Exception as e:
                logger.error(f"Error updating position {order_id}: {e}")
        
        return closed_trades
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        total_positions = len(self.positions)
        total_value = self.current_capital
        
        # Add unrealized P&L from open positions
        for position in self.positions.values():
            # This would need current market prices to calculate unrealized P&L
            pass
        
        return {
            "current_capital": self.current_capital,
            "total_positions": total_positions,
            "daily_risk_used": self.daily_risk_used,
            "max_drawdown": self.max_drawdown,
            "current_drawdown": self.current_drawdown,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.winning_trades / max(1, self.total_trades),
            "total_profit": self.total_profit,
            "total_loss": self.total_loss,
            "net_profit": self.total_profit - self.total_loss
        }
    
    def get_risk_metrics(self) -> Dict:
        """Get risk management metrics"""
        return {
            "daily_risk_used_pct": (self.daily_risk_used / self.current_capital) * 100,
            "daily_risk_remaining": (self.current_capital * MAX_DAILY_RISK) - self.daily_risk_used,
            "max_position_size": self.current_capital * MAX_POSITION_SIZE,
            "positions_remaining": MAX_TOTAL_POSITIONS - len(self.positions),
            "can_trade": self.daily_risk_used < self.current_capital * MAX_DAILY_RISK
        }
