# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 11:27:09 2022

@author: utilisateur
"""
import glob as glb
import os
import shutil

def PPP(concat_dir,
        verbose=0,
        stdppp=0.0025):
    concat_dir_ppp = concat_dir.replace('concat', f'concat_stdppp_{stdppp}')
    shutil.copytree(concat_dir, concat_dir_ppp)
    list_files = sorted(glb.glob(concat_dir_ppp+'/*.rnx'))
    print(list_files)
    for file in list_files:
       marker = file.split("/")[-1][:4]
       cmd = f"export LANG=C\ncd {concat_dir_ppp}\npdp3 -z S {stdppp} -n {marker} " + file.split("/")[-1]
       os.system(cmd)

if __name__ =='__main__':
    folder = './s1_1314/concat/'
    PPP(folder, stdppp=0.0025)
    PPP(folder, stdppp=0.0025/2)
    folder = './s1_1214/concat/'
    PPP(folder, stdppp=0.0025)
    PPP(folder, stdppp=0.0025/2)
