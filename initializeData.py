#@Baptiste Menetrier
"""
Initialize buffer files used to temporaly store data logged by the buyo and remove files from previous acquisition. 
Warning: this function deletes all log files and should then used carefully. 
"""

import os

root = '/home/pi/BuyoData'
listFolder = ['NMEA', 'UBX', 'METEO', 'RINEX']

for folder in listFolder:
    os.system(f"rm {root}/{folder}/log{folder}*")
    if folder == 'UBX':
        extension = '.ubx'
    else:
        extension = '.txt'
    os.system(f"touch {root}/{folder}/log{folder}{extension}")
