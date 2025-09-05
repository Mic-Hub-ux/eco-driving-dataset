
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Disattiva output grafico

from trend_extraction import trend_extraction
from trend_classification import trend_classification

# === STEP 1: Caricamento file ===
input_name = input("Nome file guida da analizzare:").strip()
input_path = os.path.join("../input_dataset", input_name)
if not os.path.exists(input_path):
    print(f" File non trovato: {input_path}")
    exit()

df = pd.read_csv(input_path)

# === STEP 2: Estrazione statistiche descrittive ===
def conta_cambi(colonna):
    return (colonna.diff() != 0).sum()

profilo = {
    "mean_speed": df["speed"].mean(),
    "std_speed": df["speed"].std(),
    "max_speed": df["speed"].max(),

    "mean_accelerator": df["accelerator"].mean(),
    "std_accelerator": df["accelerator"].std(),
    "max_accelerator": df["accelerator"].max(),

    "mean_brake": df["brakePressure"].mean(),
    "max_brake": df["brakePressure"].max(),
    "breake_time": (df["brakePressure"] > 0).sum(),

    "mean_rpm": df["rpm"].mean(),
    "std_rpm": df["rpm"].std(),

    "gear_changes": conta_cambi(df["gear"]),

    "mean_fuelRate": df["fuelRate"].mean(),
    "max_fuelRate": df["fuelRate"].max(),

    "distance_traveled": df["odometer"].max() - df["odometer"].min(),
    "duration_sec": df["timestamp"].max() - df["timestamp"].min()
}

# === STEP 3: Calcolo IDS medio sui transitori ===
real_dict = {
    "Trip_Distance_High_Resolution": df["distanceTraveled"].astype(str).tolist(),
    "Tachograph_vehicle_speed": df["speed"].astype(str).tolist(),
    "Time": df["timestamp"].astype(str).tolist(),
    "gnss_Altitude": df["altitude"].astype(str).tolist(),
    "gnss_Latitude": df["lat"].astype(str).tolist(),
    "gnss_Longitude": df["lng"].astype(str).tolist()
}

vehicleData = {
    'name': 'ford',
    'mtot': 15954,
    'unladenMass': 15729,
    'payload': 225,
    'vmax': 90,
    'cr0': 0.006,
    'cr1': 2.9808e-06,
    'cx': 1,
    'refArea': 5.3,
    'fMapCoeff': [[1.15417804e+07, 1.22724270e+04, 5.86859277e+04],
                  [-5.88340912e+01, 2.03735928e+01, 1.98408506e+00],
                  [2.74425090e+01, 2.16634905e+01, 1.05266995e+00]]
}
timestamp = int(float(df["timestamp"].iloc[0]))

# Suppress output from trend_extraction and trend_classification
import sys
import contextlib

with open(os.devnull, "w") as fnull:
    with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
        trend_extraction("100016", "truck", timestamp, vehicleData, real_dict)
        results = trend_classification()

ids_lista = []
for dev in results.values():
    ids_lista.extend(dev.get("IDS", []))

ids_media = np.mean(ids_lista) if ids_lista else np.nan
profilo["IDS"] = ids_media

# === STEP 4: Assegna etichetta ===
def etichetta(ids):
    if pd.isna(ids):
        return "sconosciuto"
    elif ids < 0.3:
        return "calmo"
    elif ids < 0.7:
        return "medio"
    else:
        return "aggressivo"

profilo["stile_guida"] = etichetta(ids_media)

# === STEP 5: Salvataggio nel dataset cumulativo ===
output_dir = "../dataset_finale"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "dataset_profilato.csv")
df_profilo = pd.DataFrame([profilo])

if os.path.exists(output_path):
    df_cumulativo = pd.read_csv(output_path)
    df_profilo = df_profilo.round(3)  # Arrotonda a 3 decimali
    df_cumulativo = pd.concat([
        df_cumulativo,
        df_profilo
    ], ignore_index=True)
else:
    df_cumulativo = df_profilo

df_cumulativo.to_csv(output_path, index=False)
print("\nProfilo aggiunto a ../dataset_finale/dataset_profilato.csv")
print(df_profilo.T)
