import numpy as np 
from datetime import datetime
import time

PATH_METEO = r'/home/pi/data/METEO/logMETEO.txt'
# PATH_METEO = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\testsimu_meteo.txt'

def simulate_METEO():

    T0 = 21
    P0 = 1014
    H0 = 50
    while True:
        with open(PATH_METEO, 'a') as f:
            now = datetime.now() # current date and time
            date_str = now.strftime("%d%M%Y %H:%M:%S")
            temperature = T0 + np.random.random()
            pressure = P0 + np.random.random()
            humidity = H0 + np.random.random()
            line = f'{date_str}, {temperature}, {pressure}, {humidity}\n'
            
            f.writelines(line)
        time.sleep(10)
            
if __name__ == '__main__':
    simulate_METEO()
