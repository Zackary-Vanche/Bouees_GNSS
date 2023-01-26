import os 
from getOS import getOS
import numpy as np

# GLOBAL 
OS = getOS()

if OS == 'Linux':
    PATH = '/home/pi/BuoyConfig/UserConfig'
else:
    PATH = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\setBuoyConfig\UserConfig'

if OS == 'Linux':
    CONFIG_FILE = '/boot/BuoyConfig.txt'
else:
    CONFIG_FILE = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\setBuoyConfig\BuoyConfig.txt'

ITEMS = ['wifi', 'ap']
CONFIG_FILENAMES = ['userWifiConfig.txt', 'userAccessPointConfig.txt']
DEFAULT_CONFIG_FILENAMES = ['defaultWifiConfig.txt', 'defaultAccessPointConfig.txt']

def getConfigDico():
    dico = {'user': {ITEMS[i]: CONFIG_FILENAMES[i] for i in range(len(ITEMS))},
            'default': {ITEMS[i]: DEFAULT_CONFIG_FILENAMES[i] for i in range(len(ITEMS))}}
    return dico

def setConfig(dest, item, config_type):
    dico = getConfigDico()

    config_file = dico[config_type][item]

    if OS == 'Linux':
        src = f'{PATH}/{config_file}'
    else:
        src = f'{PATH}\{config_file}'

    cmd = f'sudo cp {src} {dest}'
    os.system(cmd)

# WIFI
def setDefaultWifi():
    dest = '/etc/wpa_supplicant/wpa_supplicant.conf'
    setConfig(dest, item='wifi', config_type='default')

def setUserWifi(config):
    userWifi = config['userWifi']

    if OS == 'Linux':
        filepath = f'{PATH}/{CONFIG_FILENAMES[0]}'
    else:
        filepath = f'{PATH}\{CONFIG_FILENAMES[0]}'

    writeUserWifiFile(userWifi, filepath)
    updateWifiConfig()
    
def updateWifiConfig():
    dest = '/etc/wpa_supplicant/wpa_supplicant.conf'
    setConfig(dest, item='wifi', config_type='user')

def writeUserWifiFile(userWifi, filepath):
    
    lines = ['ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev', 
            'update_config=1', 
            'country=FR', 
            'network={', 
            userWifi[0], 
            userWifi[1],
            '}']
    
    lines = [line + '\n' for line in lines]

    with open(filepath, 'w') as f:
        f.writelines(lines)

# ACCESS POINT
def setDefaultAP():
    dest = '/etc/hostapd/hostapd.conf'
    setConfig(dest, item='ap', config_type='default')

def setUserAP(config):
    userAP = config['userAP']

    if OS == 'Linux':
        filepath = f'{PATH}/{CONFIG_FILENAMES[1]}'
    else:
        filepath = f'{PATH}\{CONFIG_FILENAMES[1]}'

    writeUserAPFile(userAP, filepath)
    updateAPConfig()
    
def updateAPConfig():
    dest = '/etc/hostapd/hostapd.conf'
    setConfig(dest, item='ap', config_type='user')

def writeUserAPFile(userAP, filepath):

    lines = ['country_code=FR', 
            'interface=wlan0',
            userAP[0], 
            'channel=9',
            'auth_algs=1',
            'wpa=2', 
            userAP[1],
            'wpa_key_mgmt=WPA-PSK',
            'wpa_pairwise=TKIP CCMP', 
            'rsn_pairwise=CCMP']
    
    lines = [line + '\n' for line in lines]

    with open(filepath, 'w') as f:
        f.writelines(lines)

# UTILITIES
def createEmptyConfigFiles():    
    for filename in CONFIG_FILENAMES:

        if OS == 'Linux':
            cmd = f'touch {PATH}/{filename}'
        else: 
            cmd = f'touch {PATH}\{filename}'
            
        os.system(cmd)
    
def readConfig(filename):
    items = ['userWifi', 'userAP']

    with open(filename, 'r') as f:
        # content = f.read()
        lines = getLines(f)
        baliseIdx = getBaliseIdx(lines)

    content = getContent(lines, baliseIdx)
    nbItems = len(items)

    config = {}
    for it in range(nbItems):
        item = items[it]
        itemContent = content[it]
        newEntry = {item: itemContent}
        config.update(newEntry)

    return config

def getContent(lines, baliseIdx):
    content = []
    for i in range(len(baliseIdx)-1):
        ib = baliseIdx[i]
        ibp1 = baliseIdx[i+1]
        itemLines = lines[ib+1:ibp1]
        content.append(itemLines)
    return content

def getLines(f):
    lines = np.array(f.readlines())
    nbLines = len(lines)
    blankLines = np.array([False] * nbLines)
    for il in range(nbLines):
        line = lines[il]
        # Get rid of empty lines 
        if line == '\n':    
            blankLines[il] = True
        # Get rid of '\n' caracters 
        lines[il] = lines[il].replace('\n', '')
    return lines[~blankLines]

def getBaliseIdx(lines):
    balise = '#'
    baliseIdx = []
    for il in range(len(lines)):
        line = lines[il]
        if balise in line:
            baliseIdx.append(il)
    return baliseIdx


if __name__ == '__main__':

    config = readConfig(CONFIG_FILE)

    createEmptyConfigFiles()

    # setUserWifi(config)
    setUserAP(config)