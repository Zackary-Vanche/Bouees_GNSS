# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 11:27:09 2022

@author: utilisateur
"""

import os

def ConcatRnx(directory,
              concat_dir,
              file_name,
              verbose = 0,
              marker = 'boue',
              receiver_number = '00',
              iso_country_code = 'FRA'):
    """
    Prend en entrée un répertoire.
    Concatène tous les fichiers .obs de ce répertoire et enregistre le résultat dans le dossier concat_dir
    """
    directory = directory.replace('\\', '/')
    if not os.path.exists(concat_dir):
        os.mkdir(concat_dir)
    list_files = os.listdir(directory)
    list_obs = []
    for file in list_files:
        if file.split('.')[-1] == 'obs':
            list_obs.append(directory + '/' + file)
    rnx2_file = concat_dir + f'/{file_name}.obs'
    # log_file = concat_dir + f'/{file_name}_log.txt'
    # Concaténation
    cmd = f"gfzrnx -finp {' '.join(list_obs)} -fout {rnx2_file} -f -v 3 " # -errlog {log_file}"
    if verbose > 0:
        print(cmd, '\n')
    os.system(cmd)
    # Nomination du fichier avec la bonne convention
    cmd = f"gfzrnx -finp {rnx2_file} -fout {concat_dir}/::RX3::{marker},{receiver_number},{iso_country_code}"
    os.system(cmd)
    # On change l'extension du fichier de rnx à obs
    for file in os.listdir(concat_dir):
        file = concat_dir + '/' + file
        if file.split('.')[-1] == 'rnx': 
            os.rename(file, file.replace('.rnx', '.obs'))
    # Suppression des fichiers temporaires
    os.remove(rnx2_file)