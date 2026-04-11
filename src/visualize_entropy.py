import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV  = os.path.join(BASE_DIR, "outputs", "entropy_results.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load entropy results ───────────────────────────────────────────────────────
df = pd.read_csv(INPUT_CSV, index_col="Rank")
df = df.sort_values("Entropy", ascending=False)

# ── Colour each bar by entropy level ──────────────────────────────────────────
def get_color(entropy):
    if entropy >= 8.0:
        return "#E85D24"   # high   → red/orange
    elif entropy >= 4.0:
        return "#EF9F27"   # medium → amber
    elif entropy >= 1.0:
        return "#1D9E75"   # low    → teal
    else:
        return "#B4B2A9"   # near 0 → gray

colors = [get_color(h) for h in df["Entropy"]]

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — All 52 attributes ranked by entropy
# ══════════════════════════════════════════════════════════════════════════════
fig1, ax1 = plt.subplots(figsize=(14, 10))

bars = ax1.barh(df["Attribute"], df["Entropy"], color=colors, edgecolor="white",
                linewidth=0.4, height=0.7)

# value labels on each bar
for bar, val in zip(bars, df["Entropy"]):
    ax1.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
             f"{val:.2f}", va="center", ha="left", fontsize=7, color="#444")

ax1.set_xlabel("Shannon Entropy (bits)", fontsize=12)
ax1.set_title("Shannon Entropy of All 52 Browser Fingerprint Attributes",
              fontsize=14, fontweight="bold", pad=16)
ax1.set_xlim(0, df["Entropy"].max() + 1.2)
ax1.invert_yaxis()
ax1.tick_params(axis="y", labelsize=7.5)
ax1.tick_params(axis="x", labelsize=10)
ax1.spines[["top", "right"]].set_visible(False)
ax1.grid(axis="x", linestyle="--", alpha=0.4)

# legend
legend_patches = [
    mpatches.Patch(color="#E85D24", label="High  (≥ 8.0)"),
    mpatches.Patch(color="#EF9F27", label="Medium (4.0 – 7.9)"),
    mpatches.Patch(color="#1D9E75", label="Low   (1.0 – 3.9)"),
    mpatches.Patch(color="#B4B2A9", label="Near zero (< 1.0)"),
]
ax1.legend(handles=legend_patches, loc="lower right", fontsize=9,
           framealpha=0.7, title="Entropy Level", title_fontsize=9)

plt.tight_layout()
path1 = os.path.join(OUTPUT_DIR, "entropy_all_attributes.png")
fig1.savefig(path1, dpi=150, bbox_inches="tight")
print(f"✅ Saved: entropy_all_attributes.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Top 10 vs Bottom 10 side by side
# ══════════════════════════════════════════════════════════════════════════════
top10 = df.head(10)
bot10 = df.tail(10).sort_values("Entropy", ascending=True)

fig2, (ax_top, ax_bot) = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle("Browser Fingerprint Attributes — Most vs Least Unique",
              fontsize=14, fontweight="bold", y=1.01)

# top 10
top_colors = [get_color(h) for h in top10["Entropy"]]
b1 = ax_top.barh(top10["Attribute"], top10["Entropy"],
                 color=top_colors, edgecolor="white", linewidth=0.4, height=0.7)
for bar, val in zip(b1, top10["Entropy"]):
    ax_top.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=8)
ax_top.set_title("Top 10 — Most Unique", fontsize=12, fontweight="bold", color="#E85D24")
ax_top.invert_yaxis()
ax_top.set_xlabel("Entropy (bits)")
ax_top.spines[["top", "right"]].set_visible(False)
ax_top.grid(axis="x", linestyle="--", alpha=0.4)
ax_top.tick_params(axis="y", labelsize=8.5)

# bottom 10
bot_colors = [get_color(h) for h in bot10["Entropy"]]
b2 = ax_bot.barh(bot10["Attribute"], bot10["Entropy"],
                 color=bot_colors, edgecolor="white", linewidth=0.4, height=0.7)
for bar, val in zip(b2, bot10["Entropy"]):
    ax_bot.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}", va="center", fontsize=8)
ax_bot.set_title("Bottom 10 — Least Unique", fontsize=12, fontweight="bold", color="#888780")
ax_bot.invert_yaxis()
ax_bot.set_xlabel("Entropy (bits)")
ax_bot.spines[["top", "right"]].set_visible(False)
ax_bot.grid(axis="x", linestyle="--", alpha=0.4)
ax_bot.tick_params(axis="y", labelsize=8.5)

plt.tight_layout()
path2 = os.path.join(OUTPUT_DIR, "entropy_top_bottom.png")
fig2.savefig(path2, dpi=150, bbox_inches="tight")
print(f"✅ Saved: entropy_top_bottom.png")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Paper comparison bar chart (Table IX)
# ══════════════════════════════════════════════════════════════════════════════
paper_data = {
    "Screen_Inner"        : 6.4125,
    "Device_SpeechEngines": 5.3226,
    "Fonts_Documents"     : 4.9793,
    "Header_Connection"   : 4.9280,
    "Canvas_GetImageData" : 4.7300,
    "Device_VR"           : 0.0000,
    "Device_Gamepads"     : 0.1593,
}

attrs     = list(paper_data.keys())
paper_vals = list(paper_data.values())
our_vals  = [df.loc[df["Attribute"] == a, "Entropy"].values[0]
             if a in df["Attribute"].values else 0.0 for a in attrs]

x     = np.arange(len(attrs))
width = 0.35

fig3, ax3 = plt.subplots(figsize=(13, 6))
b_paper = ax3.bar(x - width/2, paper_vals, width, label="Paper (fpting.com)",
                  color="#534AB7", alpha=0.85, edgecolor="white")
b_ours  = ax3.bar(x + width/2, our_vals,   width, label="Our Synthetic Dataset",
                  color="#1D9E75", alpha=0.85, edgecolor="white")

for bar in b_paper:
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=8)
for bar in b_ours:
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=8)

ax3.set_xticks(x)
ax3.set_xticklabels(attrs, rotation=20, ha="right", fontsize=9)
ax3.set_ylabel("Shannon Entropy (bits)", fontsize=11)
ax3.set_title("Shannon Entropy Comparison — Paper vs Our Dataset (Table IX)",
              fontsize=13, fontweight="bold", pad=14)
ax3.legend(fontsize=10)
ax3.spines[["top", "right"]].set_visible(False)
ax3.grid(axis="y", linestyle="--", alpha=0.4)
ax3.set_ylim(0, max(max(paper_vals), max(our_vals)) + 1.5)

plt.tight_layout()
path3 = os.path.join(OUTPUT_DIR, "entropy_comparison.png")
fig3.savefig(path3, dpi=150, bbox_inches="tight")
print(f"✅ Saved: entropy_comparison.png")

plt.close("all")
print("\n✅ All 3 charts generated in outputs/")