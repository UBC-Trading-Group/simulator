import heapq
from typing import Dict, List, Optional, Tuple

from app.schemas.order import OrderModel, OrderSide, OrderStatus


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
        Use heap to always get the best bid / best ask first
        Refer to "Number of items in backlog" for reference

        Mapping is
        ticker -> HEAP of orders

        buys will be max heap (to get highest bid)
        -> (-price, quantity, <ORDER_OBJ>)

        sells will be min heap (to get lowest ask)
        -> (price, quantity, <ORDER_OBJ>)

        price is index 0
        quantity is index 1
        order object is index 2
        """
        self.buys: Dict[str, List[Tuple[float, int, OrderModel]]] = {}
        self.sells: Dict[str, List[Tuple[float, int, OrderModel]]] = {}
        self.last_traded_price: Dict[str, float] = {}
        self.CLAMPED_DELTA_COEFF: float = 2.5
        self.PRICE_IDX = 0
        self.QUANTITY_IDX = 1
        self.ORDER_OBJ_IDX = 2

    def _get_book(
        self, ticker: str, side: OrderSide
    ) -> List[Tuple[float, int, OrderModel]]:
        """Helper to get or init the correct per-ticker list."""
        if side == OrderSide.BUY:
            if ticker not in self.buys:
                self.buys[ticker] = []
            return self.buys[ticker]
        else:
            if ticker not in self.sells:
                self.sells[ticker] = []
            return self.sells[ticker]

    def add_order(self, order: OrderModel) -> None:
        price = order.price
        side = order.side
        ticker = order.ticker
        quantity = order.quantity

        # ID will be automatically set if not provided
        book = self._get_book(ticker, side)

        if side == OrderSide.BUY:
            heapq.heappush(book, (-price, quantity, order))
        elif side == OrderSide.SELL:
            heapq.heappush(book, (price, quantity, order))
        else:
            raise ValueError("Invalid side")

    def remove_order(self, order: OrderModel) -> bool:
        """
        Remove order from order book
        Has to be linear scan since multiple orders can have same price
        """
        side = order.side
        ticker = order.ticker
        orders = self._get_book(ticker, side)

        for i, entry in enumerate(orders):
            _, _, order_obj = entry
            if order_obj.id == order.id:
                orders.pop(i)
                heapq.heapify(orders)  # maintain the heap property
                return True
        return False

    def best_bid(self, ticker: str) -> Optional[OrderModel]:
        if ticker not in self.buys or not self.buys[ticker]:
            return None
        return self.buys[ticker][0][self.ORDER_OBJ_IDX]

    def best_ask(self, ticker: str) -> Optional[OrderModel]:
        if ticker not in self.sells or not self.sells[ticker]:
            return None
        return self.sells[ticker][0][self.ORDER_OBJ_IDX]

    def clamped_spread(self, ticker: str) -> Optional[float]:
        best_bid_w_clamp = self.best_bid_within_clamp(ticker)
        best_ask_w_clamp = self.best_ask_within_clamp(ticker)
        if best_bid_w_clamp and best_ask_w_clamp:
            return best_ask_w_clamp.price - best_bid_w_clamp.price
        return None

    def best_bid_within_clamp(self, ticker: str) -> Optional[OrderModel]:
        clamp_price = self.bid_clamp(ticker)
        if clamp_price is None:
            return self.best_bid(ticker)

        best: Optional[OrderModel] = None

        for entry in self.buys.get(ticker, []):
            order = entry[self.ORDER_OBJ_IDX]
            price = order.price

            if price <= clamp_price:
                if best is None or price > best.price:
                    best = order

        return best

    def best_ask_within_clamp(self, ticker: str) -> Optional[OrderModel]:
        clamp_price = self.ask_clamp(ticker)
        if clamp_price is None:
            return self.best_ask(ticker)

        best: Optional[OrderModel] = None

        for entry in self.sells.get(ticker, []):
            order = entry[self.ORDER_OBJ_IDX]
            price = order.price

            if price >= clamp_price:
                if best is None or price < best.price:
                    best = order

        return best

    def clamp_range(self, ticker: str) -> Optional[float]:
        # Need a previous trade to compute clamp
        if ticker not in self.last_traded_price:
            return None

        mid = self.mid_price(ticker)
        if mid is None:
            return None

        last = self.last_traded_price[ticker]
        return abs(mid - last)

    def bid_clamp(self, ticker: str) -> Optional[float]:
        mid = self.mid_price(ticker)
        if mid is None:
            return None

        clamp_range = self.clamp_range(ticker)
        if clamp_range is None:
            return None

        return mid + clamp_range * self.CLAMPED_DELTA_COEFF

    def ask_clamp(self, ticker: str) -> Optional[float]:
        mid = self.mid_price(ticker)
        if mid is None:
            return None

        clamp_range = self.clamp_range(ticker)
        if clamp_range is None:
            return None

        return mid - clamp_range * self.CLAMPED_DELTA_COEFF

    def mid_price(self, ticker: str) -> Optional[float]:
        highest_bid = self.best_bid(ticker)
        lowest_ask = self.best_ask(ticker)
        if highest_bid and lowest_ask:
            return (highest_bid.price + lowest_ask.price) / 2
        return None

    def match_order(self, order: OrderModel) -> tuple[OrderStatus, int]:
        """
        Matches buy with corresponding sell orders, or sell with buy orders.
        Matching is price-priority based (max bid vs min ask), partial fills allowed.
        Updates last traded price and order book.
        Returns: (status, remaining quantity)
        """
        side = order.side
        ticker = order.ticker
        quantity = order.quantity
        initial_quantity = quantity

        # Select the heap for the opposite side
        if side == OrderSide.BUY:
            opposite_heap = self.sells.setdefault(ticker, [])
            is_buy = True
        else:
            opposite_heap = self.buys.setdefault(ticker, [])
            is_buy = False

        # If no opposite orders, just add to book
        if not opposite_heap:
            self.add_order(order)
            return OrderStatus.OPEN, initial_quantity

        while quantity > 0 and opposite_heap:
            best_entry = opposite_heap[0]
            opp_price, opp_qty, opp_order = best_entry if not is_buy else best_entry

            if is_buy:
                # Sell heap stores (price, qty, order_obj)
                if opp_price > order.price:
                    break  # cannot match
            else:
                # Buy heap stores (-price, qty, order_obj)
                if -opp_price < order.price:
                    break  # cannot match

            traded_qty = min(quantity, opp_order.quantity)
            trade_price = opp_order.price

            self.last_traded_price[ticker] = trade_price

            opp_order.quantity -= traded_qty
            quantity -= traded_qty

            heapq.heappop(opposite_heap)
            if opp_order.quantity > 0:
                # Set modify flag to prevent generating a new uuid
                self.add_order(opp_order)

        # Handle the remaining quantities (if any)
        if quantity == initial_quantity:
            # Nothing matched
            self.add_order(order)
            return OrderStatus.OPEN, initial_quantity
        elif quantity > 0:
            # Partially matched
            order.quantity = quantity
            self.add_order(order)
            return OrderStatus.PARTIALLY_FILLED, quantity
        else:
            # Fully matched
            return OrderStatus.FILLED, 0
