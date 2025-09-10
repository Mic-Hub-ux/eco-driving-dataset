
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')

from trend_extraction import trend_extraction
from trend_classification import trend_classification

import contextlib
import sys

# === Configurazione ===
input_dir = "input_dataset"
output_dir = "dataset_finale"
output_path = os.path.join(output_dir, "dataset_profilato.csv")
os.makedirs(output_dir, exist_ok=True)

# === Carica dataset esistente se presente ===
if os.path.exists(output_path):
    df_totale = pd.read_csv(output_path)
else:
    df_totale = pd.DataFrame()

# === Elabora tutti i file in input_dataset/ ===
for file in sorted(os.listdir(input_dir)):
    if not file.endswith(".csv"):
        continue

    input_path = os.path.join(input_dir, file)
    try:
        df = pd.read_csv(input_path)


        # STEP 2: Profilo
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
            "tempo_con_freno": (df["brakePressure"] > 0).sum(),
            "mean_rpm": df["rpm"].mean(),
            "std_rpm": df["rpm"].std(),
            "gear_changes": conta_cambi(df["gear"]),
            "mean_fuelRate": df["fuelRate"].mean(),
            "max_fuelRate": df["fuelRate"].max(),
            "distance_traveled": df["odometer"].max() - df["odometer"].min(),
            "duration_sec": df["timestamp"].max() - df["timestamp"].min()
        }

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

        with open(os.devnull, "w") as fnull:
            with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                trend_extraction("100016", "truck", timestamp, vehicleData, real_dict)
                results = trend_classification()

        ids_lista = []
        for dev in results.values():
            ids_lista.extend(dev.get("IDS", []))

        ids_media = np.mean(ids_lista) if ids_lista else np.nan
        profilo["IDS"] = ids_media

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

        df_riga = pd.DataFrame([profilo]).round(3)
        df_totale = pd.concat([df_totale, df_riga], ignore_index=True)
        print(f"✅ Aggiunto: {file}")

    except Exception as e:
        print(f"⚠️ Errore con il file {file}: {e}")

df_totale.to_csv(output_path, index=False)
print("\n✅ Dataset finale aggiornato:", output_path)
