import numpy 
import pandas as pd 
import matplotlib.pyplot as plt
import importMeteo as Im
import importStation as Is


colNames = ['Time','T', 'H', 'P']


dataSeiche = Is.create_log_station()
dataSeiche.sort_values(by="Time", inplace=True)

dataBouee = Im.create_log_meteo()
dataBouee.sort_values(by="Time", inplace=True)


# Température
plt.figure()
plt.plot(dataSeiche['Time'], dataSeiche['T'], label="Station météo")
plt.plot(dataBouee['Time'], dataBouee['T'], label="Capteur BME280")
plt.title("Evaluation des performances du capteurs météo")
plt.ylabel('Temperature [°C]')
plt.xlabel('Date')
plt.xticks(rotation=25)
plt.xlim()
plt.legend()

# Humidité  
plt.figure()
plt.plot(dataSeiche['Time'], dataSeiche['H'], label="Station météo")
plt.plot(dataBouee['Time'], dataBouee['H'], label="Capteur BME280")
plt.title("Evaluation des performances du capteurs météo")
plt.ylabel('Humidity [%]')
plt.xlabel('Date')
plt.xticks(rotation=25)
print(plt.gca().get_xlim())
plt.legend()

# Pression
plt.figure()
plt.plot(dataSeiche['Time'], dataSeiche['P'], label="Station météo")
plt.plot(dataBouee['Time'], dataBouee['P'], label="Capteur BME280")
plt.title("Evaluation des performances du capteurs météo")
plt.ylabel('Pressure [hPa]')
plt.xlabel('Date')
plt.xticks(rotation=25)
plt.legend()
plt.show()