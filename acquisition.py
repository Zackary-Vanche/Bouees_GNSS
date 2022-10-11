import os
import time
import shutil
from datetime import datetime
# time.sleep(120) # ? 
#print(os.getcwd())

# Path definition
root = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Projet Guerledan\testPy'
pathAcquisition = f'{root}/acquisition'
# pathAcquisition = f'{root}\\acquisition' # Windows


T_NMEA = 10 # Save NMEA every 10 min

# Remove former folder 'acquisition'
os.system(f'rm -r {pathAcquisition}')

# Create new folder 'acquisition'
os.system(f'mkdir {pathAcquisition}')


# while True:
now = datetime.now()
current_min = now.minute
current_sec = now.second

pathfolderHour = f'{pathAcquisition}/{now.strftime("%d%m%Y_%H00")}'
# pathfolderHour = f'{pathAcquisition}\{now.strftime("%d%m%Y_%H00")}'

if ~os.path.exists(pathfolderHour):
    os.system(f'mkdir {pathfolderHour}')

filename = now.strftime("%d%m%Y_%H00")
outputFilePath_RAW = f'{pathfolderHour}/{filename}_RAW.txt'
outputFilePath_NMEA = f'{pathfolderHour}/{filename}_NMEA.txt'

# outputFilePath_RAW = f'{pathfolderHour}\{filename}_RAW.txt'
# outputFilePath_NMEA = f'{pathfolderHour}\{filename}_NMEA.txt'

cmdRAW =  f'gpspipe -o {outputFilePath_RAW} -R'
cmdNMEA =  f'gpspipe -o {outputFilePath_NMEA} -r'

# Save RAW
# os.system(cmdRAW)
print(cmdRAW)

# Save NMEA 
if (current_min%T_NMEA == 0) & (current_sec == 0):
    # os.system(cmdNMEA)
    print(cmdNMEA)

    

 
