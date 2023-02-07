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

    def __init__(self, parent='GUI'):
        # parent = 'GUI' or 'RPI'
        self.parent_is_GUI = (parent == 'GUI') # Bool to differentiate GUI use and RPI use 
        
        self.runningOSisLinux = self.getOS()
        self.nbItems = 0

        if self.parent_is_GUI:  # Buoy object instanciated by the GUI 
            
            # Build path depending on the os 
            if self.runningOSisLinux:
                self.configFiles_Path = r'./UserConfig'
            else:
                # self.configFiles_Path = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\setBuoyConfig\UserConfig'
                self.configFiles_Path = r'.\UserConfig'
                
            if not os.path.isdir(self.configFiles_Path):
                os.mkdir(configFiles_Path)

        else:   # Buoy object instanciated by the RPI
            self.configFiles_Path = '/home/pi/BuoyConfig/UserConfig'


        if self.parent_is_GUI:  # Buoy object instanciated by the GUI 
            
            # Build path depending on the os 
            if self.runningOSisLinux:
                self.configMainFile_Path = r'./UserConfig/BuoyConfig.txt'
            else:
                self.configMainFile_Path = r'.\UserConfig\BuoyConfig.txt'
                
        else:   # Buoy object instanciated by the RPI
            self.configMainFile_Path = '/boot/BuoyConfig.txt'
            
            
        self.wifi = Wifi(self)
        self.accessPoint = AccessPoint(self)
        
        # self.items = [self.wifi, self.accessPoint]
        # self.readConfig()

    def copyMainConfigFileToSDCard(self, dest):
        """
        Copy main configuration file to the SD card holding the RPi OS. Set deployment status to 0 to tell RPi config needs to be updated.
        """
        if not self.runningOSisLinux:
            dest = dest.replace('/', '\\')
        cmd = f'copy {self.configMainFile_Path} {dest}'
        os.system(cmd)

        # Change status 
        self.changeUserConfigDeployementStatus(dest)

    def changeUserConfigDeployementStatus(self, dest):
        """
        Update deployment status. The deployement status is read by the function deployUserConfig.py to check if config needs to be updated. 
            - status = 0: new config has been loaded and need to be used. 
            - status = 1: current config is up to date. 
        """
        if not self.runningOSisLinux:
            dest = dest.replace('/', '\\')
            flagFile = f'{dest}\\userConfigIsDeployed.txt'
        else:
            flagFile = f'{dest}/userConfigIsDeployed.txt'
        with open(flagFile, 'w') as f:
            f.write('0')
        

    def writeMainConfig(self, path=None):
        """Write main configuration file to be used by the raspberry pi when setting up."""
        lines = ['# Default Wifi Network to connect to when Wifi mode is activated', 
                f'{self.wifi.ssid}', 
                f'{self.wifi.psk}', 
                '# Access Point properties',
                f'{self.accessPoint.ssid}', 
                f'{self.accessPoint.wpa_passphrase}', 
                '# End of configuration']
        lines = [line + '\n' for line in lines]

        if path == None:
            path = self.configMainFile_Path
            
        with open(path, 'w') as f:
            f.writelines(lines)
        
    def readConfig(self, path=None):
        """ Reads configuration informations from configuration file and associates each element with its item's attribute."""
        
        if path == None:
            path = self.configMainFile_Path
            
        with open(path, 'r') as f:
            lines = self.getLines(f)
            baliseIdx = self.getBaliseIdx(lines)
        content = self.getContent(lines, baliseIdx)

        for it in range(self.nbItems):
            self.items[it].content = content[it]

    def applyConfig(self):
        """Applies item-related configuration for each item (updates item-related configuration files)."""

        # Wifi / AP
        cmd = : f'sudo ./setup_wlan_and_AP_modes.sh \
                    -s {self.wifi.ssid} -p {self.wifi.psk} \
                    -a {self.accessPoint.ssid} -r {self.accessPoint.wpa_passphrase}'
        os.system(cmd)
        
        # UBlox
        # TODO: complete with the dedicated python function
        # cmd = '/home/pi/ScriptPython/'
        
    def updateConfig(self):
        """Reads and apply new configuration."""
        self.readConfig()
        self.applyConfig()

    @staticmethod   
    def getContent(lines, baliseIdx):
        """Separates information read from configuration file into item-related categories."""
        content = []
        for i in range(len(baliseIdx)-1):
            ib = baliseIdx[i]
            ibp1 = baliseIdx[i+1]
            itemLines = lines[ib+1:ibp1]
            content.append(itemLines)
        return content
    
    @staticmethod
    def getLines(f):
        """Reads usefull information from configuration file."""
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
        """Gets balise indexes."""
        balise = '#'
        baliseIdx = []
        for il in range(len(lines)):
            line = lines[il]
            if balise in line:
                baliseIdx.append(il)
        return baliseIdx

    @staticmethod
    def getOS():
        """Differentiates between deployed and dev configuration."""
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
    Outputs :
        self.buoy: associated buoy configuration
        self.name: name of the item
    """
    def __init__(self, buoy):
        """Update the number of items handled by the Buoy object. 

        Args:
            buoy (Buoy): Buoy object handling the configuration. 
        """
        self.buoy = buoy
        self.buoy.nbItems += 1
        self.name = '' 

    
class Wifi(Item):
    """Class handling the wifi configuration. Wifi can be used either to provide connection 
    to the Raspberrry Pi (for update purposes for instance) or as a ssh connection. 

    Args:
        Item (Item): Mother class. 
    """
    def __init__(self, buoy):
        super().__init__(buoy)
        self.name = 'wifi'
        self.content = ['BoueesGNSS', '12345689']

        self.ssid_MinLength = 1
        self.ssid_MaxLength = 50
        self.psk_MinLength = 6
        self.psk_MaxLength = 20
        self.psk_RequiredCharacter = "!#$%&'()*+,-./:;<=>?@[\]^_{|}~"
               
    @property
    def ssid(self):
        return self._ssid
    
    @ssid.setter
    def ssid(self, new_ssid):
        self._ssid = new_ssid

    @property
    def psk(self):
        return self._psk
    
    @psk.setter
    def psk(self, new_psk):
        self._psk = new_psk

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, new_content):
        self._ssid = new_content[0]
        self._psk = new_content[1]
        self._content = new_content


class AccessPoint(Item):
    def __init__(self, buoy):
        super().__init__(buoy)
        self.name = 'accessPoint'
        self.content = ['RPiZeroW_Bouee', 'MyPassword']     # Default

        self.ssid_MinLength = 1
        self.ssid_MaxLength = 50
        self.pwd_MinLength = 6
        self.pwd_MaxLength = 20
        self.pwd_RequiredCharacter = "!#$%&'()*+,-./:;<=>?@[\]^_{|}~"

    @property
    def ssid(self):
        return self._ssid
    
    @ssid.setter
    def ssid(self, new_ssid):
        self._ssid = new_ssid
        
    @property
    def wpa_passphrase(self):
        return self._wpa_passphrase
    
    @wpa_passphrase.setter
    def wpa_passphrase(self, new_wpa_passphrase):
        self._wpa_passphrase = new_wpa_passphrase

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, new_content):
        self._ssid = new_content[0]
        self._wpa_passphrase = new_content[1]
        self._content = new_content


