/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f0f4f9',
          100: '#dbe4f0',
          200: '#b8cde2',
          300: '#8baed1',
          400: '#5c8bbe',
          500: '#3c6ea8',
          600: '#2b5589',
          700: '#21436e',
          800: '#1c385b',
          900: '#0f243d',
          950: '#091526',
        },
        clinical: {
          bg: '#f8fafc',
          card: '#ffffff',
          border: '#e2e8f0',
          text: '#0f172a',
          muted: '#64748b',
          critical: '#ef4444',
          warning: '#f59e0b',
          info: '#3b82f6',
          success: '#10b981'
        }
      },
    },
  },
  plugins: [],
}
