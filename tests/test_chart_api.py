import json
import unittest
from unittest.mock import patch

from server import chart_payload


class ChartPayloadTests(unittest.TestCase):
    @patch('server.chart_data')
    def test_returns_symbol_and_per_asset_chart_with_resistance_levels(self, mock_chart_data):
        mock_chart_data.return_value = {
            'interval': '5m',
            'points': [{'time': 1000, 'close': 100.0}],
            'resistance': {'4h': 111.0, '1d': 125.0},
            'lookback': {'4h_candles': 20, '1d_candles': 20},
        }

        body = json.loads(chart_payload('BTCUSDT'))

        self.assertEqual(body['symbol'], 'BTCUSDT')
        self.assertEqual(body['chart']['resistance']['4h'], 111.0)
        self.assertEqual(body['chart']['resistance']['1d'], 125.0)
        mock_chart_data.assert_called_once_with('BTCUSDT')

    def test_rejects_unsupported_symbol(self):
        with self.assertRaisesRegex(ValueError, 'unsupported symbol'):
            chart_payload('DOGEUSDT')


if __name__ == '__main__':
    unittest.main()
