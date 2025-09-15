// DEF: Tailwind-Konfiguration (ESM). Scannt index.html und src/*
export default /** @type {import('tailwindcss').Config} */ ({
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx}"
  ],
  theme: {
    extend: {}
  },
  plugins: []
})
