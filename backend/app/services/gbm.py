import math

import numpy as np


class GeometricBrownianMotionAssetSimulator:
    def __init__(self, current_price, mean, variance, delta):
        # queried from UBC TG DB
        self.current_price = current_price
        self.mean = mean
        self.variance = variance
        self.sigma = math.sqrt(variance)
        self.delta = delta
        self.time = 0.0

        # TODO: store previous prices

    @staticmethod
    def generate_e():
        return np.random.normal(0, 1)  # random sampling E

    def calculate(self):
        e = self.generate_e()
        # TODO: calculate drift
        drift = 0

        next_price = self.current_price * np.exp(
            (self.mean + drift - self.variance / 2) * self.delta
            + self.sigma * e * math.sqrt(self.delta)
        )

        self.current_price = next_price
        self.time += self.delta
        return next_price

    def __call__(self):
        return self.calculate()
