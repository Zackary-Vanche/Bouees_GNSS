import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QFileDialog
from mainWindow import *
from buoy import *

class BuoyUI(QWidget, Ui_MainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setupUi(parent)

        self.warningMsgType = 'Warning'
        self.warningBoxTitle = 'Warning, invalid entry!'

        self.infoMsgType = 'Information'

        self.buoy = Buoy()
        
        # Button control
        self.validateConfig_pushButton.clicked.connect(self.validateConfig)
        self.saveConfig_pushButton.clicked.connect(self.saveConfig)
        self.transferConfig_pushButton.clicked.connect(self.transferConfig)
        self.loadConfig_pushButton.clicked.connect(self.loadConfig)
        
        # Editing
        self.wifi_PSK_lineEdit.textEdited.connect(self.resetWifi_PSKConfirm)
        self.accessPoint_PWD_lineEdit.textEdited.connect(self.resetAccessPoint_PWDConfirm)
        
        # Editing finish 
        self.wifi_SSID_lineEdit.editingFinished.connect(self.checkWifi_SSID)
        self.wifi_PSK_lineEdit.editingFinished.connect(self.checkWifi_PSK)
        self.accessPoint_SSID_lineEdit.editingFinished.connect(self.checkAccessPoint_SSID)
        self.accessPoint_PWD_lineEdit.editingFinished.connect(self.checkAccessPoint_PWD)

        self.configIsSaved = False

    def resetWifi_PSKConfirm(self):
        self.wifi_ConfirmPSK_lineEdit.setText('')
        
    def resetAccessPoint_PWDConfirm(self):
        self.accessPoint_ConfirmPWD_lineEdit.setText('')
        
    def checkWifi_SSID(self):
        ssid = self.wifi_SSID_lineEdit.text()
        txt = ''
        isValid = True
        if len(ssid) < self.buoy.wifi.ssid_MinLength:
            txt += f'SSID should contain at least {self.buoy.wifi.ssid_MinLength} caracters. '
            isValid = False
        elif len(ssid) > self.buoy.wifi.ssid_MaxLength:
            txt += f'SSID should contain less than {self.buoy.wifi.ssid_MaxLength} caracters. '
            isValid = False
    
        if not isValid:
            self.showMsgBox(self.warningMsgType, self.warningBoxTitle, txt)
        
        return isValid

    def checkWifi_PSK(self):
        psk = self.wifi_PSK_lineEdit.text()
        txt = ''
        isValid = True
        if len(psk) < self.buoy.wifi.psk_MinLength:
            txt += f'Password should contain at least {self.buoy.wifi.psk_MinLength} caracters. '
            isValid = False
        elif len(psk) > self.buoy.wifi.psk_MaxLength:
            txt += f'Password should contain less than {self.buoy.wifi.psk_MaxLength} caracters. '
            isValid = False
        elif not any(c in self.buoy.wifi.psk_RequiredCharacter for c in psk):
            txt += f'Password should contain at least one special character: {self.buoy.wifi.psk_RequiredCharacter}'
            isValid = False

        if not isValid:
            self.showMsgBox(self.warningMsgType, self.warningBoxTitle, txt)

        return isValid

    def checkAccessPoint_SSID(self):
        ssid = self.accessPoint_SSID_lineEdit.text()
        txt = ''
        isValid = True
        if len(ssid) < self.buoy.accessPoint.ssid_MinLength:
            txt += f'SSID should contain at least {self.buoy.accessPoint.ssid_MinLength} caracters. '
            isValid = False
        elif len(ssid) > self.buoy.accessPoint.ssid_MaxLength:
            txt += f'SSID should contain less than {self.buoy.accessPoint.ssid_MaxLength} caracters. '
            isValid = False
        if not isValid:
            self.showMsgBox(self.warningMsgType, self.warningBoxTitle, txt)
        
        return isValid

    def checkAccessPoint_PWD(self):
        pwd = self.accessPoint_PWD_lineEdit.text()
        txt = ''
        isValid = True
        if len(pwd) < self.buoy.accessPoint.pwd_MinLength:
            txt += f'Password should contain at least {self.buoy.accessPoint.pwd_MinLength} caracters. '
            isValid = False
        elif len(pwd) > self.buoy.accessPoint.pwd_MaxLength:
            txt += f'Password should contain less than {self.buoy.accessPoint.pwd_MaxLength} caracters. '
            isValid = False
        elif not any(c in self.buoy.accessPoint.pwd_RequiredCharacter for c in pwd):
            txt += f'Password should contain at least one special character: {self.buoy.accessPoint.pwd_RequiredCharacter}'
            isValid = False

        if not isValid:
            self.showMsgBox(self.warningMsgType, self.warningBoxTitle, txt)

        return isValid

    def confirmWifiPSK(self):
        psk = self.wifi_PSK_lineEdit.text()
        confirm_psk = self.wifi_ConfirmPSK_lineEdit.text()
        isValid = True
        if psk != confirm_psk:
            isValid = False 
            txt = 'Wifi passwords are not identical!'
            self.showMsgBox(self.warningMsgType, self.warningBoxTitle, txt)
        
        return isValid

    def confirmAccessPointPWD(self):
        psk = self.accessPoint_PWD_lineEdit.text()
        confirm_psk = self.accessPoint_ConfirmPWD_lineEdit.text()
        isValid = True
        if psk != confirm_psk:
            isValid = False 
            txt = 'Access Point passwords are not identical!'
            self.showMsgBox(self.warningMsgType, self.warningBoxTitle, txt)
        
        return isValid

    def saveConfig(self):
        # Save configuration file for later use  
        configIsValid = self.checkConfig()
        if configIsValid:
            self.getConfig()
            # dest = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
            dest = self.saveFileDialog()
            self.buoy.writeMainConfig(path=dest)
            
    def loadConfig(self):
        src = self.openFileDialog() # Get filepath
        self.buoy.readConfig(path=src) # Read config from src file 
        self.updateContent()
    
    def updateContent(self):
        # Fill UI with parameters loaded into buoy object
        # WiFi 
        self.wifi_SSID_lineEdit.setText(self.buoy.wifi.ssid)
        self.wifi_PSK_lineEdit.setText(self.buoy.wifi.psk)
        self.wifi_ConfirmPSK_lineEdit.setText(self.buoy.wifi.psk)

        # AccessPoint 
        self.accessPoint_SSID_lineEdit.setText(self.buoy.accessPoint.ssid)
        self.accessPoint_PWD_lineEdit.setText(self.buoy.accessPoint.wpa_passphrase)
        self.accessPoint_ConfirmPWD_lineEdit.setText(self.buoy.accessPoint.wpa_passphrase)

        
        
    def validateConfig(self):
        # Save configuration file 
        configIsValid = self.checkConfig()
        if configIsValid:
            self.getConfig()
            self.buoy.writeMainConfig()
            self.configIsSaved = True
            
    def transferConfig(self):       
        if self.configIsSaved:
            dest = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
            self.buoy.copyMainConfigFileToSDCard(dest)
        else: 
            self.saveConfig()
            dest = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
            self.buoy.copyMainConfigFileToSDCard(dest)
    
    def checkConfig(self):
        wifiIsValid = self.checkWifi()
        accessPointIsValid = self.checkAccessPoint()
        return wifiIsValid & accessPointIsValid

    def checkWifi(self):
        ssidIsValid = self.checkWifi_SSID()
        pskIsValid = self.checkWifi_PSK()
        pskConfirm = self.confirmWifiPSK()
        return ssidIsValid & pskIsValid & pskConfirm

    def checkAccessPoint(self):
        ssidIsValid = self.checkAccessPoint_SSID()
        pwdIsValid = self.checkAccessPoint_PWD()
        pwdConfirm = self.confirmAccessPointPWD()
        return ssidIsValid & pwdIsValid & pwdConfirm

    def getConfig(self):
        self.getWifiConfig()
        self.getAccessPointConfig()
    
    def getWifiConfig(self):
        self.buoy.wifi.ssid = self.wifi_SSID_lineEdit.text()
        self.buoy.wifi.psk = self.wifi_PSK_lineEdit.text()

    def getAccessPointConfig(self):
        self.buoy.accessPoint.ssid = self.accessPoint_SSID_lineEdit.text()
        self.buoy.accessPoint.wpa_passphrase = self.accessPoint_PWD_lineEdit.text()
    
    def showMsgBox(self, MsgType, title, text):
        """Display a custom pop up message box to inform user.

        Args:
            MsgType (string): Type of message box to display ('Information' or 'Warning').
            title (string): Message box title.
            text (string): Text to display in the message box.
        """
        msg = QMessageBox(self)
        if MsgType == 'Information':
            msg.setIcon(QMessageBox.Information)
        elif MsgType == 'Warning':
            msg.setIcon(QMessageBox.Warning)

        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
    def saveFileDialog(self):
        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        # fileName, _ = QFileDialog.getSaveFileName(self,"Save configuration","","Text Files (*.txt)", options=options)
        fileName, _ = QFileDialog.getSaveFileName(self, "Save configuration", "", "Text Files (*.txt)")
        return fileName

    def openFileDialog(self):
            fileName, _ = QFileDialog.getOpenFileName(self, "Load configuration", "", "Text Files (*.txt)")
            return fileName
        
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = BuoyUI(window)
    window.show()
    sys.exit(app.exec_())
