from app.schemas.order import OrderModel


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
        order = self._ensure_model(order)

        processing_status, unprocessed_quantity = self.order_book.match_order(order)

        return {
            "status": processing_status,
            "message": "Order processed successfully",
            "unprocessed_quantity": unprocessed_quantity,
        }

    def cancel_order(self, order):
        order = self._ensure_model(order)

        success = self.order_book.remove_order(order)

        if success:
            return {"status": "CANCELLED", "message": "Order successfully cancelled"}
        else:
            return {
                "status": "NOT_FOUND",
                "message": "Order not found in the order book",
            }
