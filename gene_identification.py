
import pandas as pd
import gzip
from io import StringIO

print("Starting Gene Identification...")

# Read downloaded annotation file
with gzip.open("GPL570.annot.gz", "rt", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

header_index = next(
    i for i, line in enumerate(lines)
    if line.startswith("ID\t")
)

annotation = pd.read_csv(
    StringIO("".join(lines[header_index:])),
    sep="\t",
    dtype=str,
    low_memory=False
)

# Select correct column names
annotation = annotation[
    ["ID", "Gene symbol", "Gene title", "Gene ID"]
].copy()

# Rename columns
annotation = annotation.rename(columns={
    "ID": "Probe_ID",
    "Gene symbol": "Gene_Symbol",
    "Gene title": "Gene_Name",
    "Gene ID": "Gene_ID"
})

# Load statistical results
results = pd.read_csv("statistical_results.csv")

# Match probe IDs with gene annotation
merged = results.merge(
    annotation,
    on="Probe_ID",
    how="left"
)

# Save final annotated results
merged.to_csv("annotated_statistical_results.csv", index=False)

print("\nGENE IDENTIFICATION SUCCESSFUL!")
print("Total probes:", len(merged))
print("Identified gene symbols:", merged["Gene_Symbol"].notna().sum())

print("\nTOP 10 IDENTIFIED GENES:")
print(
    merged[
        ["Probe_ID", "Gene_Symbol", "Gene_Name", "FDR"]
    ].head(10).to_string(index=False)
)

print("\nFile saved: annotated_statistical_results.csv")
