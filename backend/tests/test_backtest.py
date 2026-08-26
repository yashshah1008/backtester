"""
Unit tests for the backtest engine.

These run against plain pandas Series — no DB, no API, no network —
which is exactly why the engine was written as pure functions.
"""

import pandas as pd
import pytest

from app.backtest import run_backtest, _max_drawdown, _sharpe_ratio, _win_rate


def make_price_series(values, start="2020-01-01"):
    dates = pd.date_range(start=start, periods=len(values), freq="B")
    return pd.Series(values, index=dates)


def test_flat_prices_produce_zero_return():
    """If price never moves, strategy and buy-and-hold should both return ~0%."""
    prices = make_price_series([100.0] * 250)
    result = run_backtest(prices, short_window=10, long_window=50)

    assert result["total_return_pct"] == pytest.approx(0.0, abs=0.01)
    assert result["buy_hold_return_pct"] == pytest.approx(0.0, abs=0.01)
    assert result["num_trades"] == 0


def test_steadily_rising_prices_are_profitable():
    """A clean uptrend should produce a positive strategy return and no drawdown-heavy losses."""
    prices = make_price_series([100 + i * 0.5 for i in range(300)])
    result = run_backtest(prices, short_window=10, long_window=50)

    assert result["buy_hold_return_pct"] > 0
    assert result["total_return_pct"] >= 0  # strategy may lag but shouldn't lose money in a clean uptrend


def test_insufficient_history_raises():
    """Fewer data points than the long window should fail loudly, not silently return zeros."""
    prices = make_price_series([100.0] * 30)
    with pytest.raises(ValueError, match="Not enough price history"):
        run_backtest(prices, short_window=10, long_window=50)


def test_short_window_must_be_less_than_long_window():
    prices = make_price_series([100.0] * 300)
    with pytest.raises(ValueError, match="short_window must be less"):
        run_backtest(prices, short_window=50, long_window=10)


def test_no_crossovers_means_no_trades():
    """A strictly monotonic short-window-always-above scenario shouldn't force phantom trades."""
    prices = make_price_series([100.0] * 60 + [200.0] * 240)  # one big jump, then flat
    result = run_backtest(prices, short_window=10, long_window=50)
    # After the initial crossover there should be very few trades, not one per day.
    assert result["num_trades"] <= 4


def test_max_drawdown_is_negative_or_zero():
    equity = pd.Series([1.0, 1.1, 0.9, 1.05, 0.8, 1.2])
    dd = _max_drawdown(equity)
    assert dd <= 0
    assert dd == pytest.approx((0.8 - 1.1) / 1.1, rel=1e-3)


def test_sharpe_ratio_zero_when_no_volatility():
    returns = pd.Series([0.0] * 100)
    assert _sharpe_ratio(returns) == 0.0


def test_win_rate_zero_when_never_held():
    df = pd.DataFrame({"position": [0, 0, 0], "daily_return": [0.01, -0.02, 0.03]})
    assert _win_rate(df) == 0.0


def test_win_rate_computed_correctly_when_held():
    df = pd.DataFrame({"position": [1, 1, 1, 1], "daily_return": [0.01, -0.02, 0.03, 0.01]})
    assert _win_rate(df) == pytest.approx(75.0)
