export default {  // Allows to use Tailwind classes without additional @theme configuration
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "si-page-bg": "var(--color-si-page-bg)",
        "si-card-bg": "var(--color-si-card-bg)",
        "si-card-border": "var(--color-si-card-border)",
        "si-input-bg": "var(--color-si-input-bg)",
        "si-input-border": "var(--color-si-input-border)",
        "si-input-icon": "var(--color-si-input-icon)",
        "si-input-text": "var(--color-si-input-text)",
        "si-label": "var(--color-si-label)",
        "si-link": "var(--color-si-link)",
        "si-btn": "var(--color-si-btn)",
        "si-btn-hover": "var(--color-si-btn-hover)",
        "si-shield": "var(--color-si-shield)",
        "si-header": "var(--color-si-header)",
        "si-footer": "var(--color-si-footer)",
        "si-footer-shield": "var(--color-si-footer-shield)",
        "si-scrollbar-fill": "var(--color-si-scrollbar-fill)",
        "si-scrollbar-background": "var(--color-si-scrollbar-background)"
      }
    }
  }
};
