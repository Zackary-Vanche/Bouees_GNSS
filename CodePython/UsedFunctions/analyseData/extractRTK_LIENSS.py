import numpy as np 
import pandas as pd
from datetime import datetime, timedelta

FILE_RGF93 = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\bouee_lienss\Map-data-2023-02-09 12_13_12.csv"
FILE_RGF93_CLEAN = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\bouee_lienss\Map-data-2023-02-09 12_13_12_clean.csv"
data_RGF93 = pd.read_csv(FILE_RGF93)

# data_clean = pd.DataFrame({'lati': [float(lat[:-2]) for lat in data.lati],
#                            'longi': [float(lon[:-2]) for lon in data.longi],
#                            'height': [float(h[:-2]) for h in data.height]})

data_clean = pd.DataFrame({'lati': data_RGF93.lati,
                           'longi': data_RGF93.longi,
                           'height':data_RGF93.height})

data_clean.to_csv(FILE_RGF93_CLEAN, index=False)


# Insert back time 
FILE_LIENSS_RTK_ITRF14 = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\bouee_lienss\Map-data-2023-02-09 12_13_12_ITRF14.csv"
FILE_LIENSS_RTK_ITRF14_TIME = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\bouee_lienss\Time-Map-data-2023-02-09 12_13_12_ITRF14.csv"

buoy = pd.read_csv(FILE_RGF93, sep=',')

# Transform time in "readable" format
init_time = datetime(1970, 1, 1, 1, 0)
index_time = pd.DatetimeIndex([init_time + timedelta(milliseconds=t) for t in buoy['time']])
buoy_time = buoy.set_index(index_time)[['metric','lati','longi','height']]

data = pd.read_csv(FILE_LIENSS_RTK_ITRF14, delimiter=',', names=['Latitude', 'Longitude', 'Height'], usecols=[0, 1, 2])
data['time'] = buoy_time.index
data['metric'] = buoy['metric']
data.to_csv(FILE_LIENSS_RTK_ITRF14_TIME, index=False)
