#!/usr/bin/env python3

import sys
import os

import numpy as np
import glob as glb

CONVBIN = '/home/clemence/RTKLIB-b34g/app/consapp/convbin/gcc/convbin'
CONVBIN = 'convbin'

def Ubx2Rnx(pubx, # ubx directory
            obs_directory, # rnx directory
            verbose=0,
            antenna_number='NONE',
            antenna_name='AS-ANT2BCAL',
            sitename='BOUE',
            observer='OBSERVER',
            agency='ENSTA_Bretagne',
            receiver_number='NONE',
            receiver_type='Z-F9P',
            TADJ=True,
            version=3
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
               # fubx = fubx.replace('\\', '/')
               obs_file_name = fubx.replace('\\', '/').split('/')[-1].split('.')[0] + '.obs'
               cmd = f'''{CONVBIN} -hr {receiver_number}/{receiver_type}/ -ha {antenna_number}/{antenna_name} -ho {observer}/{agency} -r ubx -y REJSCI -od -os -o {obs_directory}/{obs_file_name} {fubx} -hm {sitename} -v {version}'''
               if TADJ:
                   cmd = cmd + ''' -ro "-TADJ=1.0"'''
               if verbose >= 1:
                   print(cmd)
               os.system(cmd + f" > {obs_directory}/ubx2rnx.log 2>&1")
