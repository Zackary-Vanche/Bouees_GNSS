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
        self.parent_is_RPI = (parent == 'RPI')
                
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
                os.mkdir(self.configFiles_Path)

        else:   # Buoy object instanciated by the RPI
            self.configFiles_Path = '/home/pi/BuoyConfig/UserConfig'


        if self.parent_is_GUI:  # Buoy object instanciated by the GUI 
            print('Buoy object instanciated by GUI')

            # Build path depending on the os 
            if self.runningOSisLinux:
                self.configMainFile_Path = r'./UserConfig/BuoyConfig.txt'
            else:
                self.configMainFile_Path = r'.\UserConfig\BuoyConfig.txt'
                
        elif self.parent_is_RPI:   # Buoy object instanciated by the RPI
            print('Buoy object instanciated by RPI')
            self.configMainFile_Path = '/boot/BuoyConfig.txt'
            
            
        self.wifi = Wifi(self)
        self.accessPoint = AccessPoint(self)
        self.meteoSensor = MeteoSensor(self)
        self.gnssReceiver = GNSSReceiver(self)
        
        self.items = [self.wifi, self.accessPoint, self.gnssReceiver, self.meteoSensor]
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
        lines = []
        
        # WiFi
        lines += ['# Default Wifi Network to connect to when Wifi mode is activated', 
                f'{self.wifi.ssid}', 
                f'{self.wifi.psk}']
         
        # Access Point
        lines += ['# Access Point properties',
                f'{self.accessPoint.ssid}', 
                f'{self.accessPoint.wpa_passphrase}']

        # GNSS
        lines.append('# GNSS Receiver properties')
        for gnss_constellation in self.gnssReceiver.available_constellations:
            lines.append(f'{ getattr(self.gnssReceiver, gnss_constellation) }')
        lines.append(f'{ self.gnssReceiver.acquisitionPeriod }')
        
        # METEO
        lines.append('# Meteo Sensor properties')
        for meteo_property in self.meteoSensor.available_properties:
            lines.append(f'{ getattr(self.meteoSensor, meteo_property) }')
        lines.append(f'{ self.meteoSensor.acquisitionPeriod }')

        lines.append('# End of configuration')

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

        # Meteo
        print('Configuration of the meteo sensor...')
        file = '/home/pi/ScriptPython/capteur_settings.txt'
        if not os.path.isfile(file):
            cmd = f'sudo touch {file}'
            os.system(cmd)
            cmd = f'sudo chmod 666 {file}'
            os.system(cmd)
            
        lines = [f'{c},' for c in self.meteoSensor.content]
        with open(file, 'w') as f:
            f.writelines(lines)
        print('Configuration of the meteo sensor...DONE')
    
        # GNSS
        print('Configuration of the GNSS receiver...')
        # print(self.gnssReceiver.content)
        # Update constelattions 
        for i_const in range(len(self.gnssReceiver.available_constellations)):
            cmd = 'ubxtool '
            constellation = self.gnssReceiver.available_constellations[i_const]
            if self.gnssReceiver.content[i_const]: # Enable constellation
                n_freq = 2 # TODO: we use 2 to enable both frequencies to re-enable constellation, it might be possible to select single freq to enable (to investigate) 
                if constellation == 'qzss':
                    constellation = 'gps' # ubxtool disable both gps and qzss at the same time with -d gps command
                    # TODO: assert gps is selected when using qzss in the GUI 
                cmd += f'-e {constellation.upper()},{n_freq} -v 0'
                res = os.system(cmd)
                # res = 0
                # for item in self.gnssReceiver.ublox_constellations_items[constellation]:                   
                #     cmd += f'-z {item},1'
                #     res += os.system(cmd)
                    
                # TODO: Change behaviour to handle cases when constellation is already enabled (return 1)
                if res == 0: # success
                    print(f'Successfully enabled {constellation.upper()}')
                else: # Failure
                    print(f'Failed to enable {constellation.upper()}')
                    
            else: # Disable constellation
                cmd += f'-d {constellation.upper()} -v 0'
                res = os.system(cmd)
                # res = 0
                # for item in self.gnssReceiver.ublox_constellations_items[constellation]:                   
                #     cmd += f'-z {item},0'
                #     res += os.system(cmd)
                    
                if res == 0: # success
                    print(f'Successfully disabled {constellation.upper()}')
                else: # Failure
                    print(f'Failed to disable {constellation.upper()}')
            
            
        # Update Rate  
        # cmd = f'ubxtool -p CFG-RATE,{int(self.gnssReceiver.acquisitionPeriod * 1e4)} -v 0'    # Update rate (rate in millisec)
        cmd = f'ubxtool -z CFG-RATE-MEAS,{int(self.gnssReceiver.acquisitionPeriod * 1e4)}'    # Update rate (rate in millisec) (set in all layers except the default layer)
        res = os.system(cmd)
        if res == 0: # success
            print(f'Successfully updated rate to {int(self.gnssReceiver.acquisitionPeriod * 1e4)}ms')
        else: # Failure
            print(f'Failded to update rate to {int(self.gnssReceiver.acquisitionPeriod * 1e4)}ms')
        print('Configuration of the GNSS receiver...DONE')
                
        # Wifi / AP
        print('Configuration of the Wifi/AccessPoint...')
        cmd = f'sudo ./setup_wlan_and_AP_modes.sh \
                -s {self.wifi.ssid} -p {self.wifi.psk} \
                -a {self.accessPoint.ssid} -r {self.accessPoint.wpa_passphrase} -d'
        os.system(cmd)
        

        
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
        
