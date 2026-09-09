import streamlit as st
import os
import sys
import math
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from src.parser import parse_fasta_file, parse_sequence
from src.ai_engine import PathogenAIEngine, _load_model

# Page Configuration
st.set_page_config(
    page_title="PathoVariant-AI | Pathogen Mutation & Risk Analyzer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .badge-high {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
    }
    .badge-moderate {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid #F59E0B;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
    }
    .badge-benign {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid #10B981;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Sample Sequences
SAMPLE_SEQUENCES = {
    "SARS-CoV-2 Spike (High-Risk Mutation Signal)": """>sars_cov_2_spike_mutant High pathogenic mutation signal
ATGTTTGTTTTTCTTGTTTTATTGCCACTAGTCTCTAGTCAGTGTGTTAATCTTACAACCAGAACTCAATTACCCCCTGCATACACTAATTCTTTCACACGTGGTGTTTATTACCCTGACAAAGTTTTCAGATCCTCAGTTTTACATTCAACTCAGGACTTGTTCTTACCTTTCTTTTCCAATGTTACTTGGTTCCATGCTATACATGTCTCTGGGACCAATGGTACTAAGAGG""",
    "Influenza A H5N1 (Moderate Risk Variant)": """>influenza_h5n1_ha Moderate risk surveillance sequence
ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGTTACCATGCAAACAACTCGACAGAGCAGGTTGACACAATAATGGAAAAGAACGTTACTGTTACACATGCCCAAGACATACTGGAAAAGACACACAACGGGAAGCTCTGCGATCTAGATGGAGTGAAGCCTCTAATTTTGAGAGATTGTAGTGTAGCTGGATGGCTCCTCGGG""",
    "Bacteriophage Lambda (Benign Reference Control)": """>bacteriophage_lambda_benign Benign baseline genomic sequence
ATGGCTGATATTAAATCTACACTGACCCCGATTCTGGCTGCCGCTGAAGAACTGGAAAAACGCCGCGCACAGGCTGATAAAGCGGCAGAAGCGGCTGAAGCAGCGCGTCGTGAAAAAGAAGCGGCTGAGCGCGCGCGTGCAGAGGCGGAACGTGAGCGCGCAGAAGCAGAGCGTGAGCGCGCGGAAGCCGAACGCGAACGCGCAGAAGCCGAACGCGAACGTGAACGTGCTGAACGT""",
}

# Load Engine
@st.cache_resource
def get_ai_engine():
    engine = _load_model()
    if engine is None:
        engine = PathogenAIEngine()
        engine.train_baseline()
    return engine

engine = get_ai_engine()

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=600&auto=format&fit=crop&q=80", use_container_width=True)
    st.markdown("### 🧬 PathoVariant-AI")
    st.markdown("**Autonomous Pathogen Mutation & Risk Analyzer**")
    st.markdown("---")
    
    st.markdown("#### 🤖 AI Model Status")
    st.success("RandomForest + Biology Heuristic Engine Active")
    st.markdown("- **K-mer resolution:** 3-mer (64 features)")
    st.markdown("- **Classifier:** RandomForest (100 estimators)")
    st.markdown("- **Scoring:** 80% Transparent Heuristic + 20% Ensemble")
    
    st.markdown("---")
    st.markdown("#### 📌 Presets & Demos")
    preset_choice = st.selectbox("Load Sample Pathogen Sequence:", ["None"] + list(SAMPLE_SEQUENCES.keys()))
    
    st.markdown("---")
    st.markdown("#### 👨‍💻 Developer & Repository")
    st.markdown("**Author:** Tejas Parmar")
    st.markdown("[🔗 GitHub Repository](https://github.com/parmartejaskumar11-design/PathoVariant-AI)")

# Header
st.markdown('<div class="main-header">PathoVariant-AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Genomic Classification & Pathogen Mutation Functional Impact Analyzer</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🚀 Sequence Analysis", "📂 Batch Analysis", "🔬 AI Engine Architecture"])

with tab1:
    col_in1, col_in2 = st.columns([1, 1])
    
    with col_in1:
        st.subheader("1. Upload FASTA File")
        uploaded_file = st.file_uploader("Choose a FASTA file (.fasta, .fa, .fna, .txt)", type=["fasta", "fa", "fna", "txt"])
    
    with col_in2:
        st.subheader("2. Or Paste Sequence")
        default_text = ""
        if preset_choice != "None":
            default_text = SAMPLE_SEQUENCES[preset_choice]
            
        pasted_seq = st.text_area("Paste FASTA or raw DNA/RNA nucleotides:", value=default_text, height=130, placeholder=">seq_1\nATGCGATCGATCG...")

    analyze_btn = st.button("⚡ Run AI Pathogen Analysis", type="primary", use_container_width=True)

    if analyze_btn:
        content_to_parse = ""
        if uploaded_file is not None:
            content_to_parse = uploaded_file.getvalue().decode("utf-8-sig", errors="ignore")
        elif pasted_seq.strip():
            content_to_parse = pasted_seq.strip()
            if not content_to_parse.startswith(">"):
                content_to_parse = f">custom_sequence\n{content_to_parse}"
        
        if not content_to_parse:
            st.error("Please upload a FASTA file or paste a nucleotide sequence.")
        else:
            with st.spinner("Parsing genomic data & executing hybrid AI classification..."):
                parsed = parse_fasta_file(content_to_parse)
                
                if "error" in parsed and parsed["error"]:
                    st.error(f"Parsing error: {parsed['error']}")
                elif not parsed.get("records"):
                    st.error("No valid sequences could be parsed. Check FASTA formatting.")
                else:
                    records = parsed["records"]
                    results = []
                    
                    for r in records:
                        pred = engine.predict_sequence(r["sequence"])
                        results.append({
                            "id": r["id"],
                            "description": r["description"],
                            "length": r["length"],
                            "gc_content": round(r["gc_content"], 2),
                            "base_composition": r["base_composition"],
                            "protein_translation": r["protein_translation"],
                            "predicted_class": pred["predicted_class"],
                            "confidence_percent": pred["confidence_percent"],
                            "final_score": pred["final_score"],
                            "rf_score": pred["rf_score"],
                            "heuristic": pred["heuristic"],
                            "probabilities": pred["all_probabilities"]
                        })
                    
                    st.success(f"Successfully analyzed {len(results)} sequence(s)!")
                    st.markdown("---")
                    
                    # Top Metrics
                    m1, m2, m3, m4 = st.columns(4)
                    high_count = sum(1 for x in results if x["predicted_class"] == "High-Risk Variant")
                    mod_count = sum(1 for x in results if x["predicted_class"] == "Moderate Risk")
                    benign_count = sum(1 for x in results if x["predicted_class"] == "Benign Strain")
                    avg_gc = np.mean([x["gc_content"] for x in results])
                    
                    m1.metric("Total Sequences", len(results))
                    m2.metric("Mean GC Content", f"{avg_gc:.1f}%")
                    m3.metric("High-Risk Variants", high_count, delta=f"{high_count} Alert" if high_count > 0 else None, delta_color="inverse")
                    m4.metric("Benign / Moderate", f"{benign_count} / {mod_count}")
                    
                    st.markdown("### 📊 Classification Summary & Visualizations")
                    
                    # Plots Row
                    col_p1, col_p2 = st.columns([1, 1])
                    
                    with col_p1:
                        # Risk Pie
                        pie_df = pd.DataFrame([
                            {"Risk Tier": "High-Risk Variant", "Count": high_count},
                            {"Risk Tier": "Moderate Risk", "Count": mod_count},
                            {"Risk Tier": "Benign Strain", "Count": benign_count}
                        ])
                        pie_df = pie_df[pie_df["Count"] > 0]
                        fig_pie = px.pie(
                            pie_df, 
                            values="Count", 
                            names="Risk Tier", 
                            title="Risk Tier Distribution",
                            color="Risk Tier",
                            color_discrete_map={"High-Risk Variant": "#EF4444", "Moderate Risk": "#F59E0B", "Benign Strain": "#10B981"},
                            hole=0.45
                        )
                        fig_pie.update_layout(template="plotly_dark", margin=dict(t=40, b=20, l=20, r=20))
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                    with col_p2:
                        # First sequence base composition or average
                        first_rec = results[0]
                        base_df = pd.DataFrame([
                            {"Nucleotide": k, "Percentage": v}
                            for k, v in first_rec["base_composition"].items() if v > 0
                        ])
                        fig_bar = px.bar(
                            base_df, 
                            x="Nucleotide", 
                            y="Percentage", 
                            title=f"Nucleotide Composition ({first_rec['id']})",
                            color="Nucleotide",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        fig_bar.update_layout(template="plotly_dark", margin=dict(t=40, b=20, l=20, r=20), yaxis_range=[0, 100])
                        st.plotly_chart(fig_bar, use_container_width=True)

                    # Detailed sequence cards
                    st.markdown("### 📋 Sequence Details & Subscore Breakdown")
                    for idx, item in enumerate(results):
                        badge_class = "badge-high" if item["predicted_class"] == "High-Risk Variant" else ("badge-moderate" if item["predicted_class"] == "Moderate Risk" else "badge-benign")
                        
                        with st.expander(f"🧬 Sequence #{idx+1}: {item['id']} — {item['predicted_class']} ({item['confidence_percent']}% confidence)", expanded=(idx == 0)):
                            c1, c2, c3 = st.columns([1, 1, 1])
                            c1.markdown(f"**Classification:** <span class='{badge_class}'>{item['predicted_class']}</span>", unsafe_allow_html=True)
                            c1.markdown(f"**Confidence:** `{item['confidence_percent']}%`")
                            c1.markdown(f"**Composite Risk Score:** `{item['final_score']} / 100`")
                            
                            c2.markdown(f"**Sequence Length:** `{item['length']} bp`")
                            c2.markdown(f"**GC Content:** `{item['gc_content']}%`")
                            c2.markdown(f"**RandomForest Probability:** `{item['rf_score']}%`")
                            
                            sub = item["heuristic"].get("subscores", {})
                            c3.markdown("**AI Biology Subscores:**")
                            c3.markdown(f"- GC Imbalance: `{sub.get('gc_imbalance', 0):.1f}`")
                            c3.markdown(f"- Homopolymers: `{sub.get('homopolymer_runs', 0):.1f}`")
                            c3.markdown(f"- Tandem Repeats: `{sub.get('tandem_repeats', 0):.1f}`")
                            c3.markdown(f"- K-mer Repetitiveness: `{sub.get('kmer_repetitiveness', 0):.1f}`")
                            
                            if item["protein_translation"]:
                                st.markdown("**Protein Translation:**")
                                st.code(item["protein_translation"], language="text")
                    
                    # CSV Export
                    st.markdown("### 📥 Export Results")
                    export_df = pd.DataFrame([{
                        "ID": x["id"],
                        "Length": x["length"],
                        "GC_Content": x["gc_content"],
                        "Predicted_Class": x["predicted_class"],
                        "Confidence_Percent": x["confidence_percent"],
                        "Risk_Score": x["final_score"],
                        "Description": x["description"]
                    } for x in results])
                    
                    csv_data = export_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📄 Download Analysis as CSV",
                        data=csv_data,
                        file_name="pathovariant_analysis_results.csv",
                        mime="text/csv"
                    )

with tab2:
    st.subheader("📂 Batch FASTA Files Analysis")
    st.markdown("Upload multiple FASTA files simultaneously for high-throughput pathogen surveillance.")
    
    batch_files = st.file_uploader("Choose multiple FASTA files", type=["fasta", "fa", "fna", "txt"], accept_multiple_files=True, key="batch_uploader")
    
    if st.button("🚀 Analyze All Batch Files", type="primary", key="batch_btn"):
        if not batch_files:
            st.error("Please select one or more FASTA files.")
        else:
            all_batch_records = []
            file_summaries = []
            
            with st.spinner(f"Analyzing {len(batch_files)} files in parallel..."):
                for bf in batch_files:
                    content = bf.getvalue().decode("utf-8-sig", errors="ignore")
                    parsed = parse_fasta_file(content)
                    if parsed.get("records"):
                        f_high, f_mod, f_benign = 0, 0, 0
                        for r in parsed["records"]:
                            pred = engine.predict_sequence(r["sequence"])
                            p_class = pred["predicted_class"]
                            if p_class == "High-Risk Variant": f_high += 1
                            elif p_class == "Moderate Risk": f_mod += 1
                            else: f_benign += 1
                            
                            all_batch_records.append({
                                "File": bf.name,
                                "ID": r["id"],
                                "Length": r["length"],
                                "GC (%)": round(r["gc_content"], 2),
                                "Class": p_class,
                                "Confidence (%)": pred["confidence_percent"],
                                "Risk Score": pred["final_score"]
                            })
                            
                        file_summaries.append({
                            "File": bf.name,
                            "Sequences": len(parsed["records"]),
                            "High-Risk": f_high,
                            "Moderate": f_mod,
                            "Benign": f_benign
                        })
            
            if all_batch_records:
                st.success(f"Processed {len(batch_files)} file(s) containing {len(all_batch_records)} total sequences.")
                
                st.markdown("#### 📑 Per-File Summary")
                st.dataframe(pd.DataFrame(file_summaries), use_container_width=True)
                
                st.markdown("#### 🧬 All Classified Sequences")
                st.dataframe(pd.DataFrame(all_batch_records), use_container_width=True)
                
                b_df = pd.DataFrame(all_batch_records)
                st.download_button(
                    label="📥 Download Batch Results (CSV)",
                    data=b_df.to_csv(index=False).encode('utf-8'),
                    file_name="batch_pathovariant_summary.csv",
                    mime="text/csv"
                )

with tab3:
    st.subheader("🔬 AI Engine Architecture & Methodology")
    
    st.markdown("""
    PathoVariant-AI uses a **dual-engine hybrid classification system** combining biology-informed heuristics with a supervised RandomForest machine learning model:
    
    ### 1. Hybrid Ensemble Formula
    `Final Score = 0.80 * Heuristic Score + 0.20 * RandomForest Score`
    
    ### 2. Feature Extraction Pipeline
    - **K-mer Frequency Vectors**: Normalized frequency of all canonical 3-mers (64 dimensions).
    - **GC-Content Imbalance**: Divergence from pathogen baseline stability.
    - **Homopolymer Runs**: Detection of single-nucleotide repeats (>= 4 bp) indicative of slippage hotspots.
    - **Tandem Duplications & Micro-satellite Patterns**: Repetitive sequence indexing.
    
    ### 3. Classification Boundaries
    - **Benign Strain**: Score centered at 17.0 (Low mutation signal).
    - **Moderate Risk**: Score centered at 47.5 (Surveillance candidate).
    - **High-Risk Variant**: Score centered at 80.0 (Pathogenic mutation alert).
    """)
