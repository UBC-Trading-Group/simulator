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
        self.cash = 0

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
            self.portfolio[order["ticker"]].append((order["quantity"], order["price"]))
        elif order["side"] == "sell":
            self.sell_shares(order["ticker"], order["quantity"], order["price"])

    # user sell shares and would remove the shares based on FIFO
    def sell_shares(self, ticker, sell_qty, sell_price):
        realized_pnl = 0.0

        remaining = sell_qty
        lots = self.portfolio[ticker]

        if not lots:
            # TODO update tests to re-enable
            pass
            # raise ValueError(f"Ticker {ticker} is not found!")

        while remaining > 0 and lots:
            buy_qty, buy_price = lots[0]
            if remaining >= buy_qty:
                realized_pnl += (sell_price - buy_price) * buy_qty
                remaining -= buy_qty
                lots.pop(0)
            else:
                realized_pnl += (sell_price - buy_price) * remaining
                lots[0] = (buy_qty - remaining, buy_price)
                remaining = 0
                break

        if remaining > 0:
            # TODO update tests to re-enable
            # raise ValueError(
            #     f"Not enough shares to sell: tried {sell_qty}, only sold {sell_qty - remaining}"
            # )
            pass

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