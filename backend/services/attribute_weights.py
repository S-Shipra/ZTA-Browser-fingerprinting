import pandas as pd
import os

# ── Path to entropy_results.csv ───────────────────────────────────────────────
# Place entropy_results.csv inside backend/services/
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
ENTROPY_CSV  = os.path.join(BASE_DIR, "entropy_results.csv")

# ── Entropy thresholds (based on paper's Table VII) ───────────────────────────
HIGH_ENTROPY   = 5.0   # risk += 40 if changed
MEDIUM_ENTROPY = 2.0   # risk += 20 if changed
                       # below 2.0 → risk += 5 (low, nearly ignore)

# ── Map entropy value to risk weight ─────────────────────────────────────────
def entropy_to_weight(entropy_value):
    if entropy_value >= HIGH_ENTROPY:
        return 40      # high uniqueness → big risk if changed
    elif entropy_value >= MEDIUM_ENTROPY:
        return 20      # medium uniqueness → moderate risk
    else:
        return 5       # low uniqueness → nearly ignore

# ── Load all attribute weights from entropy_results.csv ──────────────────────
def load_attribute_weights():
    """
    Returns a dict:
    {
      "Screen_Inner":         40,
      "Canvas_GetImageData":  40,
      "Header_Connection":    40,
      "Device_Gamepads":       5,
      "Device_VR":             5,
      ...
    }
    """
    if not os.path.exists(ENTROPY_CSV):
        print("⚠️  entropy_results.csv not found — using default weights")
        return _default_weights()

    df = pd.read_csv(ENTROPY_CSV)
    weights = {}
    for _, row in df.iterrows():
        weights[row["Attribute"]] = entropy_to_weight(row["Entropy"])

    return weights

# ── Get weight for a single attribute ────────────────────────────────────────
def get_weight(attribute_name):
    """
    Returns risk weight for a single attribute name.
    Used by risk_engine.py like:
        w = get_weight("Screen_Inner")  → 40
    """
    weights = load_attribute_weights()
    return weights.get(attribute_name, 10)  # default 10 if not found

# ── Fallback if CSV not found ─────────────────────────────────────────────────
def _default_weights():
    return {
        "screen"   : 40,   # maps to Screen_Inner   (high entropy)
        "platform" : 20,   # medium entropy
        "language" :  5,   # low entropy
    }

# ── Friendly label for display in dashboard ──────────────────────────────────
def get_weight_label(attribute_name):
    w = get_weight(attribute_name)
    if w >= 40:
        return "HIGH"
    elif w >= 20:
        return "MEDIUM"
    else:
        return "LOW"