class MeteoSensor(Item):
    def __init__(self, buoy):
        super().__init__(buoy)
        self.name = 'meteoSensor'
        self.content = [1, 1, 1, 10]     # Default all properties set to true and 10s period of acquisition
        self.available_properties = ['temperature', 'pressure', 'humidity']
        
    @property
    def temperature(self):
        return self._temperature
    
    @temperature.setter
    def temperature(self, new_temperature):
        self._temperature = new_temperature

    @property
    def pressure(self):
        return self._pressure
    
    @pressure.setter
    def pressure(self, new_pressure):
        self._pressure = new_pressure
        
    @property
    def humidity(self):
        return self._humidity
    
    @humidity.setter
    def humidity(self, new_humidity):
        self._humidity = new_humidity
        
    @property
    def acquisitionPeriod(self):
        return self._acquisitionPeriod
    
    @acquisitionPeriod.setter
    def acquisitionPeriod(self, new_acquisitionPeriod):
        self._acquisitionPeriod = new_acquisitionPeriod

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, new_content):
        self._temperature = new_content[0]
        self._pressure = new_content[1]
        self._humidity = new_content[2]
        self._acquisitionPeriod = new_content[3]
        self._content = new_content

class GNSSReceiver(Item):
    def __init__(self, buoy):
        super().__init__(buoy)
        self.name = 'gnssReceiver'
        self.content = [1, 0, 1, 1, 0, 1, 1]     # Default 'GPS', 'SBAS', 'Galileo', 'BeiDou', 'QZSS', 'GLONASS' , acquisition period 
        self.available_constellations = ['gps', 'sbas', 'galileo', 'beidou', 'qzss', 'glonass']
        # self.ublox_constellations_all_items = {'gps_L1': 'CFG-SIGNAL-GPS_L1CA_ENA', 
        #                                    'gps_L2': 'CFG-SIGNAL-GPS_L2C_ENA', 
        #                                    'sbas_L1CA': 'CFG-SIGNAL-SBAS_L1CA_ENA',
        #                                    'galileo_E1': 'CFG-SIGNAL-GAL_E1_ENA',
        #                                    'galileo_E5B': 'CFG-SIGNAL-GAL_E5B_ENA',
        #                                    'beidou_B1': 'CFG-SIGNAL-BDS_B1_ENA',
        #                                    'beidou_B2': 'CFG-SIGNAL-BDS_B2_ENA',
        #                                    'qzss_L1CA': 'CFG-SIGNAL-QZSS_L1CA_ENA',
        #                                    'qzss_L1S': 'CFG-SIGNAL-QZSS_L1S_ENA',
        #                                    'qzss_L1CA': 'CFG-SIGNAL-QZSS_L2C_ENA',
        #                                    'glonass_L1': 'CFG-SIGNAL-GLO_L1_ENA',
        #                                    'glonass_L2': 'CFG-SIGNAL-GLO_L2_ENA',
        #                                    'gps':  'CFG-SIGNAL-GPS_ENA',
        #                                    'sbas': 'CFG-SIGNAL-SBAS_ENA',
        #                                    'galileo': 'CFG-SIGNAL-GAL_ENA',
        #                                    'beidou': 'CFG-SIGNAL-BDS_ENA',
        #                                    'qzss': 'CFG-SIGNAL-QZSS_ENA',
        #                                    'glonass': 'CFG-SIGNAL-GLO_ENA'}
        
        self.ublox_constellations_items = {'gps': ['CFG-SIGNAL-GPS_L1CA_ENA', 'CFG-SIGNAL-GPS_L2C_ENA', 'CFG-SIGNAL-GPS_ENA'], 
                                           'sbas': ['CFG-SIGNAL-SBAS_L1CA_ENA', 'CFG-SIGNAL-SBAS_ENA'], 
                                           'galileo': ['CFG-SIGNAL-GAL_E1_ENA', 'CFG-SIGNAL-GAL_E5B_ENA', 'CFG-SIGNAL-GAL_ENA'], 
                                           'beidou': ['CFG-SIGNAL-BDS_B1_ENA', 'CFG-SIGNAL-BDS_B2_ENA', 'CFG-SIGNAL-BDS_ENA'], 
                                           'qzss': ['CFG-SIGNAL-QZSS_L1CA_ENA', 'CFG-SIGNAL-QZSS_L1S_ENA', 'CFG-SIGNAL-QZSS_L2C_ENA', 'CFG-SIGNAL-QZSS_ENA'], 
                                           'glonass': ['CFG-SIGNAL-GLO_L1_ENA', 'CFG-SIGNAL-GLO_L2_ENA', 'CFG-SIGNAL-GLO_ENA']}
                                           
                
    @property
    def gps(self):
        return self._gps
    
    @gps.setter
    def gps(self, new_gps):
        self._gps = new_gps

    @property
    def sbas(self):
        return self._sbas
    
    @sbas.setter
    def sbas(self, new_sbas):
        self._sbas = new_sbas
        
    @property
    def galileo(self):
        return self._galileo
    
    @galileo.setter
    def galileo(self, new_galileo):
        self._galileo = new_galileo
        
    @property
    def beidou(self):
        return self._beidou
    
    @beidou.setter
    def beidou(self, new_beidou):
        self._beidou = new_beidou
        
    @property
    def qzss(self):
        return self._qzss
    
    @qzss.setter
    def qzss(self, new_qzss):
        self._qzss = new_qzss

    @property
    def glonass(self):
        return self._glonass
    
    @glonass.setter
    def glonass(self, new_glonass):
        self._glonass = new_glonass
        
    @property
    def acquisitionPeriod(self):
        return self._acquisitionPeriod
    
    @acquisitionPeriod.setter
    def acquisitionPeriod(self, new_acquisitionPeriod):
        self._acquisitionPeriod = int(new_acquisitionPeriod)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, new_content):
        new_content = [int(new_c) for new_c in new_content]
        self._gps = new_content[0]
        self._sbas = new_content[1]
        self._galileo = new_content[2]
        self._beidou = new_content[3]
        self._qzss = new_content[4]
        self._glonass = new_content[5]
        self._acquisitionPeriod = new_content[6]
        
        self._content = new_content