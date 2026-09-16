import json, unittest
from unittest.mock import patch
from server import chart_payload

class ChartPayloadTests(unittest.TestCase):
    @patch('server.chart_data')
    def test_returns_one_hour_and_daily_support_resistance_levels(self, mock_chart_data):
        mock_chart_data.return_value={'interval':'5m','points':[{'time':1000,'close':100.0}],
          'levels':{'1h':{'support':91.0,'resistance':111.0},'1d':{'support':80.0,'resistance':125.0}}}
        body=json.loads(chart_payload('BTCUSDT'))
        self.assertEqual(body['symbol'],'BTCUSDT')
        self.assertEqual(body['chart']['levels']['1h']['support'],91.0)
        self.assertEqual(body['chart']['levels']['1d']['resistance'],125.0)
    def test_rejects_unsupported_symbol(self):
        with self.assertRaisesRegex(ValueError,'unsupported symbol'): chart_payload('DOGEUSDT')
if __name__ == '__main__': unittest.main()
