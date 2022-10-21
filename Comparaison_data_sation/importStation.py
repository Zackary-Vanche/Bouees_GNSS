import pandas as pd
import os
from os import listdir
from os.path import isfile, join

def begin_station(file):
    colNames = ['Time','T', 'H', 'P']
    df = pd.read_csv(file,skipinitialspace=True,header=9, usecols=[0, 1, 3, 6], names=colNames)
    return df

def add_file_station(df_ori,file):
    colNames = ['Time','T', 'H', 'P']
    df = pd.read_csv(file,skipinitialspace=True,header=9, usecols=[0, 1, 3, 6], names=colNames)
    frames = [df_ori,df]
    return pd.concat(frames)

def create_log_station():
    directory = "./StationMeteo/"
    fichiers = [os.path.join(directory, f) for f in listdir(directory) if isfile(join(directory, f))] 
    df = begin_station(fichiers[0])
    for i in range(1,len(fichiers)):
        df = add_file_station(df, fichiers[i])
    parsed_date = pd.to_datetime(df["Time"], format="%Y-%m-%d %H:%M:%S")
    df["Time"] = parsed_date
    return df