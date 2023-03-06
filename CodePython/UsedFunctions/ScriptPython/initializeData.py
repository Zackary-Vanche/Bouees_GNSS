#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Menetrier Baptiste
# Created Date: 04/03/2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""
Initialize buffer files used to temporaly store data logged by the buoy 
and remove files from previous acquisition. Warning: this function deletes 
all log files and should then be used carefully. 
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
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
    os.system(f"chmod 666 {root}/{folder}/log{folder}{extension}")