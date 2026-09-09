import React from "react"
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  PieChart,
  Pie,
  Legend,
  CartesianGrid,
} from "recharts"

const GC_COLORS = ["#818cf8", "#c084fc", "#f472b6", "#34d399", "#fbbf24", "#60a5fa", "#a78bfa", "#f87171"]

export const GCContentChart = ({ records }) => {
  const data = (records || []).slice(0, 15).map((r) => ({
    id: r.id || "seq",
    gc: parseFloat(r.gc_content || 0).toFixed(1),
  }))

  return (
    <div className="w-full" style={{ minHeight: 220 }}>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="id" tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }} interval={0} angle={-35} textAnchor="end" height={55} />
          <YAxis tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: "var(--color-card)", border: "1px solid var(--color-border)", borderRadius: "0.75rem", fontSize: 12 }}
            labelStyle={{ color: "var(--color-foreground)" }}
          />
          <Bar dataKey="gc" radius={[4, 4, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={GC_COLORS[i % GC_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export const RiskDistributionPie = ({ high, moderate, benign }) => {
  const data = [
    { name: "High Risk", value: high || 0, color: "#ef4444" },
    { name: "Moderate", value: moderate || 0, color: "#f59e0b" },
    { name: "Benign", value: benign || 0, color: "#10b981" },
  ].filter((d) => d.value > 0)

  if (data.length === 0) {
    return <p className="text-sm text-muted-foreground text-center py-10">No classified sequences yet</p>
  }

  return (
    <div className="w-full" style={{ minHeight: 220 }}>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={75} label={(e) => e.name}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ background: "var(--color-card)", border: "1px solid var(--color-border)", borderRadius: "0.75rem", fontSize: 12 }}
            labelStyle={{ color: "var(--color-foreground)" }}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: "var(--color-muted-foreground)" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

export const NucleotideCompositionChart = ({ baseComp = {}, baseCounts = {} }) => {
  const data = ["A", "T", "G", "C"].map((b) => ({
    base: b,
    percent: parseFloat(baseComp[b] || 0).toFixed(1),
    count: baseCounts[b] ?? 0,
  }))

  return (
    <div className="w-full" style={{ minHeight: 220 }}>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis type="number" tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }} />
          <YAxis type="category" dataKey="base" tick={{ fill: "var(--color-muted-foreground)", fontSize: 12 }} width={30} />
          <Tooltip
            formatter={(value, _n, item) => [`${value}%`, `${item.payload.count} bases`]}
            contentStyle={{ background: "var(--color-card)", border: "1px solid var(--color-border)", borderRadius: "0.75rem", fontSize: 12 }}
            labelStyle={{ color: "var(--color-foreground)" }}
          />
          <Bar dataKey="percent" radius={[0, 4, 4, 0]}>
            {["#60a5fa", "#fbbf24", "#34d399", "#f87171"].map((c, i) => (
              <Cell key={i} fill={c} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export const ConfidenceChart = ({ records }) => {
  const data = (records || []).slice(0, 15).map((r) => ({
    id: r.id || "seq",
    confidence: parseFloat(r.confidence_percent || 0).toFixed(1),
  }))

  return (
    <div className="w-full" style={{ minHeight: 220 }}>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="id" tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }} interval={0} angle={-35} textAnchor="end" height={55} />
          <YAxis domain={[0, 100]} tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: "var(--color-card)", border: "1px solid var(--color-border)", borderRadius: "0.75rem", fontSize: 12 }}
            labelStyle={{ color: "var(--color-foreground)" }}
          />
          <Bar dataKey="confidence" fill="#818cf8" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}