import React from "react"
import { describe, it, expect, vi, afterEach } from "vitest"
import { render, screen, cleanup } from "@testing-library/react"
import App from "../App"
import {
  GCContentChart,
  RiskDistributionPie,
  NucleotideCompositionChart,
} from "../components/Charts"

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe("PathoVariant App", () => {
  it("renders the sidebar and uploader initially", () => {
    render(<App />)
    expect(screen.getAllByText(/PathoVariant/i).length).toBeGreaterThan(0)
    expect(screen.getByText(/Upload Sequence Data/i)).toBeInTheDocument()
    expect(screen.getAllByText(/Pathogen Analysis/i).length).toBeGreaterThan(0)
  })
})

describe("Chart components", () => {
  it("renders recharts containers for each chart", () => {
    const { container } = render(
      <div>
        <GCContentChart records={[{ id: "s1", gc_content: 50 }]} />
        <RiskDistributionPie high={2} moderate={1} benign={5} />
        <NucleotideCompositionChart
          baseComp={{ A: 20, T: 30, G: 25, C: 25 }}
          baseCounts={{ A: 20, T: 30, G: 25, C: 25 }}
        />
      </div>
    )
    expect(container.querySelectorAll(".recharts-responsive-container").length).toBe(3)
  })

  it("renders empty state for risk pie when no data", () => {
    render(<RiskDistributionPie high={0} moderate={0} benign={0} />)
    expect(screen.getByText(/No classified sequences yet/i)).toBeInTheDocument()
  })
})