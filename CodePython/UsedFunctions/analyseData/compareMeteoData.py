import numpy 
import pandas as pd 
import matplotlib.pyplot as plt
import datetime

delta_utc = datetime.timedelta(hours=2)
colNames = ['Time','T', 'H', 'P']

fileSeiche = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\StationMeteo\WEATHER_2022_10_13_soir.csv'
fileSeiche = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\calibration_capteur_meteo_static_06022023_07022023\WEATHER_2302492_2023-02-07_16_27_10.csv'

dataSeiche = pd.read_csv(fileSeiche, header=9, usecols=[0, 1, 3, 6], names=colNames)
dataSeiche['Time'] = pd.to_datetime(dataSeiche['Time'])
dataSeiche['Time'] += delta_utc

colNames = ['Time','T', 'P', 'H']
fileBouee = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\calibration_capteur_meteo_static_06022023_07022023\logMETEO.txt'
dataBouee = pd.read_csv(fileBouee, header=1, names=colNames)
dataBouee['Time'] = pd.to_datetime(dataBouee['Time'])
tstart = datetime.datetime(year=2023, month=2, day=6)
dataBouee = dataBouee[dataBouee['Time'] > tstart]

# Température
plt.figure()
plt.plot(dataSeiche['Time'], dataSeiche['T'], label="Station météo")
plt.plot(dataBouee['Time'], dataBouee['T'], label="Capteur BME280")
plt.title("Evaluation des performances du capteurs météo")
plt.ylabel('Temperature [°C]')
plt.xlabel('Date')
plt.legend()
plt.xticks(rotation=20)
plt.tight_layout()

# # Humidité  
plt.figure()
plt.plot(dataSeiche['Time'], dataSeiche['H'], label="Station météo")
plt.plot(dataBouee['Time'], dataBouee['H'], label="Capteur BME280")
plt.title("Evaluation des performances du capteurs météo")
plt.ylabel('Humidity [%]')
plt.xlabel('Date')
plt.legend()
plt.xticks(rotation=20)
plt.tight_layout()

# # Pression
pressure_offset = 2
plt.figure()
plt.plot(dataSeiche['Time'], dataSeiche['P'], label="Station météo")
plt.plot(dataBouee['Time'], dataBouee['P'], label="Capteur BME280")
plt.title("Evaluation des performances du capteurs météo")
plt.ylabel('Pressure [hPa]')
plt.xlabel('Date')
plt.legend()
plt.xticks(rotation=20)
plt.tight_layout()

plt.show()