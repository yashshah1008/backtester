const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  createStrategy: (payload) =>
    request("/strategies", { method: "POST", body: JSON.stringify(payload) }),
  runBacktest: (payload) =>
    request("/backtests", { method: "POST", body: JSON.stringify(payload) }),
};
