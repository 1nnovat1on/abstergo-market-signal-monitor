def ema(values, period):
    if len(values) < period:
        raise ValueError('insufficient values')
    seed = sum(values[:period]) / period
    multiplier = 2 / (period + 1)
    value = seed
    for price in values[period:]:
        value = (price - value) * multiplier + value
    return value


def rsi_wilder(values, period=14):
    if len(values) <= period:
        raise ValueError('insufficient values')
    changes = [b-a for a,b in zip(values, values[1:])]
    gains = [max(x, 0) for x in changes]
    losses = [max(-x, 0) for x in changes]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for gain, loss in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period-1) + gain) / period
        avg_loss = (avg_loss * (period-1) + loss) / period
    if avg_loss == 0:
        return 100.0
    return 100 - 100 / (1 + avg_gain / avg_loss)


def classify_rsi(value):
    if value <= 12: return 'EXTREME OVERSOLD'
    if value <= 20: return 'OVERSOLD'
    if value >= 80: return 'EXTREME OVERBOUGHT'
    if value >= 60: return 'OVERBOUGHT'
    return 'NEUTRAL'


def crossed(previous_close, close, previous_ema, current_ema):
    if previous_close <= previous_ema and close > current_ema: return 'ABOVE'
    if previous_close >= previous_ema and close < current_ema: return 'BELOW'
    return None


def resistance(candles, lookback=20):
    """Highest high across the most recent closed candles in a lookback window."""
    if not candles:
        raise ValueError('no closed candles')
    if lookback < 1:
        raise ValueError('lookback must be positive')
    return max(candle['high'] for candle in candles[-lookback:])
