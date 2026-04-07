module.exports = {
  content: [
    "./disagro_p/templates/**/*.html",
    "./disagro_p/static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#effef9",
          100: "#d7faed",
          200: "#b2f1db",
          300: "#7de2c3",
          400: "#42c7a2",
          500: "#22ac88",
          600: "#168a6d",
          700: "#146e59",
          800: "#145749",
          900: "#12483d",
        },
      },
      boxShadow: {
        panel: "0 18px 40px rgba(15, 23, 42, 0.12)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
};
