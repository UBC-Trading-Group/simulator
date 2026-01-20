import json
import random

from app.core.deps import get_logger

logger = get_logger(__name__)


class LiquidityBot:
    # TODO: fit in highest bid + lowest ask / 2 to mid price
    def __init__(self, instrument_id, mid_price, inventory):
        self.instrument_id = instrument_id
        self.mid_price = mid_price
        self.inventory = inventory

        self.base_spread = 0.005  # 0.5% base spread for realistic bid-ask
        self.stress_coefficient = random.uniform(
            0.001, 0.003
        )  # simulates investors in the market
        self.inventory_coefficient = random.uniform(
            0.0001, 0.001
        )  # how risk-averse the bot is
        self.quote_noise_sigma = random.uniform(0, 0.001)  # small noise
        
        # Random walk parameters for price noise
        self.price_volatility = 0.0045  # 0.45% volatility per tick for active movement
        self.mean_reversion = 0.97  # moderate mean reversion
        self.initial_price = mid_price
        
        # Inventory pressure - adjust mid price based on inventory
        self.inventory_pressure_coeff = 0.0005  # 0.05% price shift per unit of inventory (reduced from 0.2%)
        
        # Inventory limits to prevent extreme positions
        self.max_inventory = 200  # Maximum long position
        self.min_inventory = -200  # Maximum short position

    # TODO: adjust with bid and ask externally
    def adjust_mid_price(self, mid_price):
        self.mid_price = mid_price
    
    def update_inventory(self, inventory_change: int):
        """
        Update inventory when orders are filled.
        Positive = bought (inventory increases)
        Negative = sold (inventory decreases)
        """
        self.inventory += inventory_change
    
    def apply_random_walk(self):
        """
        Apply random walk to mid price to generate noise.
        This creates realistic price movement without using drift.
        """
        # Random shock
        shock = random.gauss(0, self.price_volatility * self.mid_price)
        
        # Mean reversion to initial price
        mean_reversion_component = (self.initial_price - self.mid_price) * (1 - self.mean_reversion)
        
        # Inventory pressure: if inventory is positive (too much bought), lower price
        # if inventory is negative (too much sold), raise price
        # Cap inventory effect to prevent extreme price movements
        capped_inventory = max(-100, min(100, self.inventory))
        inventory_pressure = -capped_inventory * self.inventory_pressure_coeff * self.initial_price
        
        # Update mid price
        new_price = self.mid_price + shock + mean_reversion_component + inventory_pressure
        
        # Ensure price stays positive (minimum 10% of initial price)
        self.mid_price = max(new_price, self.initial_price * 0.1)

    def compute_spread(self, drift_term):
        """
        spread_i = s0 + k * |Φ_i(t)| + γ * |Q_i| + η
        """
        eta = random.gauss(0, self.quote_noise_sigma)
        spread = (
            self.base_spread
            + self.stress_coefficient * abs(drift_term)
            + self.inventory_coefficient * abs(self.inventory)
            + eta
        )
        return spread

    def compute_quotes(self, spread):
        """
        Places symmetric quotes:
        bid = M_i * (1 - spread_i/2)
        ask = M_i * (1 + spread_i/2)
        """
        bid = self.mid_price * (1 - spread / 2)
        ask = self.mid_price * (1 + spread / 2)
        return bid, ask

    def depth_curve(self, level):
        """
        depth_curve = max(50 - 10 * level, 10)
        """
        return max(50 - 10 * level, 10)

    def generate_order_book(self, drift_term, levels=3):
        # Apply random walk to create price noise
        self.apply_random_walk()
        
        # Compute spread (drift_term should be 0 for liquidity bots)
        spread = self.compute_spread(drift_term)

        # Initial bid and ask at level 0
        bid, ask = self.compute_quotes(spread)

        bids = []
        asks = []

        for lvl in range(levels):
            depth = self.depth_curve(lvl)
            bid_price = round(bid - lvl * spread, 2)
            ask_price = round(ask + lvl * spread, 2)

            # Skip bid orders if inventory is too high (too long)
            if self.inventory < self.max_inventory:
                bids.append([bid_price, depth])
            
            # Skip ask orders if inventory is too low (too short)
            if self.inventory > self.min_inventory:
                asks.append([ask_price, depth])

        book_snapshot = {
            "type": "book_snapshot",
            "instrumentId": self.instrument_id,
            "bids": bids,
            "asks": asks,
        }

        return book_snapshot


# For testing only
if __name__ == "__main__":
    bot = LiquidityBot(
        instrument_id="META", mid_price=180.0, inventory=random.randint(-5, 5)
    )
    drift_term = random.uniform(-1, 1)
    snapshot = bot.generate_order_book(drift_term)
    logger.info(f"Generated order book snapshot: {json.dumps(snapshot)}")
