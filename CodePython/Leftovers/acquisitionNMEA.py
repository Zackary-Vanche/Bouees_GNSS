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
    # if pathFolderHour != previousPathFolderHour:
    #     createFolderHour = True

    # if createFolderHour:
    os.system(f'mkdir {pathFolderHour}')
    # createFolderHour = False

    filename = now.strftime("%d%m%Y_%H00")
    outputFilePath_NMEA = f'{pathFolderHour}/{filename}_NMEA.txt'

    cmdNMEA =  f'gpspipe -o {outputFilePath_NMEA} -r'

    # Save NMEA 
    # if (current_min%t_NMEA == 0) & (current_sec == 0):
    os.system(cmdNMEA)


if __name__ == '__main__':
    main()    

 
