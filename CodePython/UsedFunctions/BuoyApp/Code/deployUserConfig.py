#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Menetrier Baptiste
# Created Date: 04/03/2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""
Deploy user configuration on RPi. This script is intended to be excecuted by 
a dedicated cron task at RPi reboot.
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from buoy import * 

FLAG_DEPLOYED = '/boot/userConfigIsDeployed.txt'
def main():
    # Change permission 
    cmd =  f'sudo chmod +rw {FLAG_DEPLOYED}'
    os.system(cmd) 

    with open(FLAG_DEPLOYED, 'r') as f:
        configIsDeployed = int(f.read())    # Get status 

    with open(FLAG_DEPLOYED, 'w') as f:
        if not configIsDeployed:    # Update config
            buoy = Buoy(parent='RPI')
            buoy.updateConfig()
            f.write('1')
            # Reboot with new config
            os.system('sudo reboot')
        else:
            f.write('1')    

if __name__ == '__main__':
    main()
