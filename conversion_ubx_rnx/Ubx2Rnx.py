#!/usr/bin/env python3

import sys
import os

import numpy as np
import glob as glb

def Ubx2Rnx(pubx, # ubx directory
            obs_directory, # rnx directory
            verbose = 0
            ):
    pubx = pubx.replace('\\', '/')
    # obs_directory = '/'.join(pubx.split('/')[:-1]) + '/RNX'
    if not os.path.exists(obs_directory):
        os.mkdir(obs_directory)
    lst_ubx = sorted(glb.glob(pubx+'/*.ubx')) # liste des fichiers ubx, ordonnée par ordre alphabétique
    # Conversion de UBX à RNX2 puis de RNX2 à RNX3
    if True: # conversion des fichiers ubx -> rnx
           # print('conversion des fichiers ubx -> rnx')
           assert len(lst_ubx) != 0
           for k in range(len(lst_ubx)):
               fubx = lst_ubx[k]
               obs_file_name = fubx.split('\\')[-1].split('.')[0] + '.obs'
               cmd = f'convbin -r ubx -y REJSCI -od -os -o {obs_directory}/{obs_file_name} {fubx}'
               if verbose > 0:
                   print(cmd, '\n')
               os.system(cmd)