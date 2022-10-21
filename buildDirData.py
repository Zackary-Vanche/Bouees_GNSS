#@Baptiste Menetrier
"""
Build directories used to store data logged by the buyo. 
"""

import os

root = '/home/pi/BuyoData'
os.system(f"mkdir {root}")

listFolder = ['NMEA', 'UBX', 'METEO', 'RINEX']

for folder in listFolder:
    os.system(f"mkdir {root}/{folder}")
