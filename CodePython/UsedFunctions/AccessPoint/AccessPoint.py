import time
import subprocess as sp


SSID = 'RPiZeroW_Bouee'
INTERFACE = 'Wi-Fi'
PROFILE = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\AccessPoint\Wi-Fi-RPiZeroW_Bouee.xml'
# PROFILE = r'.\Wi-Fi-RPiZeroW_Bouee.xml'
PASSWORD = 'hydro'
AP_IP = '192.168.4.1'

def APisAvailable():
    """Return buoy AP availability: 
        True: AP is available 
        False: AP is not available
    """
    cmd = f'netsh wlan show networks | findstr SSID | findstr {SSID}'
    result = sp.run(cmd, shell=True, stdout=sp.DEVNULL) # 0 if no error, not 0 otherwise 
    # print(result.returncode)
    if result.returncode == 0:
        return True 
    else:
        return False


def APisConnected():
    """Return buoy AP connection status: 
        True: Connected to AP 
        False: Not connected to AP
    """
    cmd = f'netsh wlan show interface | findstr SSID | findstr {SSID}'
    result = sp.run(cmd, shell=True, stdout=sp.DEVNULL) # 0 if no error, not 0 otherwise 

    # print(f'Status = {status}')
    if result.returncode == 0:
        return True 
    else:
        return False

def connectToAP():
    """ Try to connect to buoy access point if available. """

    cmd = f'netsh wlan add profile filename="{PROFILE}"'
    result = sp.run(cmd, shell=True, stdout=sp.DEVNULL)

    while not APisConnected():

        # print(APisConnected())
        if APisAvailable():
            # buoy AP is available 
            print("Attempting to connect to buoy..\n")
            cmd = f'netsh wlan connect name="{SSID}" interface="{INTERFACE}"'
            result = sp.run(cmd, shell=True, stdout=sp.DEVNULL)
            time.sleep(5)
            if APisConnected():
                print("Connection to buoy successful !\n")
            else:
                print("Connection to buoy failed !\n")
        else:
            # buoy AP is out of range or not activated
            print("Buoy AP not available.\n")

        time.sleep(5)

def disconnectFromAP():
    """ Disconnect from buoy access point if connected. """

    if APisConnected():
        # User is connected to buoy 
        print("Disconnecting from buoy..\n")
        cmd = 'netsh wlan disconnect'
        result = sp.run(cmd, shell=True, stdout=sp.DEVNULL)

        if result.returncode == 0:
            print("Disconnected from buoy.\n")
        else:
            print("Disconnection from buoy failed !\n")
    else:
        # User is not connected to buoy 
        print("buoy is already disconnected.\n")


def forgetAP():
    """ Forget Access Point settings """

    cmd = f'netsh wlan delete profile name={SSID}'
    result = sp.run(cmd, shell=True, stdout=sp.DEVNULL)

def transferFileFromAP(src, dest):
    """ Transfer file from AP to local """
    if APisConnected():
        # cmd = f"pscp -batch -pw {PASSWORD} pi@raspberrypi.local:{src} {dest}"
        cmd = f"pscp -v -pw {PASSWORD} pi@{AP_IP}:{src} {dest}"
        result = sp.run(cmd, shell=True, stdout=sp.DEVNULL)
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

if __name__=="__main__":
    # pass

    # forgetAP()
    # disconnectFromAP()
    connectToAP()

    # APisAvailable()

    # src = "/home/pi/BuyoConfig/APRoutine.sh"
    # dest = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\CONFIG"
    # transferFileFromAP(src, dest)

    # getDataFromAP(dataType='all')