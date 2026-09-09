import React, { useEffect, useState } from "react"
import { Folder, Dna, AlertTriangle, Activity, Ruler } from "lucide-react"

const iconMap = {
  Folder: Folder,
  Dna: Dna,
  AlertTriangle: AlertTriangle,
  Activity: Activity,
  Ruler: Ruler,
}

const colorMap = {
  Folder: "from-blue-500/20 to-blue-600/10 text-blue-400 border-blue-500/20",
  Dna: "from-emerald-500/20 to-emerald-600/10 text-emerald-400 border-emerald-500/20",
  AlertTriangle: "from-red-500/20 to-red-600/10 text-red-400 border-red-500/20",
  Activity: "from-amber-500/20 to-amber-600/10 text-amber-400 border-amber-500/20",
  Ruler: "from-purple-500/20 to-purple-600/10 text-purple-400 border-purple-500/20",
}

const MetricsCard = ({ title, value, icon = "Activity", className = "", delay = 0 }) => {
  const [count, setCount] = useState(0)
  const numericValue = parseFloat(value)
  const isNumeric = !isNaN(numericValue) && value !== "Processing..." && value !== "Ready"

  useEffect(() => {
    if (isNumeric && numericValue > 0) {
      const duration = 1000
      const steps = 30
      const increment = numericValue / steps
      let current = 0
      const timer = setInterval(() => {
        current += increment
        if (current >= numericValue) {
          setCount(numericValue)
          clearInterval(timer)
        } else {
          setCount(Math.floor(current * 100) / 100)
        }
      }, duration / steps)
      return () => clearInterval(timer)
    } else if (isNumeric) {
      setCount(numericValue)
    } else {
      setCount(value)
    }
  }, [value, isNumeric, numericValue])

  const Icon = iconMap[icon] || Activity
  const colorClass = colorMap[icon] || colorMap.Activity

  return (
    <div
      className={`glass-card rounded-2xl p-5 relative overflow-hidden animate-scale-in ${className}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="absolute inset-0 bg-gradient-mesh opacity-50" />

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{title}</span>
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${colorClass} flex items-center justify-center border`}>
            <Icon className="w-4 h-4" />
          </div>
        </div>

        <div className="stat-value gradient-text">
          {isNumeric && typeof count === "number" ? count.toFixed(value.includes(".") ? 2 : 0) : value}
        </div>
      </div>

      <div className="absolute -bottom-4 -right-4 w-24 h-24 rounded-full bg-gradient-to-br from-primary/5 to-transparent" />
    </div>
  )
}

export default MetricsCard
