
import os
import pandas as pd

ETICHETTE_PERSONALIZZATE = ['calmo-rispettosoSegnaletica', 'calmo-ma-troppoLento', 'medio-nonRispettaLimiti', 'aggressivo-rispettosoStop', 'aggressivo-nonRispettaStop', 'aggressivo-improvvisiFreni', 'medio-rispettoso', 'calmo-ma-scarsoControllo', 'medio-imprevedibile']

def scegli_etichetta():
    print("Scegli un'etichetta personalizzata per questa guida:")
    for i, etichetta in enumerate(ETICHETTE_PERSONALIZZATE):
        print(f"  [{i}] {etichetta}")
    while True:
        scelta = input("Inserisci il numero corrispondente: ")
        if scelta.isdigit() and 0 <= int(scelta) < len(ETICHETTE_PERSONALIZZATE):
            return ETICHETTE_PERSONALIZZATE[int(scelta)]
        else:
            print("Scelta non valida. Riprova.")

# === Step 1: Carica il file CSV ===
nome_file = input("Nome del file CSV da elaborare: ").strip()
input_path = os.path.join("..", "input_dataset", nome_file)

if not os.path.exists(input_path):
    print(f" File non trovato: {input_path}")
    exit()

df = pd.read_csv(input_path)

# === Step 2: Calcolo delle feature base ===
profilo = {
    "mean_speed": df["speed"].mean(),
    "std_speed": df["speed"].std(),
    "max_speed": df["speed"].max(),
    "mean_accelerator": df["accelerator"].mean(),
    "std_accelerator": df["accelerator"].std(),
    "max_accelerator": df["accelerator"].max(),
    "mean_brake": df["brakePressure"].mean(),
    "max_brake": df["brakePressure"].max(),
    "breake_time": (df["brakeSwitch"] > 0).sum(),
    "mean_rpm": df["rpm"].mean(),
    "std_rpm": df["rpm"].std(),
    "gear_changes": df["gear"].diff().fillna(0).astype(bool).sum(),
    "mean_fuelRate": df["fuelRate"].mean(),
    "max_fuelRate": df["fuelRate"].max(),
    "distance_traveled": df["distanceTraveled"].iloc[-1] if "distanceTraveled" in df.columns else None,
    "duration_sec": len(df),
    "stile_guida": scegli_etichetta()
}

# === Step 3: Scrittura su dataset finale ===
output_path = os.path.join("..", "output_dataset", "dataset_profilato_personalizzato.csv")

df_output = pd.DataFrame([profilo])
if os.path.exists(output_path):
    df_esistente = pd.read_csv(output_path)
    df_finale = pd.concat([df_esistente, df_output], ignore_index=True)
else:
    df_finale = df_output

df_finale.to_csv(output_path, index=False)
print("Profilo guida salvato in:", output_path)
