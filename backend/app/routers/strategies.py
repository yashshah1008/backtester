from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.backtest import run_backtest
from app.market_data import fetch_close_prices, NoDataError

router = APIRouter()


@router.post("/strategies", response_model=schemas.StrategyOut)
def create_strategy(payload: schemas.StrategyCreate, db: Session = Depends(get_db)):
    if payload.short_window >= payload.long_window:
        raise HTTPException(status_code=400, detail="short_window must be less than long_window")

    strategy = models.Strategy(
        name=payload.name,
        ticker=payload.ticker.upper(),
        short_window=payload.short_window,
        long_window=payload.long_window,
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


@router.get("/strategies", response_model=list[schemas.StrategyOut])
def list_strategies(db: Session = Depends(get_db)):
    return db.query(models.Strategy).order_by(models.Strategy.created_at.desc()).all()


@router.post("/backtests", response_model=schemas.BacktestResultOut)
def create_backtest(payload: schemas.BacktestRequest, db: Session = Depends(get_db)):
    strategy = db.query(models.Strategy).filter(models.Strategy.id == payload.strategy_id).first()
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")

    try:
        prices = fetch_close_prices(strategy.ticker, payload.start_date, payload.end_date)
        result_data = run_backtest(prices, strategy.short_window, strategy.long_window)
    except NoDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    run = models.BacktestRun(
        strategy_id=strategy.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    result = models.BacktestResult(run_id=run.id, **result_data)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/backtests/{run_id}", response_model=schemas.BacktestResultOut)
def get_backtest_result(run_id: int, db: Session = Depends(get_db)):
    result = db.query(models.BacktestResult).filter(models.BacktestResult.run_id == run_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Backtest result not found")
    return result
