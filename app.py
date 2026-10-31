import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle
)

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="GeneInsight AI",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 GeneInsight AI")
st.subheader("Advanced Gene Expression Analysis & Biomarker Discovery")

st.write(
    "An interactive bioinformatics platform for gene expression, "
    "differential expression, DNA mutation analysis and biomarker exploration."
)

st.info(
    "Educational and research demonstration. "
    "Results require independent biological validation."
)

# ==========================================
# SECTION 1: SIMULATED GENE ANALYSIS
# ==========================================

st.divider()
st.header("📊 Gene Expression Analysis")

np.random.seed(42)

genes = [
    "BRCA1", "TP53", "EGFR", "MYC", "VEGFA",
    "TNF", "IL6", "APC", "KRAS", "PTEN",
    "BAX", "CDH1", "MKI67", "ERBB2", "AKT1"
]

normal = np.random.normal(10, 2, (15, 5))
disease = np.random.normal(10, 2, (15, 5))

disease[2] += 8
disease[3] += 7
disease[4] += 6
disease[6] += 5
disease[12] += 8

normal = np.clip(normal, 0.1, None)
disease = np.clip(disease, 0.1, None)

normal_df = pd.DataFrame(
    normal,
    index=genes,
    columns=[f"Normal_{i+1}" for i in range(5)]
)

disease_df = pd.DataFrame(
    disease,
    index=genes,
    columns=[f"Disease_{i+1}" for i in range(5)]
)

demo_results = pd.DataFrame({
    "Gene": genes,
    "Normal_Mean": normal_df.mean(axis=1).values,
    "Disease_Mean": disease_df.mean(axis=1).values
})

demo_results["Fold_Change"] = (
    demo_results["Disease_Mean"] /
    demo_results["Normal_Mean"]
)

demo_results["Log2_Fold_Change"] = np.log2(
    demo_results["Fold_Change"]
)

demo_results["Pattern"] = np.where(
    demo_results["Log2_Fold_Change"] >= 0.5,
    "Higher in Disease",
    np.where(
        demo_results["Log2_Fold_Change"] <= -0.5,
        "Lower in Disease",
        "No Large Change"
    )
)

col1, col2, col3 = st.columns(3)

col1.metric("Genes Analyzed", len(genes))

col2.metric(
    "Higher in Disease",
    int((demo_results["Pattern"] == "Higher in Disease").sum())
)

col3.metric(
    "Lower in Disease",
    int((demo_results["Pattern"] == "Lower in Disease").sum())
)

