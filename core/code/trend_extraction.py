import numpy as np
from json import JSONEncoder
import json
import os

import scipy

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        return obj.tolist() if isinstance(obj, np.ndarray) else super().default(obj)
    
import numpy as np

def findIndices(acceleration, dealt):
    """
    Trova e isola gli indici positivi consecutivi nel vettore di dati
    Input:
        - acceleration: accelerazione
        - dealt: dealt
    Output:
        - consecutive_indices: lista contenente gli indici positivi consecutivi trovati
    """
    
    # Trovare gli indici che soddisfano entrambe le condizioni
    positive_indices = np.where((acceleration > 0) & (dealt >= -0.5))[0]
    
    # Inizializza una lista per memorizzare gli indici positivi consecutivi
    consecutive_indices = []
    consecutive_lengths = []
    
    # Controlla se ci sono almeno 20 indici consecutivi
    if len(positive_indices) >= 20:
        start_index = 0
        consecutive_count = 1
        for i in range(1, len(positive_indices)):
            # Verifica se l'indice corrente è consecutivo rispetto all'indice precedente
            if positive_indices[i] == positive_indices[i - 1] + 1:
                consecutive_count = consecutive_count + 1
            else:
                # Se non è consecutivo, controlla se ci sono almeno 20 indici consecutivi
                if consecutive_count >= 20:
                    # Aggiungi gli indici consecutivi alla lista
                    consecutive_indices.append(positive_indices[start_index:i])
                    # Aggiungi la lunghezza della sequenza alla lista
                    consecutive_lengths.append(consecutive_count)
                # Resetta il conteggio per iniziare una nuova sequenza
                start_index = i
                consecutive_count = 1
        # Controllo finale per l'ultima sequenza
        if consecutive_count >= 20:
            consecutive_indices.append(positive_indices[start_index:])
            consecutive_lengths.append(consecutive_count)
    
    return consecutive_indices

