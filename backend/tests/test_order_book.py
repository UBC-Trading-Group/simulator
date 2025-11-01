from unittest import TestCase

from app.services.order_book import OrderBook, OrderSide, OrderStatus


class TestOrderBook(TestCase):
    def setUp(self):
        self.order_book = OrderBook()
        # Common test orders
        self.buy_order_100 = {
            "price": 100,
            "quantity": 10,
            "ticker": "AAPL",
            "user_id": "u1",
            "side": OrderSide.BUY,
        }
        self.buy_order_101 = {
            "price": 101,
            "quantity": 5,
            "ticker": "AAPL",
            "user_id": "u2",
            "side": OrderSide.BUY,
        }
        self.sell_order_102 = {
            "price": 102,
            "quantity": 8,
            "ticker": "AAPL",
            "user_id": "u3",
            "side": OrderSide.SELL,
        }
        self.sell_order_103 = {
            "price": 103,
            "quantity": 12,
            "ticker": "AAPL",
            "user_id": "u4",
            "side": OrderSide.SELL,
        }

    def test_order_insertion_start(self):
        """Test inserting buy orders at the start of the order book"""
        # Insert buy orders in descending order (should be inserted at start)
        self.order_book.add_order(self.buy_order_101.copy())
        self.order_book.add_order(self.buy_order_100.copy())

        # Verify orders are in correct order (ascending by price)
        self.assertEqual(len(self.order_book.buys), 2)
        self.assertEqual(self.order_book.buys[0]["price"], 100)
        self.assertEqual(self.order_book.buys[1]["price"], 101)

    def test_order_insertion_end(self):
        """Test inserting sell orders at the end of the order book"""
        # Insert sell orders in ascending order (should be inserted at end)
        self.order_book.add_order(self.sell_order_103.copy())
        self.order_book.add_order(self.sell_order_102.copy())

        # Verify orders are in correct order (descending by price)
        self.assertEqual(len(self.order_book.sells), 2)
        self.assertEqual(self.order_book.sells[0]["price"], 103)
        self.assertEqual(self.order_book.sells[1]["price"], 102)

    def test_order_insertion_middle(self):
        """Test inserting orders in the middle of the order book"""
        # Insert buy orders out of order
        self.order_book.add_order(
            {
                "price": 100,
                "quantity": 5,
                "ticker": "AAPL",
                "user_id": "u1",
                "side": OrderSide.BUY,
            }
        )
        self.order_book.add_order(
            {
                "price": 105,
                "quantity": 5,
                "ticker": "AAPL",
                "user_id": "u2",
                "side": OrderSide.BUY,
            }
        )
        self.order_book.add_order(
            {
                "price": 102,
                "quantity": 5,
                "ticker": "AAPL",
                "user_id": "u3",
                "side": OrderSide.BUY,
            }
        )

        # Verify orders are in correct order (ascending by price)
        self.assertEqual(len(self.order_book.buys), 3)
        self.assertEqual(self.order_book.buys[0]["price"], 100)
        self.assertEqual(self.order_book.buys[1]["price"], 102)
        self.assertEqual(self.order_book.buys[2]["price"], 105)

    def test_order_matching_partial(self):
        """Test partial order matching"""
        # Add a sell order to the book
        self.order_book.add_order(self.sell_order_102.copy())

        # Create a buy order that will be partially filled
        buy_order = {
            "price": 103,
            "quantity": 15,
            "ticker": "AAPL",
            "user_id": "u1",
            "side": OrderSide.BUY,
        }

        # Match the order
        status, remaining_qty = self.order_book.match_order(buy_order)

        # Verify the results
        self.assertEqual(status, OrderStatus.PARTIALLY_FILLED)
        self.assertEqual(remaining_qty, 7)  # 15 - 8 = 7 remaining
        self.assertEqual(
            len(self.order_book.sells), 0
        )  # Sell order should be fully matched and removed
        self.assertEqual(
            len(self.order_book.buys), 1
        )  # Buy order should be added with remaining quantity
        self.assertEqual(self.order_book.buys[0]["quantity"], 7)

    def test_order_matching_full(self):
        """Test full order matching"""
        # Add a sell order to the book
        self.order_book.add_order(self.sell_order_102.copy())

        # Create a buy order that will be fully filled
        buy_order = {
            "price": 103,
            "quantity": 5,
            "ticker": "AAPL",
            "user_id": "u1",
            "side": OrderSide.BUY,
        }

        # Match the order
        status, remaining_qty = self.order_book.match_order(buy_order)

        # Verify the results
        self.assertEqual(status, OrderStatus.FILLED)
        self.assertEqual(remaining_qty, 0)
        self.assertEqual(
            len(self.order_book.sells), 1
        )  # Sell order should still exist with reduced quantity
        self.assertEqual(
            len(self.order_book.buys), 0
        )  # Buy order should be fully matched and not added
        self.assertEqual(self.order_book.sells[0]["quantity"], 3)  # 8 - 5 = 3 remaining

    def test_order_matching_no_match(self):
        """Test order matching when no match is possible"""
        # Add a sell order with price higher than our buy order
        self.order_book.add_order(self.sell_order_103.copy())

        # Create a buy order with lower price than any sell order
        buy_order = {
            "price": 100,
            "quantity": 5,
            "ticker": "AAPL",
            "user_id": "u1",
            "side": OrderSide.BUY,
        }

        # Try to match the order
        status, remaining_qty = self.order_book.match_order(buy_order)

        # Verify the results
        self.assertEqual(status, OrderStatus.OPEN)
        self.assertEqual(remaining_qty, 5)  # No quantity was matched
        self.assertEqual(
            len(self.order_book.buys), 1
        )  # Buy order should be added to the book
        self.assertEqual(
            len(self.order_book.sells), 1
        )  # Sell order should remain unchanged

    def test_order_removal(self):
        """Test removing an order from the order book"""
        # Add an order
        self.order_book.add_order(self.buy_order_100.copy())
        self.assertEqual(len(self.order_book.buys), 1)

        # Remove the order
        result = self.order_book.remove_order(self.order_book.buys[0])

        # Verify removal
        self.assertTrue(result)
        self.assertEqual(len(self.order_book.buys), 0)

    def test_mid_price_calculation(self):
        """Test mid price calculation"""
        # With no orders, mid price should be None
        self.assertIsNone(self.order_book.mid_price())

        # Add a buy order
        self.order_book.add_order(self.buy_order_100.copy())
        self.assertIsNone(
            self.order_book.mid_price()
        )  # Still None because we need both buy and sell orders

        # Add a sell order
        self.order_book.add_order(self.sell_order_102.copy())

        # Mid price should be average of best bid and ask
        expected_mid = (100 + 102) / 2
        self.assertEqual(self.order_book.mid_price(), expected_mid)

    def test_multiple_order_matching(self):
        """Test matching an order against multiple orders"""
        # Add multiple sell orders
        self.order_book.add_order(
            {
                "price": 101,
                "quantity": 3,
                "ticker": "AAPL",
                "user_id": "u1",
                "side": OrderSide.SELL,
            }
        )
        self.order_book.add_order(
            {
                "price": 102,
                "quantity": 5,
                "ticker": "AAPL",
                "user_id": "u2",
                "side": OrderSide.SELL,
            }
        )

        # Create a large buy order that will match both sell orders
        buy_order = {
            "price": 103,
            "quantity": 7,
            "ticker": "AAPL",
            "user_id": "u3",
            "side": OrderSide.BUY,
        }

        # Match the order
        status, remaining_qty = self.order_book.match_order(buy_order)

        # Verify the results
        self.assertEqual(status, OrderStatus.FILLED)
        self.assertEqual(remaining_qty, 0)  # all filled

        # here, we take the worst ask first, so only 101 should be left
        self.assertEqual(len(self.order_book.sells), 1)
        self.assertEqual(self.order_book.sells[0]["quantity"], 1)
        self.assertEqual(self.order_book.sells[0]["price"], 101)

        # nothing is added to the buys
        self.assertEqual(len(self.order_book.buys), 0)