st.dataframe(
    demo_results.round(3),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# SECTION 2: INDIVIDUAL GENE EXPLORER
# ==========================================

st.divider()
st.header("🔍 Individual Gene Explorer")

selected_gene = st.selectbox(
    "Select Gene",
    genes
)

selected_row = demo_results[
    demo_results["Gene"] == selected_gene
].iloc[0]

col1, col2 = st.columns(2)

col1.metric(
    "Normal Expression",
    f"{selected_row['Normal_Mean']:.2f}"
)

col2.metric(
    "Disease Expression",
    f"{selected_row['Disease_Mean']:.2f}"
)

fig, ax = plt.subplots(figsize=(7, 4))

ax.bar(
    ["Normal", "Disease"],
    [
        selected_row["Normal_Mean"],
        selected_row["Disease_Mean"]
    ]
)

ax.set_title(f"Gene Expression: {selected_gene}")
ax.set_ylabel("Mean Expression")

st.pyplot(fig)
plt.close(fig)

# ==========================================
# SECTION 3: HEATMAP
# ==========================================

st.divider()
st.header("🌡️ Gene Expression Heatmap")

combined_df = pd.concat(
    [normal_df, disease_df],
    axis=1
)

fig, ax = plt.subplots(figsize=(12, 6))

heatmap = ax.imshow(
    combined_df.values,
    aspect="auto",
    interpolation="nearest"
)

ax.set_yticks(range(len(genes)))
ax.set_yticklabels(genes)

ax.set_xticks(range(combined_df.shape[1]))
ax.set_xticklabels(
    combined_df.columns,
    rotation=45,
    ha="right"
)

ax.set_title("Simulated Gene Expression Patterns")

fig.colorbar(
    heatmap,
    ax=ax,
    label="Expression"
)

fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

# ==========================================
# SECTION 4: SIMULATED DATA DOWNLOAD
# ==========================================

st.divider()
st.header("📥 Download Gene Analysis")

st.download_button(
    "Download Gene Analysis CSV",
    data=demo_results.to_csv(index=False),
    file_name="GeneInsight_Gene_Analysis.csv",
    mime="text/csv"
)

# ==========================================
# SECTION 5: CUSTOM CSV UPLOAD
# ==========================================

st.divider()
st.header("📂 Upload Gene Expression Dataset")

uploaded_file = st.file_uploader(
    "Upload CSV Dataset",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        uploaded_df = pd.read_csv(uploaded_file)

        uploaded_df.columns = (
            uploaded_df.columns.astype(str).str.strip()
        )

        st.subheader("Uploaded Dataset Preview")

        st.dataframe(
            uploaded_df.head(10),
            use_container_width=True
        )

        st.success("Dataset uploaded successfully!")

        st.write("Rows:", uploaded_df.shape[0])
        st.write("Columns:", uploaded_df.shape[1])

        # Automatic insights

        if "Gene" in uploaded_df.columns:

            normal_cols = [
                c for c in uploaded_df.columns
                if c.lower().startswith("normal")
            ]

            disease_cols = [
                c for c in uploaded_df.columns
                if c.lower().startswith("disease")
            ]

            if normal_cols and disease_cols:

                uploaded_df["Normal_Mean"] = (
                    uploaded_df[normal_cols].mean(axis=1)
                )

                uploaded_df["Disease_Mean"] = (
                    uploaded_df[disease_cols].mean(axis=1)
                )

                uploaded_df["Difference"] = (
                    uploaded_df["Disease_Mean"] -
                    uploaded_df["Normal_Mean"]
                )

                st.subheader("🤖 Automatic Gene Insights")

                st.dataframe(
                    uploaded_df[
                        [
                            "Gene",
                            "Normal_Mean",
                            "Disease_Mean",
                            "Difference"
                        ]
                    ],
                    use_container_width=True
                )

            else:
                st.info(
                    "For automatic comparison, provide Normal_1 "
                    "and Disease_1 type columns."
                )

    except Exception as error:
        st.error(f"CSV Error: {error}")

# ==========================================
# SECTION 6: PDF AND EXCEL REPORT
# ==========================================

st.divider()
st.header("📄 Professional Analysis Reports")

if uploaded_file is not None:

    try:
        uploaded_file.seek(0)

        report_data = pd.read_csv(uploaded_file)

        report_data.columns = (
            report_data.columns.astype(str).str.strip()
        )

        if "Gene" in report_data.columns:

            normal_cols = [
                c for c in report_data.columns
                if c.lower().startswith("normal")
            ]

            disease_cols = [
                c for c in report_data.columns
                if c.lower().startswith("disease")
            ]

            if normal_cols and disease_cols:

                report_data["Normal_Mean"] = (
                    report_data[normal_cols].mean(axis=1)
                )

                report_data["Disease_Mean"] = (
                    report_data[disease_cols].mean(axis=1)
                )

                report_data["Difference"] = (
                    report_data["Disease_Mean"] -
                    report_data["Normal_Mean"]
                )

                report_data["Fold_Change"] = (
                    report_data["Disease_Mean"] /
                    report_data["Normal_Mean"].replace(0, np.nan)
                )

                report_results = report_data[
                    [
                        "Gene",
                        "Normal_Mean",
                        "Disease_Mean",
                        "Difference",
                        "Fold_Change"
                    ]
                ].copy()

                # Excel

                excel_buffer = io.BytesIO()

                with pd.ExcelWriter(
                    excel_buffer,
                    engine="openpyxl"
                ) as writer:

                    report_results.to_excel(
                        writer,
                        index=False,
                        sheet_name="Gene Analysis"
                    )

                st.download_button(
                    "📊 Download Excel Report",
                    data=excel_buffer.getvalue(),
                    file_name="GeneInsight_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # PDF

                pdf_buffer = io.BytesIO()

                doc = SimpleDocTemplate(
                    pdf_buffer,
                    pagesize=A4
                )

                styles = getSampleStyleSheet()

                story = [
                    Paragraph(
                        "GeneInsight AI",
                        styles["Title"]
                    ),
                    Paragraph(
                        "Gene Expression Analysis Report",
                        styles["Heading2"]
                    ),
                    Spacer(1, 15),
                    Paragraph(
                        "Generated: " +
                        datetime.now().strftime("%d-%m-%Y %H:%M"),
                        styles["Normal"]
                    ),
                    Spacer(1, 15)
                ]

                table_data = [
                    [
                        "Gene",
                        "Normal",
                        "Disease",
                        "Difference",
                        "Fold Change"
                    ]
                ]

                for _, row in report_results.iterrows():

                    table_data.append([
                        str(row["Gene"]),
                        f"{row['Normal_Mean']:.2f}",
                        f"{row['Disease_Mean']:.2f}",
                        f"{row['Difference']:.2f}",
                        (
                            f"{row['Fold_Change']:.2f}"
                            if pd.notna(row["Fold_Change"])
                            else "N/A"
                        )
                    ])

                table = Table(
                    table_data,
                    repeatRows=1
                )

                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]))

                story.append(table)

                doc.build(story)

                st.download_button(
                    "📄 Download PDF Report",
                    data=pdf_buffer.getvalue(),
                    file_name="GeneInsight_Report.pdf",
                    mime="application/pdf"
                )

    except Exception as error:
        st.error(f"Report Error: {error}")

