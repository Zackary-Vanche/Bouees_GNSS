import pandas as pd
import os
from os import listdir
from os.path import isfile, join

def begin_meteo(file):
    df = pd.read_csv(file,skipinitialspace=True)
    if df.columns[0]!="date":
            df = pd.read_csv(file,names=["date","temperature_C","pression_hPa","humidity_per"],skipinitialspace=True)
    return df

def add_file_meteo(df_ori,file):
    df = pd.read_csv(file,skipinitialspace=True)
    if df.columns[0]!="date":
            df = pd.read_csv(file,names=df_ori.columns,skipinitialspace=True)
    frames = [df_ori,df]
    return pd.concat(frames)

def create_log_meteo():
    #directory = "./BoueeV2/13102022/data_testInterieur/METEO/"
    directory = "./BoueeV2/13102022_14102022/METEO/"
    fichiers = [os.path.join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]
    df = begin_meteo(fichiers[0])
    for i in range(1,len(fichiers)):
        df = add_file_meteo(df, fichiers[i])
    parsed_date = pd.to_datetime(df["date"], format='%d%m%Y %H:%M:%S')
    df["date"] = parsed_date
    df = df.rename(columns={"date":"Time","temperature_C":"T","pression_hPa":"P","humidity_per":"H"})
    return df