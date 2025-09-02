import json
import os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import scipy
def polynomial_fit(x, y, degree):
    """Fit a polynomial of a given degree to x and y data."""
    p = np.polyfit(x, y, degree)
    return np.poly1d(p)

def timestamp_matches(timestamp_str, filter_timestamp):
    """Check if the timestamp matches the filter criteria."""
    timestamp = int(timestamp_str)  # Convert the timestamp to an integer
    ts = datetime.fromtimestamp(timestamp / 1000)  # Convert milliseconds to seconds
    if filter_timestamp.get('year') and ts.year != filter_timestamp['year']:
        return False
    if filter_timestamp.get('month') and ts.month != filter_timestamp['month']:
        return False
    if filter_timestamp.get('day') and ts.day != filter_timestamp['day']:
        return False
    if filter_timestamp.get('hour') and ts.hour != filter_timestamp['hour']:
        return False
    return True

def trend_classification(filter_idDevice=None, filter_vehicle=None, filter_vehicleModel=None, filter_timestamp=None):
    file_path = "Analysis/data/transitori.json"

    # Load the JSON data
    if os.path.exists(file_path):
        with open(file_path, "r") as infile:
            try:
                data = json.load(infile)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Filter the data
    filtered_data = []
    for item in data:
        if filter_idDevice:
            if isinstance(filter_idDevice, list):
                if item['idDevice'] not in filter_idDevice:
                    continue
            else:
                if item['idDevice'] != filter_idDevice:
                    continue
        if filter_vehicle and item['vehicle'] != filter_vehicle:
            continue
        if filter_vehicleModel and item['vehicleData']['name'] != filter_vehicleModel:
            continue
        if filter_timestamp and not timestamp_matches(item['timestamp'], filter_timestamp):
            continue
        filtered_data.append(item)
    
    # Create a dictionary to hold data for each idDevice
    devices_data = {}
    
    # Organize data by idDevice
    for item in filtered_data:
        device_id = item['idDevice']
        if device_id not in devices_data:
            devices_data[device_id] = []
        devices_data[device_id].append(item)

    rho_air = 1.225; # [kg/m^3]
    g = 9.81; # [m/s^2]
    # Process each idDevice separately
    results = {}
    for device_id, items in devices_data.items():
        ds_all = []
        vel_all = []

        # Calculate parameters for each item of the current idDevice
        for item in items:
            vehicle_data = item.get('vehicleData', {})
            massTot = vehicle_data.get('mtot', 30000)  # Default to 30000 kg if not present
            #print('massTot', massTot)
            maxP = vehicle_data.get('maxP', 353000)  # Default to 353000 W if not present
            #print('maxP', maxP)
            refArea = vehicle_data.get('refArea', 9.2)  # Default to 9.2 m^2 if not present
            #print('refArea', refArea)
            Cx = vehicle_data.get('cx', 0.75)  # Default to 0.75 if not present
            #print('Cx', Cx)
            vmean_list = item.get('vmean', [])
            if not vmean_list:  # lista vuota
                continue
            vmean_val = vmean_list[0]
            Crr = vehicle_data.get('cr0', 0.006) + vehicle_data.get('cr1', 0) * vmean_val / 3.6
            #print('Crr', Crr)
            dydx = np.array(item.get('dydx', [0]))
            #print('dydx', dydx)

            vel_media = np.array(item['vmean'])
            #vel_media = vel_media / 3.6
           
            acc_media = np.array(item['acc_media'])
            #print('acc_media', acc_media)
            theta = np.arctan(dydx / 100)
            #print('theta', theta)

            # Fres_b(i) = 0.5 * Cd * rho_air * Af * vel_mediab(i)^2 + Crr * m * g * cos(theta_b(i)) + m * g * sin(theta_b(i)); % N
            Fres = 0.5 * Cx * rho_air * refArea * vel_media**2 + Crr * massTot * g * np.cos(theta) + massTot * g * np.sin(theta) #N
            
            Pres = Fres * vel_media
            
            dvdt = (0.9 * maxP - Pres) / (massTot * vel_media)
            
            ds = acc_media / dvdt
           
            ds = np.clip(ds, 0, 1)
           
            indici = np.where((ds > 0) & (ds < 1))[0]
            #print(indici)
            vel_media = vel_media[indici]
            ds = ds[indici]
            

            # Add calculated parameters to the item
            item['calculated_ds'] = ds.tolist()
            item['calculated_vel_media'] = vel_media.tolist()

            ds_all.extend(ds)
            vel_all.extend(vel_media)

        # Store results for each device_id
        #print('ds_all',ds_all)
        #print(vel_all)
        ds_all = np.array(ds_all)
        vel_all = np.array(vel_all)
        
        vel_min = np.floor(np.min(vel_all))
        vel_max = np.ceil(np.max(vel_all))
        vel_intervals = np.arange(vel_min, vel_max + 1, 1)

        # Initialize vectors for max and min values
        max_ds = np.zeros(len(vel_intervals) - 1)
        min_ds = np.zeros(len(vel_intervals) - 1)

        # Find max and min values for each speed interval
        for i in range(len(vel_intervals) - 1):
            vel_range = (vel_all >= vel_intervals[i]) & (vel_all < vel_intervals[i + 1])
            ds_in_range = ds_all[vel_range]
            if ds_in_range.size > 0:
                max_ds[i] = np.max(ds_in_range)
                min_ds[i] = np.min(ds_in_range)
            else:
                max_ds[i] = np.nan
                min_ds[i] = np.nan

        # Remove NaN values from data
        valid_max = ~np.isnan(max_ds)
        valid_min = ~np.isnan(min_ds)
        vel_intervals_mid = (vel_intervals[:-1] + vel_intervals[1:]) / 2

        # Perform polynomial fitting
        if np.any(valid_max):
            p_max = polynomial_fit(vel_intervals_mid[valid_max], max_ds[valid_max], 3)  # Polynomial of degree 3
        else:
            p_max = None

        if np.any(valid_min):
            p_min = polynomial_fit(vel_intervals_mid[valid_min], min_ds[valid_min], 2)  # Polynomial of degree 2
        else:
            p_min = None

        # Calculate IDS
        if p_max is not None and p_min is not None:
            vel_media = vel_all
            ds = ds_all
            IDS = np.zeros(len(ds))
            for i in range(len(ds)):
                f_min1 = np.polyval(p_min, vel_media[i])
                f_max1 = np.polyval(p_max, vel_media[i])
                if f_min1 > f_max1:
                    f_min1, f_max1 = f_max1, f_min1
                IDS[i] = (ds[i] - f_min1) / (f_max1 - f_min1)
            IDS = np.clip(IDS, 0, 1)
        else:
            IDS = None

        # Store results for each device_id
        results[device_id] = {
            'calculated_ds': ds_all.tolist(),
            'calculated_vel_media': vel_all.tolist(),
            'polynomial_max': p_max,
            'polynomial_min': p_min,
            'IDS': IDS.tolist() if IDS is not None else None
        }

    # Inizializza figure per IDS plot
    plt.figure(figsize=(10, 6))

    # Plot IDS per ciascun device_id
    for device_id, data in results.items():
        IDS = data['IDS']
        vel_media = data['calculated_vel_media']
        
        # Plot IDS sovrapposti
        if IDS is not None:
            plt.plot(vel_media, IDS, '.', markersize=10, label=f'device {device_id}')

    plt.xlabel('v media [m/s]')
    plt.ylabel('IDS')
    plt.ylim([0, 1])
    plt.legend()
    plt.title('Livello di aggressività del conducente rispetto alla velocità')
    plt.show()

    # Inizializza figure per l'istogramma
    plt.figure(figsize=(10, 6))

    # Calcolo e plot dell'istogramma per ciascun device_id
    numBins = 5
    for device_id, data in results.items():
        if device_id == filtered_data[0]['idDevice']:
            IDS = data['IDS']
            if IDS is not None:
                counts, binEdges = np.histogram(IDS, bins=numBins, density=True)
                binCenters = binEdges[:-1] + np.diff(binEdges) / 2
                #print(binCenters, counts, binEdges)

                # Plot dell'istogramma sovrapposto
                plt.bar(binCenters, counts, width=np.diff(binEdges), alpha=0.5, label=f'device {device_id}')

            plt.xlabel('IDS')
            plt.ylabel('Probability')
            plt.title('Istogramma IDS per tutti i device')
            plt.legend()
            plt.show()
        
    return results