import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
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
        self.sendConfig_pushButton.clicked.connect(self.sendConfig)
        self.wifi_SSID_lineEdit.editingFinished.connect(self.checkWifi_SSID)
        self.wifi_PSK_lineEdit.editingFinished.connect(self.checkWifi_PSK)
        # self.accessPoint_SSID_lineEdit.editingFinished.connect(self.checkAccessPoint_SSID)
        # self.accessPoint_PWD_lineEdit.editingFinished.connect(self.checkAccessPoint_PWD)

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

    def sendConfig(self):
        configIsValid = self.checkConfig()
        if configIsValid:
            self.getConfig()
            self.buoy.writeMainConfig()
            print('Config sent')

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
        msg = QMessageBox(self)
        if MsgType == 'Information':
            msg.setIcon(QMessageBox.Information)
        elif MsgType == 'Warning':
            msg.setIcon(QMessageBox.Warning)

        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = BuoyUI(window)
    window.show()
    sys.exit(app.exec_())
