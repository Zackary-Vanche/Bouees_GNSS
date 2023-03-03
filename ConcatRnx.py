# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 11:27:09 2022

@author: utilisateur
"""

import os
import numpy as np
import datetime as d

def ConcatRnx(directory,
              concat_dir,
              file_name,
              verbose=0,
              marker='boue',
              receiver_number='00',
              iso_country_code='FRA',
              sitename='BOUE',
              version=3):
    """
    Prend en entrée un répertoire.
    Concatène tous les fichiers .obs de ce répertoire et enregistre le résultat dans le dossier concat_dir
    """

    version_int = int(float(version))
    try:
        assert version_int in [2, 3]
    except AssertionError:
        print('Version must be 2 or 3')
        raise

    directory = directory.replace('\\', '/')
    if not os.path.exists(concat_dir):
        os.mkdir(concat_dir)
    list_files = os.listdir(directory)
    list_obs = []
    for file in list_files:
        if file.split('.')[-1] == 'obs':
            list_obs.append(directory + '/' + file)
    rnx2_file = concat_dir + f'/{file_name}.obs'

    # Concaténation
    cmd = f"gfzrnx -finp {' '.join(list_obs)} -fout {rnx2_file} -f -vo {version}"
    if verbose >= 1:
        print(cmd)
    os.system(cmd + f" > {concat_dir}/ConcatRnx_1.log 2>&1")

    # Nomination du fichier avec la bonne convention
    # Fichier complet
    if version_int == 2:
        cmd = f"gfzrnx -finp {rnx2_file} -fout {concat_dir}/::RX2:: -f -site {sitename} -vo 2"
    elif version_int == 3:
        cmd = f"gfzrnx -finp {rnx2_file} -fout {concat_dir}/::RX3::{marker},{receiver_number},{iso_country_code} -f -site {sitename} -vo 3"
    if verbose >= 1:
        print(cmd)
    os.system(cmd + f" > {concat_dir}/ConcatRnx_2.log 2>&1")
    # Fichiers journaliers
    cmd = cmd + " -split 86400"
    if verbose >= 1:
        print(cmd)
    os.system(cmd + f" > {concat_dir}/ConcatRnx_3.log 2>&1")

    # Suppression des fichiers temporaires
    # if os.path.exists(rnx2_file):
    #     os.remove(rnx2_file)