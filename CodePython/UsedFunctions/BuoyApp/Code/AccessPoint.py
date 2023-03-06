#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Menetrier Baptiste
# Created Date: 04/03/2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""
Functions to connect to buoy access point.  
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import os
import platform
import time
import numpy as np

# AP_PROFILE_TEMPLATE = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\BuoyApp\AccessPoint\buoy_ap_profile_template.xml'
# AP_PROFILE = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\BuoyApp\AccessPoint\buoy_ap_profile.xml'
AP_PROFILE_TEMPLATE = r'.\AccessPoint\buoy_ap_profile_template.xml'
AP_PROFILE = r'.\AccessPoint\buoy_ap_profile.xml'

# AP_PROFILE = r'.\buoy_ap_profile.xml'
PASSWORD = 'hydro'
AP_IP = '192.168.4.1'
SSID = 'RPiZeroW_Bouee'


## Updated version to handle Linux ##
if platform.system() == "Windows":
    INTERFACE_CMD = "netsh interface show interface Wi-Fi | findstr /C:\"Connected\""
    CONNECT_CMD = "netsh wlan connect name=\"{}\" interface=\"Wi-Fi\""
elif platform.system() == "Linux":
    INTERFACE_CMD = "iw dev | awk '$1==\"Interface\"{print $2}'"
    CONNECT_CMD = "nmcli device wifi connect {} ifname {}"

def APisAvailable(ssid):
    """Return buoy AP availability: 
        True: AP is available 
        False: AP is not available
    """
    if platform.system() == "Windows":
        cmd = f'netsh wlan show networks | findstr SSID | findstr {ssid}'
    elif platform.system() == "Linux":
        cmd = f"nmcli device wifi list | grep {ssid}"
    status = os.system(cmd) # 0 if no error, not 0 otherwise 
    # print(status)
    if status == 0:
        return True 
    else:
        return False

def APisConnected(ssid):
    """Return buoy AP connection status: 
        True: Connected to AP 
        False: Not connected to AP
    """
    if platform.system() == "Windows":
        cmd = f'netsh wlan show interface | findstr SSID | findstr {ssid}'
        status = os.system(cmd) # 0 if no error, not 0 otherwise 
    elif platform.system() == "Linux":
        cmd = f"nmcli device show | grep GENERAL.CONNECTION | grep -q {ssid}"
        status = os.system(cmd) # 0 if no error, not 0 otherwise 
    # print(f'Status = {status}')
    if status == 0:
        return True 
    else:
        return False

def connectToAP(ssid):
    """ Try to connect to buoy access point if available. """

    start_time = time.time()

    if platform.system() == "Windows":
        cmd = f'netsh wlan add profile filename="{AP_PROFILE}"'
        status = os.system(cmd)
    elif platform.system() == "Linux":
        cmd = f'sudo nmcli device wifi rescan'
        status = os.system(cmd)

    while not APisConnected(ssid):

        # print(APisConnected(ssid))
        if APisAvailable(ssid):
            # buoy AP is available 
            print("Attempting to connect to buoy..\n")
            if platform.system() == "Windows":
                cmd = CONNECT_CMD.format(ssid)
                
            elif platform.system() == "Linux":
                interface = os.popen(INTERFACE_CMD).read().strip()
                cmd = CONNECT_CMD.format(ssid, interface)
                cmd = f'sudo {cmd}'
            status = os.system(cmd)
            time.sleep(5)
            if APisConnected(ssid):
                print("Connection to buoy successful !\n")
            else:
                print("Connection to buoy failed !\n")
        else:
            # buoy AP is out of range or not activated
            elapsed_time = np.round(time.time() - start_time, 0)
            if elapsed_time < 60:
                print(f"Buoy AP not available,  elapsed time = {elapsed_time}s.\n")
            elif elapsed_time < 3600:
                elapsed_time_min = elapsed_time // 60
                elapsed_time_sec = elapsed_time % 60
                print(f"Buoy AP not available,  elapsed time = {elapsed_time_min}m, {elapsed_time_sec}s.\n")

        time.sleep(5)
        
def add_accessPoint_profile():
    cmd = f'netsh wlan add profile {AP_PROFILE}'
    status = os.system(cmd)

def set_ap_profile(ssid, pwd):
    ssid_hex = str_to_hex(ssid)
        
    with open(AP_PROFILE_TEMPLATE, 'r') as f:
        lines = f.readlines()
        
        lines[2] = lines[2].replace('ap_name', ssid)
        lines[5] = lines[5].replace('5250695A65726F575F426F756565', ssid_hex)
        lines[6] = lines[6].replace('ap_name', ssid)
        lines[21] = lines[21].replace('ap_pwd', pwd)
    
    with open(AP_PROFILE, 'w') as f:
        f.writelines(lines) 
        
