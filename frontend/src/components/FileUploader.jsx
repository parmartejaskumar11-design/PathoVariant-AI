import React, { useState, useRef } from "react"
import { Upload, X, FileText, CheckCircle, ClipboardPaste } from "lucide-react"

const FileUploader = ({
  acceptedFiles = ".fasta,.fastq",
  onSelect,
  disabled = false,
  multiple = false,
}) => {
  const [uploading, setUploading] = useState(false)
  const [file, setFile] = useState(null)
  const [files, setFiles] = useState([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [mode, setMode] = useState("upload")
  const [pastedText, setPastedText] = useState("")
  const [pasteError, setPasteError] = useState("")
  const fileInputRef = useRef(null)

  const allowedExts = [
    ...acceptedFiles.split(","),
    ".fa",
    ".fna",
    ".fas",
    ".fq",
    ".txt",
  ]
    .map((f) => f.trim().toLowerCase().replace(/\./g, ""))
    .filter(Boolean)

  const processFile = (selectedFiles) => {
    if (!selectedFiles || selectedFiles.length === 0) return
    if (multiple) {
      const accepted = []
      const rejected = []
      for (const f of selectedFiles) {
        const ext = (f.name.split(".").pop() || "").toLowerCase()
        if (allowedExts.includes(ext)) {
          accepted.push(f)
        } else {
          rejected.push(f.name)
        }
      }
      if (rejected.length > 0) {
        setPasteError(`Unsupported file type: ${rejected.join(", ")}. Only FASTA (.fasta, .fa, .fna) or FASTQ (.fastq) files are supported.`)
      }
      if (accepted.length > 0) {
        setFiles(accepted)
        setFile(accepted[0])
        setPasteError("")
        setPastedText("")
        if (onSelect) onSelect(accepted)
      }
    } else {
      const selectedFile = selectedFiles[0]
      const fileExt = (selectedFile.name.split(".").pop() || "").toLowerCase()
      if (allowedExts.includes(fileExt)) {
        setFile(selectedFile)
        setFiles([])
        setPastedText("")
        setPasteError("")
        if (onSelect) onSelect([selectedFile])
        return true
      } else {
        setPasteError(`Unsupported file type ".${fileExt}". Please upload a FASTA (.fasta, .fa, .fna) or FASTQ (.fastq) file.`)
        setFile(null)
        return false
      }
    }
  }

  const processPastedText = () => {
    const text = pastedText.trim()
    if (!text) {
      setPasteError("Please paste a sequence first.")
      return
    }

    let fastaContent = text
    const hasHeader = text.startsWith(">")
    if (!hasHeader) {
      const cleanSeq = text.replace(/\s+/g, "").toUpperCase()
      if (!cleanSeq) {
        setPasteError("Sequence appears to be empty.")
        return
      }
      fastaContent = `>pasted_sequence\n${cleanSeq}`
    }

    try {
      const pastedFile = new File([fastaContent], "pasted_sequence.fasta", { type: "text/plain" })
      setFile(pastedFile)
      setPasteError("")
      if (onSelect) onSelect([pastedFile])
    } catch (err) {
      setPasteError("Could not process pasted sequence: " + err.message)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setUploading(false)
    setIsDragOver(false)
    const dropped = []
    const items = e.dataTransfer.items
    for (let i = 0; i < items.length; i++) {
      if (items[i].kind === "file") {
        dropped.push(items[i].getAsFile())
      }
    }
    processFile(dropped)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setUploading(true)
    setIsDragOver(true)
  }

  const handleDragLeave = () => {
    setUploading(false)
    setIsDragOver(false)
  }

  const handleClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  const handleFileChange = (e) => {
    const selected = Array.from(e.target.files || [])
    if (selected.length > 0) {
      processFile(selected)
    }
    e.target.value = ""
  }

  const removeFile = (e) => {
    e.stopPropagation()
    setFile(null)
    setFiles([])
    setPastedText("")
    setPasteError("")
    setUploading(false)
    if (onSelect) onSelect([])
  }

  return (
    <div className="animate-scale-in delay-200">
      <div className="mb-6 animate-slide-up">
        <h2 className="text-2xl font-bold gradient-text mb-2">Upload Sequence Data</h2>
        <p className="text-muted-foreground text-sm">
          Upload a FASTA file or paste a sequence for AI-powered pathogen analysis and variant classification
        </p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".fasta,.fastq,.fa,.fna,.fq,.fastq.gz,.fasta.gz,.txt"
        onChange={handleFileChange}
        multiple={multiple}
        className="hidden"
        style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", opacity: 0 }}
      />

      {/* Mode Tabs */}
      <div className="flex gap-2 mb-4 animate-slide-up delay-100">
        <button
          type="button"
          onClick={() => setMode("upload")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
            mode === "upload"
              ? "bg-primary/15 text-primary-300 border border-primary/30"
              : "bg-white/5 text-muted-foreground border border-border/30 hover:bg-white/10"
          }`}
        >
          <Upload className="w-4 h-4" />
          Upload File
        </button>
        <button
          type="button"
          onClick={() => setMode("paste")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
            mode === "paste"
              ? "bg-primary/15 text-primary-300 border border-primary/30"
              : "bg-white/5 text-muted-foreground border border-border/30 hover:bg-white/10"
          }`}
        >
          <ClipboardPaste className="w-4 h-4" />
          Paste Sequence
        </button>
      </div>

      {mode === "upload" ? (
        <>
          {pasteError && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-300 p-3 rounded-xl mb-3 flex items-center justify-between gap-3 animate-slide-up">
              <span className="text-sm flex items-center gap-2">
                <X className="w-4 h-4 shrink-0" />
                {pasteError}
              </span>
              <button onClick={() => setPasteError("")} className="text-red-400 hover:text-red-300 shrink-0">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
          <div
          className={`relative rounded-2xl border-2 border-dashed transition-all duration-500 cursor-pointer overflow-hidden ${
            isDragOver
              ? "border-primary-400 bg-primary/10 scale-[1.02] shadow-glow-lg"
              : file
              ? "border-green-500/30 bg-green-500/5"
              : "border-border hover:border-primary/50 hover:bg-primary/5"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
          style={{ minHeight: "220px" }}
        >
          <div className="absolute inset-0 bg-gradient-mesh opacity-30" />

          {isDragOver && (
            <div className="absolute inset-0 bg-primary/5 animate-pulse" />
          )}

          <div className="relative z-10 flex flex-col items-center justify-center h-full p-12">
            {file || files.length > 0 ? (
              <div className="text-center animate-scale-in">
                <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-400" />
                </div>
                {files.length > 1 ? (
                  <>
                    <h3 className="text-lg font-semibold text-foreground mb-1">
                      {files.length} files ready for batch analysis
                    </h3>
                    <div className="text-left mx-auto max-w-[320px] mb-4 space-y-1">
                      {files.slice(0, 5).map((f) => (
                        <div key={f.name + f.size} className="text-xs text-muted-foreground flex items-center justify-between px-3 py-1.5 rounded-lg bg-white/5 border border-border/30">
                          <span className="font-mono truncate">{f.name}</span>
                          <span>{(f.size / 1024).toFixed(1)} KB</span>
                        </div>
                      ))}
                      {files.length > 5 && (
                        <p className="text-xs text-muted-foreground/60">+{files.length - 5} more…</p>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    <h3 className="text-lg font-semibold text-foreground mb-1">{file.name}</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </>
                )}
                <button
                  onClick={removeFile}
                  className="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-500/10 border border-red-500/20 flex items-center gap-2 mx-auto"
                >
                  <X className="w-4 h-4" />
                  Remove file{files.length > 1 ? "s" : ""}
                </button>
              </div>
            ) : (
              <div className="text-center animate-fade-in">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary/10 to-purple-500/10 border border-primary/20 flex items-center justify-center mx-auto mb-6 animate-float">
                  <Upload className="w-9 h-9 text-primary-400" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  Drag & drop your FASTA file
                </h3>
                <p className="text-sm text-muted-foreground mb-1">
                  or click to browse files
                </p>
                <p className="text-xs text-muted-foreground/60">
                  Supports .fasta, .fastq formats
                </p>
              </div>
            )}
          </div>
        </div>
        </>
      ) : (
        <div
          className={`relative rounded-2xl border-2 transition-all duration-500 overflow-hidden ${
            file
              ? "border-green-500/30 bg-green-500/5"
              : "border-border"
          }`}
        >
          <div className="absolute inset-0 bg-gradient-mesh opacity-20" />
          <div className="relative z-10 p-6">
            {file ? (
              <div className="text-center animate-scale-in">
                <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-400" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-1">{file.name}</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
                <button
                  onClick={removeFile}
                  className="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-500/10 border border-red-500/20 flex items-center gap-2 mx-auto"
                >
                  <X className="w-4 h-4" />
                  Remove and paste again
                </button>
              </div>
            ) : (
              <>
                <p className="text-sm text-muted-foreground mb-3">
                  Paste your DNA/RNA sequence below (FASTA format or raw sequence):
                </p>
                <textarea
                  value={pastedText}
                  onChange={(e) => {
                    setPastedText(e.target.value)
                    setPasteError("")
                  }}
                  placeholder={">my_sequence\nATCGATCGATCGATCGATCGATCG\nGCTAGCTAGCTAGCTAGCTAGC"}
                  className="w-full min-h-[160px] bg-background/80 border border-border rounded-xl p-4 font-mono text-sm text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:border-primary/50 transition-colors resize-y"
                  spellCheck={false}
                />
                {pasteError && (
                  <p className="mt-2 text-xs text-red-400 flex items-center gap-1">
                    <X className="w-3 h-3" />
                    {pasteError}
                  </p>
                )}
                <div className="flex items-center gap-3 mt-4">
                  <button
                    type="button"
                    onClick={processPastedText}
                    disabled={disabled}
                    className="btn-primary flex items-center gap-2"
                  >
                    <ClipboardPaste className="w-4 h-4" />
                    Analyze Sequence
                  </button>
                  <p className="text-xs text-muted-foreground/60">
                    Accepts raw sequence or FASTA with multiple records
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <div className="mt-6 flex items-center gap-6 text-xs text-muted-foreground/60 animate-slide-up delay-300">
        <div className="flex items-center gap-2">
          <FileText className="w-3.5 h-3.5" />
          <span>Biopython parser</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3.5 h-3.5 rounded-full bg-gradient-to-br from-primary/30 to-purple-500/30" />
          <span>AI classification engine</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3.5 h-3.5 rounded-full bg-gradient-to-br from-emerald-500/30 to-emerald-600/30" />
          <span>Real-time analysis</span>
        </div>
      </div>
    </div>
  )
}

export default FileUploader