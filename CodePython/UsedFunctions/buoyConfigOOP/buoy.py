import os
import numpy as np

"""
Main classes used to handle the buoy configuration. 
The Buoy class is both used:
    -   To write the configuration file then used on the RPi (with the configuration defined using the dedicated UI BuoyUI).
    -   To deploy the configuration on the RPi using the configuration file previously created (reboot routine on RPi). 

Item classes handle the different item than can be configured by user. 
"""

class Buoy:
    """
    Main class describing the buoy configuration
    """

    def __init__(self):
        """
        Define the default attributes of the class
        """
        self.runningOSisLinnux = self.getOS()
        self.nbItems = 0

        if self.runningOSisLinnux:
            self.configFiles_Path = '/home/pi/BuoyConfig/UserConfig'
        else:
            self.configFiles_Path = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\setBuoyConfig\UserConfig'

        if self.runningOSisLinnux:
            self.configMainFile_Path = '/boot/BuoyConfig.txt'
        else:
            self.configMainFile_Path = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\setBuoyConfig\BuoyConfig.txt'

        self.wifi = Wifi(self)
        self.accessPoint = AccessPoint(self)
        
        self.items = [self.wifi, self.accessPoint]

        # self.readConfig()

    def writeMainConfig(self):
        """
        Write main configuration file to be used by the raspberry pi when setting up. 
        """
        lines = ['# Default Wifi Network to connect to when Wifi mode is activated', 
                f'{self.wifi.ssid}', 
                f'{self.wifi.psk}', 
                '# Access Point properties',
                f'{self.accessPoint.ssid}', 
                f'{self.accessPoint.wpa_passphrase}', 
                '# End of configuration']
        lines = [line + '\n' for line in lines]

        with open(self.configMainFile_Path, 'w') as f:
            f.writelines(lines)
        
    def readConfig(self):
        """
        Reads configuration informations from configuration file and associates each element with its item's attribute. 
        """
        with open(self.configMainFile_Path, 'r') as f:
            lines = self.getLines(f)
            baliseIdx = self.getBaliseIdx(lines)
        content = self.getContent(lines, baliseIdx)

        for it in range(self.nbItems):
            self.items[it].content = content[it]

    def applyConfig(self):
        """ 
        Applies item-related configuration for each item (updates item-related configuration files).
        """
        for item in self.items:
            item.applyConfig()

    def updateConfig(self):
        """
        Reads and apply new configuration.
        """
        self.readConfig()
        self.applyConfig()

    @staticmethod   
    def getContent(lines, baliseIdx):
        """
        Separates informations read from configuration file into item-related categories. 
        """
        content = []
        for i in range(len(baliseIdx)-1):
            ib = baliseIdx[i]
            ibp1 = baliseIdx[i+1]
            itemLines = lines[ib+1:ibp1]
            content.append(itemLines)
        return content
    
    @staticmethod
    def getLines(f):
        """
        Reads usefull information from configuration file.
        """
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
    
    @staticmethod
    def getBaliseIdx(lines):
        """
        Gets balise indexes.
        """
        balise = '#'
        baliseIdx = []
        for il in range(len(lines)):
            line = lines[il]
            if balise in line:
                baliseIdx.append(il)
        return baliseIdx

    @staticmethod
    def getOS():
        """
        Differentiates between deployed and dev configuration.
        """
        if os.name == 'nt':
            return False
        else:
            return True


class Item:
    """
    Class to handle general methods for the different items to configure (wifi, access point, ...)
    Inputs :
          buoy: associated buoy configuration
          name: name of the item
          dest: path of the configuration file to modify 
    Outputs :
        self.buoy: associated buoy configuration
        self.name: name of the item
        self.dest: path of the configuration file to modify
        self.src: path of the configuration file to use  
    """

    def __init__(self, buoy):
        self.buoy = buoy
        self.buoy.nbItems += 1
        self.name = '' 
        self.dest = ''
        self.configFilename = ''

    def setSrc(self):
        if self.buoy.runningOSisLinnux:
            self.src = f'{self.buoy.configFiles_Path}/{self.configFilename}'
        else:
            self.src = f'{self.buoy.configFiles_Path}\{self.configFilename}'

        if not os.path.exists(self.src):
            self.createEmptyConfigFile()

    def createEmptyConfigFile(self):    
        cmd = f'touch {self.src}'                
        os.system(cmd)

    def writeUserItemFile(self):
        lines = [line + '\n' for line in self.lines]
        with open(self.src, 'w') as f:
            f.writelines(lines)

    def copyConfig(self):
        cmd = f'sudo cp {self.src} {self.dest}'
        os.system(cmd)

    def applyConfig(self):
        self.writeUserItemFile()
        self.copyConfig()


    
class Wifi(Item):
    def __init__(self, buoy):
        super().__init__(buoy)
        self.name = 'wifi'
        self.dest = '/etc/wpa_supplicant/wpa_supplicant.conf'
        self.configFilename = 'userWifiConfig.txt'
        self.setSrc()

        self.content = ['BoueesGNSS', '12345689']

        self.ssid_MinLength = 1
        self.ssid_MaxLength = 50
        self.psk_MinLength = 6
        self.psk_MaxLength = 20
        self.psk_RequiredCharacter = "!#$%&'()*+,-./:;<=>?@[\]^_{|}~"
               
    
    def setLines(self):
        self.lines = ['ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev', 
                'update_config=1', 
                'country=FR', 
                'network={', 
                f'ssid="{self.ssid}"', 
                f'psk="{self.psk}"',
                '}']

    @property
    def ssid(self):
        return self._ssid
    
    @ssid.setter
    def ssid(self, new_ssid):
        self._ssid = new_ssid
        self.setLines()

    @property
    def psk(self):
        return self._psk
    
    @psk.setter
    def psk(self, new_psk):
        self._psk = new_psk
        self.setLines()

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, new_content):
        self._ssid = new_content[0]
        self._psk = new_content[1]
        self._content = new_content
        self.setLines()

class AccessPoint(Item):
    def __init__(self, buoy):
        super().__init__(buoy)
        self.name = 'wifi'
        self.dest = '/etc/wpa_supplicant/wpa_supplicant.conf'
        self.configFilename = 'userAccessPointConfig.txt'
        self.setSrc()

        self.content = ['RPiZeroW_Bouee', 'MyPassword']

        self.ssid_MinLength = 1
        self.ssid_MaxLength = 50
        self.pwd_MinLength = 6
        self.pwd_MaxLength = 20
        self.pwd_RequiredCharacter = "!#$%&'()*+,-./:;<=>?@[\]^_{|}~"

    def setLines(self):
        self.lines = ['country_code=FR', 
                'interface=wlan0',
                f'ssid={self.ssid}', 
                'channel=9',
                'auth_algs=1',
                'wpa=2', 
                f'wpa_passphrase={self.wpa_passphrase}',
                'wpa_key_mgmt=WPA-PSK',
                'wpa_pairwise=TKIP CCMP', 
                'rsn_pairwise=CCMP']

    @property
    def ssid(self):
        return self._ssid
    
    @ssid.setter
    def ssid(self, new_ssid):
        self._ssid = new_ssid
        self.setLines()

    @property
    def wpa_passphrase(self):
        return self._wpa_passphrase
    
    @wpa_passphrase.setter
    def wpa_passphrase(self, new_wpa_passphrase):
        self._wpa_passphrase = new_wpa_passphrase
        self.setLines()

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, new_content):
        self._ssid = new_content[0]
        self._wpa_passphrase = new_content[1]
        self._content = new_content
        self.setLines()


