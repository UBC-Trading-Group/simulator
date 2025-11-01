class OrderProcessor:
    def __init__(self, order_book, price_engine):
        self.order_book = order_book
        self.price_engine = price_engine

    def process_order(self, order):
        """
        See expected order format in order_book.py

        Match order with order book, use match_order in order book
        - If successful, modify / remove corresponding order, then modify price in price engine (DO THIS ONE LATER)
        - If unsuccessful, add order to order book
        Return status of order

        TODO: handle market, limit, stop order
        """
        processing_status, unprocessed_quantity = self.order_book.match_order(order)

        # Price engine update will be implemented later
        return {
            "status": processing_status,
            "message": "Order processed successfully",
            "unprocessed_quantity": unprocessed_quantity,
        }

    def cancel_order(self, order):
        """
        See expected order format in order_book.py

        Remove order from order book
        Return status of cancellation
        """
        success = self.order_book.remove_order(order)
        if success:
            return {"status": "CANCELLED", "message": "Order successfully cancelled"}
        else:  # most likely will be impossible to reach this point
            return {
                "status": "NOT_FOUND",
                "message": "Order not found in the order book",
            }
