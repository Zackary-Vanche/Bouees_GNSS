# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 09:16:18 2022

@author: utilisateur
"""

from ExtractGz import ExtractGz
from ConcatRnx import ConcatRnx
from Ubx2Rnx import Ubx2Rnx
import os

# Attention, cette fonction peut écraser un fichier existant
# Si le fichier de sortie spécifié existe déjà
def Ubx2ConcatRnx(root_dir,
                  TADJ=True,
                  version=3.05,
                  verbose=0):
    """
    Cette fonction prend en entrée un dossier root_dir.
    Dans l'ordre:
        Elle extrait les fichiers GZ du dossier '/UBX'.
        Elle convertit les fichiers ubx du dossier root_dir + '/UBX' en RNX et les enregistre dans root_dir + '/RNX'.
        Elle concatène ces fichiers et enregistre le résultat dans root_dir + '/RNX/concat'.
    """
    
    print(f'Treating {root_dir}')

    ubx_dir = root_dir + '/UBX'
    if TADJ:
        rnx_dir = root_dir + f'/RNX{version}_TADJ'
    else:
        rnx_dir = root_dir + f'/RNX{version}'
    concat_dir = rnx_dir + '/concat'
    file_name = 'temp'
    if not os.path.exists(ubx_dir): # Dans ce cas, nous n'avons pas de fichiers à traiter
        print('The folder does not exists')
        return

    print('ExtractGz')
    ExtractGz(ubx_dir,
              ubx_dir,
              verbose=verbose)

    print('Ubx2Rnx')
    Ubx2Rnx(ubx_dir,
            rnx_dir,
            TADJ=TADJ,
            version=version,
            verbose=verbose)

    print('ConcatRnx')
    ConcatRnx(rnx_dir,
              concat_dir,
              file_name,
              version=version,
              verbose=verbose)

if __name__ == "__main__":
    folder_list = ['C:/Users/utilisateur/Desktop/Data_guerledan_clean/semaine_2/BoueeGNSS_Centipede/data_clean']
    folder_list = ['C:/Users/utilisateur/Desktop/Data_guerledan_clean/semaine_2/data_bouee_05022023_10022023/data']
    folder_list = ['C:/Users/utilisateur/Desktop/Data_guerledan_clean/semaine_2/data_bouee_05022023_10022023/data']
    for folder in folder_list:
        for TADJ in [True, False]: # [True, False]:
            for version in [3.05, 2.11]: # [3.05, 2.11]:
                Ubx2ConcatRnx(root_dir=folder,
                              TADJ=TADJ,
                              version=version,
                              verbose=0)
    #Ubx2ConcatRnx('C:/Users/utilisateur/Documents/ENSTA/Guerledan/CODES/12102022_14102022')
