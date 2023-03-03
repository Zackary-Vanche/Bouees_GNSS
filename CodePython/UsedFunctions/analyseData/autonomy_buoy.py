import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt

# data = np.loadtxt(r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\CONFIG\conso_buoy.txt', skiprows=1)
data = pd.read_csv(r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\CONFIG\RaspberryPi_conso.csv', header=1, delimiter=';',
                   names=['time', 'conso', 'wifi_status'])

data.time = pd.to_datetime(data.time)

plt.subplot(211)
plt.plot(data.time, data.conso)
plt.xticks([])
plt.ylabel('Consomation [mA]')
# plt.title('Consomation éléctrique')

plt.subplot(212)
plt.plot(data.time, data.wifi_status, marker='+')
plt.xlabel('Temps')
plt.ylabel('Statut wifi')

plt.suptitle('Evolution de la consomation éléctrique de la bouée')
plt.tight_layout()
plt.savefig(r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Rapport\conso_buoy.png')