import unittest
from datetime import datetime, timedelta

from web.buy_signals import analyze_multi_timeframes


class BuySignalTests(unittest.TestCase):
    def test_multi_timeframe_detects_drop_and_oversold(self):
        now = datetime(2026, 1, 1, 12, 0, 0)
        rows = []
        for index in range(60):
            timestamp = now - timedelta(minutes=59 - index)
            price = 100 - (index * 0.5)
            rows.append((price, timestamp))

        indicators = {"price": 70.5, "ma20": 76.0, "rsi": 28.0}
        signals = analyze_multi_timeframes(rows, indicators)

        active = [item for item in signals if item["signal"] == "BUY"]
        self.assertTrue(active)
        self.assertIn("RSI_OVERSOLD", active[0]["reasons"])
        self.assertIn("BELOW_MA20", active[0]["reasons"])

    def test_multi_timeframe_handles_not_enough_rows(self):
        now = datetime(2026, 1, 1, 12, 0, 0)
        rows = [(100.0, now), (101.0, now + timedelta(minutes=1))]
        indicators = {"price": 101.0, "ma20": 100.0, "rsi": 55.0}
        signals = analyze_multi_timeframes(rows, indicators)

        self.assertEqual(len(signals), 4)
        self.assertTrue(all(item["signal"] is None for item in signals))