# ==========================================
# SECTION 7: DNA MUTATION DETECTION
# ==========================================

st.divider()
st.header("🧬 DNA Mutation Detection")

reference_dna = st.text_area(
    "Reference DNA Sequence",
    "ATGCTAGCTA",
    key="reference_dna"
)

query_dna = st.text_area(
    "Query DNA Sequence",
    "ATGATAGCTA",
    key="query_dna"
)


def align_dna(seq1, seq2):

    match = 2
    mismatch = -1
    gap = -2

    n, m = len(seq1), len(seq2)

    score = [[0] * (m + 1) for _ in range(n + 1)]
    trace = [[None] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        score[i][0] = i * gap
        trace[i][0] = "up"

    for j in range(1, m + 1):
        score[0][j] = j * gap
        trace[0][j] = "left"

    for i in range(1, n + 1):

        for j in range(1, m + 1):

            diagonal = score[i-1][j-1] + (
                match if seq1[i-1] == seq2[j-1]
                else mismatch
            )

            up = score[i-1][j] + gap
            left = score[i][j-1] + gap

            best = max(diagonal, up, left)

            score[i][j] = best

            if best == diagonal:
                trace[i][j] = "diag"
            elif best == up:
                trace[i][j] = "up"
            else:
                trace[i][j] = "left"

    aligned1 = []
    aligned2 = []

    i, j = n, m

    while i > 0 or j > 0:

        direction = trace[i][j]

        if direction == "diag":

            aligned1.append(seq1[i-1])
            aligned2.append(seq2[j-1])

            i -= 1
            j -= 1

        elif direction == "up":

            aligned1.append(seq1[i-1])
            aligned2.append("-")

            i -= 1

        else:

            aligned1.append("-")
            aligned2.append(seq2[j-1])

            j -= 1

    return (
        "".join(reversed(aligned1)),
        "".join(reversed(aligned2))
    )


if st.button("🔍 Detect Mutations"):

    ref = "".join(reference_dna.upper().split())
    query = "".join(query_dna.upper().split())

    if not ref or not query:

        st.error("Enter both DNA sequences.")

    elif not set(ref).issubset(set("ACGT")) or not set(query).issubset(set("ACGT")):

        st.error("Only A, C, G and T are allowed.")

    elif max(len(ref), len(query)) > 1000:

        st.error("Maximum sequence length is 1000 bases.")

    else:

        aligned_ref, aligned_query = align_dna(ref, query)

        st.code(
            f"Reference: {aligned_ref}\nQuery:     {aligned_query}"
        )

        mutations = []

        ref_pos = 0

        for a, b in zip(aligned_ref, aligned_query):

            if a != "-":
                ref_pos += 1

            if a == b:
                continue

            if a == "-":
                mutation_type = "Insertion"

            elif b == "-":
                mutation_type = "Deletion"

            else:
                mutation_type = "Substitution"

            mutations.append({
                "Position": ref_pos,
                "Reference": a,
                "Query": b,
                "Mutation": mutation_type
            })

        if mutations:

            mutation_df = pd.DataFrame(mutations)

            st.dataframe(mutation_df)

            st.download_button(
                "Download Mutation Report",
                mutation_df.to_csv(index=False),
                file_name="Mutation_Report.csv"
            )

        else:

            st.success("No differences detected.")

# ==========================================
# SECTION 8: DNA RNA PROTEIN TRANSLATION
# ==========================================

st.divider()
st.header("🧬 DNA → RNA → Protein Translation")

dna_input = st.text_area(
    "Enter DNA Sequence",
    "ATGGCTTTTAAATGA",
    key="translation_dna"
)

genetic_code = {
    "TTT":"F","TTC":"F","TTA":"L","TTG":"L",
    "TCT":"S","TCC":"S","TCA":"S","TCG":"S",
    "TAT":"Y","TAC":"Y","TAA":"*","TAG":"*",
    "TGT":"C","TGC":"C","TGA":"*","TGG":"W",
    "CTT":"L","CTC":"L","CTA":"L","CTG":"L",
    "CCT":"P","CCC":"P","CCA":"P","CCG":"P",
    "CAT":"H","CAC":"H","CAA":"Q","CAG":"Q",
    "CGT":"R","CGC":"R","CGA":"R","CGG":"R",
    "ATT":"I","ATC":"I","ATA":"I","ATG":"M",
    "ACT":"T","ACC":"T","ACA":"T","ACG":"T",
    "AAT":"N","AAC":"N","AAA":"K","AAG":"K",
    "AGT":"S","AGC":"S","AGA":"R","AGG":"R",
    "GTT":"V","GTC":"V","GTA":"V","GTG":"V",
    "GCT":"A","GCC":"A","GCA":"A","GCG":"A",
    "GAT":"D","GAC":"D","GAA":"E","GAG":"E",
    "GGT":"G","GGC":"G","GGA":"G","GGG":"G"
}

if st.button("🔬 Translate DNA"):

    dna = "".join(dna_input.upper().split())

    if not dna:

        st.error("Enter DNA sequence.")

    elif not set(dna).issubset(set("ACGT")):

        st.error("Invalid DNA sequence.")

    elif len(dna) > 30000:

        st.error("Maximum length is 30000 bases.")

    else:

        rna = dna.replace("T", "U")

        protein = []

        for i in range(0, len(dna)-2, 3):

            codon = dna[i:i+3]

            amino = genetic_code[codon]

            if amino == "*":

                protein.append("STOP")
                break

            protein.append(amino)

        protein_sequence = "".join(protein)

        st.subheader("Translation Results")

        st.write("DNA:")
        st.code(dna)

        st.write("RNA:")
        st.code(rna)

        st.write("Protein:")
        st.code(protein_sequence)

        st.metric("DNA Length", f"{len(dna)} bp")

        st.download_button(
            "Download Translation Results",
            f"DNA: {dna}\nRNA: {rna}\nProtein: {protein_sequence}",
            file_name="Translation_Report.txt"
        )

# ==========================================
# SECTION 9: GC CONTENT ANALYSIS
# ==========================================

st.divider()
st.header("🧬 DNA Composition & Quality Analyzer")

dna_quality = st.text_area(
    "Enter DNA for GC Analysis",
    "ATGGCTTTTAAATGA",
    key="gc_sequence"
)

if st.button("📊 Analyze DNA Composition"):

    seq = "".join(dna_quality.upper().split())

    if not seq:

        st.error("Enter DNA sequence.")

    elif not set(seq).issubset(set("ACGT")):

        st.error("Only A, T, G, C allowed.")

    else:

        counts = {
            "A": seq.count("A"),
            "T": seq.count("T"),
            "G": seq.count("G"),
            "C": seq.count("C")
        }

        gc = (
            (counts["G"] + counts["C"]) /
            len(seq)
        ) * 100

        at = (
            (counts["A"] + counts["T"]) /
            len(seq)
        ) * 100

        col1, col2, col3 = st.columns(3)

        col1.metric("Length", f"{len(seq)} bp")
        col2.metric("GC Content", f"{gc:.2f}%")
        col3.metric("AT Content", f"{at:.2f}%")

        nucleotide_df = pd.DataFrame({
            "Nucleotide": list(counts.keys()),
            "Count": list(counts.values())
        })

        st.bar_chart(
            nucleotide_df.set_index("Nucleotide")
        )

        st.dataframe(nucleotide_df)

# ==========================================
# SECTION 10: REAL GSE42568 DATASET
# ==========================================

st.divider()

st.title("🧬 GSE42568 - Breast Cancer Analysis")

st.write(
    "Real gene expression analysis using "
    "GEO breast cancer dataset GSE42568."
)

try:

    metadata = pd.read_csv("sample_metadata.csv")

    comparison = pd.read_csv("comparison_results.csv")

    metadata.columns = metadata.columns.str.strip()
    comparison.columns = comparison.columns.str.strip()

    cancer_count = (
        metadata["Sample_Type"] == "Cancer"
    ).sum()

    normal_count = (
        metadata["Sample_Type"] == "Normal"
    ).sum()

    st.subheader("📊 Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Samples", len(metadata))
    col2.metric("Cancer Samples", int(cancer_count))
    col3.metric("Normal Samples", int(normal_count))

    st.subheader("Cancer vs Normal Expression")

    top_n = st.selectbox(
        "Select Top Probes",
        [5, 10, 15, 20],
        index=1
    )

    top_results = comparison.nlargest(
        top_n,
        "Absolute_Difference"
    ).sort_values("Absolute_Difference")

    chart_data = top_results.set_index("Probe_ID")[
        ["Normal_Mean", "Cancer_Mean"]
    ]

    st.bar_chart(chart_data)

    st.subheader("Top Expression Differences")

    st.dataframe(
        top_results,
        use_container_width=True
    )

    st.download_button(
        "Download GSE42568 Results",
        top_results.to_csv(index=False),
        file_name="GSE42568_Results.csv"
    )

    st.success("Real dataset loaded successfully!")

except Exception as error:

    st.error(f"Dataset loading error: {error}")

# ==========================================
# SECTION 11: STATISTICAL ANALYSIS
# ==========================================

st.divider()
st.header("📈 Statistical Analysis")

try:

    stat_results = pd.read_csv(
        "statistical_results.csv"
    )

    stat_results.columns = (
        stat_results.columns.astype(str).str.strip()
    )

    required = [
        "Probe_ID",
        "Cancer_Mean",
        "Normal_Mean",
        "Mean_Difference",
        "P_Value",
        "FDR"
    ]

    missing = [
        c for c in required
        if c not in stat_results.columns
    ]

    if missing:

        st.error(f"Missing columns: {missing}")

    else:

        for col in [
            "Cancer_Mean",
            "Normal_Mean",
            "Mean_Difference",
            "P_Value",
            "FDR"
        ]:

            stat_results[col] = pd.to_numeric(
                stat_results[col],
                errors="coerce"
            )

        stat_results = stat_results.dropna(
            subset=["FDR", "Cancer_Mean", "Normal_Mean"]
        )

        significant = stat_results[
            stat_results["FDR"] < 0.05
        ]

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Probes",
            len(stat_results)
        )

        col2.metric(
            "Significant Probes (FDR < 0.05)",
            len(significant)
        )

        st.subheader("Top Significant Probes")

        top_stat = significant.sort_values(
            "FDR"
        ).head(20)

        st.dataframe(
            top_stat,
            use_container_width=True
        )

        st.download_button(
            "Download Statistical Results",
            stat_results.to_csv(index=False),
            file_name="Statistical_Results.csv"
        )

