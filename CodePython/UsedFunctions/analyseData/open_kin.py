# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 08:43:12 2023

@author: utilisateur
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas
from datetime import datetime
import pyproj as pp
import math

def open_buoy(file_name):
    """
        Open as Dataframe files from GNSS buoy.

        Parameters
        ----------
        file_name : str
            file to open
            file is the PridePPP output for the position

        Returns
        -------
        buoy : Dataframe
            A single Dataframe containing all positions from
            the GNSS buoy data (PridePPP output)
        """

    print('Opening GNSS buoy position file')

    pos = pandas.read_csv(file_name,
                          skiprows=42,
                          delim_whitespace=True,
                          index_col=False,
                          names=['Mjd', 'Sod', 'X', 'Y', 'Z', 'Latitude', 'Longitude', 'Height', 'Nsat/GREC2C3J_0',
                                 'Nsat/GREC2C3J_1', 'Nsat/GREC2C3J_2', 'Nsat/GREC2C3J_3', 'Nsat/GREC2C3J_4',
                                 'Nsat/GREC2C3J_5', 'Nsat/GREC2C3J_6',
                                 'PDOP', '*'])
    pos = pos.loc[(pos['X']) != '*']
    pos.reset_index(inplace=True, drop=True)
    pos = pos.apply(lambda col:pandas.to_numeric(col, errors='coerce'))
    pos['Mjd'] = pos['Mjd'].astype('float')
    pos.drop(columns=['Nsat/GREC2C3J_0','Nsat/GREC2C3J_1', 'Nsat/GREC2C3J_2',
                      'Nsat/GREC2C3J_3', 'Nsat/GREC2C3J_4','Nsat/GREC2C3J_5',
                      'Nsat/GREC2C3J_6', '*'],
             axis=1,
             inplace=True)
    return pos

if __name__ == "__main__":
    pos_LIENSs = open_buoy('kin_2023039_boue_LIENSs')
    pos_Bouee2 = open_buoy('kin_2023039_boue_Bouee2')
    print('')
    