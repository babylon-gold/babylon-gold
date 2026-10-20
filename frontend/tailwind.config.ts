import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        gold: {
          50: '#fef9f0',
          100: '#fdf3e1',
          200: '#fbe7c3',
          300: '#f8dba5',
          400: '#f5c967',
          500: '#f2b631',
          600: '#d9a02a',
          700: '#b08a23',
          800: '#88711c',
          900: '#615815',
        },
      },
      direction: {
        rtl: 'rtl',
        ltr: 'ltr',
      },
    },
  },
  plugins: [],
}
export default config
