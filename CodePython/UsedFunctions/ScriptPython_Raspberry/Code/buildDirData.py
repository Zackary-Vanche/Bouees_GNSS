#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Menetrier Baptiste
# Created Date: 04/03/2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""
Build directories used to store data logged by the buoy. 
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import os

root = '/home/pi/BuoyData'
os.system(f"mkdir {root}")

listFolder = ['NMEA', 'UBX', 'METEO', 'RINEX']

for folder in listFolder:
    os.system(f"mkdir {root}/{folder}")
