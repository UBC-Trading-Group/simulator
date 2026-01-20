class UserState:
    """Example of a portfolio
    "ticker": [(qty, price), (qty, price)]

    {
        "AAPL": [(1, 120), (2, 125)],
        "MSFT": [(3, 310)]
    }
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.cash = 500000.0  # Start with 500k cash

        self.portfolio = {}  # contains user's portfolio
        self.unfulfilled_trades = (
            []
        )  # orders that have not been fulfilled or position is not closed
        self.fulfilled_trades = (
            []
        )  # orders that have been fulfilled or position is closed

        self.total_shares = 0
        self.prev_avg_price = 0
        self.total_realized_pnl = 0.0
        self.rank = 0
        
        # Anti-manipulation limits
        self.trade_history = []  # List of (ticker, quantity, side, timestamp)

    # adds order that has not been closed
    def add_unfulfilled_trade(self, order):
        self.unfulfilled_trades.append(order)

    # adds order that has been closed and so we call get_avg_price here
    def add_fulfilled_trades(self, order):
        self.fulfilled_trades.append(order)

        if order["ticker"] not in self.portfolio:
            self.portfolio[order["ticker"]] = []

        if order["side"] == "buy":
            # Check if we have short positions to close first
            if self.portfolio[order["ticker"]]:
                # Close short positions first (FIFO)
                buy_qty = order["quantity"]
                buy_price = order["price"]
                lots = self.portfolio[order["ticker"]]
                
                while buy_qty > 0 and lots and lots[0][0] < 0:  # Negative qty = short
                    short_qty, short_price = lots[0]
                    short_qty = abs(short_qty)  # Make positive for calculation
                    
                    if buy_qty >= short_qty:
                        # Close entire short position
                        pnl = (short_price - buy_price) * short_qty  # Profit if buy < short
                        self.total_realized_pnl += pnl
                        buy_qty -= short_qty
                        lots.pop(0)
                    else:
                        # Partially close short
                        pnl = (short_price - buy_price) * buy_qty
                        self.total_realized_pnl += pnl
                        lots[0] = (-(short_qty - buy_qty), short_price)  # Keep negative
                        buy_qty = 0
                        break
                
                # If still have buy quantity left, add as long position
                if buy_qty > 0:
                    self.portfolio[order["ticker"]].append((buy_qty, buy_price))
            else:
                # No positions, just add long
                self.portfolio[order["ticker"]].append((order["quantity"], order["price"]))
                
        elif order["side"] == "sell":
            self.sell_shares(order["ticker"], order["quantity"], order["price"])

    # user sell shares and would remove the shares based on FIFO
    def sell_shares(self, ticker, sell_qty, sell_price):
        realized_pnl = 0.0

        remaining = sell_qty
        lots = self.portfolio[ticker]

        # Close long positions first (FIFO)
        # Only process positive quantities (long positions)
        i = 0
        while remaining > 0 and i < len(lots):
            buy_qty, buy_price = lots[i]
            
            # Skip short positions (negative quantities) and continue to next lot
            if buy_qty <= 0:
                i += 1
                continue
            
            if remaining >= buy_qty:
                # Close entire long position
                realized_pnl += (sell_price - buy_price) * buy_qty
                remaining -= buy_qty
                lots.pop(i)
                # Don't increment i, as we removed an element
            else:
                # Partially close long position
                realized_pnl += (sell_price - buy_price) * remaining
                lots[i] = (buy_qty - remaining, buy_price)
                remaining = 0
                break

        # If still have remaining quantity, it's a short sale
        # Store as negative quantity to track short positions
        if remaining > 0:
            # Add as negative lot (short position)
            lots.append((-remaining, sell_price))

        self.total_realized_pnl += realized_pnl

    def get_avg_price(self, order_price, order_quantity) -> float:
        prev_quantity = self.total_shares
        self.total_shares += order_quantity

        if self.total_shares == 0:
            return 0

        avg_price = (
            (self.prev_avg_price * prev_quantity) + (order_price * order_quantity)
        ) / self.total_shares

        self.prev_avg_price = avg_price

        return avg_price

    def get_total_realized_pnl(self):
        return self.total_realized_pnl

    def set_rank(self, rank):
        self.rank = rank

    def get_rank(self):
        return self.rank
    
    def get_position(self, ticker: str) -> int:
        """
        Get current position (net quantity) for a ticker.
        Returns positive for long, negative for short.
        Calculated from all fulfilled trades (buys minus sells).
        """
        net_position = 0
        
        # Sum all fulfilled trades for this ticker
        for trade in self.fulfilled_trades:
            if trade["ticker"] == ticker:
                if trade["side"] == "buy":
                    net_position += trade["quantity"]
                else:  # sell
                    net_position -= trade["quantity"]
        
        return net_position
    
    def add_trade_to_history(self, ticker: str, quantity: int, side: str, timestamp: float):
        """Track trades for rate limiting"""
        self.trade_history.append((ticker, quantity, side, timestamp))
    
    def get_recent_volume(self, ticker: str, time_window_seconds: float, current_time: float) -> int:
        """
        Get total volume traded for a ticker within a time window.
        Used for rate limiting.
        """
        cutoff_time = current_time - time_window_seconds
        volume = sum(
            qty for t, qty, side, ts in self.trade_history
            if t == ticker and ts >= cutoff_time
        )
        return volume
    
    def check_reversal_risk(self, ticker: str, side: str, current_time: float, lookback_seconds: float = 60) -> bool:
        """
        Check if user is trying to reverse position too quickly (pump & dump detection).
        Returns True if this looks like a reversal (suspicious).
        """
        cutoff_time = current_time - lookback_seconds
        recent_trades = [
            (qty, s) for t, qty, s, ts in self.trade_history
            if t == ticker and ts >= cutoff_time
        ]
        
        if not recent_trades:
            return False
        
        # Check if the last trade was the opposite side
        last_qty, last_side = recent_trades[-1]
        
        # Suspicious if:
        # - Last trade was a large buy (>100) and now trying to sell
        # - Last trade was a large sell (>100) and now trying to buy
        if last_side != side and last_qty >= 100:
            return True
        
        return False
    
    def has_sufficient_cash(self, required_amount: float) -> bool:
        """Check if user has enough cash for a purchase"""
        return self.cash >= required_amount
    
    def get_cash(self) -> float:
        """Get current cash balance"""
        return self.cash
    
    def calculate_unrealized_pnl(self, current_prices: dict) -> float:
        """
        Calculate unrealized P&L based on current market prices.
        current_prices: dict of {ticker: current_price}
        Handles both long positions (positive qty) and short positions (negative qty).
        """
        unrealized_pnl = 0.0
        
        for ticker, lots in self.portfolio.items():
            if ticker not in current_prices:
                continue
            
            current_price = current_prices[ticker]
            for qty, entry_price in lots:
                if qty > 0:
                    # Long position: profit when price goes up
                    unrealized_pnl += (current_price - entry_price) * qty
                else:
                    # Short position (qty is negative): profit when price goes down
                    unrealized_pnl += (entry_price - current_price) * abs(qty)
        
        return unrealized_pnl
    
    def get_portfolio_market_value(self, current_prices: dict) -> float:
        """
        Calculate total market value of portfolio.
        For long positions: current_price * qty
        For short positions: entry_price * qty - current_price * qty (what you'd need to close)
        current_prices: dict of {ticker: current_price}
        """
        market_value = 0.0
        
        for ticker, lots in self.portfolio.items():
            if ticker not in current_prices:
                continue
            
            current_price = current_prices[ticker]
            for qty, entry_price in lots:
                if qty > 0:
                    # Long: value is current market price
                    market_value += current_price * qty
                else:
                    # Short: value is negative (liability to buy back)
                    market_value += current_price * qty  # qty is negative, so this subtracts
        
        return market_value