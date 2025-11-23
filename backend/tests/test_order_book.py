from unittest import TestCase

from app.schemas.order import OrderModel, OrderSide, OrderStatus
from app.services.order_book import OrderBook


class TestOrderBook(TestCase):
    def setUp(self):
        self.order_book = OrderBook()
        # Common test orders as OrderModel instances
        self.buy_order_100 = OrderModel(
            price=100,
            quantity=10,
            ticker="AAPL",
            user_id="u1",
            side=OrderSide.BUY,
        )
        self.buy_order_101 = OrderModel(
            price=101,
            quantity=5,
            ticker="AAPL",
            user_id="u2",
            side=OrderSide.BUY,
        )
        self.sell_order_102 = OrderModel(
            price=102,
            quantity=8,
            ticker="AAPL",
            user_id="u3",
            side=OrderSide.SELL,
        )
        self.sell_order_103 = OrderModel(
            price=103,
            quantity=12,
            ticker="AAPL",
            user_id="u4",
            side=OrderSide.SELL,
        )

    def test_order_insertion_start(self):
        """Test inserting buy orders at the start of the order book"""
        self.order_book.add_order(self.buy_order_101)
        self.order_book.add_order(self.buy_order_100)

        # Verify best bid is correct
        self.assertEqual(len(self.order_book.buys["AAPL"]), 2)
        best_bid_prices = [order.price for _, _, order in self.order_book.buys["AAPL"]]
        self.assertIn(100, best_bid_prices)
        self.assertIn(101, best_bid_prices)
        self.assertEqual(self.order_book.buys["AAPL"][0][2].price, max(best_bid_prices))

    def test_order_insertion_end(self):
        """Test inserting sell orders at the end of the order book"""
        self.order_book.add_order(self.sell_order_103)
        self.order_book.add_order(self.sell_order_102)

        self.assertEqual(len(self.order_book.sells["AAPL"]), 2)
        sell_prices = [order.price for _, _, order in self.order_book.sells["AAPL"]]
        self.assertIn(102, sell_prices)
        self.assertIn(103, sell_prices)
        self.assertEqual(self.order_book.sells["AAPL"][0][2].price, min(sell_prices))

    def test_order_insertion_middle(self):
        """Test inserting orders in the middle of the order book"""
        self.order_book.add_order(
            OrderModel(
                price=100, quantity=5, ticker="AAPL", user_id="u1", side=OrderSide.BUY
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=105, quantity=5, ticker="AAPL", user_id="u2", side=OrderSide.BUY
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=102, quantity=5, ticker="AAPL", user_id="u3", side=OrderSide.BUY
            )
        )

        self.assertEqual(len(self.order_book.buys["AAPL"]), 3)
        prices = [order.price for _, _, order in self.order_book.buys["AAPL"]]
        for p in [100, 102, 105]:
            self.assertIn(p, prices)
        self.assertEqual(self.order_book.buys["AAPL"][0][2].price, max(prices))

    def test_order_matching_partial(self):
        """Test partial order matching"""
        self.order_book.add_order(self.sell_order_102)

        buy_order = OrderModel(
            price=103, quantity=15, ticker="AAPL", user_id="u1", side=OrderSide.BUY
        )
        status, remaining_qty = self.order_book.match_order(buy_order)

        self.assertEqual(status, OrderStatus.PARTIALLY_FILLED)
        self.assertEqual(remaining_qty, 7)

        # Sell heap should be empty
        self.assertEqual(len(self.order_book.sells["AAPL"]), 0)

        # Buy order should be in the book with remaining quantity
        self.assertEqual(len(self.order_book.buys["AAPL"]), 1)
        self.assertEqual(self.order_book.buys["AAPL"][0][2].quantity, 7)

    def test_order_matching_full(self):
        """Test full order matching"""
        self.order_book.add_order(self.sell_order_102)

        buy_order = OrderModel(
            price=103, quantity=5, ticker="AAPL", user_id="u1", side=OrderSide.BUY
        )
        status, remaining_qty = self.order_book.match_order(buy_order)

        self.assertEqual(status, OrderStatus.FILLED)
        self.assertEqual(remaining_qty, 0)

        self.assertEqual(len(self.order_book.sells["AAPL"]), 1)
        self.assertEqual(len(self.order_book.buys.get("AAPL", [])), 0)
        self.assertEqual(self.order_book.sells["AAPL"][0][2].quantity, 3)

    def test_order_matching_no_match(self):
        """Test order matching when no match is possible"""
        self.order_book.add_order(self.sell_order_103)

        buy_order = OrderModel(
            price=100, quantity=5, ticker="AAPL", user_id="u1", side=OrderSide.BUY
        )
        status, remaining_qty = self.order_book.match_order(buy_order)

        self.assertEqual(status, OrderStatus.OPEN)
        self.assertEqual(remaining_qty, 5)
        self.assertEqual(len(self.order_book.buys["AAPL"]), 1)
        self.assertEqual(len(self.order_book.sells["AAPL"]), 1)

    def test_order_removal(self):
        """Test removing an order from the order book"""
        self.order_book.add_order(self.buy_order_100)
        self.assertEqual(len(self.order_book.buys["AAPL"]), 1)

        result = self.order_book.remove_order(self.order_book.buys["AAPL"][0][2])
        self.assertTrue(result)
        self.assertEqual(len(self.order_book.buys["AAPL"]), 0)

    def test_mid_price_calculation(self):
        """Test mid price calculation"""
        self.assertIsNone(self.order_book.mid_price("AAPL"))

        self.order_book.add_order(self.buy_order_100)
        self.assertIsNone(self.order_book.mid_price("AAPL"))

        self.order_book.add_order(self.sell_order_102)
        expected_mid = (100 + 102) / 2
        self.assertEqual(self.order_book.mid_price("AAPL"), expected_mid)

    def test_multiple_order_matching(self):
        """Test matching an order against multiple orders"""
        self.order_book.add_order(
            OrderModel(
                price=101, quantity=3, ticker="AAPL", user_id="u1", side=OrderSide.SELL
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=102, quantity=5, ticker="AAPL", user_id="u2", side=OrderSide.SELL
            )
        )

        buy_order = OrderModel(
            price=103, quantity=7, ticker="AAPL", user_id="u3", side=OrderSide.BUY
        )
        status, remaining_qty = self.order_book.match_order(buy_order)

        self.assertEqual(status, OrderStatus.FILLED)
        self.assertEqual(remaining_qty, 0)

        # After match, one sell order remains with quantity 1
        remaining_sells = [o[2] for o in self.order_book.sells["AAPL"]]
        self.assertEqual(len(remaining_sells), 1)
        self.assertEqual(remaining_sells[0].quantity, 1)
        self.assertEqual(remaining_sells[0].price, 102)

        self.assertEqual(len(self.order_book.buys.get("AAPL", [])), 0)


    def test_clamp_ignores_extreme_high_bid(self):
        """Test that placing an outlier bid does not affect mid-price"""
        # Place 2 normal orders
        self.order_book.add_order(
            OrderModel(
                price=100, quantity=3, ticker="AAPL", user_id="u1", side=OrderSide.BUY
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=102, quantity=3, ticker="AAPL", user_id="u2", side=OrderSide.SELL
            )
        )

        # Last traded price set near the mid
        self.order_book.last_traded_price["AAPL"] = 101


        # Compute initial mid for clamp
        self.order_book.finalize_tick("AAPL")

        print("Mid price before extreme bid:", self.order_book.mid_price("AAPL"))

        #Place an extreme bid outlier
        self.order_book.add_order(
            OrderModel(
                price=100000, quantity=3, ticker="AAPL", user_id="u7", side=OrderSide.BUY
            )
        )

        print("Mid price after extreme bid:", self.order_book.mid_price("AAPL"))

        # Best bid with clamp must ignore outlier
        best_bid_clamped = self.order_book.best_bid_within_clamp("AAPL")
        self.assertEqual(best_bid_clamped.price, 100)

        # Best bid without clamp should show the outlier
        best_bid_unclamped = self.order_book.best_bid("AAPL")
        self.assertEqual(best_bid_unclamped.price, 100000)




