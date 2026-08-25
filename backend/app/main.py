from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import strategies

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Backtester API",
    description="Rule-based strategy backtesting engine (MA crossover) with risk-adjusted metrics.",
    version="0.1.0",
)

# Skeleton stage: wide open. Tighten to the deployed frontend's origin before shipping.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(strategies.router, prefix="/api", tags=["strategies"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
