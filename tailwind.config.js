/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './dashboard/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          hover: '#2563eb',
        },
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        'bg-primary': '#0f172a',
        'bg-secondary': '#1e293b',
        'bg-card': '#334155',
        'text-primary': '#f1f5f9',
        'text-secondary': '#cbd5e1',
        'border': '#475569',
      },
    },
  },
  plugins: [],
}
