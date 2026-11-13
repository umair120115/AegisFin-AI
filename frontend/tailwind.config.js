/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        fintech: {
          dark: '#080C14',
          card: '#0F172A',
          border: '#1E293B',
          accent: '#3B82F6',
          safe: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444',
          muted: '#64748B'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
