from app.schemas.order import OrderModel
from dependencies import get_instrument_manager


class OrderProcessor:
    def __init__(self, order_book, price_engine):
        self.order_book = order_book
        self.price_engine = price_engine

    def _ensure_model(self, order):
        """Convert dict to OrderModel if needed."""
        if isinstance(order, OrderModel):
            return order
        return OrderModel(**order)

    def process_order(self, order):
        import time
        
        order: OrderModel = self._ensure_model(order)
        instrument_manager = get_instrument_manager()

        if not instrument_manager.is_valid_instrument(order.ticker):
            return {
                "status": "INVALID_INSTRUMENT",
                "message": "Invalid instrument",
            }
        
        # Anti-manipulation checks
        MAX_POSITION = 5000
        MAX_ORDER_SIZE = 500  # Maximum shares per single order
        MAX_VOLUME_PER_MINUTE = 1000  # Maximum shares per ticker per minute
        
        user_state = self.order_book._get_user_state(order.user_id)
        current_position = user_state.get_position(order.ticker)
        current_time = time.time()
        
        # 1. Check single order size limit
        if order.quantity > MAX_ORDER_SIZE:
            return {
                "status": "ORDER_SIZE_EXCEEDED",
                "message": f"Order size exceeds maximum of {MAX_ORDER_SIZE} shares per order",
                "unprocessed_quantity": order.quantity,
            }
        
        # 2. Check volume rate limit (per minute)
        recent_volume = user_state.get_recent_volume(order.ticker, 60, current_time)
        if recent_volume + order.quantity > MAX_VOLUME_PER_MINUTE:
            return {
                "status": "RATE_LIMIT_EXCEEDED",
                "message": f"Trading volume limit exceeded. Max {MAX_VOLUME_PER_MINUTE} shares per minute per ticker. Current: {recent_volume}",
                "unprocessed_quantity": order.quantity,
            }
        
        # 3. Check for rapid position reversals (pump & dump detection)
        if user_state.check_reversal_risk(order.ticker, order.side.value, current_time, lookback_seconds=30):
            return {
                "status": "REVERSAL_BLOCKED",
                "message": "Cannot reverse large position within 30 seconds. Wait before changing direction.",
                "unprocessed_quantity": order.quantity,
            }
        
        # 4. Check position limits (5000 per ticker)
        if order.side.value == "buy":
            new_position = current_position + order.quantity
        else:  # sell
            new_position = current_position - order.quantity
        
        if new_position > MAX_POSITION:
            return {
                "status": "POSITION_LIMIT_EXCEEDED",
                "message": f"Order would exceed maximum long position of {MAX_POSITION}. Current position: {current_position}",
                "unprocessed_quantity": order.quantity,
            }
        elif new_position < -MAX_POSITION:
            return {
                "status": "POSITION_LIMIT_EXCEEDED",
                "message": f"Order would exceed maximum short position of {MAX_POSITION}. Current position: {current_position}",
                "unprocessed_quantity": order.quantity,
            }

        # Process the order
        processing_status, unprocessed_quantity = self.order_book.match_order(order)
        
        # Track this trade for rate limiting
        user_state.add_trade_to_history(order.ticker, order.quantity, order.side.value, current_time)

        return {
            "status": processing_status,
            "message": "Order processed successfully",
            "unprocessed_quantity": unprocessed_quantity,
        }

    def cancel_order(self, order):
        order: OrderModel = self._ensure_model(order)
        instrument_manager = get_instrument_manager()

        if not instrument_manager.is_valid_instrument(order.ticker):
            return {
                "status": "INVALID_INSTRUMENT",
                "message": "Invalid instrument",
            }

        success = self.order_book.remove_order(order)

        if success:
            return {"status": "CANCELLED", "message": "Order successfully cancelled"}
        else:
            return {
                "status": "NOT_FOUND",
                "message": "Order not found in the order book",
            }

    def check_order_status(self, order):
        order: OrderModel = self._ensure_model(order)
        status = self.order_book.check_order_status(order)
        fulfilled_amount = self.order_book.check_order_fulfilled_amount(order)
        return {
            "status": status,
            "fulfilled_amount": fulfilled_amount,
            "order_id": order.id,
            "unfilled_amount": order.quantity - fulfilled_amount,
        }

    def get_portfolio(self, user_id: str):
        return self.order_book.get_portfolio(user_id)

    def get_unfulfilled_orders(self, user_id: str):
        return self.order_book.get_unfulfilled_orders(user_id)

    def get_fulfilled_orders(self, user_id: str):
        return self.order_book.get_fulfilled_orders(user_id)
