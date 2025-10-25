import bisect

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
        buys[0] is the lowest bid order, buys sorted ascending
        sells[0] is the highest ask order, sells sorted descending
        """
        self.buys = []
        self.sells = []
        
    def add_order(self, order):
        price = order["price"]
        side = order["side"]
        
        if side == "buy":
            prices = [o["price"] for o in self.buys]
            idx = bisect.bisect_left(prices, price)
            self.buys.insert(idx, order)
        elif side == "sell":
            # Invert sign to maintain descending order
            prices = [-o["price"] for o in self.sells]
            idx = bisect.bisect_left(prices, -price)
            self.sells.insert(idx, order)
        else:
            raise ValueError("Invalid side")
    
    def best_bid(self):
        if not self.buys:
            return None
        return self.buys[-1]
    
    def best_ask(self):
        if not self.sells:
            return None
        return self.sells[-1]

    def mid_price(self):
        highest_bid = self.best_bid()
        lowest_ask = self.best_ask()
        if highest_bid and lowest_ask:
            return (highest_bid["price"] + lowest_ask["price"]) / 2
        return None

    def match_order(self, order):
        """
        Matches buy with corresponding sell order, or sell with corresponding buy order
        
        TODO
        Matching should happen based on proximity to mid price
        Return status whether matching was successful
        """
        
            