"""
Backtest engine.

Deliberately written as pure functions that take a price DataFrame and
return results — no DB session, no HTTP, no I/O. That's what makes this
module trivial to unit test (see tests/test_backtest.py) and safe to
develop/validate *before* wiring up the API or database at all.

Strategy: simple moving-average crossover.
- Go long when the short-window MA crosses above the long-window MA.
- Exit to cash when it crosses back below.
- No shorting, no leverage, no transaction costs (documented as a
  known simplification — see README "Assumptions").
"""
import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def generate_signals(prices: pd.Series, short_window: int, long_window: int) -> pd.DataFrame:
    """
    Given a series of closing prices, compute the two moving averages
    and a position column: 1 = holding, 0 = in cash.
    """
    if short_window >= long_window:
        raise ValueError("short_window must be less than long_window")

    df = pd.DataFrame({"close": prices})
    df["short_ma"] = df["close"].rolling(window=short_window, min_periods=short_window).mean()
    df["long_ma"] = df["close"].rolling(window=long_window, min_periods=long_window).mean()

    # Position is 1 the day *after* short_ma crosses above long_ma — you can't
    # trade on the same bar's close that generated the signal.
    df["signal"] = (df["short_ma"] > df["long_ma"]).astype(int)
    df["position"] = df["signal"].shift(1).fillna(0)

    return df


def run_backtest(prices: pd.Series, short_window: int, long_window: int) -> dict:
    """
    Run the MA-crossover backtest and return a results dict.

    Raises ValueError if there isn't enough price history to compute
    the long moving average at all — surfaced to the caller (API layer)
    as a 400, not silently returning empty/zero results.
    """
    if len(prices) < long_window + 1:
        raise ValueError(
            f"Not enough price history: need at least {long_window + 1} days, got {len(prices)}"
        )

    df = generate_signals(prices, short_window, long_window)
    df["daily_return"] = df["close"].pct_change().fillna(0)

    # Strategy only earns the day's return while holding a position.
    df["strategy_return"] = df["daily_return"] * df["position"]

    df["strategy_equity"] = (1 + df["strategy_return"]).cumprod()
    df["buy_hold_equity"] = (1 + df["daily_return"]).cumprod()

    total_return_pct = (df["strategy_equity"].iloc[-1] - 1) * 100
    buy_hold_return_pct = (df["buy_hold_equity"].iloc[-1] - 1) * 100

    max_drawdown_pct = _max_drawdown(df["strategy_equity"]) * 100
    sharpe_ratio = _sharpe_ratio(df["strategy_return"])
    num_trades = int(df["position"].diff().abs().sum())  # counts entries + exits
    win_rate_pct = _win_rate(df)

    equity_curve = [
        {
            "date": str(idx.date()) if hasattr(idx, "date") else str(idx),
            "strategy": round(float(row["strategy_equity"]), 4),
            "buy_hold": round(float(row["buy_hold_equity"]), 4),
        }
        for idx, row in df.iterrows()
    ]

    return {
        "total_return_pct": round(float(total_return_pct), 2),
        "buy_hold_return_pct": round(float(buy_hold_return_pct), 2),
        "max_drawdown_pct": round(float(max_drawdown_pct), 2),
        "sharpe_ratio": round(float(sharpe_ratio), 2),
        "num_trades": num_trades,
        "win_rate_pct": round(float(win_rate_pct), 2),
        "equity_curve": equity_curve,
    }


def _max_drawdown(equity: pd.Series) -> float:
    """Largest peak-to-trough decline in the equity curve, as a negative fraction."""
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    return float(drawdown.min()) if len(drawdown) else 0.0


def _sharpe_ratio(daily_returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Annualized Sharpe ratio from daily returns.
    Returns 0 if volatility is zero (e.g. strategy never entered a position)
    rather than dividing by zero.
    """
    excess = daily_returns - (risk_free_rate / TRADING_DAYS_PER_YEAR)
    std = excess.std()
    if std == 0 or np.isnan(std):
        return 0.0
    return (excess.mean() / std) * np.sqrt(TRADING_DAYS_PER_YEAR)


def _win_rate(df: pd.DataFrame) -> float:
    """
    Fraction of *held* days with a positive return.
    A simplification vs. a true per-trade win rate (which would require
    tracking individual trade entry/exit P&L) — documented in the README.
    """
    held_days = df[df["position"] == 1]
    if len(held_days) == 0:
        return 0.0
    winning_days = (held_days["daily_return"] > 0).sum()
    return (winning_days / len(held_days)) * 100
