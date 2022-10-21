import numpy 
import pandas as pd 
import matplotlib.pyplot as plt


colNames = ['Time','T', 'H', 'P']

fileSeiche = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\StationMeteo\WEATHER_2022_10_13_soir.csv'
dataSeiche = pd.read_csv(fileSeiche, header=9, usecols=[0, 1, 2, 6], names=colNames)

colNames = ['Time','T', 'P', 'H']
fileBouee = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\BoueeV2\13102022_14102022\METEO\logMETEO.txt-2022101317'
dataBouee = pd.read_csv(fileBouee, header=1, names=colNames)

# Température
plt.figure()
plt.plot(dataSeiche['Time'], dataSeiche['T'], label="Station météo")
plt.plot(dataBouee['Time'], dataBouee['T'], label="Capteur BME280")
plt.title("Evaluation des performances du capteurs météo")
plt.ylabel('Temperature [°C]')
plt.xlabel('Date')
plt.legend()

# Humidité  
plt.figure()
plt.plot(dataSeiche['Time'], dataSeiche['H'], label="Station météo")
plt.plot(dataBouee['Time'], dataBouee['H'], label="Capteur BME280")
plt.title("Evaluation des performances du capteurs météo")
plt.ylabel('Humidity [%]')
plt.xlabel('Date')
plt.legend()

# Pression
plt.figure()
plt.plot(dataSeiche['Time'], dataSeiche['P'], label="Station météo")
plt.plot(dataBouee['Time'], dataBouee['P'], label="Capteur BME280")
plt.title("Evaluation des performances du capteurs météo")
plt.ylabel('Pressure [hPa]')
plt.xlabel('Date')
plt.legend()


plt.show()