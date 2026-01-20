import heapq
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from app.schemas.order import OrderModel, OrderSide, OrderStatus
from app.services.user import UserState


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

        """
        Order mapping gives us quick access if we have order id 
        """
        self.order_mapping: Dict[str, OrderModel] = {}
        
        """
        All orders ever placed (for history tracking)
        """
        self.all_orders: Dict[str, OrderModel] = {}

        """
        Trader mapping gives us quick access if we have trader id 
        """
        self.trader_mapping: Dict[str, Set[str]] = {}

        """
        User state mapping gives us quick access to user state
        """
        self.user_state_mapping: Dict[str, object] = {}

        """
        Gives us quick check if order is fulfilled 
        """
        self.fulfilled_orders: Set[str] = set()

        """
        Used to compute clamp 
        """
        self.last_traded_price: Dict[str, float] = {}
        self.previous_mid = {}

        """
        Coefficient used to compute clamp 
        """
        self.CLAMPED_DELTA_COEFF: float = 2.5

        """
        Indices used to access heap 
        """
        self.PRICE_IDX = 0
        self.QUANTITY_IDX = 1
        self.ORDER_OBJ_IDX = 2

    def _get_user_state(self, user_id: str) -> UserState:
        # init user if not exist
        if user_id not in self.user_state_mapping:
            self.user_state_mapping[user_id] = UserState(user_id=user_id)
        return self.user_state_mapping[user_id]

    def _apply_trade_to_user(
        self,
        user_id: str,
        ticker: str,
        side: OrderSide,
        quantity: int,
        price: float,
    ):
        user_state = self._get_user_state(user_id)

        trade = {
            "ticker": ticker,
            "side": side.value,
            "quantity": quantity,
            "price": price,
        }

        user_state.add_fulfilled_trades(trade)

        if side == OrderSide.BUY:
            user_state.cash -= quantity * price
        else:
            user_state.cash += quantity * price

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

    def get_bids(self, ticker: str):
        return [
            entry[self.ORDER_OBJ_IDX]
            for entry in sorted(self.buys.get(ticker, []), key=lambda x: -x[0])
        ]

    def get_asks(self, ticker: str):
        return [
            entry[self.ORDER_OBJ_IDX]
            for entry in sorted(self.sells.get(ticker, []), key=lambda x: x[0])
        ]

    def has_ticker(self, ticker: str) -> bool:
        return ticker in self.buys or ticker in self.sells

    def _add_order_to_trader_mapping(self, order: OrderModel, execution_price: float = None):
        user_id = order.user_id
        if user_id not in self.trader_mapping:
            self.trader_mapping[user_id] = set()
        self.trader_mapping[user_id].add(order.id)
        # Store a copy with execution price if provided, otherwise original
        if execution_price and execution_price > 0:
            order_copy = OrderModel(
                id=order.id,
                price=execution_price,
                quantity=order.quantity,
                ticker=order.ticker,
                side=order.side,
                user_id=order.user_id,
            )
            self.all_orders[order.id] = order_copy
        else:
            self.all_orders[order.id] = order

    def _get_trader_orders(self, user_id: str) -> Set[str]:
        return self.trader_mapping.get(user_id, set())

    def get_trader_unfulfilled_orders(self, user_id: str) -> List[OrderModel]:
        trader_orders = self._get_trader_orders(user_id)

        # here we take the set difference to get unfulfilled orders
        unfulfilled_order_ids = trader_orders - self.fulfilled_orders

        unfulfilled_orders = []
        for unfulfilled_order_id in unfulfilled_order_ids:
            unfulfilled_orders.append(self.order_mapping[unfulfilled_order_id])
        return unfulfilled_orders

    def get_trader_fulfilled_orders(self, user_id: str) -> List[OrderModel]:
        trader_orders = self._get_trader_orders(user_id)

        # here we take the set intersection to get fulfilled orders
        fulfilled_order_ids = trader_orders & self.fulfilled_orders

        fulfilled_orders = []
        for fulfilled_order_id in fulfilled_order_ids:
            fulfilled_orders.append(self.order_mapping[fulfilled_order_id])
        return fulfilled_orders

    def get_portfolio(self, user_id: str):
        # note we do not delete from the map to maintain a history of orders
        portfolio = defaultdict(int)
        for fulfilled_order_id in list(self.fulfilled_orders):
            current_order = self.order_mapping[fulfilled_order_id]
            if current_order.user_id == user_id:
                if current_order.side == OrderSide.BUY:
                    portfolio[current_order.ticker] += current_order.quantity
                else:
                    portfolio[current_order.ticker] -= current_order.quantity
        return portfolio

    def get_trader_orders_with_status(self, user_id: str) -> List[dict]:
        """Return all orders for a trader with proper status (open/partially_filled/filled), sorted by timestamp."""
        orders: List[dict] = []
        for order_id in self._get_trader_orders(user_id):
            # Get order from all_orders (includes filled orders)
            if order_id not in self.all_orders:
                continue
            original_order = self.all_orders[order_id]
            
            # Determine status
            if order_id in self.fulfilled_orders:
                status = "filled"
                remaining_qty = 0
            elif order_id in self.order_mapping:
                current_order = self.order_mapping[order_id]
                if current_order.quantity < original_order.quantity:
                    status = "partially_filled"
                else:
                    status = "open"
                remaining_qty = current_order.quantity
            else:
                # Order no longer in book but not in fulfilled - probably cancelled
                continue
            
            orders.append(
                {
                    "order_id": str(original_order.id),
                    "symbol": original_order.ticker,
                    "quantity": original_order.quantity,
                    "filled_quantity": original_order.quantity - remaining_qty,
                    "price": original_order.price,
                    "type": original_order.side.value,
                    "status": status,
                    "created_at": original_order.created_at.isoformat() if hasattr(original_order, 'created_at') else None,
                }
            )
        # Sort by timestamp, newest first
        orders.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        return orders

    def check_order_status(self, order: OrderModel) -> OrderStatus:
        # Check if the order was fulfiled
        if order.id in self.fulfilled_orders:
            return OrderStatus.FILLED

        # Check if the order even exists in the book
        if order.id not in self.order_mapping:
            raise ValueError("Order not found")

        return OrderStatus.OPEN

    def check_order_fulfilled_amount(self, order: OrderModel) -> int:
        # Check how much of the order has been fulfilled
        if order.id not in self.order_mapping:
            raise ValueError("Order not found")

        # fulfilled amount = initial amount - remaining amount
        fulfilled_amount = order.quantity - self.order_mapping[order.id].quantity

        return fulfilled_amount

    def add_order(self, order: OrderModel) -> None:
        price = order.price
        side = order.side
        ticker = order.ticker
        quantity = order.quantity

        if quantity <= 0:
            return

        # ID will be automatically set if not provided
        book = self._get_book(ticker, side)

        if side == OrderSide.BUY:
            self.order_mapping[order.id] = order
            # Don't call _add_order_to_trader_mapping here - already called in match_order
            heapq.heappush(book, (-price, quantity, order))
        elif side == OrderSide.SELL:
            self.order_mapping[order.id] = order
            # Don't call _add_order_to_trader_mapping here - already called in match_order
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

        # Use the mid from the previous tick
        prev_mid = self.previous_mid.get(ticker)
        if prev_mid is None:
            return None

        last_price = self.last_traded_price[ticker]
        return abs(prev_mid - last_price)

    def bid_clamp(self, ticker: str) -> Optional[float]:
        mid = self.mid_price_for_clamp(ticker)
        if mid is None:
            return None

        clamp_range = self.clamp_range(ticker)
        if clamp_range is None:
            return None

        return mid + clamp_range * self.CLAMPED_DELTA_COEFF

    def ask_clamp(self, ticker: str) -> Optional[float]:
        mid = self.mid_price_for_clamp(ticker)
        if mid is None:
            return None

        clamp_range = self.clamp_range(ticker)
        if clamp_range is None:
            return None

        return mid - clamp_range * self.CLAMPED_DELTA_COEFF

    def mid_price(self, ticker: str) -> Optional[float]:
        highest_bid = self.best_bid_within_clamp(ticker)
        lowest_ask = self.best_ask_within_clamp(ticker)
        if highest_bid and lowest_ask:
            mid = (highest_bid.price + lowest_ask.price) / 2

            # Update previous mid **inside** mid_price
            self.previous_mid[ticker] = mid

            return mid
        return None

    def mid_price_for_clamp(self, ticker: str) -> Optional[float]:
        """Return the mid price from the previous tick, used ONLY for clamp."""
        return self.previous_mid.get(ticker)

    def match_order(
        self, order: OrderModel, is_liquidity_bot: bool = False
    ) -> tuple[OrderStatus, int, float]:
        """
        Matches buy with corresponding sell orders, or sell with buy orders.
        Matching is price-priority based (max bid vs min ask), partial fills allowed.
        Updates last traded price and order book.
        Returns: (status, remaining quantity, average execution price)
        """
        side = order.side
        ticker = order.ticker
        quantity = order.quantity
        initial_quantity = quantity
        
        # Will track order after we know execution price
        
        # Track total cost for weighted average price calculation
        total_cost = 0.0
        filled_quantity = 0

        # Select the heap for the opposite side
        if side == OrderSide.BUY:
            opposite_heap = self.sells.setdefault(ticker, [])
            is_buy = True
        else:
            opposite_heap = self.buys.setdefault(ticker, [])
            is_buy = False

        # If no opposite orders, just add to book
        # Liquidity bot orders are added to book without matching
        if not opposite_heap or is_liquidity_bot:
            self.add_order(order)
            return OrderStatus.OPEN, initial_quantity, 0.0

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
            
            # Track for average execution price
            total_cost += traded_qty * trade_price
            filled_quantity += traded_qty

            # Apply trade to user (USER STATE)
            self._apply_trade_to_user(
                user_id=order.user_id,
                ticker=ticker,
                side=order.side,
                quantity=traded_qty,
                price=trade_price,
            )

            # Apply trade to opposite user (USER STATE)
            self._apply_trade_to_user(
                user_id=opp_order.user_id,
                ticker=ticker,
                side=opp_order.side,
                quantity=traded_qty,
                price=trade_price,
            )

            opp_order.quantity -= traded_qty
            quantity -= traded_qty

            heapq.heappop(opposite_heap)
            if opp_order.quantity > 0:
                self.add_order(opp_order)
            else:
                # in this case, the order is fully matched
                self.fulfilled_orders.add(opp_order.id)

        # Calculate average execution price
        avg_price = total_cost / filled_quantity if filled_quantity > 0 else 0.0

        # Track order with execution price (for non-liquidity bots)
        if not is_liquidity_bot:
            self._add_order_to_trader_mapping(order, avg_price if avg_price > 0 else order.price)

        # Handle the remaining quantities (if any)
        if quantity == initial_quantity:
            # Nothing matched
            self.add_order(order)
            # Add to user's unfulfilled trades
            self._get_user_state(order.user_id).add_unfulfilled_trade(order)
            return OrderStatus.OPEN, initial_quantity, 0.0
        elif quantity > 0:
            # Partially matched
            order.quantity = quantity
            self.add_order(order)
            # Add to user's unfulfilled trades
            self._get_user_state(order.user_id).add_unfulfilled_trade(order)
            return OrderStatus.PARTIALLY_FILLED, quantity, avg_price
        else:
            # Fully matched
            self.fulfilled_orders.add(order.id)
            return OrderStatus.FILLED, 0, avg_price
