
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings("ignore")

# === Step 0: Caricamento dataset ===
dataset_path = os.path.join("dataset_finale", "dataset_profilato_old.csv")
if not os.path.exists(dataset_path):
    print(f"❌ File non trovato: {dataset_path}")
    exit()

df = pd.read_csv(dataset_path)

# === Step 1: Selezione colonne numeriche ===
numeric_df = df.select_dtypes(include=["float64", "int64"]).dropna(axis=1)

# === Step 2: Calcolo correlazioni con IDS ===
correlations = []
for col in numeric_df.columns:
    if col == "IDS":
        continue
    r, p = pearsonr(df["IDS"], df[col])
    if p < 0.05:
        correlations.append((col, r, p))

if len(correlations) < 2:
    print("⚠️ Non abbastanza variabili significativamente correlate con IDS.")
    exit()

# === Step 3: Costruzione combinazione pesata ===
correlations.sort(key=lambda x: abs(x[1]), reverse=True)
print("\n✅ Variabili selezionate per combinazione pesata con i relativi pesi (basati su Pearson r):")
total_abs_corr = sum(abs(r) for _, r, _ in correlations)
weights = {}
for col, r, _ in correlations:
    w = abs(r) / total_abs_corr
    weights[col] = w
    print(f"{col:<25} peso = {w:.3f}")

# === Step 4: Calcolo nuova variabile combinata pesata ===
df["combinazione_pesata"] = sum(df[col] * w for col, w in weights.items())

# === Step 5: Scatterplot combinazione_pesata vs IDS ===
if "stile_guida" in df.columns:
    palette = {"calmo": "green", "medio": "blue", "aggressivo": "red"}
else:
    palette = None

plt.figure(figsize=(9, 6))
sns.scatterplot(data=df, x="combinazione_pesata", y="IDS", hue="stile_guida", palette=palette, s=80, edgecolor="black")
plt.title("Scatter: Combinazione pesata delle feature vs IDS")
plt.xlabel("Combinazione pesata")
plt.ylabel("IDS")
plt.grid(True)
plt.tight_layout()
plt.show()
