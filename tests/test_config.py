import unittest

from bot.config import BOT_RULES, BUY_SIGNAL_RULES


class ConfigTests(unittest.TestCase):
    def test_bot_rules_have_expected_keys(self):
        self.assertIn("fast_drop_threshold", BOT_RULES)
        self.assertIn("stale_after_seconds", BOT_RULES)

    def test_buy_signal_rules_have_timeframes(self):
        self.assertTrue(BUY_SIGNAL_RULES["timeframes"])
        self.assertIn("minutes", BUY_SIGNAL_RULES["timeframes"][0])
