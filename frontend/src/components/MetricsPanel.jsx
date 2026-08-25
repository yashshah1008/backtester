function signColor(value) {
  if (value > 0) return "text-terminal-green";
  if (value < 0) return "text-terminal-red";
  return "text-terminal-text";
}

function Metric({ label, value, colorize }) {
  return (
    <div className="panel p-4">
      <div className="label-eyebrow mb-2">{label}</div>
      <div className={`data-mono text-2xl ${colorize ? signColor(value) : "text-terminal-text"}`}>
        {value}
      </div>
    </div>
  );
}

export default function MetricsPanel({ result }) {
  if (!result) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      <Metric label="Strategy return" value={`${result.total_return_pct}%`} colorize />
      <Metric label="Buy & hold return" value={`${result.buy_hold_return_pct}%`} colorize />
      <Metric label="Max drawdown" value={`${result.max_drawdown_pct}%`} colorize />
      <Metric label="Sharpe ratio" value={result.sharpe_ratio} colorize />
      <Metric label="Win rate" value={`${result.win_rate_pct}%`} />
      <Metric label="Trades" value={result.num_trades} />
    </div>
  );
}
