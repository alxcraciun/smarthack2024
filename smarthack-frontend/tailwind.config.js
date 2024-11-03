/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Roboto', 'sans-serif'],
      },
      gridTemplateColumns: {
        '70/30': '70% 28%',
      },
      colors: {
        'op-white': '#f5f5f9',
        'op-aqua': '#14BDEB',
        'op-blue': '#2b59c3'
      },
    },
  },
  plugins: [],
};