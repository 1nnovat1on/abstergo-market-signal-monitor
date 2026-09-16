from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlparse
import json, time
from indicators import ema, rsi_wilder, classify_rsi, crossed, resistance, support

ROOT = Path(__file__).parent
SYMBOLS = ('BTCUSDT','ETHUSDT')
INTERVALS = ('5m','1h')
BINANCE = 'https://data-api.binance.vision/api/v3/klines'

def closed_candles(symbol, interval, limit):
    url = f'{BINANCE}?symbol={symbol}&interval={interval}&limit={limit}'
    req = Request(url, headers={'User-Agent':'Abstergo-Market-Monitor/1.0'})
    with urlopen(req, timeout=12) as response:
        rows = json.load(response)
    now = int(time.time() * 1000)
    return [
        {'open_time': int(r[0]), 'close_time': int(r[6]), 'high': float(r[2]), 'low': float(r[3]), 'close': float(r[4])}
        for r in rows if int(r[6]) < now
    ]


def fetch(symbol, interval):
    closed = closed_candles(symbol, interval, 250)
    closes = [c['close'] for c in closed]
    if len(closes) < 202: raise ValueError('Not enough closed candles')
    current, previous = closes[-1], closes[-2]
    payload = {}
    for period in (100,150,200):
        now = ema(closes, period)
        before = ema(closes[:-1], period)
        payload[str(period)] = {'value':now,'distance_pct':(current-now)/now*100}
        if period in (100,200): payload[str(period)]['cross'] = crossed(previous,current,before,now)
    rsi = rsi_wilder(closes,14)
    return {'interval':interval,'price':current,'rsi':rsi,'rsi_zone':classify_rsi(rsi),
            'emas':payload,'closed_at':closed[-1]['close_time'],'source':'Binance public market data'}


def chart_data(symbol):
    candles = closed_candles(symbol, '5m', 96)
    if len(candles) < 2: raise ValueError('Not enough closed chart candles')
    one_hour = closed_candles(symbol, '1h', 21)
    daily = closed_candles(symbol, '1d', 21)
    return {
        'interval': '5m',
        'points': [{'time': c['close_time'], 'close': c['close']} for c in candles],
        'levels': {
            '1h': {'support': support(one_hour, 20), 'resistance': resistance(one_hour, 20)},
            '1d': {'support': support(daily, 20), 'resistance': resistance(daily, 20)},
        },
        'lookback': {'1h_candles': 20, '1d_candles': 20},
    }

def chart_payload(symbol):
    """Validated single-asset chart payload for the public dashboard."""
    if symbol not in SYMBOLS:
        raise ValueError('unsupported symbol')
    return json.dumps({'symbol': symbol, 'chart': chart_data(symbol)})


def snapshot():
    result={'generated_at':int(time.time()*1000),'assets':{}}
    for symbol in SYMBOLS:
        result['assets'][symbol]={'symbol':symbol,'timeframes':{}}
        for interval in INTERVALS:
            try: result['assets'][symbol]['timeframes'][interval]=fetch(symbol,interval)
            except Exception as exc: result['assets'][symbol]['timeframes'][interval]={'error':str(exc)}
    return result

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean=urlparse(path).path.lstrip('/') or 'index.html'
        return str((ROOT/clean).resolve())
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/market':
            body=json.dumps(snapshot()).encode()
            self.send_response(200); self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(body)))
            self.end_headers(); self.wfile.write(body); return
        if parsed.path == '/api/chart':
            symbol = parsed.query.split('symbol=', 1)[1].split('&', 1)[0] if 'symbol=' in parsed.query else ''
            try:
                body = chart_payload(symbol).encode()
                self.send_response(200)
            except ValueError as exc:
                body = json.dumps({'error': str(exc)}).encode()
                self.send_response(400)
            self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(body)))
            self.end_headers(); self.wfile.write(body); return
        super().do_GET()
    def log_message(self, fmt, *args): pass

if __name__=='__main__':
    print('Dashboard: http://127.0.0.1:8788', flush=True)
    ThreadingHTTPServer(('127.0.0.1',8788),Handler).serve_forever()
