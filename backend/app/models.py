"""
ORM models.

Three tables, matching the design doc:
- Strategy: a saved strategy definition (ticker + rule + parameters)
- BacktestRun: one execution of a strategy over a date range
- BacktestResult: the computed output of a run (1:1 with BacktestRun)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ticker = Column(String, nullable=False, index=True)
    rule_type = Column(String, nullable=False, default="ma_crossover")
    short_window = Column(Integer, nullable=False, default=50)
    long_window = Column(Integer, nullable=False, default=200)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    runs = relationship("BacktestRun", back_populates="strategy", cascade="all, delete-orphan")


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    start_date = Column(String, nullable=False)  # ISO date, e.g. "2019-01-01"
    end_date = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    strategy = relationship("Strategy", back_populates="runs")
    result = relationship("BacktestResult", back_populates="run", uselist=False, cascade="all, delete-orphan")


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("backtest_runs.id"), nullable=False)

    total_return_pct = Column(Float, nullable=False)
    buy_hold_return_pct = Column(Float, nullable=False)
    max_drawdown_pct = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    num_trades = Column(Integer, nullable=False)
    win_rate_pct = Column(Float, nullable=False)

    # Equity curve stored as JSON: [{"date": "2020-01-01", "strategy": 1.0, "buy_hold": 1.0}, ...]
    equity_curve = Column(JSON, nullable=False)

    run = relationship("BacktestRun", back_populates="result")