except Exception as error:

    st.error(f"Statistical Analysis Error: {error}")

# ==========================================
# SECTION 12: VOLCANO PLOT
# ==========================================

st.divider()

st.header("🌋 Volcano Plot - Differential Gene Expression")

try:

    volcano_data = pd.read_csv(
        "statistical_results.csv"
    )

    volcano_data.columns = (
        volcano_data.columns.astype(str).str.strip()
    )

    required_columns = [
        "Probe_ID",
        "Cancer_Mean",
        "Normal_Mean",
        "FDR"
    ]

    missing = [
        c for c in required_columns
        if c not in volcano_data.columns
    ]

    if missing:

        st.error(
            f"Required columns not found: {missing}"
        )

    else:

        for col in [
            "Cancer_Mean",
            "Normal_Mean",
            "FDR"
        ]:

            volcano_data[col] = pd.to_numeric(
                volcano_data[col],
                errors="coerce"
            )

        volcano_data = volcano_data.replace(
            [np.inf, -np.inf],
            np.nan
        )

        volcano_data = volcano_data.dropna(
            subset=[
                "Cancer_Mean",
                "Normal_Mean",
                "FDR"
            ]
        )

        # Calculate log2 fold change
        volcano_data["Log2_Fold_Change"] = np.log2(
            (
                volcano_data["Cancer_Mean"] + 0.01
            ) /
            (
                volcano_data["Normal_Mean"] + 0.01
            )
        )

        # Calculate negative log10 FDR
        volcano_data["Neg_Log10_FDR"] = -np.log10(
            volcano_data["FDR"].clip(
                lower=1e-300
            )
        )

        # Classify expression
        volcano_data["Significance"] = np.where(
            (
                (volcano_data["FDR"] < 0.05) &
                (volcano_data["Log2_Fold_Change"] > 1)
            ),
            "Upregulated",

            np.where(
                (
                    (volcano_data["FDR"] < 0.05) &
                    (volcano_data["Log2_Fold_Change"] < -1)
                ),
                "Downregulated",
                "Not Significant"
            )
        )

        # Plot
        fig, ax = plt.subplots(figsize=(12, 7))

        for category in [
            "Upregulated",
            "Downregulated",
            "Not Significant"
        ]:

            subset = volcano_data[
                volcano_data["Significance"] == category
            ]

            ax.scatter(
                subset["Log2_Fold_Change"],
                subset["Neg_Log10_FDR"],
                label=category,
                alpha=0.6,
                s=15
            )

        ax.axvline(
            x=1,
            linestyle="--",
            label="Log2FC Threshold"
        )

        ax.axvline(
            x=-1,
            linestyle="--"
        )

        ax.axhline(
            y=-np.log10(0.05),
            linestyle="--",
            label="FDR Threshold"
        )

        ax.set_xlabel("Log2 Fold Change")
        ax.set_ylabel("-Log10 FDR")

        ax.set_title(
            "GSE42568 Differential Gene Expression"
        )

        ax.legend()
        ax.grid(alpha=0.2)

        fig.tight_layout()

        st.pyplot(fig)

        plt.close(fig)

        # Statistics

        st.subheader("📊 Differential Expression Statistics")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Upregulated Probes",
            int(
                (
                    volcano_data["Significance"] ==
                    "Upregulated"
                ).sum()
            )
        )

        col2.metric(
            "Downregulated Probes",
            int(
                (
                    volcano_data["Significance"] ==
                    "Downregulated"
                ).sum()
            )
        )

        col3.metric(
            "Not Significant",
            int(
                (
                    volcano_data["Significance"] ==
                    "Not Significant"
                ).sum()
            )
        )

        # Top differential probes

        st.subheader("🧬 Top Differentially Expressed Probes")

        top_genes = volcano_data.sort_values(
            "FDR"
        ).head(20)

        st.dataframe(
            top_genes,
            use_container_width=True
        )

        # Download

        st.download_button(
            "📥 Download Volcano Plot Data",
            volcano_data.to_csv(index=False),
            file_name="Volcano_Plot_Results.csv",
            mime="text/csv"
        )

        st.success(
            "Volcano Plot generated successfully!"
        )

        st.caption(
            "Note: These are probe-level results. "
            "Probe IDs are not necessarily unique gene symbols. "
            "Gene annotation is required for biological interpretation. "
            "Log2 fold change is calculated from group means "
            "using a 0.01 pseudocount."
        )

