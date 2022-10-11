import os
import time
import shutil
from datetime import datetime

time.sleep(120) # Wait for synchronisation 


# Path definition
# root = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\testPy' # Test sous windows 
root = r'.'

pathData = f'{root}/data'
# pathData = f'{root}\\data' # Test sous windows 

T_NMEA = 10 # Save NMEA every 10 min

# Remove former folder 'acquisition'
os.system(f'rm -r {pathData}')

# Create new folder 'acquisition'
os.system(f'mkdir {pathData}')


while True:
    now = datetime.now()
    current_min = now.minute
    current_sec = now.second

    pathfolderHour = f'{pathData}/{now.strftime("%d%m%Y_%H00")}'
    # pathfolderHour = f'{pathData}\{now.strftime("%d%m%Y_%H00")}' # Test sous windows 

    if ~os.path.exists(pathfolderHour):
        os.system(f'mkdir {pathfolderHour}')

    filename = now.strftime("%d%m%Y_%H00")
    outputFilePath_RAW = f'{pathfolderHour}/{filename}_RAW.ubx'
    outputFilePath_NMEA = f'{pathfolderHour}/{filename}_NMEA.txt'

    # outputFilePath_RAW = f'{pathfolderHour}\{filename}_RAW.ubx' # Test sous windows 
    # outputFilePath_NMEA = f'{pathfolderHour}\{filename}_NMEA.txt' # Test sous windows 

    # cmdRAW =  f'gpspipe -o {outputFilePath_RAW} -R'
    cmdRINEX =  f'gpsrinex -f {outputFilePath_RAW}'

    cmdNMEA =  f'gpspipe -o {outputFilePath_NMEA} -r'

    # # Save RAW
    # os.system(cmdRAW)
    # os.system(f'echo.>{outputFilePath_RAW}')
    # print(cmdRAW)

    # Save RINEX 
    os.system(cmdRINEX)

    # Save NMEA 
    if (current_min%T_NMEA == 0) & (current_sec == 0):
        os.system(cmdNMEA)
        # os.system(f'echo.>{outputFilePath_NMEA}')
        # print(cmdNMEA)

    

 
