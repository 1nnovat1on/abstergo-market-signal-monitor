from pathlib import Path
import unittest
class ChartUiTests(unittest.TestCase):
 def test_dashboard_requests_and_labels_one_hour_daily_support_resistance(self):
  page=(Path(__file__).parent.parent/'index.html').read_text(encoding='utf-8')
  self.assertIn("candles(symbol,'1h',250)",page)
  self.assertIn('1 HOUR SUPPORT',page); self.assertIn('1 HOUR RESISTANCE',page)
  self.assertIn('DAILY SUPPORT',page); self.assertIn('DAILY RESISTANCE',page)
  self.assertIn('drawChart',page)
if __name__=='__main__': unittest.main()
