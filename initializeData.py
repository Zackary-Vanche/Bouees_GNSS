import os

root = '/home/pi/data'
listFolder = ['NMEA', 'UBX', 'METEO', 'RINEX']

for folder in listFolder:
    os.system(f"rm {root}/{folder}/log{folder}*")
    if folder == 'UBX':
        extension = '.ubx'
    else:
        extension = '.txt'
    os.system(f"touch {root}/{folder}/log{folder}{extension}")
