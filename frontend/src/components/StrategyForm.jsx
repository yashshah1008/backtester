import { useState } from "react";

const FIELD_BASE =
  "w-full bg-terminal-bg border border-terminal-border rounded px-3 py-2 font-mono text-sm text-terminal-text placeholder-terminal-muted focus:border-terminal-amber transition-colors";

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="label-eyebrow block mb-1.5">{label}</span>
      {children}
    </label>
  );
}

export default function StrategyForm({ onSubmit, isLoading }) {
  const [form, setForm] = useState({
    ticker: "AAPL",
    shortWindow: 50,
    longWindow: 200,
    startDate: "2019-01-01",
    endDate: "2024-01-01",
  });

  const update = (key) => (e) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="panel p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="label-eyebrow">Strategy Parameters</h2>
        <span className="label-eyebrow text-terminal-amberDim">MA Crossover</span>
      </div>

      <Field label="Ticker">
        <input
          className={FIELD_BASE}
          value={form.ticker}
          onChange={update("ticker")}
          placeholder="AAPL"
          required
        />
      </Field>

      <div className="grid grid-cols-2 gap-3">
        <Field label="Short window (days)">
          <input
            type="number"
            className={FIELD_BASE}
            value={form.shortWindow}
            onChange={update("shortWindow")}
            min="1"
            required
          />
        </Field>
        <Field label="Long window (days)">
          <input
            type="number"
            className={FIELD_BASE}
            value={form.longWindow}
            onChange={update("longWindow")}
            min="2"
            required
          />
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Field label="Start date">
          <input
            type="date"
            className={FIELD_BASE}
            value={form.startDate}
            onChange={update("startDate")}
            required
          />
        </Field>
        <Field label="End date">
          <input
            type="date"
            className={FIELD_BASE}
            value={form.endDate}
            onChange={update("endDate")}
            required
          />
        </Field>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-terminal-amber text-terminal-bg font-mono text-sm font-semibold uppercase tracking-wide py-2.5 rounded hover:bg-terminal-amber/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? "Running backtest…" : "Run backtest"}
      </button>
    </form>
  );
}
