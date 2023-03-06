import os
import time
import shutil
from datetime import datetime

# time.sleep(120) # Wait for synchronisation 

def main():
    # Path definition
    root = r'.'
    pathData = f'{root}/data/NMEA'

    # Remove former folder 'acquisition'
    os.system(f'rm -r {pathData}')

    # Create new folder 'acquisition'
    os.system(f'mkdir {pathData}')

    # createFolderHour = True 
    pathFolderHour = ''

    # while True:
    # previousPathFolderHour = pathFolderHour
    now = datetime.now()

    pathFolderHour = f'{pathData}/{now.strftime("%d%m%Y_%H00")}'
        # createFolderHour = False

    filename = now.strftime("%d%m%Y_%H00")
    outputFilePath_RINEX = f'{pathFolderHour}/{filename}_RINEX.txt'

    cmdRINEX =  f'gpsrinex -f {outputFilePath_RINEX}'

    # Save RINEX 
    os.system(cmdRINEX)

    
if __name__ == "__main__":
    main()


 
