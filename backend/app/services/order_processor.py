class OrderProcessor:
    def __init__(self, order_book, price_engine):
        self.order_book = order_book
        self.price_engine = price_engine
    
    def process_order(self, order):
        """
        See expected order format in order_book.py
        
        TODO
        Match order with order book
        - If successful, modify / remove corresponding order, then modify price in price engine
        - If unsuccessful, add order to order book
        Return status of order
        """
    
    def cancel_order(self, order):
        """
        See expected order format in order_book.py
        
        TODO
        Remove order from order book
        Return status of cancellation
        """