# def APisAvailable(ssid):
#     """Return buoy AP availability: 
#         True: AP is available 
#         False: AP is not available
#     """
#     cmd = f'netsh wlan show networks | findstr SSID | findstr {ssid}'
#     status = os.system(cmd) # 0 if no error, not 0 otherwise 
#     # print(status)
#     if status == 0:
#         return True 
#     else:
#         return False


# def APisConnected(ssid):
#     """Return buoy AP connection status: 
#         True: Connected to AP 
#         False: Not connected to AP
#     """
#     cmd = f'netsh wlan show interface | findstr SSID | findstr {ssid}'
#     status = os.system(cmd) # 0 if no error, not 0 otherwise 

#     # print(f'Status = {status}')
#     if status == 0:
#         return True 
#     else:
#         return False

# def connectToAP(ssid):
#     """ Try to connect to buoy access point if available. """

#     start_time = time.time()
#     cmd = f'netsh wlan add profile filename="{AP_PROFILE}"'
#     status = os.system(cmd)

#     while not APisConnected():

#         # print(APisConnected())
#         if APisAvailable():
#             # buoy AP is available 
#             print("Attempting to connect to buoy..\n")
#             cmd = f'netsh wlan connect name="{ssid}" interface="{INTERFACE}"'
#             status = os.system(cmd)
#             time.sleep(5)
#             if APisConnected():
#                 print("Connection to buoy successful !\n")
#             else:
#                 print("Connection to buoy failed !\n")
#         else:
#             # buoy AP is out of range or not activated
#             elapsed_time = np.round(time.time() - start_time, 0)
#             if elapsed_time < 60:
#                 print(f"Buoy AP not available,  elapsed time = {elapsed_time}s.\n")
#             elif elapsed_time < 3600:
#                 elapsed_time_min = elapsed_time // 60
#                 elapsed_time_sec = elapsed_time % 60
#                 print(f"Buoy AP not available,  elapsed time = {elapsed_time_min}m, {elapsed_time_sec}s.\n")

#         time.sleep(5)

def disconnectFromAP():
    """ Disconnect from buoy access point if connected. """

    if APisConnected():
        # User is connected to buoy 
        print("Disconnecting from buoy..\n")
        cmd = 'netsh wlan disconnect'
        status = os.system(cmd)

        if status == 0:
            print("Disconnected from buoy.\n")
        else:
            print("Disconnection from buoy failed !\n")
    else:
        # User is not connected to buoy 
        print("buoy is already disconnected.\n")


def forgetAP(ssid):
    """ Forget Access Point settings """

    cmd = f'netsh wlan delete profile name={ssid}'
    status = os.system(cmd)
     
        
def transferFileFromAP(src, dest):
    """ Transfer file from AP to local """
    if APisConnected():
        # cmd = f"pscp -batch -pw {PASSWORD} pi@raspberrypi.local:{src} {dest}"
        cmd = f"pscp -v -pw {PASSWORD} pi@{AP_IP}:{src} {dest}"
        status = os.system(cmd)
        # print(f"{src}\n") 
    else:
        print("File transfer failed, AP is not connected")

def getDataFromAP(dataType='all'):
    """ Download all archived data from AP"""
    print("Downloading data from buoy..")
    # NMEA 
    if dataType == 'NMEA' or dataType == 'all':
        src = "/home/pi/BuyoData/NMEA/*.gz"
        dest = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\CONFIG"
        transferFileFromAP(src, dest)

    if dataType == 'UBX' or dataType == 'all':
        src = "/home/pi/BuyoData/UBX/*.gz"
        dest = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\CONFIG"
        transferFileFromAP(src, dest)

    if dataType == 'METEO' or dataType == 'all':
        src = "/home/pi/BuyoData/METEO/*.gz"
        dest = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\CONFIG"
        transferFileFromAP(src, dest)

   
   
def str_to_hex(txt_to_convert):
    string = txt_to_convert.encode('utf-8')
    txt_hex = string.hex().upper()
    return txt_hex
    
if __name__=="__main__":
    # pass

    # forgetAP()
    # disconnectFromAP()
    ssid = 'buoyAccessPoint'
    # ssid = 'buoyAccessPoint 2'
    pwd = 'password!'
    set_ap_profile(ssid, pwd)
    
    
    connectToAP(ssid)

    # APisAvailable()

    # src = "/home/pi/BuyoConfig/APRoutine.sh"
    # dest = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\CONFIG"
    # transferFileFromAP(src, dest)

    # getDataFromAP(dataType='all')
    
