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
    
    def remove_order(self, order):
        """
        Remove order from order book
        Has to be linear scan since multiple orders can have same price
        
        TODO: Probably can (partially) optimize by using bin search to get range first
        """
        side = order["side"]
        orders = self.buys if side == "buy" else self.sells
        
        for i, o in enumerate(orders):
            if o == order:
                orders.pop(i)
                return True
        return False
    
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
        Matching should happen based on proximity to mid price, closest to mid price goes first
        Return status whether matching was successful
        """
        side = order["side"]
        opposite_side_orders = self.sells if side == "buy" else self.buys
        
        if not opposite_side_orders:
            return False, None
            
        mid = self.mid_price()
        if mid is None:
            return False, None
            
        # Find the best matching order (closest to mid price)
        best_match = None
        best_diff = float('inf')
        best_idx = -1
        
        # TODO: use sorted property to optimize
        for i, opposite_order in enumerate(opposite_side_orders):
            if (side == "buy" and opposite_order["price"] > order["price"]) or \
               (side == "sell" and opposite_order["price"] < order["price"]):
                continue  # Price doesn't match, ignore
                
            # Calculate absolute difference from mid price
            diff = abs(opposite_order["price"] - mid)
            if diff < best_diff:
                best_diff = diff
                best_match = opposite_order
                best_idx = i
                
        if best_match is None:
            # Can't be matched, add to order book
            self.add_order(order)
            return False, None
            
        # Remove the matched order from the order book
        # TODO: this assumes that the quantity matches, implement logic to handle otherwise
        opposite_side_orders.pop(best_idx)
        return True, best_match