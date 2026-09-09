import React from "react"
import { Dna, Sun, Moon } from "lucide-react"

const Navbar = ({ darkMode, onToggle }) => {
  const toggle = () => {
    const root = document.documentElement
    root.classList.toggle("dark", !darkMode)
    onToggle(!darkMode)
  }

  return (
    <header className="glass-panel sticky top-0 z-50 animate-slide-up">
      <div className="flex items-center justify-between px-6 py-3.5">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center shadow-glow">
              <Dna className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold gradient-text">PathoVariant-AI</h1>
              <p className="text-xs text-muted-foreground -mt-0.5">Autonomous Pathogen Mutation Analyzer</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-border/30">
            <div className="status-dot" />
            <span className="text-xs text-muted-foreground">API Connected</span>
          </div>

          <button
            onClick={toggle}
            className="btn-ghost p-2.5 rounded-xl"
            title={darkMode ? "Light Mode" : "Dark Mode"}
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 flex items-center justify-center border border-primary/20">
            <span className="text-xs font-bold text-primary-400">PV</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Navbar
