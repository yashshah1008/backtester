/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Trading-terminal palette: near-black base, phosphor-amber signal,
        // cool slate for structure, muted signal-green/red for P&L.
        terminal: {
          bg: "#0B0D10",
          panel: "#12151A",
          border: "#22262E",
          text: "#D8DEE6",
          muted: "#6B7280",
          amber: "#E8A33D",
          amberDim: "#8A6423",
          green: "#4FAE7F",
          red: "#C4544D",
        },
      },
      fontFamily: {
        mono: ["'IBM Plex Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
        sans: ["'Inter'", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
