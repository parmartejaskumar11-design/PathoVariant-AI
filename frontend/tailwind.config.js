/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--color-background)",
        foreground: "var(--color-foreground)",
        card: "var(--color-card)",
        "card-foreground": "var(--color-card-foreground)",
        primary: {
          DEFAULT: "#6366f1",
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
        muted: {
          DEFAULT: "var(--color-muted)",
          foreground: "var(--color-muted-foreground)",
        },
        sidebar: {
          DEFAULT: "var(--color-sidebar)",
        },
        accent: {
          DEFAULT: "var(--color-accent)",
          foreground: "var(--color-accent-foreground)",
        },
        border: "var(--color-border)",
        input: "var(--color-border)",
        ring: "#6366f1",
        destructive: {
          DEFAULT: "#ef4444",
          foreground: "#fef2f2",
        },
      },
      borderRadius: {
        lg: "1rem",
        md: "0.75rem",
        sm: "0.5rem",
      },
      boxShadow: {
        glow: "0 0 30px rgba(99, 102, 241, 0.15)",
        "glow-lg": "0 0 60px rgba(99, 102, 241, 0.2)",
        "inner-glow": "inset 0 1px 0 rgba(255, 255, 255, 0.05)",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-mesh": "linear-gradient(135deg, rgba(99,102,241,0.05) 0%, transparent 50%, rgba(139,92,246,0.05) 100%)",
      },
      animation: {
        "fade-in": "fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards",
        "slide-up": "slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards",
        "slide-right": "slideRight 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards",
        "scale-in": "scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards",
        float: "float 6s ease-in-out infinite",
        glow: "glow 3s ease-in-out infinite alternate",
        shimmer: "shimmer 3s infinite",
        "spin-slow": "spin-slow 3s linear infinite",
        "pulse-dot": "pulse-dot 2s infinite",
      },
    },
  },
  plugins: [],
}
