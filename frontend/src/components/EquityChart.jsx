import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="panel px-3 py-2 text-xs font-mono">
      <div className="text-terminal-muted mb-1">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {p.value.toFixed(3)}
        </div>
      ))}
    </div>
  );
}

export default function EquityChart({ equityCurve }) {
  if (!equityCurve?.length) return null;

  // Thin the x-axis labels so they don't collide on long date ranges.
  const tickInterval = Math.max(Math.floor(equityCurve.length / 8), 1);

  return (
    <div className="panel p-5">
      <h2 className="label-eyebrow mb-4">Equity Curve — Strategy vs. Buy &amp; Hold</h2>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={equityCurve} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#22262E" strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            interval={tickInterval}
            tick={{ fill: "#6B7280", fontSize: 11, fontFamily: "IBM Plex Mono" }}
            stroke="#22262E"
          />
          <YAxis
            tick={{ fill: "#6B7280", fontSize: 11, fontFamily: "IBM Plex Mono" }}
            stroke="#22262E"
            domain={["auto", "auto"]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, fontFamily: "IBM Plex Mono", color: "#D8DEE6" }} />
          <Line
            type="monotone"
            dataKey="strategy"
            name="Strategy"
            stroke="#E8A33D"
            dot={false}
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="buy_hold"
            name="Buy & Hold"
            stroke="#6B7280"
            dot={false}
            strokeWidth={1.5}
            strokeDasharray="4 3"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
