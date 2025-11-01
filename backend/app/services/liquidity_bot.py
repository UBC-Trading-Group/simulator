import json
import random

from app.core.logging import get_logger

logger = get_logger(__name__)


class LiquidityBot:
    # TODO: fit in highest bid + lowest ask / 2 to mid price
    def __init__(self, instrument_id, mid_price, inventory):
        self.instrument_id = instrument_id
        self.mid_price = mid_price
        self.inventory = inventory

        self.base_spread = 0.1  # per suggestion
        self.stress_coefficient = random.uniform(
            0.05, 0.15
        )  # simulates investors in the market
        self.inventory_coefficient = random.uniform(
            0.005, 0.05
        )  # how risk-averse the bot is
        self.quote_noise_sigma = random.uniform(0, 0.05)  # per DC discussion

    # TODO: adjust with bid and ask externally
    def adjust_mid_price(self, mid_price):
        self.mid_price = mid_price

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
        spread = self.compute_spread(drift_term)

        # Initial bid and ask at level 0
        bid, ask = self.compute_quotes(spread)

        bids = []
        asks = []

        for lvl in range(levels):
            depth = self.depth_curve(lvl)
            bid_price = round(bid - lvl * spread, 2)
            ask_price = round(ask + lvl * spread, 2)

            bids.append([bid_price, depth])
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
