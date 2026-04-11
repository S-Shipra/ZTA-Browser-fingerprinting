import pandas as pd
import numpy as np
import os

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH   = os.path.join(BASE_DIR, "data", "fingerprints.csv")
OUTPUT_DIR  = os.path.join(BASE_DIR, "outputs")
OUTPUT_CSV  = os.path.join(OUTPUT_DIR, "entropy_results.csv")
OUTPUT_TXT  = os.path.join(OUTPUT_DIR, "entropy_report.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Algorithm 1 from paper — Shannon Entropy ─────────────────────────────────
def calculate_shannon_entropy(series):
    """
    Input  : a pandas Series of browser fingerprint attribute values
    Output : Shannon Entropy (H) of that attribute

    Formula: H = -sum( p(x) * log2(p(x)) )
    """
    value_counts = series.value_counts()
    total_count  = value_counts.sum()           # step 2: total count of all values
    entropy      = 0.0                          # step 3: initialise entropy to 0.0

    for count in value_counts:                  # step 4: for each value count
        if count > 0:                           # step 5: if count > 0
            probability = count / total_count   # step 6: p = count / total
            entropy    -= probability * np.log2(probability)  # step 7: H -= p*log2(p)

    return round(entropy, 4)                    # step 8: return result

# ── Load dataset ─────────────────────────────────────────────────────────────
print("=" * 60)
print("  BROWSER FINGERPRINT — SHANNON ENTROPY ANALYSIS")
print("=" * 60)

df = pd.read_csv(DATA_PATH)
print(f"\n✅ Dataset loaded: {df.shape[0]} fingerprints × {df.shape[1]} attributes\n")

# ── Calculate entropy for every attribute ────────────────────────────────────
results = []
for col in df.columns:
    h = calculate_shannon_entropy(df[col])
    unique_vals = df[col].nunique()
    results.append({
        "Attribute"    : col,
        "Entropy"      : h,
        "Unique_Values": unique_vals,
        "Total_Values" : len(df[col])
    })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values("Entropy", ascending=False).reset_index(drop=True)
results_df.index += 1  # rank starts at 1

# ── Save entropy_results.csv ──────────────────────────────────────────────────
results_df.to_csv(OUTPUT_CSV, index_label="Rank")
print(f"✅ entropy_results.csv saved to outputs/\n")

# ── Print Table VII equivalent (top 5) ───────────────────────────────────────
print("-" * 60)
print(f"  TABLE VII — TOP 5 MOST UNIQUE ATTRIBUTES (highest entropy)")
print("-" * 60)
print(f"  {'Rank':<6} {'Attribute':<40} {'Entropy':>8}")
print("-" * 60)
for _, row in results_df.head(5).iterrows():
    print(f"  {row.name:<6} {row['Attribute']:<40} {row['Entropy']:>8.4f}")

# ── Print Table VIII equivalent (bottom 5) ───────────────────────────────────
print()
print("-" * 60)
print(f"  TABLE VIII — LEAST UNIQUE ATTRIBUTES (lowest entropy)")
print("-" * 60)
print(f"  {'Rank':<6} {'Attribute':<40} {'Entropy':>8}")
print("-" * 60)
for _, row in results_df.tail(5).iterrows():
    print(f"  {row.name:<6} {row['Attribute']:<40} {row['Entropy']:>8.4f}")

# ── Paper comparison (Table IX equivalent) ───────────────────────────────────
paper_attrs = {
    "Screen_Inner"      : 6.4125,
    "Device_SpeechEngines": 5.3226,
    "Fonts_Documents"   : 4.9793,
    "Header_Connection" : 4.9280,
    "Canvas_GetImageData": 4.7300,
    "Device_VR"         : 0.0000,
    "Device_Gamepads"   : 0.1593,
}

print()
print("-" * 60)
print("  TABLE IX — COMPARISON WITH PAPER (fpting.com results)")
print("-" * 60)
print(f"  {'Attribute':<30} {'Paper':>8}  {'Ours':>8}  {'Diff':>8}")
print("-" * 60)
for attr, paper_val in paper_attrs.items():
    our_val = results_df.loc[results_df["Attribute"] == attr, "Entropy"].values
    our_val = our_val[0] if len(our_val) > 0 else 0.0
    diff    = round(our_val - paper_val, 4)
    print(f"  {attr:<30} {paper_val:>8.4f}  {our_val:>8.4f}  {diff:>+8.4f}")

# ── Save entropy_report.txt ──────────────────────────────────────────────────
with open(OUTPUT_TXT, "w") as f:
    f.write("BROWSER FINGERPRINT — SHANNON ENTROPY REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Dataset : {df.shape[0]} fingerprints, {df.shape[1]} attributes\n\n")
    f.write("TOP 5 MOST UNIQUE ATTRIBUTES\n")
    f.write("-" * 60 + "\n")
    for _, row in results_df.head(5).iterrows():
        f.write(f"  Rank {row.name}: {row['Attribute']:<40} H = {row['Entropy']:.4f}\n")
    f.write("\nLEAST UNIQUE ATTRIBUTES\n")
    f.write("-" * 60 + "\n")
    for _, row in results_df.tail(5).iterrows():
        f.write(f"  Rank {row.name}: {row['Attribute']:<40} H = {row['Entropy']:.4f}\n")

print()
print(f"✅ entropy_report.txt saved to outputs/")
print("=" * 60)