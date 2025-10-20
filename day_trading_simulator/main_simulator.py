"""
Main Day Trading Simulator - Orchestrates all components
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule
import random

from config import *
from data_feed import MarketDataFeed
from trading_strategies import StrategyManager, TradingSignal
from portfolio_manager import PortfolioManager
from excel_logger import ExcelLogger

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(f"{LOGS_DIR}/simulator.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DayTradingSimulator:
    def __init__(self, initial_capital: float = INITIAL_PORTFOLIO_VALUE):
        self.data_feed = MarketDataFeed()
        self.strategy_manager = StrategyManager(self.data_feed)
        self.portfolio_manager = PortfolioManager(initial_capital)
        self.excel_logger = ExcelLogger()
        
        self.is_running = False
        self.trading_thread = None
        self.daily_trades_completed = {}  # Track trades per strategy per day
        
        # Initialize daily tracking
        self._reset_daily_tracking()
        
        logger.info(f"Day Trading Simulator initialized with ${initial_capital:,.2f}")
    
    def _reset_daily_tracking(self):
        """Reset daily tracking variables"""
        current_date = datetime.now().date()
        self.daily_trades_completed = {
            strategy: 0 for strategy in self.strategy_manager.strategies.keys()
        }
        logger.info(f"Daily tracking reset for {current_date}")
    
    def start_simulation(self):
        """Start the trading simulation"""
        if self.is_running:
            logger.warning("Simulation is already running")
            return
        
        self.is_running = True
        
        # Start data feed
        self.data_feed.start_feed()
        
        # Start trading loop in separate thread
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        
        # Schedule daily reset
        schedule.every().day.at("00:01").do(self._reset_daily_tracking)
        
        logger.info("Day Trading Simulation started")
    
    def stop_simulation(self):
        """Stop the trading simulation"""
        self.is_running = False
        
        # Stop data feed
        self.data_feed.stop_feed()
        
        # Wait for trading thread to finish
        if self.trading_thread:
            self.trading_thread.join(timeout=5)
        
        logger.info("Day Trading Simulation stopped")
    
    def _trading_loop(self):
        """Main trading loop"""
        logger.info("Trading loop started")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                current_date = current_time.date()
                
                # Check if market is open
                if not self.data_feed.is_market_open():
                    time.sleep(60)  # Check every minute when market is closed
                    continue
                
                # Update existing positions
                self._update_positions()
                
                # Look for new trading opportunities
                self._scan_for_opportunities()
                
                # Run scheduled tasks
                schedule.run_pending()
                
                # Sleep before next iteration
                time.sleep(30)  # Check every 30 seconds during market hours
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(60)  # Wait before retrying
    
    def _update_positions(self):
        """Update all open positions"""
        try:
            closed_trades = self.portfolio_manager.update_positions(
                self.data_feed, self.strategy_manager
            )
            
            if closed_trades:
                # Log closed trades to Excel
                market_directions = {}
                atr_data = {}
                entry_signals = {}
                
                for trade in closed_trades:
                    market_directions[trade.ticker] = self.data_feed.get_market_direction(trade.ticker)
                    
                    # Get ATR at entry (approximate)
                    hist_data = self.data_feed.get_historical_data(trade.ticker, "5d")
                    if not hist_data.empty and 'ATR' in hist_data.columns:
                        atr_data[trade.ticker] = hist_data['ATR'].iloc[-1]
                    else:
                        atr_data[trade.ticker] = 0.0
                    
                    entry_signals[trade.ticker] = f"{trade.strategy} signal"
                
                self.excel_logger.log_multiple_trades(
                    closed_trades, market_directions, atr_data, entry_signals
                )
                
                logger.info(f"Updated {len(closed_trades)} positions")
                
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    def _scan_for_opportunities(self):
        """Scan for new trading opportunities"""
        try:
            current_date = datetime.now().date()
            
            # Check if we can trade more today
            for strategy_name in self.strategy_manager.strategies.keys():
                if self.daily_trades_completed[strategy_name] >= STRATEGIES_PER_DAY:
                    continue
                
                # Look for opportunities with this strategy
                opportunities = self._find_opportunities(strategy_name)
                
                for ticker, signal in opportunities:
                    if self._can_take_trade(strategy_name):
                        success = self._execute_trade(ticker, strategy_name, signal)
                        if success:
                            self.daily_trades_completed[strategy_name] += 1
                            logger.info(f"Executed {strategy_name} trade in {ticker} "
                                      f"({self.daily_trades_completed[strategy_name]}/{STRATEGIES_PER_DAY})")
                            break  # Move to next strategy
                
                # Small delay between strategies
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"Error scanning for opportunities: {e}")
    
    def _find_opportunities(self, strategy_name: str) -> List[tuple]:
        """Find trading opportunities for a specific strategy"""
        opportunities = []
        
        try:
            # Get strategy
            strategy = self.strategy_manager.strategies[strategy_name]
            
            # Check each ticker
            for ticker in self.data_feed.tickers:
                try:
                    signal = strategy.generate_signal(ticker)
                    if signal and signal.confidence > 0.7:  # High confidence signals only
                        opportunities.append((ticker, signal))
                except Exception as e:
                    logger.error(f"Error generating signal for {ticker} with {strategy_name}: {e}")
            
            # Sort by confidence (highest first)
            opportunities.sort(key=lambda x: x[1].confidence, reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding opportunities for {strategy_name}: {e}")
        
        return opportunities
    
    def _can_take_trade(self, strategy_name: str) -> bool:
        """Check if we can take a trade for this strategy"""
        # Check if we've already completed the daily quota
        if self.daily_trades_completed[strategy_name] >= STRATEGIES_PER_DAY:
            return False
        
        # Check portfolio risk limits
        risk_metrics = self.portfolio_manager.get_risk_metrics()
        if not risk_metrics["can_trade"]:
            return False
        
        # Check if we have available capital
        portfolio_summary = self.portfolio_manager.get_portfolio_summary()
        if portfolio_summary["current_capital"] < 1000:  # Minimum capital threshold
            return False
        
        return True
    
    def _execute_trade(self, ticker: str, strategy_name: str, signal: TradingSignal) -> bool:
        """Execute a trade based on signal"""
        try:
            # Calculate risk amount
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            risk_per_trade = portfolio_summary["current_capital"] * MAX_POSITION_SIZE * 0.5  # Conservative risk
            
            # Get ATR for better risk calculation
            hist_data = self.data_feed.get_historical_data(ticker, "5d")
            atr = hist_data['ATR'].iloc[-1] if not hist_data.empty and 'ATR' in hist_data.columns else 0.0
            
            # Adjust risk based on ATR
            if atr > 0:
                risk_per_trade = min(risk_per_trade, atr * 100)  # Max 100 shares worth of ATR risk
            
            # Open position
            order_id = self.portfolio_manager.open_position(
                ticker=ticker,
                strategy=strategy_name,
                signal_action=signal.action,
                entry_price=signal.price,
                stop_loss=signal.stop_loss,
                target_price=signal.target_price,
                risk_amount=risk_per_trade,
                setup_quality=min(5, max(1, int(signal.confidence * 5))),  # Convert confidence to 1-5 scale
                notes=f"Confidence: {signal.confidence:.2f}, {signal.reason}"
            )
            
            if order_id:
                logger.info(f"Opened {signal.action} position in {ticker} using {strategy_name}")
                return True
            else:
                logger.warning(f"Failed to open position in {ticker}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing trade in {ticker}: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get current simulation status"""
        portfolio_summary = self.portfolio_manager.get_portfolio_summary()
        risk_metrics = self.portfolio_manager.get_risk_metrics()
        
        return {
            "is_running": self.is_running,
            "market_open": self.data_feed.is_market_open(),
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "portfolio": portfolio_summary,
            "risk": risk_metrics,
            "daily_trades": self.daily_trades_completed,
            "open_positions": len(self.portfolio_manager.positions)
        }
    
    def force_close_all_positions(self):
        """Force close all open positions (emergency exit)"""
        try:
            closed_trades = []
            
            for order_id in list(self.portfolio_manager.positions.keys()):
                position = self.portfolio_manager.positions[order_id]
                current_price = self.data_feed.get_current_price(position.ticker)
                
                if current_price:
                    trade = self.portfolio_manager.close_position(order_id, current_price, "Force Close")
                    if trade:
                        closed_trades.append(trade)
            
            if closed_trades:
                # Log to Excel
                market_directions = {}
                atr_data = {}
                entry_signals = {}
                
                for trade in closed_trades:
                    market_directions[trade.ticker] = self.data_feed.get_market_direction(trade.ticker)
                    atr_data[trade.ticker] = 0.0  # Placeholder
                    entry_signals[trade.ticker] = "Force close"
                
                self.excel_logger.log_multiple_trades(
                    closed_trades, market_directions, atr_data, entry_signals
                )
                
                logger.info(f"Force closed {len(closed_trades)} positions")
            
        except Exception as e:
            logger.error(f"Error force closing positions: {e}")
    
    def run_backtest(self, start_date: str, end_date: str, tickers: List[str] = None):
        """Run a backtest simulation (for testing purposes)"""
        logger.info(f"Starting backtest from {start_date} to {end_date}")
        
        # This would implement backtesting logic
        # For now, just log the request
        logger.info("Backtest functionality not yet implemented")

