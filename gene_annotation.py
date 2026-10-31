import pandas as pd

print("Loading annotation file...")

# Read annotation rows directly
rows = []

with open("GPL570.annot", "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        fields = line.rstrip("\r\n").split("\t")

        if len(fields) == 21 and fields[0].strip().endswith(
            ("_at", "_s_at", "_x_at")
        ):
            rows.append(fields)

# Create annotation dataframe
annotation = pd.DataFrame(rows, columns=[
    "Probe_ID",
    "Gene_title",
    "Gene_symbol",
    "Gene_ID",
    "UniGene_title",
    "UniGene_symbol",
    "UniGene_ID",
    "Nucleotide_Title",
    "GI",
    "GenBank_Accession",
    "Platform_CLONEID",
    "Platform_ORF",
    "Platform_SPOTID",
    "Chromosome_location",
    "Chromosome_annotation",
    "GO_Function",
    "GO_Process",
    "GO_Component",
    "GO_Function_ID",
    "GO_Process_ID",
    "GO_Component_ID"
])

print("Annotation rows:", len(annotation))

# Remove duplicate probe IDs
annotation = annotation.drop_duplicates(subset="Probe_ID")

# Load statistical results
results = pd.read_csv("statistical_results.csv")

# Merge annotation
merged = results.merge(
    annotation[["Probe_ID", "Gene_title", "Gene_symbol", "Gene_ID"]],
    on="Probe_ID",
    how="left"
)

# Save output
merged.to_csv("annotated_statistical_results.csv", index=False)

print("\nGene annotation completed!")
print("Total probes:", len(merged))
print("Mapped symbols:", merged["Gene_symbol"].notna().sum())

print("\nFirst 10 annotated probes:")
print(merged[["Probe_ID", "Gene_symbol", "Gene_title"]].head(10))

print("\nSaved: annotated_statistical_results.csv")