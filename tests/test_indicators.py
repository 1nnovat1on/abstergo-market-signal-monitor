import unittest
from indicators import ema, rsi_wilder, classify_rsi, crossed, resistance

class IndicatorTests(unittest.TestCase):
    def test_ema_constant_series(self):
        self.assertEqual(ema([10.0] * 250, 200), 10.0)

    def test_ema_requires_period_values(self):
        with self.assertRaises(ValueError):
            ema([1.0, 2.0], 3)

    def test_rsi_all_gains_is_100(self):
        self.assertEqual(rsi_wilder(list(range(1, 40)), 14), 100.0)

    def test_rsi_zones_use_strongest_threshold(self):
        self.assertEqual(classify_rsi(10), 'EXTREME OVERSOLD')
        self.assertEqual(classify_rsi(18), 'OVERSOLD')
        self.assertEqual(classify_rsi(50), 'NEUTRAL')
        self.assertEqual(classify_rsi(65), 'OVERBOUGHT')
        self.assertEqual(classify_rsi(85), 'EXTREME OVERBOUGHT')

    def test_cross_requires_side_change(self):
        self.assertEqual(crossed(99, 101, 100, 100), 'ABOVE')
        self.assertEqual(crossed(101, 99, 100, 100), 'BELOW')
        self.assertIsNone(crossed(101, 102, 100, 100))

    def test_resistance_is_highest_high_in_closed_lookback(self):
        candles = [
            {'high': 99}, {'high': 104}, {'high': 102}, {'high': 111}, {'high': 108},
        ]
        self.assertEqual(resistance(candles, lookback=3), 111)
        self.assertEqual(resistance(candles, lookback=99), 111)

    def test_resistance_requires_a_closed_candle(self):
        with self.assertRaises(ValueError):
            resistance([])

if __name__ == '__main__':
    unittest.main()
