import { useState } from "react";
import StrategyForm from "./components/StrategyForm.jsx";
import MetricsPanel from "./components/MetricsPanel.jsx";
import EquityChart from "./components/EquityChart.jsx";
import { api } from "./api.js";

export default function App() {
  const [result, setResult] = useState(null);
  const [lastRun, setLastRun] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (form) => {
    setIsLoading(true);
    setError(null);
    try {
      const strategy = await api.createStrategy({
        name: `${form.ticker} MA ${form.shortWindow}/${form.longWindow}`,
        ticker: form.ticker,
        short_window: Number(form.shortWindow),
        long_window: Number(form.longWindow),
      });

      const backtestResult = await api.runBacktest({
        strategy_id: strategy.id,
        start_date: form.startDate,
        end_date: form.endDate,
      });

      setResult(backtestResult);
      setLastRun({ ticker: form.ticker.toUpperCase(), ...form });
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-terminal-border px-6 py-4 flex items-center justify-between">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-terminal-amber text-lg font-semibold">$</span>
          <h1 className="font-mono text-lg font-semibold tracking-tight">backtester</h1>
          <span className="label-eyebrow hidden sm:inline">moving-average crossover engine</span>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs text-terminal-muted">
          <span className="w-1.5 h-1.5 rounded-full bg-terminal-green inline-block" />
          api connected
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-6">
        <StrategyForm onSubmit={handleSubmit} isLoading={isLoading} />

        <section className="space-y-6">
          {error && (
            <div className="panel border-terminal-red/50 p-4">
              <div className="label-eyebrow text-terminal-red mb-1">Backtest failed</div>
              <p className="text-sm text-terminal-text/90">{error}</p>
            </div>
          )}

          {!result && !error && !isLoading && (
            <div className="panel p-10 text-center">
              <p className="font-mono text-sm text-terminal-muted">
                Configure a strategy and run a backtest to see results here.
              </p>
            </div>
          )}

          {isLoading && (
            <div className="panel p-10 text-center">
              <p className="font-mono text-sm text-terminal-amber animate-pulse">
                Fetching price history and running simulation…
              </p>
            </div>
          )}

          {result && lastRun && (
            <>
              <div className="label-eyebrow">
                {lastRun.ticker} · {lastRun.startDate} → {lastRun.endDate}
              </div>
              <MetricsPanel result={result} />
              <EquityChart equityCurve={result.equity_curve} />
            </>
          )}
        </section>
      </main>
    </div>
  );
}
