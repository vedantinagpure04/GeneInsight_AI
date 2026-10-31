import pandas as pd

print("Starting AI Gene Insights Module...")

# Load top significant genes
df = pd.read_csv("top_20_genes.csv")

# Biological information for selected genes
gene_roles = {
    "COL10A1": "Collagen protein involved in extracellular matrix formation.",
    "NECTIN4": "Cell adhesion molecule involved in cell-to-cell interactions.",
    "RAB15": "Protein involved in intracellular vesicle transport.",
    "MMP11": "Matrix metalloproteinase involved in extracellular matrix remodeling.",
    "FGFR3": "Receptor involved in fibroblast growth factor signaling.",
    "HELLS": "Chromatin remodeling protein involved in DNA regulation.",
    "TRIM45": "Protein associated with cellular signaling and regulation.",
    "RSPH1": "Protein associated with ciliary structure and function.",
    "FBXL16": "Protein containing an F-box domain, associated with protein regulation.",
    "GTF2IRD2": "Protein associated with transcriptional regulation."
}

insights = []

for _, row in df.iterrows():

    gene = str(row["Gene_Symbol"])
    name = str(row["Gene_Name"])
    difference = float(row["Mean_Difference"])
    fdr = float(row["FDR"])

    role = gene_roles.get(
        gene,
        "Biological role requires further literature investigation."
    )

    if difference > 0:
        direction = "Higher expression in cancer samples"
    elif difference < 0:
        direction = "Lower expression in cancer samples"
    else:
        direction = "No mean expression difference"

    if fdr < 0.05:
        significance = "Statistically significant"
    else:
        significance = "Not statistically significant"

    report = {
        "Gene": gene,
        "Gene_Name": name,
        "Mean_Difference": difference,
        "FDR": fdr,
        "Expression_Pattern": direction,
        "Significance": significance,
        "Biological_Role": role
    }

    insights.append(report)

# Create DataFrame
result = pd.DataFrame(insights)

# Save CSV
result.to_csv("ai_gene_insights.csv", index=False)

# Generate text report
with open("AI_Gene_Insights_Report.txt", "w", encoding="utf-8") as file:

    file.write("GENEINSIGHT AI - GENE INSIGHTS REPORT\n")
    file.write("=" * 50 + "\n\n")

    for _, row in result.iterrows():

        file.write(f"Gene: {row['Gene']}\n")
        file.write(f"Gene Name: {row['Gene_Name']}\n")
        file.write(f"Expression: {row['Expression_Pattern']}\n")
        file.write(f"FDR: {row['FDR']:.3e}\n")
        file.write(f"Significance: {row['Significance']}\n")
        file.write(f"Biological Role: {row['Biological_Role']}\n")
        file.write("-" * 50 + "\n")

print("\nAI GENE INSIGHTS GENERATED!")

print(result[
    ["Gene", "Expression_Pattern", "Biological_Role"]
].to_string(index=False))

print("\nFiles created:")
print("1. ai_gene_insights.csv")
print("2. AI_Gene_Insights_Report.txt")