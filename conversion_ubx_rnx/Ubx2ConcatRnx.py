# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 09:16:18 2022

@author: utilisateur
"""

from ConcatRnx import ConcatRnx
from Ubx2Rnx import Ubx2Rnx
import os

def Ubx2ConcatRnx(root_dir):
    """
    Cette fonction prend en entrée un dossier root_dir.
    Elle convertit les fichiers ubx du dossier root_dir + '/UBX' en RNX
    qu'elle enregistre dans root_dir + '/RNX'.
    Puis, elle concatène ces fichiers et enregistre le résultat dans root_dir + '/RNX/concat'.
    """
    ubx_dir = root_dir + '/UBX'
    if not os.path.exists(ubx_dir): # Dans ce cas, nous n'avons pas de fichiers à traiter
        return
    rnx_dir = root_dir + '/RNX'
    concat_dir = rnx_dir + '/concat'
    file_name = 'temp'
    Ubx2Rnx(ubx_dir, rnx_dir)
    ConcatRnx(rnx_dir, concat_dir, file_name) 
    # Attention, cette fonction peut écraser un fichier existant
    # Si le fichier de sortie spécifié existe déjà

if __name__ == "__main__":
    Ubx2ConcatRnx('C:/Users/utilisateur/Desktop/Guerledan/Bouees_GNSS/DATA/data_2022_2023/BoueeV2/testLog23102022')