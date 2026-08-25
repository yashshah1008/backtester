"""
Pydantic schemas — the request/response contract for the API.
Kept separate from ORM models on purpose: the API shape and the DB
shape are allowed to diverge (e.g. we never want to accept an `id`
on create), and conflating them is a common source of bugs.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class StrategyCreate(BaseModel):
    name: str
    ticker: str = Field(..., examples=["AAPL"])
    short_window: int = Field(50, gt=0)
    long_window: int = Field(200, gt=0)


class StrategyOut(BaseModel):
    id: int
    name: str
    ticker: str
    rule_type: str
    short_window: int
    long_window: int
    created_at: datetime

    class Config:
        from_attributes = True


class BacktestRequest(BaseModel):
    strategy_id: int
    start_date: str = Field(..., examples=["2019-01-01"])
    end_date: str = Field(..., examples=["2024-01-01"])


class EquityPoint(BaseModel):
    date: str
    strategy: float
    buy_hold: float


class BacktestResultOut(BaseModel):
    id: int
    run_id: int
    total_return_pct: float
    buy_hold_return_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    num_trades: int
    win_rate_pct: float
    equity_curve: list[EquityPoint]

    class Config:
        from_attributes = True