except FileNotFoundError:

    st.error(
        "statistical_results.csv not found. "
        "Place the file in the GeneInsight_AI project folder."
    )

except Exception as error:

    st.error(
        f"Volcano Plot Error: {error}"
    )

# ==========================================
# SECTION 13: GENE ANNOTATION
# ==========================================

st.divider()
st.header("🧬 Gene Identification & Annotation")

try:
    annotated = pd.read_csv("annotated_statistical_results.csv")

    st.metric(
        "Identified Gene Symbols",
        annotated["Gene_symbol"].nunique()
    )

    # Display important columns first
    display_columns = [
        "Probe_ID",
        "Gene_symbol",
        "Gene_title",
        "Cancer_Mean",
        "Normal_Mean",
        "Mean_Difference",
        "P_Value",
        "FDR"
    ]

    available_columns = [
        col for col in display_columns
        if col in annotated.columns
    ]

    st.subheader("Annotated Gene Results")

    st.dataframe(
        annotated[available_columns].head(20),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Annotated Gene Results",
        annotated.to_csv(index=False),
        file_name="Annotated_Gene_Results.csv",
        mime="text/csv"
    )

except Exception as e:
    st.warning(f"Annotation file unavailable: {e}")


# ==========================================
# SECTION 14: TOP GENES
# ==========================================