def main():
    """Main function to run the simulator"""
    try:
        # Create and start simulator
        simulator = DayTradingSimulator()
        
        print("Day Trading Simulator")
        print("====================")
        print("Commands:")
        print("  start - Start simulation")
        print("  stop - Stop simulation")
        print("  status - Show current status")
        print("  close - Force close all positions")
        print("  exit - Exit program")
        print()
        
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == "start":
                    simulator.start_simulation()
                    print("Simulation started. Press Ctrl+C to stop or enter 'stop' command.")
                    
                elif command == "stop":
                    simulator.stop_simulation()
                    print("Simulation stopped.")
                    
                elif command == "status":
                    status = simulator.get_status()
                    print(f"\nCurrent Status:")
                    print(f"  Running: {status['is_running']}")
                    print(f"  Market Open: {status['market_open']}")
                    print(f"  Current Capital: ${status['portfolio']['current_capital']:,.2f}")
                    print(f"  Open Positions: {status['open_positions']}")
                    print(f"  Total Trades: {status['portfolio']['total_trades']}")
                    print(f"  Win Rate: {status['portfolio']['win_rate']:.1%}")
                    print(f"  Net Profit: ${status['portfolio']['net_profit']:,.2f}")
                    print()
                    
                elif command == "close":
                    confirm = input("Are you sure you want to force close all positions? (y/N): ")
                    if confirm.lower() == 'y':
                        simulator.force_close_all_positions()
                        print("All positions force closed.")
                    else:
                        print("Operation cancelled.")
                        
                elif command == "exit":
                    if simulator.is_running:
                        simulator.stop_simulation()
                    print("Exiting...")
                    break
                    
                else:
                    print("Invalid command. Try: start, stop, status, close, exit")
                    
            except KeyboardInterrupt:
                print("\nReceived interrupt signal...")
                if simulator.is_running:
                    simulator.stop_simulation()
                break
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
