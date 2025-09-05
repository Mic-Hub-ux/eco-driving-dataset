
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings("ignore")

# === Step 0: Caricamento dataset reale ===
dataset_path = os.path.join("../dataset_finale", "dataset_profilato.csv")
if not os.path.exists(dataset_path):
    print(f"❌ File non trovato: {dataset_path}")
    exit()

df = pd.read_csv(dataset_path)

# === Step 1: Selezione colonne numeriche valide ===
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
numeric_cols = [c for c in numeric_cols if c != "IDS"]

# Escludi colonne costanti o non valide
valid_cols = []
for col in numeric_cols:
    valori = pd.to_numeric(df[col], errors="coerce")
    if valori.nunique() > 1 and not valori.isnull().all():
        valid_cols.append(col)

# === Step 2: Normalizzazione Min-Max ===
df_norm = df.copy()
for col in valid_cols:
    min_val = df[col].min()
    max_val = df[col].max()
    if max_val != min_val:
        df_norm[col] = (df[col] - min_val) / (max_val - min_val)
    else:
        df_norm[col] = 0.0

# === Step 3: Calcolo pesi da |r| ===
correlations = []
for col in valid_cols:
    r, _ = pearsonr(df["IDS"], df[col])
    correlations.append((col, r))

correlations.sort(key=lambda x: abs(x[1]), reverse=True)
total_abs_r = sum(abs(r) for _, r in correlations)
weights = {col: abs(r) / total_abs_r if total_abs_r != 0 else 0 for col, r in correlations}

# === Step 4: Costruzione combinazione pesata ===
df["combinazione_pesata"] = sum(df_norm[col] * weights[col] for col in weights)

# === Step 5: Scatterplot ===
plt.figure(figsize=(9, 6))
palette = {"calmo": "green", "medio": "blue", "aggressivo": "red"} if "stile_guida" in df.columns else None
sns.scatterplot(data=df, x="combinazione_pesata", y="IDS", hue="stile_guida", palette=palette, s=80, edgecolor="black")
plt.title("Scatterplot: Combinazione pesata vs IDS (dataset reale)")
plt.xlabel("Combinazione pesata")
plt.ylabel("IDS")
plt.grid(True)
plt.tight_layout()
plt.show()
