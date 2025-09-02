
import os
import pandas as pd

# === Step 1: Carica il file CSV ===
nome_file = input("Nome del file CSV da elaborare (es: guida_mario.csv): ").strip()
nome_base = os.path.splitext(nome_file)[0]
input_path = os.path.join("..", "input", nome_file)

if not os.path.exists(input_path):
    print(f"File non trovato: {input_path}")
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
    "brake_time": (df["brakeSwitch"] > 0).sum(),
    "mean_rpm": df["rpm"].mean(),
    "std_rpm": df["rpm"].std(),
    "gear_changes": df["gear"].diff().fillna(0).astype(bool).sum(),
    "mean_fuelRate": df["fuelRate"].mean(),
    "max_fuelRate": df["fuelRate"].max(),
    "distance_traveled": df["distanceTraveled"].iloc[-1] if "distanceTraveled" in df.columns else None,
    "duration_sec": len(df)
}

# === Step 3: Scrittura su singolo CSV ===
output_path = os.path.join("..", "output", f"{nome_base}_profilato.csv")
df_output = pd.DataFrame([profilo])
df_output.to_csv(output_path, index=False)

print("Profilo guida salvato in:", output_path)