st.divider()
st.header("🏆 Top Differentially Expressed Genes")

try:
    top_genes_data = pd.read_csv("top_20_genes.csv")

    st.metric(
        "Unique Genes Identified",
        top_genes_data["Gene_symbol"].nunique()
        if "Gene_symbol" in top_genes_data.columns
        else len(top_genes_data)
    )

    st.subheader("Top 20 Differentially Expressed Genes")

    # Important columns first
    preferred_columns = [
        "Gene_symbol",
        "Gene_title",
        "Probe_ID",
        "Cancer_Mean",
        "Normal_Mean",
        "Mean_Difference",
        "P_Value",
        "FDR"
    ]

    available_columns = [
        col for col in preferred_columns
        if col in top_genes_data.columns
    ]

    if available_columns:
        st.dataframe(
            top_genes_data[available_columns],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(
            top_genes_data,
            use_container_width=True,
            hide_index=True
        )

    st.download_button(
        "Download Top Genes",
        top_genes_data.to_csv(index=False),
        file_name="Top_Genes.csv",
        mime="text/csv"
    )

except Exception as e:
    st.warning(f"Top genes file unavailable: {e}")


# ==========================================
# SECTION 15: REAL EXPRESSION HEATMAP
# ==========================================

st.divider()
st.header("🌡️ Real Breast Cancer Expression Heatmap")

try:
    st.image(
        "gene_expression_heatmap.png",
        caption="GSE42568 - Normal and Cancer Sample Expression",
        use_container_width=True
    )

    with open("gene_expression_heatmap.png", "rb") as image_file:
        st.download_button(
            "Download Expression Heatmap",
            image_file,
            file_name="GeneInsight_Heatmap.png",
            mime="image/png"
        )

except Exception as e:
    st.warning(f"Heatmap unavailable: {e}")


# ==========================================
# SECTION 16: AI GENE INSIGHTS
# ==========================================

st.divider()
st.header("🤖 AI-Based Gene Insights")

try:
    insights = pd.read_csv("ai_gene_insights.csv")

    st.write(
        "Rule-based interpretation of significant genes "
        "using expression differences and annotation information."
    )

    st.dataframe(insights, use_container_width=True)

    st.download_button(
        "Download AI Gene Insights",
        insights.to_csv(index=False),
        file_name="AI_Gene_Insights.csv",
        mime="text/csv"
    )

except Exception as e:
    st.warning(f"AI insights unavailable: {e}")


# ==========================================
# SECTION 17: RESEARCH REPORT
# ==========================================

st.divider()
st.header("📄 AI Research Summary")

try:
    with open("AI_Gene_Insights_Report.txt", "r", encoding="utf-8") as report_file:
        report_text = report_file.read()

    st.text_area("Gene Research Report", report_text, height=300)

    st.download_button(
        "Download Research Report",
        report_text,
        file_name="GeneInsight_Research_Report.txt",
        mime="text/plain"
    )

except Exception as e:
    st.warning(f"Research report unavailable: {e}")

# ==========================================
# END OF APPLICATION
# ==========================================

st.divider()

st.success(
    "🧬 GeneInsight AI - Analysis Dashboard Loaded"
)

st.caption(
    "Developed for educational bioinformatics research."
)