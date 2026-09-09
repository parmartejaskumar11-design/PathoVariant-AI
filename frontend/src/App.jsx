import React, { useState, useEffect } from "react"
import { Download, AlertTriangle, ChevronRight, X } from "lucide-react"
import MetricsCard from "./components/MetricsCard"
import FileUploader from "./components/FileUploader"
import Navbar from "./components/Navbar"
import {
  GCContentChart,
  RiskDistributionPie,
  NucleotideCompositionChart,
  ConfidenceChart,
} from "./components/Charts"

const App = () => {
  const [files, setFiles] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState(null)
  const [analyzeError, setAnalyzeError] = useState("")
  const [darkMode, setDarkMode] = useState(true)

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode)
  }, [darkMode])

  const toggleDarkMode = () => setDarkMode((d) => !d)

  useEffect(() => {
    if (files.length > 0) {
      processFiles(files)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [files])

  const processFiles = async (selectedFiles) => {
    setIsProcessing(true)
    setAnalyzeError("")
    setAnalysisResults(null)
    try {
      if (selectedFiles.length === 1) {
        const formData = new FormData()
        formData.append("file", selectedFiles[0])
        const response = await fetch("/api/analyze", { method: "POST", body: formData })
        const result = await response.json()
        if (!response.ok || result.error) {
          setAnalyzeError(result.error || `Analysis failed (HTTP ${response.status}). Please try again.`)
        } else {
          setAnalysisResults(result)
        }
      } else {
        const formData = new FormData()
        selectedFiles.forEach((f) => formData.append("files", f))
        const response = await fetch("/api/analyze-batch", { method: "POST", body: formData })
        const result = await response.json()
        if (!response.ok || result.error) {
          setAnalyzeError(result.error || `Batch analysis failed (HTTP ${response.status}).`)
        } else {
          setAnalysisResults(result)
        }
      }
    } catch (error) {
      console.error("Analysis error:", error)
      setAnalyzeError("Could not reach the analysis server. Make sure the backend is running on port 8000, then try again.")
    } finally {
      setIsProcessing(false)
    }
  }

  const exportCSV = (data) => {
    const headers = ["ID", "Sequence", "Length", "GC Content (%)", "A (%)", "T (%)", "G (%)", "C (%)", "Predicted Class", "Confidence (%)"]
    const rows = data.map((item) => [
      item.id,
      item.full_sequence?.substring(0, 30) + "..." || "",
      item.length,
      item.gc_content,
      item.base_composition?.A ?? 0,
      item.base_composition?.T ?? 0,
      item.base_composition?.G ?? 0,
      item.base_composition?.C ?? 0,
      item.predicted_class,
      item.confidence_percent,
    ])
    const csvContent = [headers.join(","), ...rows.map((row) => row.join(","))].join("\n")
    const link = document.createElement("a")
    link.setAttribute("href", "data:text/csv;charset=utf-8," + encodeURIComponent(csvContent))
    link.setAttribute("download", "pathovariant-analysis.csv")
    link.click()
  }

  if (!analysisResults) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar darkMode={darkMode} onToggle={toggleDarkMode} />
        <div className="flex min-h-[calc(100vh-60px)]">
          <div className="flex-1 overflow-y-auto p-8">
            {analyzeError && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-300 p-4 rounded-xl mb-4 flex items-start justify-between gap-3 animate-slide-up">
                <span className="text-sm flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  {analyzeError}
                </span>
                <button onClick={() => setAnalyzeError("")} className="text-red-400 hover:text-red-300 shrink-0">
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
            <FileUploader acceptedFiles=".fasta" onSelect={setFiles} disabled={isProcessing} multiple={true} />
          </div>
        </div>
      </div>
    )
  }

  const records = analysisResults.records || []
  const isBatch = !!analysisResults.per_file
  const totalSeq = analysisResults.sequence_metadata?.total_sequences || 0
  const totalBases = analysisResults.sequence_metadata?.total_bases || 0
  const avgGc = analysisResults.sequence_metadata?.average_gc_content || 0
  const baseComp = analysisResults.sequence_metadata?.base_composition || {}
  const baseCounts = analysisResults.sequence_metadata?.base_counts || {}
  const highRisk = analysisResults.ai_classifications?.high_risk_detections || 0
  const moderateRisk = analysisResults.ai_classifications?.moderate_risk_detections || 0
  const benignCount = analysisResults.ai_classifications?.benign_count || 0

  const baseBars = [
    { base: "A", value: baseComp.A || 0, count: baseCounts.A ?? 0, color: "from-blue-500 to-blue-400", badge: "text-blue-400 bg-blue-500/10 border-blue-500/20" },
    { base: "T", value: baseComp.T || 0, count: baseCounts.T ?? 0, color: "from-amber-500 to-amber-400", badge: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
    { base: "G", value: baseComp.G || 0, count: baseCounts.G ?? 0, color: "from-emerald-500 to-emerald-400", badge: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
    { base: "C", value: baseComp.C || 0, count: baseCounts.C ?? 0, color: "from-rose-500 to-rose-400", badge: "text-rose-400 bg-rose-500/10 border-rose-500/20" }
  ]

  return (
    <div className="min-h-screen bg-background">
      <Navbar darkMode={darkMode} onToggle={toggleDarkMode} />
      <div className="flex min-h-[calc(100vh-60px)]">
        <div className="flex-1 overflow-y-auto p-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8 animate-slide-up">
            <div>
              <h1 className="text-3xl font-bold gradient-text mb-1">
                {isBatch ? "Batch Analysis Dashboard" : "Analysis Dashboard"}
              </h1>
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <span>Pathogen Analysis</span>
                <ChevronRight className="w-3 h-3" />
                <span className="text-primary-400">Results</span>
              </p>
            </div>
            <button
              onClick={() => setAnalysisResults(null)}
              className="btn-primary flex items-center gap-2"
            >
              New Analysis
            </button>
          </div>

          {/* Batch summary */}
          {isBatch && (
            <div className="glass-card rounded-2xl p-6 mb-8">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                Batch Summary — {analysisResults.total_files} files, {analysisResults.grand_total_sequences} sequences
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-red-500/20">
                  <span className="text-sm text-muted-foreground">High Risk</span>
                  <span className="text-xl font-bold text-red-400">{analysisResults.grand_summary?.high_risk}</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-amber-500/20">
                  <span className="text-sm text-muted-foreground">Moderate</span>
                  <span className="text-xl font-bold text-amber-400">{analysisResults.grand_summary?.moderate_risk}</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-emerald-500/20">
                  <span className="text-sm text-muted-foreground">Benign</span>
                  <span className="text-xl font-bold text-emerald-400">{analysisResults.grand_summary?.benign}</span>
                </div>
              </div>
              <div className="mt-4 space-y-2">
                {analysisResults.per_file?.map((pf, i) => (
                  <div key={i} className="flex items-center justify-between text-xs bg-white/5 border border-border/30 rounded-lg px-3 py-2">
                    <span className="font-mono text-primary-300">{pf.filename}</span>
                    <span className="text-muted-foreground">
                      {pf.total_sequences} seq · High <span className="text-red-400">{pf.high_risk}</span> · Mod <span className="text-amber-400">{pf.moderate_risk}</span> · Benign <span className="text-emerald-400">{pf.benign}</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5 mb-8">
            <MetricsCard title="Total Sequences" value={totalSeq.toString()} icon="Folder" delay={100} />
            <MetricsCard title="Total Length (bp)" value={totalBases.toString()} icon="Ruler" delay={150} />
            <MetricsCard title="Avg GC Content" value={avgGc.toFixed(2)} icon="Dna" delay={200} />
            <MetricsCard title="High-Risk Detections" value={highRisk.toString()} icon="AlertTriangle" delay={300} />
            <MetricsCard title="Processing Status" value={isProcessing ? "Processing..." : "Complete"} icon="Activity" delay={400} />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="glass-card rounded-2xl p-6 animate-slide-up delay-300">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-5">
                GC Content Distribution
              </h3>
              <GCContentChart records={records} />
            </div>

            <div className="glass-card rounded-2xl p-6 animate-slide-up delay-400">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-5">
                Risk Classification Summary
              </h3>
              <div className="space-y-5">
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-border/30">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse-dot" />
                    <span className="text-sm font-medium">High-Risk Variants</span>
                  </div>
                  <span className="text-xl font-bold text-red-400">{highRisk}</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-border/30">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-amber-400 animate-pulse-dot" />
                    <span className="text-sm font-medium">Moderate Risk</span>
                  </div>
                  <span className="text-xl font-bold text-amber-400">{moderateRisk}</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-border/30">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-emerald-500" />
                    <span className="text-sm font-medium">Benign Sequences</span>
                  </div>
                  <span className="text-xl font-bold text-emerald-400">{benignCount}</span>
                </div>

                <div className="mt-2">
                  <div className="h-2.5 bg-white/5 rounded-full overflow-hidden flex">
                    <div
                      className="h-full bg-gradient-to-r from-red-500 to-red-400 rounded-l-full transition-all duration-1000"
                      style={{ width: totalSeq > 0 ? `${(highRisk / totalSeq) * 100}%` : "0%" }}
                    />
                    <div
                      className="h-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-1000"
                      style={{ width: totalSeq > 0 ? `${(moderateRisk / totalSeq) * 100}%` : "0%" }}
                    />
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-r-full transition-all duration-1000"
                      style={{ width: totalSeq > 0 ? `${(benignCount / totalSeq) * 100}%` : "0%" }}
                    />
                  </div>
                  <div className="flex justify-between mt-2">
                    <span className="text-xs text-red-400/80">{totalSeq > 0 ? ((highRisk / totalSeq) * 100).toFixed(1) : 0}% High</span>
                    <span className="text-xs text-amber-400/80">{totalSeq > 0 ? ((moderateRisk / totalSeq) * 100).toFixed(1) : 0}% Moderate</span>
                    <span className="text-xs text-emerald-400/80">{totalSeq > 0 ? ((benignCount / totalSeq) * 100).toFixed(1) : 0}% Benign</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6 animate-slide-up delay-500">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-5">
                Nucleotide Composition
              </h3>

              <div className="h-4 bg-white/5 rounded-full overflow-hidden flex mb-6">
                {baseBars.map((bar) => (
                  <div
                    key={bar.base}
                    className={`h-full bg-gradient-to-r ${bar.color} transition-all duration-1000`}
                    style={{ width: `${bar.value}%` }}
                  />
                ))}
              </div>

              <div className="space-y-4">
                {baseBars.map((bar, index) => (
                  <div key={bar.base} className="flex items-center gap-3 animate-slide-right" style={{ animationDelay: `${(index + 4) * 50}ms` }}>
                    <span className={`w-9 h-6 rounded-md bg-gradient-to-br ${bar.badge} border flex items-center justify-center text-xs font-bold`}>{bar.base}</span>
                    <div className="flex-1 h-2.5 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full bg-gradient-to-r ${bar.color} transition-all duration-1000 ease-out`}
                        style={{ width: `${bar.value}%`, transitionDelay: `${index * 100}ms` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-foreground w-9 text-right font-semibold">{bar.count}</span>
                    <span className="text-xs font-mono text-muted-foreground w-14 text-right">{bar.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Additional charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-1 glass-card rounded-2xl p-6 animate-slide-up delay-400">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-5">
                Risk Distribution
              </h3>
              <RiskDistributionPie high={highRisk} moderate={moderateRisk} benign={benignCount} />
            </div>

            <div className="lg:col-span-1 glass-card rounded-2xl p-6 animate-slide-up delay-500">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-5">
                Nucleotide Composition Chart
              </h3>
              <NucleotideCompositionChart baseComp={baseComp} baseCounts={baseCounts} />
            </div>

            <div className="lg:col-span-1 glass-card rounded-2xl p-6 animate-slide-up delay-500">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-5">
                Classification Confidence
              </h3>
              <ConfidenceChart records={records} />
            </div>
          </div>

          {/* Results Table */}
          <div className="glass-card rounded-2xl p-6 animate-slide-up delay-500">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                Classification Results
              </h3>
              <button
                onClick={() => exportCSV(records)}
                className="btn-primary flex items-center gap-2 text-xs"
              >
                <Download className="w-3.5 h-3.5" />
                Export CSV
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border/30">
                    <th className="text-left p-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">ID</th>
                    <th className="text-left p-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Sequence</th>
                    <th className="text-left p-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Length</th>
                    <th className="text-left p-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">GC Content</th>
                    <th className="text-left p-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">A / T / G / C</th>
                    <th className="text-left p-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Predicted Class</th>
                    <th className="text-left p-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((record, index) => (
                    <tr
                      key={index}
                      className="border-b border-border/10 hover:bg-white/5 transition-colors duration-200 animate-fade-in"
                      style={{ animationDelay: `${(index + 6) * 50}ms` }}
                    >
                      <td className="p-3 font-mono text-xs text-primary-300">{record.id}</td>
                      <td className="p-3 font-mono text-xs text-muted-foreground">
                        {record.full_sequence?.substring(0, 20) + "..." || ""}
                      </td>
                      <td className="p-3">{record.length}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded-md bg-primary/10 text-primary-300 text-xs font-medium">
                          {record.gc_content}%
                        </span>
                      </td>
                      <td className="p-3">
                        <div className="grid grid-cols-2 gap-1.5 min-w-[150px]">
                          {[
                            { b: "A", c: record.base_counts?.A ?? 0, p: record.base_composition?.A ?? 0, cls: "text-blue-400" },
                            { b: "T", c: record.base_counts?.T ?? 0, p: record.base_composition?.T ?? 0, cls: "text-amber-400" },
                            { b: "G", c: record.base_counts?.G ?? 0, p: record.base_composition?.G ?? 0, cls: "text-emerald-400" },
                            { b: "C", c: record.base_counts?.C ?? 0, p: record.base_composition?.C ?? 0, cls: "text-rose-400" }
                          ].map((x) => (
                            <span key={x.b} className="text-[11px] font-mono text-muted-foreground/80">
                              <span className={`font-bold ${x.cls}`}>{x.b}</span> {x.c} <span className="text-muted-foreground/50">({x.p}%)</span>
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                          record.predicted_class === "High-Risk Variant"
                            ? "bg-red-500/10 text-red-400 border border-red-500/20"
                            : record.predicted_class === "Moderate Risk"
                            ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                            : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        }`}>
                          {record.predicted_class}
                        </span>
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-white/5 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full"
                              style={{ width: `${record.confidence_percent}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium text-muted-foreground">{record.confidence_percent}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App