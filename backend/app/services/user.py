class UserState:
    """Example of a portfolio
    "ticker": [(qty, price), (qty, price)]

    {
        "AAPL": [(1, 120), (2, 125)],
        "MSFT": [(3, 310)]
    }
    """

    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
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
            raise ValueError(f"Ticker {ticker} is not found!")

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
            raise ValueError(
                f"Not enough shares to sell: tried {sell_qty}, only sold {sell_qty - remaining}"
            )

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
