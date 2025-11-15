import bisect
import uuid
from enum import Enum


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"


class OrderBook:
    """
    Example of an order:
    {
        "price": 101.5,
        "quantity": 5,
        "ticker": "AAPL",
        "user_id": "u1",
        "side": "buy"
    }
    """

    def __init__(self):
        """
        Uses binary search, bisect to maintain sorted order

        The worst order always goes first, so
        buys[<TICKER>][0] is the lowest bid order, buys sorted ascending
        sells[<TICKER>][0] is the highest ask order, sells sorted descending
        """
        self.buys = {}
        self.sells = {}

    def _get_book(self, ticker, side):
        """Helper to get or init the correct per-ticker list."""
        if side == OrderSide.BUY:
            if ticker not in self.buys:
                self.buys[ticker] = []
            return self.buys[ticker]
        else:
            if ticker not in self.sells:
                self.sells[ticker] = []
            return self.sells[ticker]

    def add_order(self, order):
        price = order["price"]
        side = order["side"]
        ticker = order["ticker"]

        # add ID for easier matching
        order["id"] = uuid.uuid4()

        orders = self._get_book(ticker, side)

        if side == OrderSide.BUY:
            prices = [o["price"] for o in orders]
            idx = bisect.bisect_left(prices, price)
            orders.insert(idx, order)
        elif side == OrderSide.SELL:
            # Invert sign to maintain descending order
            prices = [-o["price"] for o in orders]
            idx = bisect.bisect_left(prices, -price)
            orders.insert(idx, order)
        else:
            raise ValueError("Invalid side")

    def remove_order(self, order):
        """
        Remove order from order book
        Has to be linear scan since multiple orders can have same price

        TODO: Probably can (partially) optimize by using bin search to get range first
        """
        side = order["side"]
        ticker = order["ticker"]
        orders = self._get_book(ticker, side)

        for i, o in enumerate(orders):
            if o == order:
                orders.pop(i)
                return True
        return False

    def best_bid(self, ticker):
        if ticker not in self.buys or not self.buys[ticker]:
            return None
        return self.buys[ticker][-1]

    def best_ask(self, ticker):
        if ticker not in self.sells or not self.sells[ticker]:
            return None
        return self.sells[ticker][-1]

    def mid_price(self, ticker):
        highest_bid = self.best_bid(ticker)
        lowest_ask = self.best_ask(ticker)
        if highest_bid and lowest_ask:
            return (highest_bid["price"] + lowest_ask["price"]) / 2
        return None

    def match_order(self, order):
        """
        Matches buy with corresponding sell order, or sell with corresponding buy order
        Matching should happen based on proximity to mid price, closest to mid price goes first
        Return status whether matching was successful
        Partial matching is possible

        TODO Brian -> revisit algo
        TODO Brian -> write unit tests (test_order_book.py)
        This function will be called many times so best to optimize
        """
        # 1. required variables
        side = order["side"]
        quantity = order["quantity"]
        initial_quantity = order["quantity"]
        ticker = order["ticker"]

        opposite_side_orders = (
            self.sells.get(ticker, [])
            if side == OrderSide.BUY
            else self.buys.get(ticker, [])
        )

        # 2. nothing to scan through anyways
        if not opposite_side_orders:
            self.add_order(order)
            return OrderStatus.OPEN, initial_quantity

        # 3. no mid price -> order book is only filled on one side
        mid = self.mid_price(ticker)
        if mid is None:  # we know it's the same side because we did check in 2)
            mid = opposite_side_orders[0]["price"]  # use the worst

        # 4. look through opposite side orders
        """
        TODO Brian -> revisit algo
        a. Sort once based on proximity to avoid repeated scans when multiple orders are meant to be matched
        b. Create a mapping of order ID -> delta (so we can update order book in one linear scan)
        c. After iteration, status can be "FILLED", "PARTIALLY_FILLED", "OPEN"
        """
        sorted_opposites = sorted(
            opposite_side_orders, key=lambda o: abs(o["price"] - mid)
        )
        order_deltas = {}  # maps order ID -> delta
        matched_trades = (
            []
        )  # keep track of trades that are matched (do we need this for logs?)

        i = 0
        while i < len(sorted_opposites) and quantity > 0:
            opposite = sorted_opposites[i]

            # skip if price not compatible
            if (side == OrderSide.BUY and opposite["price"] > order["price"]) or (
                side == OrderSide.SELL and opposite["price"] < order["price"]
            ):
                i += 1
                continue

            # determine fill amount
            traded_qty = min(quantity, opposite["quantity"])
            trade_price = opposite[
                "price"
            ]  # or mid, or last price depending on your model

            # keep track of deltas for opposite orders
            order_deltas[opposite["id"]] = traded_qty

            matched_trades.append(
                {
                    "buy": order if side == OrderSide.BUY else opposite,
                    "sell": opposite if side == OrderSide.BUY else order,
                    "price": trade_price,
                    "quantity": traded_qty,
                }
            )

            # update quantity remaining
            quantity -= traded_qty

            # move to next order
            i += 1

        # 5. update actual order book using stored deltas in one linear scan (as mentioned in 4b)
        # !!! MAKE A COPY since we are modifying the list in place
        for original_opposite in list(opposite_side_orders):
            if original_opposite["id"] in order_deltas:
                original_opposite["quantity"] -= order_deltas[original_opposite["id"]]
                if original_opposite["quantity"] == 0:
                    opposite_side_orders.remove(original_opposite)

        # 6. determine matching status
        matching_status = None
        if quantity == initial_quantity:  # NOTHING was processed
            matching_status = OrderStatus.OPEN
            self.add_order(order)
        elif quantity > 0:  # SOME were processed
            order["quantity"] = quantity
            matching_status = OrderStatus.PARTIALLY_FILLED
            self.add_order(order)
        else:  # EVERYTHING was processed
            matching_status = OrderStatus.FILLED

        return matching_status, quantity
