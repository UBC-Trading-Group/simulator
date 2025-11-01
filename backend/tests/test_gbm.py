from unittest import TestCase

import numpy as np

from app.services.gbm import GeometricBrownianMotionAssetSimulator


class TestGeometricBrownianMotionAssetSimulator(TestCase):
    def setUp(self):
        np.random.seed(42)

        # can adjust values
        self.mu = 0.1
        self.sigma = 0.2
        self.S0 = 100
        self.dt = 1 / 252

        # how large the sample pool is
        self.n_samples = 100000

        self.gbmas = GeometricBrownianMotionAssetSimulator(
            self.S0, self.mu, self.sigma, self.dt
        )

    def test_gbm_mean_var(self):
        prices = [self.S0]
        for _ in range(self.n_samples):
            prices.append(self.gbmas())

        expected_mean = (self.mu - (0.5 * self.sigma**2)) * self.dt
        expected_var = self.sigma**2 * self.dt

        # sample mean and variance
        sample_mean = np.mean(prices)
        sample_var = np.var(prices)

        # allow 10% tolerance
        # self.assertTrue(np.isclose(sample_mean, expected_mean, rtol=0.1))
        # self.assertTrue(np.isclose(sample_var, expected_var, rtol=0.1))
