/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
          'lmao-yellow': '#fad67e',
      },
      screens: {
          '5s': '330px',
      },
    },
  },
  plugins: [],
}

