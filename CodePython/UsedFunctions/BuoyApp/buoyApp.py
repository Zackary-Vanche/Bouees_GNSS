import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QMainWindow, QPushButton, QLineEdit, QProgressBar, QCheckBox, QSpinBox
from PyQt5 import QtCore # Timer (to remove)
from PyQt5 import uic
# from mainWindow import *
from buoy import *

# Live data 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import pandas as pd
import time
import pynmea2
import paramiko  # library for SSH
import numpy as np 

from raw_data_in_real_time import *
from AccessPoint.AccessPoint import *

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class APConnectionUI(QMainWindow):
    def __init__(self, mainUI):
        super(APConnectionUI, self).__init__()
        
        # Load the ui file 
        uic.loadUi(r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\buoyApp\AP_ConnectionDialogWindow.ui", self)
        self.mainUI = mainUI
        
        ################################################
        #######        Widgets definition        #######
        ################################################
        self.loadConfig_pushButton = self.findChild(QPushButton, "loadConfig_pushButton")
        self.connectToAP_pushButton = self.findChild(QPushButton, "connectToAP_pushButton")
        self.accessPoint_SSID_lineEdit = self.findChild(QLineEdit, "accessPoint_SSID_lineEdit")
        self.accessPoint_PWD_lineEdit = self.findChild(QLineEdit, "accessPoint_PWD_lineEdit")
        self.accessPoint_ConfirmPWD_lineEdit = self.findChild(QLineEdit, "accessPoint_ConfirmPWD_lineEdit")
        self.waitConnection_progressBar = self.findChild(QProgressBar, "waitConnection_progressBar")

        ################################################
        #######          Slots definition        #######
        ################################################        
        self.loadConfig_pushButton.clicked.connect(self.loadConfig)
        self.connectToAP_pushButton.clicked.connect(self.connectToAP)
        
        self.ap_ssid = 'buoyAccessPoint'
        self.ap_pwd = 'password!'
        
    def connectToAP(self):
        """ Try to connect to buoy access point if available. """
        
        self.ap_ssid = self.accessPoint_SSID_lineEdit.text()
        self.ap_pwd = self.accessPoint_PWD_lineEdit.text()
        
        # Time between two excecution of APRoutine.sh
        tot_time_to_wait = 15 * 60
        
        set_ap_profile(self.ap_ssid, self.ap_pwd)
        
        start_time = time.time()
        add_accessPoint_profile()
        self.mainUI.ap_is_connected = APisConnected(ssid=self.ap_ssid)
        
        while not self.mainUI.ap_is_connected:

            if APisAvailable(ssid=self.ap_ssid):
                # buoy AP is available 
                print("Attempting to connect to buoy..\n")
                cmd = f'netsh wlan connect name="{self.ap_ssid}" interface="{INTERFACE}"'
                result = sp.run(cmd, shell=True, stdout=sp.DEVNULL)
                time.sleep(5)
                if APisConnected(ssid=self.ap_ssid):
                    print("Connection to buoy successful !\n")
                    self.mainUI.ap_is_connected = True
                    self.close()
                else:
                    print("Connection to buoy failed !\n")
                    self.mainUI.ap_is_connected = False
                    
            else:
                # self.waitConnection_progressBar.setMaximum(0)
                # buoy AP is out of range or not activated
                elapsed_time = np.round(time.time() - start_time, 0)
                # self.waitConnection_progressBar.setValue(elapsed_time / tot_time_to_wait)
                if elapsed_time < 60:
                    print(f"Buoy AP not available,  elapsed time = {elapsed_time}s.\n")
                elif elapsed_time < 3600:
                    elapsed_time_min = elapsed_time // 60
                    elapsed_time_sec = elapsed_time % 60
                    print(f"Buoy AP not available,  elapsed time = {elapsed_time_min}m, {elapsed_time_sec}s.\n")

            time.sleep(5)
        self.close()


    def openFileDialog(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Load configuration", "", "Text Files (*.txt)")
        return fileName
        
    def loadConfig(self):
            src = self.openFileDialog() # Get filepath
            self.mainUI.buoy.readConfig(path=src) # Read config from src file 
            self.updateContent()
            
    def updateContent(self):
        # AccessPoint 
        self.accessPoint_SSID_lineEdit.setText(self.mainUI.buoy.accessPoint.ssid)
        self.accessPoint_PWD_lineEdit.setText(self.mainUI.buoy.accessPoint.wpa_passphrase)
        self.accessPoint_ConfirmPWD_lineEdit.setText(self.mainUI.buoy.accessPoint.wpa_passphrase)
        
class BuoyUI(QMainWindow):
    def __init__(self):
        super(BuoyUI, self).__init__()
        
        # Load the ui file 
        uic.loadUi(r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\buoyApp\buoyApp.ui", self)
        # uic.loadUi("mainWindow.ui", self)

        ################################################
        #######        Widgets definition        #######
        ################################################
        # QPushButton
        self.validateConfig_pushButton = self.findChild(QPushButton, "validateConfig_pushButton")
        self.saveConfig_pushButton = self.findChild(QPushButton, "saveConfig_pushButton")
        self.transferConfig_pushButton = self.findChild(QPushButton, "transferConfig_pushButton")
        self.loadConfig_pushButton = self.findChild(QPushButton, "loadConfig_pushButton")
        # QLineEdit 
        self.wifi_SSID_lineEdit = self.findChild(QLineEdit, "wifi_SSID_lineEdit")
        self.wifi_PSK_lineEdit = self.findChild(QLineEdit, "wifi_PSK_lineEdit")
        self.wifi_ConfirmPSK_lineEdit = self.findChild(QLineEdit, "wifi_ConfirmPSK_lineEdit")
        self.accessPoint_SSID_lineEdit = self.findChild(QLineEdit, "accessPoint_SSID_lineEdit")
        self.accessPoint_PWD_lineEdit = self.findChild(QLineEdit, "accessPoint_PWD_lineEdit")
        self.accessPoint_ConfirmPWD_lineEdit = self.findChild(QLineEdit, "accessPoint_ConfirmPWD_lineEdit")

        # QCheckBox
        self.available_GNSS_constellations = ['GPS', 'SBAS', 'Galileo', 'BeiDou', 'QZSS', 'GLONASS']
        self.GNSS_checkBox = {gnss_cons: self.findChild(QCheckBox, f"{gnss_cons}_checkBox") for gnss_cons in self.available_GNSS_constellations}
            
        self.available_METEO_properties = ['temperature', 'pressure', 'humidity']
        self.METEO_checkBox = {prop: self.findChild(QCheckBox, f"{prop}_checkBox") for prop in self.available_METEO_properties}
                 
        # QSpinBox
        self.gnss_acquisitionPeriod_spinBox = self.findChild(QSpinBox, "gnss_acquisitionPeriod_spinBox")
        self.meteo_acquisitionPeriod_spinBox = self.findChild(QSpinBox, "meteo_acquisitionPeriod_spinBox")
        
        ################################################
        #######          Slots definition        #######
        ################################################
        # Button control
        self.validateConfig_pushButton.clicked.connect(self.validateConfig)
        self.saveConfig_pushButton.clicked.connect(self.saveConfig)
        self.transferConfig_pushButton.clicked.connect(self.transferConfig)
        self.loadConfig_pushButton.clicked.connect(self.loadConfig)
        # Text edited
        self.wifi_PSK_lineEdit.textEdited.connect(self.resetWifi_PSKConfirm)
        self.accessPoint_PWD_lineEdit.textEdited.connect(self.resetAccessPoint_PWDConfirm)
        # Text editing finished
        self.wifi_SSID_lineEdit.editingFinished.connect(self.checkWifi_SSID)
        self.wifi_PSK_lineEdit.editingFinished.connect(self.checkWifi_PSK)
        self.accessPoint_SSID_lineEdit.editingFinished.connect(self.checkAccessPoint_SSID)
        self.accessPoint_PWD_lineEdit.editingFinished.connect(self.checkAccessPoint_PWD)

        ################################################
        #######         Configuration page      #######
        ################################################
        # Warning messages 
        self.warningMsgType = 'Warning'
        self.warningBoxTitle = 'Warning, invalid entry!'
        self.infoMsgType = 'Information'

        # Buoy object 
        self.buoy = Buoy() # TODO: replace Buoy by Buoy_V2
        
        # Boolean to track save status 
        self.configIsSaved = False
        
        ################################################
        #######           Access point          #######
        ################################################
        self.ap_is_connected = APisConnected(ssid='buoyAccessPoint')
        self.ap_connection_window = None
        
        ################################################
        #######             Live data            #######
        ################################################
        # TODO: update to ask for user input and handle connection process 
        self.hostname = '192.168.4.1'
        # self.hostname = '192.168.43.124'
        self.username = 'pi'
        self.password = 'hydro'

        
        # GNSS window 
        self.show_live_data_GNSS_pushButton.clicked.connect(self.plot_live_GNSS_data)
        self.gnss_items_to_display = ['hdop', 'vdop', 'pdop', 'snr', 'pos']
        gnss_plots = ['dop', 'snr', 'pos']
        self.canvas_GNSS = {item: MplCanvas(self, width=5, height=4, dpi=100) for item in gnss_plots}
        self.verticalLayout_data_GNSS = {item: getattr(self, f'verticalLayout_data_{item}') for item in gnss_plots}
        
        for item in gnss_plots:
            self.verticalLayout_data_GNSS[item].addWidget(self.canvas_GNSS[item])
            
        self._plot_ref_GNSS = {item: None for item in gnss_plots} # reference to the plotted line
        
        # Initialize DOP figure
        self.canvas_GNSS['dop'].axes.set_ylabel('DOP')
        self.canvas_GNSS['dop'].axes.set_xlabel('Time')
        self.canvas_GNSS['dop'].axes.tick_params(axis='x', labelrotation = 20)
        self.canvas_GNSS['dop'].axes.legend(labels=['hdop', 'vdop', 'pdop'], loc='upper left')
        self.canvas_GNSS['dop'].axes.set_title('Dilution of precision')
        self.canvas_GNSS['dop'].figure.set_tight_layout(True)
        
        
        # Initialize position figure
        self.canvas_GNSS['pos'].axes.set_xlabel('E [m]')
        self.canvas_GNSS['pos'].axes.set_ylabel('N [m]')
        self.canvas_GNSS['pos'].axes.ticklabel_format(axis='both', useOffset=False, style='plain')
        self.canvas_GNSS['pos'].axes.grid()
        self.canvas_GNSS['pos'].axes.set_title('UTM zone')
        self.canvas_GNSS['pos'].axes.tick_params(axis='x', labelrotation=20)
        self.canvas_GNSS['pos'].axes.locator_params(axis='both', nbins=5)
        self.canvas_GNSS['pos'].figure.set_tight_layout(True)
        
        # Initialize snr figure
        self.canvas_GNSS['snr'].axes.set_xlabel('PRN')
        self.canvas_GNSS['snr'].axes.set_ylabel('SNR')
        self.canvas_GNSS['snr'].axes.set_title('Signal to noise ratio')
        self.canvas_GNSS['snr'].axes.tick_params(axis='x', labelrotation = 90)
        self.canvas_GNSS['snr'].figure.set_tight_layout(True)

        # Initialise datafram
        self.nb_gnss_values_to_display = 100
        data_GNSS_keys = ['time', 'x_utm', 'y_utm', 'n_utm', 'hdop', 'vdop', 'pdop']
        self.prn = []
        for i_prn in range(12*4):
            if i_prn <=9:
                prn = f'0{i_prn}'
            else:
                prn = str(i_prn)
            data_GNSS_keys += [f'snr_prn_{prn}']
            self.prn.append(prn)
        
        # Initialize datframe 
        self.data_GNSS = pd.DataFrame({key: np.zeros((self.nb_gnss_values_to_display)) for key in data_GNSS_keys})
        #Initialise time vector 
        for i in range(len(self.data_GNSS.time)):
            now = datetime.datetime.now()
            self.data_GNSS.time.iloc[i] = now.astimezone(datetime.timezone.utc).time() # To match nmea utc time 
            plt.pause(0.001)

        # METEO window 
        
        self.show_live_data_METEO_pushButton.clicked.connect(self.plot_live_METEO_data)
        self.meteo_items_to_display = ['pressure', 'temperature', 'humidity']
        self.canvas_METEO = {item: MplCanvas(self, width=5, height=4, dpi=100) for item in self.meteo_items_to_display}
        self.verticalLayout_data_METEO = {item: getattr(self, f'verticalLayout_data_{item}') for item in self.meteo_items_to_display}
        
        for item in self.meteo_items_to_display:
            self.verticalLayout_data_METEO[item].addWidget(self.canvas_METEO[item])
            
        self._plot_ref_METEO = {item: None for item in self.meteo_items_to_display} # reference to the plotted line            
        self.y_axes_ranges_METEO = {'pressure': 50, 'temperature': 10,'humidity': 50} # Ranges to initialize plots 
        self.default_value_METEO = {'pressure': 1013, 'temperature': 21,'humidity': 50} # Default values to initializes plots 
        self.y_axes_offset_METEO = {'pressure': 5, 'temperature': 2,'humidity': 5} # Visual y ranges to apply 
        
        for item in self.meteo_items_to_display:
            self.canvas_METEO[item].axes.set_ylim([self.default_value_METEO[item] - self.y_axes_ranges_METEO[item], \
                    self.default_value_METEO[item] + self.y_axes_ranges_METEO[item]])
        
        # Initialise datafram
        self.nb_meteo_values_to_display = 10
        data_METEO_keys = ['time'] + self.meteo_items_to_display
        self.data_METEO = pd.DataFrame({key: np.empty((self.nb_meteo_values_to_display)) for key in data_METEO_keys})
        # Initialise time vector 
        for i in range(len(self.data_METEO.time)):
            self.data_METEO.time.iloc[i] = datetime.datetime.now()
            plt.pause(0.001)

        # Initialise figures 
        self.canvas_METEO['pressure'].axes.set_xlabel('Time')
        self.canvas_METEO['pressure'].axes.set_ylabel('Pressure [hPa]')
        # self.canvas_METEO['pressure'].axes.tick_params(axis='x', labelrotation = 10)
        self.canvas_METEO['pressure'].figure.set_tight_layout(True)
        
        self.canvas_METEO['temperature'].axes.set_ylabel('Temperature [°C]')
        # self.canvas_METEO['temperature'].axes.tick_params(axis='x', labelrotation = 10)
        self.canvas_METEO['temperature'].figure.set_tight_layout(True)

        self.canvas_METEO['humidity'].axes.set_ylabel('Humidity [%]')
        # self.canvas_METEO['humidity'].axes.tick_params(axis='x', labelrotation = 10)
        self.canvas_METEO['humidity'].figure.set_tight_layout(True)

                        
        # Show app 
        self.show()

    ################################################
    #######       Live data functions        #######
    ################################################
    
    ### METEO data ###
    def plot_live_METEO_data(self):
        
        # self.ap_is_connected = APisConnected(ssid=self.ap_ssid)
        
        if self.ap_is_connected: # user connected to ap 
            
            # Initialize an SSH client
            self.client_METEO, self.channel_METEO = init_ssh_client(self.hostname, self.username, self.password)
            self.channel_METEO.send("tail -f /home/pi/data/METEO/logMETEO.txt\n") # Read meteo data
            self.channel_METEO_init = True 
            
            self.update_METEO_plot()

            # Setup a timer to trigger the redraw by calling update_plot.
            self.timer_meteo = QtCore.QTimer()
            self.timer_meteo.setInterval(11000) # TODO: handle different sampling rates 
            self.timer_meteo.timeout.connect(self.update_METEO_plot)
            self.timer_meteo.start()
        
        else: # user not connected to ap
            self.show_connection_window()
            
    
    def get_meteo_data(self):
        # self.channel_METEO.send("tail -1 /home/pi/data/METEO/logMETEO.txt\n") # Read last meteo data 

        if self.channel_METEO_init:
            time.sleep(1)
            self.channel_METEO_init = False
            
        line = self.channel_METEO.recv(1024).decode("utf-8")
        line = line.split('\r\n')
        line = line[-2]
        # print(line)

        try:
            meteo_data = line.split(",") 
            timestamp = datetime.datetime.strptime(meteo_data[0], '%Y-%m-%d %H:%M:%S')
            data_to_append = pd.DataFrame({'time': [timestamp], 
                                        'temperature': [float(meteo_data[1])], 
                                        'pressure': [float(meteo_data[2])], 
                                        'humidity': [float(meteo_data[3])]})
            self.data_METEO = pd.concat([self.data_METEO, data_to_append])
        except:
            print(f'Error while parsing meteo data. Line to parse: {line}')
            
        # Keep limited data size 
        self.data_METEO = self.data_METEO.set_index(np.arange(0, len(self.data_METEO.time)))
        if len(self.data_METEO.time) > self.nb_meteo_values_to_display:
            self.data_METEO = self.data_METEO.iloc[-self.nb_meteo_values_to_display:]
        
    def update_METEO_plot(self):
        self.get_meteo_data() # Get last data 
        
        # Get xticks position and labels to display time on x-axis 
        xticks_pos = np.array([i for i in range(len(self.data_METEO.time))])
        xticks_label = np.array([self.data_METEO.time.iloc[i].time() for i in range(len(self.data_METEO.time))])
                     
        for item in self.meteo_items_to_display:
            # Note: we no longer need to clear the axis.
            if self._plot_ref_METEO[item] is None:
                # First time we have no plot reference, so do a normal plot.
                plot_refs = self.canvas_METEO[item].axes.plot(np.array(self.data_METEO[item]), color='k', marker='+')
                self._plot_ref_METEO[item] = plot_refs[0]
            else:
                # We have a reference, we can use it to update the data for that line.
                self._plot_ref_METEO[item].set_ydata(self.data_METEO[item])
                
            # Trigger the canvas to update and redraw.
            self.canvas_METEO[item].axes.set_ylim([np.min(self.data_METEO[item]) - self.y_axes_offset_METEO[item],
                                                   np.max(self.data_METEO[item]) + self.y_axes_offset_METEO[item]])

            self.canvas_METEO[item].axes.set_xticks(xticks_pos)
            self.canvas_METEO[item].axes.set_xticklabels(xticks_label)
            self.canvas_METEO[item].draw()

    ### GNSS data ###
    def plot_live_GNSS_data(self):
        
        # self.ap_is_connected = APisConnected(ssid=self.ap_ssid)
        
        if self.ap_is_connected: # user connected to ap 
            
            # Initialize an SSH client
            self.client_GNSS, self.channel_GNSS = init_ssh_client(self.hostname, self.username, self.password)
            self.channel_GNSS.send("gpspipe -r\n") # command to read NMEA sentences
            self.channel_GNSS_init = True 

            self.update_GNSS_plot()

            # Setup a timer to trigger the redraw by calling update_plot.
            self.timer_gnss = QtCore.QTimer()
            self.timer_gnss.setInterval(1200) # TODO: handle different sampling rates 
            self.timer_gnss.timeout.connect(self.update_GNSS_plot)
            self.timer_gnss.start()
        
        else: # user not connected to ap
            self.show_connection_window()
            
        
    def get_gnss_data(self):
        
        if self.channel_GNSS_init:
            time.sleep(3)
            # self.channel_GNSS_init = False 
            lines = self.channel_GNSS.recv(3000).decode("utf-8")
            lines = lines.split('\n$GPZDA')
            sequence = '\n$GPZDA' + lines[-2]
        else:
            lines = self.channel_GNSS.recv(3000).decode("utf-8")
            lines = lines.split('\n$GPZDA')
            # Avoid issue if decoded lines start with $GPZDA
            if lines[-1][0:6] != '$GPZDA':
                sequence = '$GPZDA' + lines[-1]
            else:
                sequence = lines[-1]
            
        sentences = sequence.split('\r\r')
        sentences = sentences[:-1]

        data_GNSS_dic = {}
        # print(sentences)
        
        try:
            # GPZDA
            sentence_gpzda = sentences[0]
            msg = pynmea2.parse(sentence_gpzda, check=False)
            # data_GNSS_dic['time'] = [msg.timestamp.strftime('%H:%M:%S')]
            data_GNSS_dic['time'] = [msg.timestamp]
            
            # GPGGA
            sentence_gpgga = sentences[1]
            msg = pynmea2.parse(sentence_gpgga, check=False)
            x_utm, y_utm, n_utm = proj_to_UTM(np.array(msg.longitude), np.array(msg.latitude)) # Proj to UTM                
            data_GNSS_dic['x_utm'] = [x_utm]
            data_GNSS_dic['y_utm'] = [y_utm]
            data_GNSS_dic['n_utm'] = [n_utm]
            
            # GPRMC
            sentence_gprmc = sentences[2] # Not used yet
            
            # GPGSA
            sentence_gpgsa = sentences[3]
            msg = pynmea2.parse(sentence_gpgsa, check=False)
            data_GNSS_dic['hdop'] = [msg.hdop]
            data_GNSS_dic['vdop'] = [msg.vdop]
            data_GNSS_dic['pdop'] = [msg.pdop]
    
            # GPGBS
            sentence_gpgsb = sentences[4] # Not used yet
            
            for prn in self.prn:
                data_GNSS_dic[f'snr_prn_{prn}'] = [np.nan] 
                
            # GPGSV
            for i_gsv in range(5, len(sentences)):
                sentence_gpgsv = sentences[i_gsv]
                msg = pynmea2.parse(sentence_gpgsv, check=False)

                for i in range(1, 5):
                    idx = msg.name_to_idx[f'snr_{i}']
                    idx_prn = msg.name_to_idx[f'sv_prn_num_{i}']

                    if idx <= len(msg.data)-1:
                        prn = msg.data[idx_prn]
                        # For the moment keep only GPS satelites with prn <= 32
                        if prn in self.prn:
                            data_GNSS_dic[f'snr_prn_{prn}'] = [float(msg.data[idx])]

            data_to_append = pd.DataFrame(data_GNSS_dic)
            self.data_GNSS = pd.concat([self.data_GNSS, data_to_append])
            
            # Keep limited data size 
            self.data_GNSS = self.data_GNSS.set_index(np.arange(0, len(self.data_GNSS.time)))
            self.data_GNSS = self.data_GNSS.iloc[-self.nb_gnss_values_to_display:]
            
            # Initialise entire array to the first value when reading data for the first time
            if self.channel_GNSS_init:
                for key in self.data_GNSS.keys():
                    if key != 'time':
                        self.data_GNSS[key][:] = self.data_GNSS[key].iloc[-1] 
                self.channel_GNSS_init = False
        except:
            print(f'Error while parsing NMEA data. Sequence to parse: {sentences}')
            
      
    def update_GNSS_plot(self):
        # Drop off the first y element, append a new one.
        self.get_gnss_data() # Update dataframe 
        
        ### DOPS ###
        self.canvas_GNSS['dop'].axes.cla() # For some reason it seems impossible to correctly updating the DOP plot at 1hz without clearing it manually before 
        
        dop_color = {'hdop': 'b', 'vdop': 'k', 'pdop': 'g'}
        # Note: we no longer need to clear the axis.
        if self._plot_ref_GNSS['dop'] is None:
            # First time we have no plot reference, so do a normal plot.
            
            for dop in ['hdop', 'vdop', 'pdop']:
            # for dop in ['pdop']:
                plot_refs = self.canvas_GNSS['dop'].axes.plot(self.data_GNSS[dop], label=dop, color=dop_color[dop])
                self._plot_ref_GNSS[dop] = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            for dop in ['hdop', 'vdop', 'pdop']:
                self._plot_ref_GNSS[dop].set_ydata(self.data_GNSS[dop])
                
        # Reset all plot 
        self.canvas_GNSS['dop'].axes.set_title('Dilution of precision')
        self.canvas_GNSS['dop'].axes.set_ylabel('DOP')
        self.canvas_GNSS['dop'].axes.set_xlabel('Time')
        self.canvas_GNSS['dop'].axes.tick_params(axis='x', labelrotation = 20)
        self.canvas_GNSS['dop'].axes.legend(labels=['hdop', 'vdop', 'pdop'], loc='upper left')
        
        xticks_pos = np.array([i for i in range(len(self.data_GNSS.time))])
        xticks_label = np.array([self.data_GNSS.time.iloc[i] for i in range(len(self.data_GNSS.time))])
        nb_ticks_to_display = 5
        idx_ticks_to_display = np.linspace(1, len(xticks_pos)-1, nb_ticks_to_display, dtype=int)# subsampling ticks for clarity
        self.canvas_GNSS['dop'].axes.set_xticks(xticks_pos[idx_ticks_to_display])
        self.canvas_GNSS['dop'].axes.set_xticklabels(xticks_label[idx_ticks_to_display])
            
        # Trigger the canvas to update and redraw.
        self.canvas_GNSS['dop'].draw()

            
        ### POS ###
        # Note: we no longer need to clear the axis.
        if self._plot_ref_GNSS['pos'] is None:
            # First time we have no plot reference, so do a normal plot.
            plot_refs = self.canvas_GNSS['pos'].axes.plot(np.array(self.data_GNSS.x_utm),
                                                          np.array(self.data_GNSS.y_utm),
                                                          color='k', linestyle='--',
                                                          marker='+', markersize=10)

            self._plot_ref_GNSS['pos'] = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref_GNSS['pos'].set_xdata(np.array(self.data_GNSS.x_utm))
            self._plot_ref_GNSS['pos'].set_ydata(np.array(self.data_GNSS.y_utm))
                        
        # Trigger the canvas to update and redraw.
        x_offset = 2
        y_offset = 2
        self.canvas_GNSS['pos'].axes.set_xlim([np.min(self.data_GNSS.x_utm)-x_offset, np.max(self.data_GNSS.x_utm)+x_offset])
        self.canvas_GNSS['pos'].axes.set_ylim([np.min(self.data_GNSS.y_utm)-y_offset, np.max(self.data_GNSS.y_utm)+y_offset])
        self.canvas_GNSS['pos'].axes.set_title(f'UTM zone n°{int(self.data_GNSS.n_utm.iloc[-1])}')
        self.canvas_GNSS['pos'].draw()
        
        ### SNR ### 
        all_snr = np.array([self.data_GNSS[f'snr_prn_{prn}'].iloc[-1] for prn in self.prn])
        if self._plot_ref_GNSS['snr'] is None:
            # First time we have no plot reference, so do a normal plot.
            plot_refs = self.canvas_GNSS['snr'].axes.bar(self.prn,
                                                          all_snr)

            self._plot_ref_GNSS['snr'] = plot_refs
        else:
            # We have a reference, we can use it to update the data for that line.
            for rect, snr in zip(self._plot_ref_GNSS['snr'], all_snr):
                rect.set_height(snr)
            
        self.canvas_GNSS['snr'].draw()
        
        

            

    ################################################
    #######     Configuration functions      #######
    ################################################
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
        
        # GNSS
        self.gnss_acquisitionPeriod_spinBox.setValue( int(self.buoy.gnssReceiver.acquisitionPeriod) )
        for gnss_constellation in self.available_GNSS_constellations:
            self.GNSS_checkBox[gnss_constellation].setChecked( bool( int(getattr(self.buoy.gnssReceiver, gnss_constellation.lower())) ) )
            
        # Meteo
        self.meteo_acquisitionPeriod_spinBox.setValue( int(self.buoy.meteoSensor.acquisitionPeriod) )
        for meteo_property in self.available_METEO_properties:
            self.METEO_checkBox[meteo_property].setChecked( bool( int(getattr(self.buoy.meteoSensor, meteo_property)) ) )

        
    def validateConfig(self):
        # Save configuration file 
        configIsValid = self.checkConfig()
        if configIsValid:
            self.getConfig()
            self.buoy.writeMainConfig()
            self.configIsSaved = True
            
    def transferConfig(self):       
        if self.configIsSaved:
            dest = QFileDialog.getExistingDirectory(self, 'Select Folder')
            self.buoy.copyMainConfigFileToSDCard(dest)
        else: 
            self.validateConfig()
            dest = QFileDialog.getExistingDirectory(self, 'Select Folder')
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
        self.getGNSSConfig()
        self.getMETEOConfig()
    
    def getWifiConfig(self):
        self.buoy.wifi.ssid = self.wifi_SSID_lineEdit.text()
        self.buoy.wifi.psk = self.wifi_PSK_lineEdit.text()

    def getAccessPointConfig(self):
        self.buoy.accessPoint.ssid = self.accessPoint_SSID_lineEdit.text()
        self.buoy.accessPoint.wpa_passphrase = self.accessPoint_PWD_lineEdit.text()
        
    def getGNSSConfig(self):
        for gnss_constellation in self.available_GNSS_constellations:
            gnss_checkBox = self.GNSS_checkBox[gnss_constellation]
            if gnss_checkBox.isChecked():
                setattr(self.buoy.gnssReceiver, gnss_constellation.lower(), 1) 
            else:
                setattr(self.buoy.gnssReceiver, gnss_constellation.lower(), 0) 
        self.buoy.gnssReceiver.acquisitionPeriod = int(self.gnss_acquisitionPeriod_spinBox.value())
        
    def getMETEOConfig(self):
        for meteo_property in self.available_METEO_properties:
            meteo_checkBox = self.METEO_checkBox[meteo_property]
            if meteo_checkBox.isChecked():
                setattr(self.buoy.meteoSensor, meteo_property, 1) 
            else:
                setattr(self.buoy.meteoSensor, meteo_property, 0) 
        self.buoy.meteoSensor.acquisitionPeriod = int(self.meteo_acquisitionPeriod_spinBox.value())

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

    ################################################
    #######    Connection to access point    #######
    ################################################
    def show_connection_window(self):
        if self.ap_connection_window is None:
            self.ap_connection_window = APConnectionUI(self)
            self.ap_connection_window.show()

        else:
            self.ap_connection_window.close()  # Close window.
            self.ap_connection_window = None  # Discard reference.
        
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    UIWindow = BuoyUI()
    app.exec_()
