from pathlib import Path
import unittest


class ChartUiTests(unittest.TestCase):
    def test_dashboard_requests_one_chart_per_asset_and_labels_resistance(self):
        page = (Path(__file__).parent.parent / 'index.html').read_text(encoding='utf-8')
        self.assertIn("'/api/chart?symbol='", page)
        self.assertIn('4 HOUR RESISTANCE', page)
        self.assertIn('DAILY RESISTANCE', page)
        self.assertIn('drawChart', page)


if __name__ == '__main__':
    unittest.main()