def trend_extraction(idDevice, vehicle, timestamp, vehicleData, real_dict):
    # real_dict['distanceTraveled'] = real_dict["Trip_Distance_High_Resolution"]
    # real_dict['speed']=real_dict["Tachograph_vehicle_speed"]
    # real_dict["time"]=real_dict["Time"]
    # real_dict["altitude"]=real_dict["gnss_Altitude"]
    # real_dict["lng"]=real_dict["gnss_Longitude"]
    # real_dict["lat"]=real_dict["gnss_Latitude"]
    
    # Estrai i dati dal dizionario e converti in array di tipo float
    space = np.array(real_dict["Trip_Distance_High_Resolution"], dtype=float)
    speed = np.array(real_dict["Tachograph_vehicle_speed"], dtype=float)
    time = np.array(real_dict["Time"], dtype=float)
    alt = np.array(real_dict["gnss_Altitude"], dtype=float)
    lng = np.array(real_dict["gnss_Longitude"], dtype=float)
    lat = np.array(real_dict["gnss_Latitude"], dtype=float)

    # Trova gli elementi univoci e gli indici
    val, elem_univoc = np.unique(space, return_index=True)
    sorted_indices = np.sort(elem_univoc)

    # Assicurati che sorted_indices sia di tipo int
    sorted_indices = sorted_indices.astype(int)

    # Ordina gli array basati sugli indici univoci
    space = val.astype(float)
    speed = speed[sorted_indices]
    alt = alt[sorted_indices]
    lat = lat[sorted_indices]
    lng = lng[sorted_indices]

    # Calcolo della media mobile
    window_size = 10

    # Assicurati che 'speed' sia di tipo float
    speed = np.asarray(speed, dtype=float)
    

    # Usa np.convolve per calcolare la media mobile
    speed = np.convolve(speed, np.ones(window_size, dtype=float), mode='valid') / window_size
    
    
    alt = np.convolve(alt, np.ones(window_size)/window_size, mode='valid')/window_size
    
    # Per mantenere la lunghezza originale di alt e speed
    speed = np.concatenate((np.full(window_size - 1, np.nan), speed))
    alt = np.concatenate((np.full(window_size - 1, np.nan), alt))
    
    # Calcolo dell'accelerazione e della dealt
    acceleration = np.diff(speed)
    dealt = np.diff(alt)
    # Aggiungi l'ultimo elemento per mantenere la stessa lunghezza
    #dealt = np.append(dealt, dealt[-1])
    
    consecutive_indices=findIndices(acceleration, dealt)
    
    ## Transitori apprezzabili
    # Inizializza le liste di output come vuote
    distance_transitori = []
    speed_transitori = []
    alt_transitori = []
    lat_transitori = []
    lng_transitori = []
    tempo_transitori = []

    # Itera attraverso la lista di indici
    for indices in consecutive_indices:
        # Estrai gli indici attuali
        indici = indices
        
        # Estrai le parti dei vettori usando gli indici
        estrattoDistance = space[indici]
        estrattoSpeed = speed[indici]
        estrattoAltitudine = alt[indici]
        estrattoLatitudine = lat[indici]
        estrattoLongitudine = lng[indici]
        estrattoTempo = time[indici]

        # Calcola la differenza tra il primo e l'ultimo elemento del vettore estratto
        differenza = estrattoSpeed[-1] - estrattoSpeed[0]
        
        # Se la differenza è almeno 20, aggiungi i vettori alle liste di output
        if differenza >= 20:
            distance_transitori.append(estrattoDistance)
            speed_transitori.append(estrattoSpeed)
            alt_transitori.append(estrattoAltitudine)
            lat_transitori.append(estrattoLatitudine)
            lng_transitori.append(estrattoLongitudine)
            tempo_transitori.append(estrattoTempo)

    # Calcolo dei valori di accelerazione media e di pendenza media
    # Estrai i valori iniziali e finali di space dai transitori
    space_start = [c[0] for c in distance_transitori]
    space_stop = [c[-1] for c in distance_transitori]

    # Inizializza le liste per i risultati
    start_indices = []
    stop_indices = []
    dydx = []
    vmin = []
    vmax = []
    vmean = []
    dv = []
    dt = []
    acc_media = []
    ds = []

    for space_start_val, space_stop_val in zip(space_start, space_stop):
        # Trova gli indici corrispondenti ai valori di space_start e space_stop
        start_idx = np.where(space == space_start_val)[0][0]
        stop_idx = np.where(space == space_stop_val)[0][0]

        start_indices.append(start_idx)
        stop_indices.append(stop_idx)

        # Estrai i dati del transitorio
        space_tr = space[start_idx:stop_idx + 1]
        speed_tr = speed[start_idx:stop_idx + 1]
        time_tr = time[start_idx:stop_idx + 1]

        # Calcola la pendenza media (dydx)
        alt_start = alt[start_idx]
        alt_stop = alt[stop_idx]
        pendenza = ((alt_stop - alt_start) / (space_stop_val - space_start_val)) * 100
        dydx.append(pendenza)

        # Calcola i valori di velocità minima, massima e media
        vmin_val = speed_tr[0]
        vmax_val = np.max(speed_tr)
        vmean_val = (speed_tr[-1] + speed_tr[0]) / 2
        vmin.append(vmin_val)
        vmax.append(vmax_val)
        vmean.append(vmean_val)

        # Calcola la variazione di velocità e il tempo
        dv_val = (vmax_val - speed_tr[0]) / 3.6
        dt_val = time_tr[-1] - time_tr[0]
        dv.append(dv_val)
        dt.append(dt_val)

        # Calcola l'accelerazione media
        acc_media_val = dv_val / dt_val
        acc_media.append(acc_media_val)

        # Calcola la variazione di spazio
        ds_val = space_tr[-1] - space_tr[0]
        ds.append(ds_val)
        
    output_dict = {
        'timestamp': timestamp,
        'idDevice': idDevice,
        'vehicle': vehicle,
        'vehicleData': vehicleData,
        'lat_transitori': lat_transitori,
        'lng_transitori': lng_transitori,
        'alt_transitori': alt_transitori,
        'distance_transitori': distance_transitori,
        'vmean': vmean,
        'dydx': dydx,
        'acc_media': acc_media,
        'tempo_transitori': tempo_transitori,
        'speed_transitori': speed_transitori,
        'vmin': vmin,
        'vmax': vmax
    }
    # Path to the JSON file
    file_path = "Analysis/data/transitori.json"
    data=[output_dict]
    # Write the updated data back to the file
    with open(file_path, "w") as outfile:
        json.dump(data, outfile, cls=NumpyArrayEncoder, indent=4)
    
    return output_dict