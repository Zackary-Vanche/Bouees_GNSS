import time
import os


SSID = 'RPiZeroW_Bouee'
INTERFACE = 'Wi-Fi'
PROFILE = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\AccessPoint\Wi-Fi-RPiZeroW_Bouee.xml'
PASSWORD = "hydro"

def connnectToAP():
    """ Try to connect to buyo access point if available. """
    buyoConnected = False

    cmd0 = f'netsh wlan add profile filename="{PROFILE}"'
    status = os.system(cmd0)

    while not buyoConnected:
        cmd1 = f'netsh wlan show networks | findstr SSID | findstr {SSID}'
        status = os.system(cmd1)
        # print(status)

        if not status:
            # Buyo AP is available 
            print("Attempting to connect to buyo..\n")
            cmd2 = f'netsh wlan connect name="{SSID}" interface="{INTERFACE}"'
            try:
                status = os.system(cmd2)
                buyoConnected = True
                print("Connection to buyo successful !\n")
            except:
                print("Connection to buyo failed !\n")
        else:
            # Buyo AP is out of range 
            print("Buyo out of range.\n")

        time.sleep(5)

def disconnectFromAP():
    """ Disconnect from buyo access point if connected. """

    cmd1 = f'netsh wlan show interfaces | findstr SSID | findstr {SSID}'
    status = os.system(cmd1)
    # print(status)

    if not status:
        # User is connected to Buyo 
        print("Disconnecting from buyo..\n")
        cmd2 = 'netsh wlan disconnect'
        try:
            status = os.system(cmd2)
            print("Disconnected from buyo.\n")
        except:
            print("Disconnection from buyo failed !\n")
    else:
        # User is not connected to buyo 
        print("Buyo not connected.\n")

        time.sleep(5)

def forgetAP():
    """ Forget Access Point settings"""

    cmd = f'netsh wlan delete profile name={SSID}'
    status = os.system(cmd)

def transferFileFromAP(src, dest):
    "Transfer file from AP to local"
    # cmd = f"pscp -batch -pw {PASSWORD} pi@raspberrypi.local:{src} {dest}"
    cmd = f"pscp -pw {PASSWORD} pi@raspberrypi.local:{src} {dest}"

    status = os.system(cmd) 

def getDataFromAP(dataType='all'):
    """ Download all archived data from AP"""
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

    # forgetAP()
    # disconnectFromAP()
    # connnectToAP()

    # src = "/home/pi/BuyoConfig/APRoutine.sh"
    # dest = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\CONFIG"
    # transferFileFromAP(src, dest)

    getDataFromAP(dataType='NMEA')