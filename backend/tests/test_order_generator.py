import asyncio
from unittest import TestCase

from app.schemas.order import OrderModel, OrderSide
from app.services.gbm_manager import GBMManager
from app.services.instrument_manager import InstrumentManager
from app.services.order_book import OrderBook
from app.services.order_generator import OrderGenerator


class TestOrderGenerator(TestCase):
    def setUp(self):
        # Create an OrderBook instance
        self.order_book = OrderBook()

        # Common test orders
        self.buy_order_100 = OrderModel(
            price=100,
            quantity=10,
            ticker="AAPL",
            user_id="u1",
            side=OrderSide.BUY,
        )
        self.sell_order_102 = OrderModel(
            price=102,
            quantity=5,
            ticker="AAPL",
            user_id="u2",
            side=OrderSide.SELL,
        )

        # Simple GBM manager stub
        class DummyGBMManager:
            def get_ticker_current_gbm_price(self, ticker):
                return 101  # hardcoded mid price for testing

        self.gbm_manager = DummyGBMManager()

        # InstrumentManager stub returning instruments with hardcoded IDs
        class DummyInstrument:
            def __init__(self, id):
                self.id = id

        self.instrument_manager = type(
            "DummyIM",
            (),
            {"get_all_instruments": lambda self: [DummyInstrument("AAPL")]},
        )()

        # Create OrderGenerator instance
        self.generator = OrderGenerator(
            instrument_manager=self.instrument_manager,
            order_book=self.order_book,
            gbm_manager=self.gbm_manager,
            interval_seconds=0.01,
        )

    # Test the current spread when there are no orders, should be none
    def test_current_spread_none_when_no_orders(self):
        """Test the current spread when there are no orders, should be none"""
        self.assertIsNone(self.generator._current_spread("AAPL"))

    def test_current_spread_with_orders(self):
        """Test the spread when there are orders"""
        # Add buy and sell orders
        self.order_book.add_order(self.buy_order_100)
        self.order_book.add_order(self.sell_order_102)
        spread = self.generator._current_spread("AAPL")
        self.assertEqual(spread, 102 - 100)

    def test_current_spread_with_only_a_buy(self):
        """Test the spread when there is only a buy"""
        self.order_book.add_order(self.buy_order_100)
        self.assertIsNone(self.generator._current_spread("AAPL"))

    def test_current_spread_with_only_a_sell(self):
        """Test the spread when there is only a sell"""
        self.order_book.add_order(self.sell_order_102)
        self.assertIsNone(self.generator._current_spread("AAPL"))

    def test_derive_spread(self):
        """Test derive spread"""
        self.order_book.add_order(self.buy_order_100)
        self.order_book.add_order(self.sell_order_102)
        spread = self.generator._derive_spread("AAPL")
        self.assertEqual(spread, 2)

    def test_derive_spread_none_when_no_spread(self):
        """Test derive spread when no spread, should be none"""
        spread = self.generator._derive_spread("AAPL")
        self.assertIsNone(spread)

    def test_process_ticker_match_created_order_2_sells(self):
        """_process_ticker should create orders and match them leaving 2 sells"""

        # Initial orders
        self.order_book.add_order(
            OrderModel(
                price=90, quantity=1, ticker="AAPL", side=OrderSide.BUY, user_id="u1"
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=110, quantity=2, ticker="AAPL", side=OrderSide.SELL, user_id="u2"
            )
        )

        # Set previous mid so spread calculation works
        self.order_book.previous_mid["AAPL"] = 100
        self.order_book.last_traded_price["AAPL"] = 102

        # Call _process_ticker
        print("Before _process_ticker:")
        print(
            "Buys:",
            [(o.price, o.quantity) for _, _, o in self.order_book.buys.get("AAPL", [])],
        )
        print(
            "Sells:",
            [
                (o.price, o.quantity)
                for _, _, o in self.order_book.sells.get("AAPL", [])
            ],
        )

        # The orders generated should match1 of the 110 sell and leave the other one
        self.generator._process_ticker("AAPL")

        print("After _process_ticker:")
        print(
            "Buys:",
            [(o.price, o.quantity) for _, _, o in self.order_book.buys.get("AAPL", [])],
        )
        print(
            "Sells:",
            [
                (o.price, o.quantity)
                for _, _, o in self.order_book.sells.get("AAPL", [])
            ],
        )

        buys = self.order_book.buys["AAPL"]
        sells = self.order_book.sells["AAPL"]

        self.assertEqual(len(buys), 1)
        self.assertEqual(len(sells), 2)

    def test_process_ticker_match_created_order_2_buys(self):
        """_process_ticker should create orders and match them leaving 2 buys"""

        # Initial orders
        self.order_book.add_order(
            OrderModel(
                price=95, quantity=2, ticker="AAPL", side=OrderSide.BUY, user_id="u1"
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=110, quantity=1, ticker="AAPL", side=OrderSide.SELL, user_id="u2"
            )
        )

        # Set previous mid so spread calculation works
        self.order_book.previous_mid["AAPL"] = 100
        self.order_book.last_traded_price["AAPL"] = 102

        # Call _process_ticker
        print("Before _process_ticker:")
        print(
            "Buys:",
            [(o.price, o.quantity) for _, _, o in self.order_book.buys.get("AAPL", [])],
        )
        print(
            "Sells:",
            [
                (o.price, o.quantity)
                for _, _, o in self.order_book.sells.get("AAPL", [])
            ],
        )

        self.generator._process_ticker("AAPL")

        print("After _process_ticker:")
        print(
            "Buys:",
            [(o.price, o.quantity) for _, _, o in self.order_book.buys.get("AAPL", [])],
        )
        print(
            "Sells:",
            [
                (o.price, o.quantity)
                for _, _, o in self.order_book.sells.get("AAPL", [])
            ],
        )

        buys = self.order_book.buys["AAPL"]
        sells = self.order_book.sells["AAPL"]

        # Matches the one created and leaves behind 2 of the same price which is correct
        self.assertEqual(len(buys), 1)
        self.assertEqual(len(sells), 1)

    def test_process_ticker_match_created_orders(self):
        """" _process_ticker should create orders and match them""" ""

        # Initial orders
        self.order_book.add_order(
            OrderModel(
                price=90, quantity=1, ticker="AAPL", side=OrderSide.BUY, user_id="u1"
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=110, quantity=1, ticker="AAPL", side=OrderSide.SELL, user_id="u2"
            )
        )

        # Set previous mid so spread calculation works
        self.order_book.previous_mid["AAPL"] = 100
        self.order_book.last_traded_price["AAPL"] = 102

        # Call _process_ticker
        print("Before _process_ticker:")
        print(
            "Buys:",
            [(o.price, o.quantity) for _, _, o in self.order_book.buys.get("AAPL", [])],
        )
        print(
            "Sells:",
            [
                (o.price, o.quantity)
                for _, _, o in self.order_book.sells.get("AAPL", [])
            ],
        )

        # The orders generated should match1 of the 110 sell and leave the other one
        self.generator._process_ticker("AAPL")

        print("After _process_ticker:")
        print(
            "Buys:",
            [(o.price, o.quantity) for _, _, o in self.order_book.buys.get("AAPL", [])],
        )
        print(
            "Sells:",
            [
                (o.price, o.quantity)
                for _, _, o in self.order_book.sells.get("AAPL", [])
            ],
        )

        buys = self.order_book.buys["AAPL"]
        sells = self.order_book.sells["AAPL"]

        self.assertEqual(len(buys), 1)
        self.assertEqual(len(sells), 1)

    def test_run_once(self):
        # Test running the async generator for a short time
        self.order_book.add_order(
            OrderModel(
                price=90, quantity=1, ticker="AAPL", side=OrderSide.BUY, user_id="u1"
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=110, quantity=1, ticker="AAPL", side=OrderSide.SELL, user_id="u2"
            )
        )

        # Set previous mid and last traded price so spread calculation works
        self.order_book.previous_mid["AAPL"] = 100
        self.order_book.last_traded_price["AAPL"] = 110

        async def run_once():
            # Run only one loop manually
            self.generator.is_running = True
            for instrument in self.instrument_manager.get_all_instruments():
                self.generator._process_ticker(instrument.id)
            self.generator.is_running = False

        asyncio.run(run_once())

        # Orders should have been placed
        self.assertEqual(len(self.order_book.buys["AAPL"]), 1)
        self.assertEqual(len(self.order_book.sells["AAPL"]), 1)

    def test_process_ticker_no_gbm_price(self):
        """_process_ticker does nothing if GBM returns None"""

        class DummyGBMNone:
            def get_ticker_current_gbm_price(self, ticker):
                return None

        self.generator.gbm_manager = DummyGBMNone()
        self.generator._process_ticker("AAPL")

        # Nothing should be added :)
        self.assertNotIn("AAPL", self.order_book.buys)
        self.assertNotIn("AAPL", self.order_book.sells)

    def test_process_ticker_partial_match_quantity(self):
        """_process_ticker partially matches existing orders and updates quantities"""
        self.order_book.add_order(
            OrderModel(
                price=95, quantity=2, ticker="AAPL", side=OrderSide.BUY, user_id="u1"
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=105, quantity=3, ticker="AAPL", side=OrderSide.SELL, user_id="u2"
            )
        )

        self.order_book.previous_mid["AAPL"] = 100
        self.order_book.last_traded_price["AAPL"] = 102

        self.generator._process_ticker("AAPL")

        buys = [o.quantity for _, _, o in self.order_book.buys["AAPL"]]
        sells = [o.quantity for _, _, o in self.order_book.sells["AAPL"]]

        self.assertTrue(all(q > 0 for q in buys))
        self.assertTrue(all(q > 0 for q in sells))

    def test_process_ticker_multiple_instruments(self):
        """Test for multiple ticketrs that they are in the order book"""

        class DummyIMMultiple:
            def get_all_instruments(self):
                return [
                    type("Inst", (), {"id": "AAPL"})(),
                    type("Inst", (), {"id": "TSLA"})(),
                ]

        self.generator.instrument_manager = DummyIMMultiple()
        self.order_book.add_order(
            OrderModel(
                price=100, quantity=1, ticker="AAPL", side=OrderSide.BUY, user_id="u1"
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=102, quantity=1, ticker="AAPL", side=OrderSide.SELL, user_id="u2"
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=200, quantity=1, ticker="TSLA", side=OrderSide.BUY, user_id="u3"
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=202, quantity=1, ticker="TSLA", side=OrderSide.SELL, user_id="u4"
            )
        )
        self.order_book.previous_mid["AAPL"] = 100
        self.order_book.previous_mid["TSLA"] = 200
        self.order_book.last_traded_price["AAPL"] = 101
        self.order_book.last_traded_price["TSLA"] = 201

        self.generator._process_ticker("AAPL")
        self.generator._process_ticker("TSLA")

        self.assertEqual(set(self.order_book.buys.keys()), {"AAPL", "TSLA"})

    def test_process_ticker_zero_quantity_orders(self):
        """rders with zero quantity should be ignored and if process_ticker is called it should not place orders as spread is 0"""
        # Add zero-quantity orders
        self.order_book.add_order(
            OrderModel(
                price=100, quantity=0, ticker="AAPL", side=OrderSide.BUY, user_id="u1"
            )
        )
        self.order_book.add_order(
            OrderModel(
                price=102, quantity=0, ticker="AAPL", side=OrderSide.SELL, user_id="u2"
            )
        )

        # Set previous_mid and last_traded_price
        self.order_book.previous_mid["AAPL"] = 101
        self.order_book.last_traded_price["AAPL"] = 101

        # Call _process_ticker
        print(
            "Buys:",
            [(o.price, o.quantity) for _, _, o in self.order_book.buys.get("AAPL", [])],
        )
        print(
            "Sells:",
            [
                (o.price, o.quantity)
                for _, _, o in self.order_book.sells.get("AAPL", [])
            ],
        )

        # _process_ticker should skip zero-quantity orders and add new ones
        self.generator._process_ticker("AAPL")

        print(
            "Buys:",
            [(o.price, o.quantity) for _, _, o in self.order_book.buys.get("AAPL", [])],
        )
        print(
            "Sells:",
            [
                (o.price, o.quantity)
                for _, _, o in self.order_book.sells.get("AAPL", [])
            ],
        )

        buys = self.order_book.buys.get("AAPL", [])
        sells = self.order_book.sells.get("AAPL", [])

        # The zero-quantity orders should be ingored
        self.assertEqual(len(buys), 0)
        self.assertEqual(len(sells), 0)
