# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 11:09:43 2022

@author: utilisateur
"""

import os
import gzip
import shutil

def ExtractGz(directory,
              extract_dir,
              verbose = 0):
    if not os.path.exists(extract_dir):
        os.mkdir(extract_dir)
    list_files = os.listdir(directory)
    list_gz = []
    for file in list_files:
        if file.split('.')[-1] == 'gz':
            list_gz.append(file)
    for file_in_name in list_gz:
        assert file_in_name.split('.')[-1] == 'gz'
        file_out_name = extract_dir + '/' + file_in_name.replace('.gz', '')
        file_in_name = directory + '/' + file_in_name
        with gzip.open(file_in_name, 'rb') as f_in:
            with open(file_out_name, 'wb') as f_out:
                try:
                    shutil.copyfileobj(f_in, f_out)
                except:
                    print(file_in_name)
                    raise

if __name__ == "__main__":
    directory = 'C:/Users/utilisateur/Desktop/Guerledan/Bouees_GNSS/DATA/data_2022_2023/BoueeV2/testLog23102022/NMEA'
    extract_dir = directory + '/extract'
    ExtractGz(directory, extract_dir)
