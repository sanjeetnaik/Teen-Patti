/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        'splash': "url('assets/splash.jpg')",
        'mobile-splash': "url('assets/mobile_splash.jpg')",
        'bg': "url('assets/bg.jpg')",
        'mobile-table': "url('assets/table-mobile.png')"
      },
      backgroundColor : {
        "accent": "#919767",
        "primary": "#212120" 
      }
    }
  },
  plugins: [],
}