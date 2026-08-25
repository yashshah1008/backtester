# Design Doc — Strategy Backtester

## Problem
Given a stock ticker and a simple trading rule, simulate how that rule would
have performed historically, and compare it against simply buying and
holding the same stock over the same period.

## Scope (v1)
- One strategy type: moving-average crossover (short MA crosses above/below
  long MA). Chosen because it's simple to reason about, easy to validate by
  hand, and a legitimate, widely-used building block in real quant strategies.
- No shorting, no leverage, no transaction costs/slippage. These are known
  simplifications, not oversights — documented here and in `backtest.py`,
  and each one is a natural "v2" extension.
- Single-ticker backtests only (no portfolio-level, multi-asset backtests in v1).

## Data model
- **Strategy**: a saved configuration (ticker, short/long window).
- **BacktestRun**: one execution of a strategy over a date range.
- **BacktestResult**: the computed output of a run (1:1 with a run).

Separating `Strategy` from `BacktestRun` lets the same strategy be re-run
over different date ranges without redefining it — matches how a user
would actually want to explore "how would this have done in 2020 vs 2022?"

## API
- `POST /api/strategies` — define a strategy
- `GET /api/strategies` — list saved strategies
- `POST /api/backtests` — run a backtest for a strategy over a date range
- `GET /api/backtests/{run_id}` — fetch a past result

## Backtest engine design
The engine (`app/backtest.py`) is written as pure functions operating on a
pandas Series of closing prices — no database or HTTP dependency. This was
a deliberate choice, not an afterthought: it means the hardest, most
bug-prone logic (signal generation, return calculation, risk metrics) can
be built and unit-tested in complete isolation before any API or database
code exists, and it keeps the test suite fast (no DB fixtures needed for
the core logic).

**Signal timing**: a position is entered the day *after* a crossover signal
appears, since in reality you can't trade on the same closing price that
generated the signal. This is a common backtesting bug (look-ahead bias)
and worth calling out explicitly — it demonstrates awareness of a real
pitfall in this domain rather than just calling `pandas.rolling()`.

## Metrics reported
- **Total return** — strategy's cumulative return over the period
- **Buy & hold return** — baseline for comparison
- **Max drawdown** — largest peak-to-trough decline (risk, not just return)
- **Sharpe ratio** — return per unit of volatility, annualized
- **Win rate** — % of held days with a positive return (a simplification —
  a true per-trade win rate would need individual trade P&L tracking,
  which is a reasonable v2 addition)
- **Number of trades** — entries + exits, so the user can sanity-check that
  the strategy isn't trading suspiciously often

## Known limitations (v1)
- No transaction costs or slippage — real returns would be lower.
- No shorting — the strategy can only be long or in cash.
- Win rate is per-day-held, not per-trade.
- Single ticker only.

## Tech stack rationale
- **FastAPI**: async-capable, automatic OpenAPI docs, minimal boilerplate.
- **SQLAlchemy + SQLite (dev) / Postgres (prod)**: same ORM code either way;
  SQLite keeps local setup to zero config, Postgres is what a real
  deployment should use.
- **yfinance**: free, no API key required, reliable enough for a portfolio
  project (Alpha Vantage's free tier rate-limits too aggressively for
  interactive use).
- **React + Tailwind + Recharts**: fast to build a clean, data-dense UI
  without hand-rolling chart rendering.
