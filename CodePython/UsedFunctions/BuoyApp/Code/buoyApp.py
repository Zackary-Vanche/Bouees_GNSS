#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Menetrier Baptiste
# Created Date: 04/03/2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""
GUI classes to handle configuration of the buoy and live data visualisation.
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import sys
import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, \
    QMainWindow, QPushButton, QLineEdit, QProgressBar, QCheckBox, \
    QSpinBox, QStatusBar
from PyQt5 import QtCore # Timer 
from PyQt5 import uic

# Live data 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import subprocess as sp
import pandas as pd
import numpy as np 
import pynmea2
import time

from raw_data_in_real_time import *
from AccessPoint import *
from buoy import *

class MplCanvas(FigureCanvas):
    """Class to handle plot in GUI.

    Args:
        FigureCanvas (FigureCanvas)
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class APConnectionUI(QMainWindow):
    """Connection window used to connect to access point. 

    Args:
        QMainWindow (QMainWindow)
    """
    def __init__(self, mainUI):
        super(APConnectionUI, self).__init__()
        
        # Load the ui file 
        # uic.loadUi(r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\buoyApp\UI\AP_ConnectionDialogWindow.ui", self)
        uic.loadUi(r".\UI\AP_ConnectionDialogWindow.ui", self)

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

        if platform.system() == "Windows":
            set_ap_profile(self.ap_ssid, self.ap_pwd)
            add_accessPoint_profile()

        elif platform.system() == "Linux":
            cmd = f'sudo nmcli device wifi rescan'
            status = os.system(cmd)
            

        start_time = time.time()
        self.mainUI.ap_is_connected = APisConnected(self.ap_ssid)
        
        while not self.mainUI.ap_is_connected:

            if APisAvailable(self.ap_ssid):
                # buoy AP is available 
                print("Attempting to connect to buoy..\n")
                if platform.system() == "Windows":
                    cmd = CONNECT_CMD.format(self.ap_ssid)
                elif platform.system() == "Linux":
                    interface = os.popen(INTERFACE_CMD).read().strip()
                    cmd = CONNECT_CMD.format(self.ap_ssid, interface)
                    cmd = f'sudo {cmd}'
                    
                status = os.system(cmd)
                time.sleep(1)
                
                if APisConnected(self.ap_ssid):
                    print("Connection to buoy successful !\n")
                    self.mainUI.ap_is_connected = True
                    self.mainUI.update_status()
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
        """Open dialog file to load configuration.

        Returns:
            str: configuration full path
        """
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
        # uic.loadUi(r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\buoyApp\UI\buoyApp.ui", self)
        uic.loadUi(r".\UI\buoyApp.ui", self)

        ################################################
        #######        Widgets definition        #######
        ################################################

        # QCheckBox
        self.available_GNSS_constellations = ['GPS', 'SBAS', 'Galileo', 'BeiDou', 'QZSS', 'GLONASS']
        self.GNSS_checkBox = {gnss_cons: self.findChild(QCheckBox, f"{gnss_cons}_checkBox") for gnss_cons in self.available_GNSS_constellations}
            
        self.available_METEO_properties = ['temperature', 'pressure', 'humidity']
        self.METEO_checkBox = {prop: self.findChild(QCheckBox, f"{prop}_checkBox") for prop in self.available_METEO_properties}
                 
                
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
        self.buoy = Buoy()
        
        # Boolean to track save status 
        self.configIsSaved = False
        
        ################################################
        #######           Access point          #######
        ################################################
        self.ap_is_connected = APisConnected(ssid='buoyAccessPoint')
        self.update_status()
        self.ap_connection_window = None
        
        ################################################
        #######             Live data            #######
        ################################################
        # TODO: update to ask for user input and handle connection process 
        self.hostname = '192.168.4.1'
        # self.hostname = '192.168.43.124'
        self.username = 'pi'
        self.password = 'hydro'

        self.plot_processing_time = 1000
        self.timer_min_interval = 500
        
        # GNSS window 
        self.gnss_livePlot_initialised = False 
        self.show_live_data_GNSS_pushButton.clicked.connect(self.plot_live_GNSS_data)
        self.stop_live_data_GNSS_pushButton.clicked.connect(self.stop_gnssLive)
        
        self.nmea_tmpfile = "/tmp/live_data_nmea.txt"
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
        self.meteo_logfile = "/home/pi/data/METEO/logMETEO.txt"
        self.meteo_settingfile = "/home/pi/ScriptPython/capteur_settings.txt"
        self.meteo_livePlot_initialised = False 
        
        self.show_live_data_METEO_pushButton.clicked.connect(self.plot_live_METEO_data)
        self.stop_live_data_METEO_pushButton.clicked.connect(self.stop_meteoLive)
        
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
        self.canvas_METEO['pressure'].figure.set_tight_layout(True)
        
        self.canvas_METEO['temperature'].axes.set_ylabel('Temperature [°C]')
        self.canvas_METEO['temperature'].figure.set_tight_layout(True)

        self.canvas_METEO['humidity'].axes.set_ylabel('Humidity [%]')
        self.canvas_METEO['humidity'].figure.set_tight_layout(True)

                        
        # Show app 
        self.show()

    ################################################
    #######       Live data functions        #######
    ################################################
    
    ### METEO data ###
    def plot_live_METEO_data(self):
        """ Initialise meteo plot. """
                
        if self.ap_is_connected: # user connected to ap 
            
            # Initialize an SSH client
            self.client_METEO, self.channel_METEO = init_ssh_client(self.hostname, self.username, self.password)
            # self.channel_METEO.send("tail -f /home/pi/data/METEO/logMETEO.txt\n") # Read meteo data
            self.channel_METEO_init = True 
            

            # Setup a timer to trigger the redraw by calling update_plot.
            meteo_rate = self.getMeteoRate()
            time.sleep(meteo_rate / 1000 + 0.5) # Wait to make sure nmea sentences are received before reading
            self.timer_meteo = QtCore.QTimer()
            self.timer_meteo.setInterval(max(meteo_rate - self.plot_processing_time, self.timer_min_interval))
            self.timer_meteo.timeout.connect(self.update_METEO_plot)
            self.timer_meteo.start()
        
            self.update_METEO_plot()
            self.meteo_livePlot_initialised = True 
            
        else: # user not connected to ap
            self.show_connection_window()
    
    def getMeteoRate(self):
        """Get current acquisition rate.

        Returns:
            rate: Acquisition rate used by BME280 sensor
        """
        cmd = f"cat {self.meteo_settingfile}"
        stdin, stdout, stderr = self.client_METEO.exec_command(cmd)
        settings = stdout.readlines()[0].split(',')
        rate = int(settings[-2])
        return rate
    
    def get_meteo_data(self):
        """ Read meteo data. """
        
        n_lines_to_read = 2
        cmd = f"tail -n {n_lines_to_read} {self.meteo_logfile}"
        stdin, stdout, stderr = self.client_METEO.exec_command(cmd)
        line = stdout.readlines()[0]

        try:
            meteo_data = line.split(",") 
            timestamp = datetime.datetime.strptime(meteo_data[0], '%d%m%Y %H:%M:%S')
            if meteo_data[1] != '':
                temp = float(meteo_data[1])
            else:
                temp = np.nan
                
            if meteo_data[2] != '':
                pressure = float(meteo_data[2])
            else:
                pressure = np.nan
                
            if meteo_data[3] != '':
                humidity = float(meteo_data[3])
            else:
                humidity = np.nan
                
            data_to_append = pd.DataFrame({'time': [timestamp], 
                                        'temperature': [temp], 
                                        'pressure': [pressure], 
                                        'humidity': [humidity]})
            self.data_METEO = pd.concat([self.data_METEO, data_to_append])
        except:
            print(f'Error while parsing meteo data. Line to parse: {line}')
            
        # Keep limited data size 
        self.data_METEO = self.data_METEO.set_index(np.arange(0, len(self.data_METEO.time)))
        if len(self.data_METEO.time) > self.nb_meteo_values_to_display:
            self.data_METEO = self.data_METEO.iloc[-self.nb_meteo_values_to_display:]
        
    def update_METEO_plot(self):
        """ Update plot with last meteo data. """
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
            if not (np.isnan(np.min(self.data_METEO[item])) or np.isnan(np.max(self.data_METEO[item]))):
                self.canvas_METEO[item].axes.set_ylim([np.min(self.data_METEO[item]) - self.y_axes_offset_METEO[item],
                                                    np.max(self.data_METEO[item]) + self.y_axes_offset_METEO[item]])

            self.canvas_METEO[item].axes.set_xticks(xticks_pos)
            self.canvas_METEO[item].axes.set_xticklabels(xticks_label)
            self.canvas_METEO[item].draw()

    ### GNSS data ###
    def plot_live_GNSS_data(self):
        """ Initialise ssh connection to get real time data from buoy and start QtCore.QtTimer to update plot. """
                
        if self.ap_is_connected: # user connected to ap 
            
            # Initialize an SSH client
            self.client_GNSS, self.channel_GNSS = init_ssh_client(self.hostname, self.username, self.password)
            cmd = f"gpspipe -o {self.nmea_tmpfile} -r"
            self.client_GNSS.exec_command(cmd)
            self.channel_GNSS_init = True 
            
            
            # Setup a timer to trigger the redraw by calling update_plot.
            gnss_rate = self.getUbloxRate() 
            time.sleep(gnss_rate / 1000 + 0.5) # Wait to make sure nmea sentences are received before reading
            self.timer_gnss = QtCore.QTimer()
            self.timer_gnss.setInterval(max(gnss_rate - self.plot_processing_time, self.timer_min_interval))
            self.timer_gnss.timeout.connect(self.update_GNSS_plot)
            self.timer_gnss.start()

            self.update_GNSS_plot()
            self.gnss_livePlot_initialised = True 
            
        else: # user not connected to ap
            self.show_connection_window()
     
    def getUbloxRate(self):
        """ Get current acquisition rate.

        Returns:
            rate: acquisition rate used by the u-blox module
        """
        cmd = "ubxtool -g CFG-RATE-MEAS | fgrep CFG-RATE-MEAS"
        stdin, stdout, stderr = self.client_GNSS.exec_command(cmd)
        rate_level0 = stdout.readlines()[0]
        rate_level0 = rate_level0.split(' ')
        rate = int(rate_level0[-1][:-1])
        return rate
    
    def get_gnss_data(self):
        """ Read NMEA data from buoy. """
        
        n_lines_to_read = 16
        cmd = f"tail -n {n_lines_to_read} {self.nmea_tmpfile}"
        stdin, stdout, stderr = self.client_GNSS.exec_command(cmd)
        lines = stdout.readlines()
        # print(lines)
        
        sequence_complete = False
        sequence = []
        
        try:
            while not sequence_complete:
                nmea_msg = lines.pop()
                # print(nmea_msg)
                sequence.append(nmea_msg)
                if nmea_msg[:6] == '$GPZDA':
                    sequence_complete = True

            sequence.reverse()
            data_GNSS_dic = {}
        
            # GPZDA
            sentence_gpzda = sequence[0]
            msg = pynmea2.parse(sentence_gpzda, check=False)
            # data_GNSS_dic['time'] = [msg.timestamp.strftime('%H:%M:%S')]
            data_GNSS_dic['time'] = [msg.timestamp]
            
            # GPGGA
            sentence_gpgga = sequence[1]
            msg = pynmea2.parse(sentence_gpgga, check=False)
            x_utm, y_utm, n_utm = proj_to_UTM(np.array(msg.longitude), np.array(msg.latitude)) # Proj to UTM                
            data_GNSS_dic['x_utm'] = [x_utm]
            data_GNSS_dic['y_utm'] = [y_utm]
            data_GNSS_dic['n_utm'] = [n_utm]
            
            # GPRMC
            sentence_gprmc = sequence[2] # Not used yet
            
            # GPGSA
            sentence_gpgsa = sequence[3]
            msg = pynmea2.parse(sentence_gpgsa, check=False)
            data_GNSS_dic['hdop'] = [msg.hdop]
            data_GNSS_dic['vdop'] = [msg.vdop]
            data_GNSS_dic['pdop'] = [msg.pdop]

            # GPGBS
            sentence_gpgsb = sequence[4] # Not used yet
            
            for prn in self.prn:
                data_GNSS_dic[f'snr_prn_{prn}'] = [np.nan] 
                
            # GPGSV
            for i_gsv in range(5, len(sequence)):
                sentence_gpgsv = sequence[i_gsv]
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
            print(f'Error while parsing NMEA data. Sequence to parse: {sequence}')
            
      
    def update_GNSS_plot(self):
        """ Update GNSS plot in GUI with last data recorded. """
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
        """ Reset wifi password to empty string in GUI. """
        self.wifi_ConfirmPSK_lineEdit.setText('')
        
    def resetAccessPoint_PWDConfirm(self):
        """ Reset access point password to empty string in GUI. """
        self.accessPoint_ConfirmPWD_lineEdit.setText('')
        
    def checkWifi_SSID(self):
        """ Assert wifi SSID matches basic requirements. 

        Returns:
            bool: True if ok, False otherwise
        """
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
        """ Assert wifi password matches basic requirements

        Returns:
            bool: True if ok, False otherwise
        """
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
        """ Assert access point SSID matches basic requirements.

        Returns:
            _type_: _description_
        """
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
        """ Assert access point password matches basic requirements.

        Returns:
            bool: True if ok, False otherwise
        """
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
        """ Assert password and comfirm password are identical for wifi.

        Returns:
            bool: True if ok, False otherwise
        """
        psk = self.wifi_PSK_lineEdit.text()
        confirm_psk = self.wifi_ConfirmPSK_lineEdit.text()
        isValid = True
        if psk != confirm_psk:
            isValid = False 
            txt = 'Wifi passwords are not identical!'
            self.showMsgBox(self.warningMsgType, self.warningBoxTitle, txt)
        
        return isValid

    def confirmAccessPointPWD(self):
        """ Assert password and comfirm password are identical for access point.

        Returns:
            bool: True if ok, False otherwise
        """
        psk = self.accessPoint_PWD_lineEdit.text()
        confirm_psk = self.accessPoint_ConfirmPWD_lineEdit.text()
        isValid = True
        if psk != confirm_psk:
            isValid = False 
            txt = 'Access Point passwords are not identical!'
            self.showMsgBox(self.warningMsgType, self.warningBoxTitle, txt)
        
        return isValid

    def saveConfig(self):
        """ Save configuration for later use. """
        # Save configuration file for later use  
        configIsValid = self.checkConfig()
        if configIsValid:
            self.getConfig()
            # dest = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
            dest = self.saveFileDialog()
            self.buoy.writeMainConfig(path=dest)
            
    def loadConfig(self):
        """ Load configuration. """
        src = self.openFileDialog() # Get filepath
        self.buoy.readConfig(path=src) # Read config from src file 
        self.updateContent()
    
    def updateContent(self):
        """ Fill GUI with parameters loaded into buoy object.  """

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
        """ Assert configuration is valid and associate each element to the corresponding
        attribute in the Buoy class. """
        # Save configuration file 
        configIsValid = self.checkConfig()
        if configIsValid:
            self.getConfig()
            self.buoy.writeMainConfig()
            self.configIsSaved = True
            
    def transferConfig(self):
        """ Transfert configuration to SD card for deployment. """       
        if self.configIsSaved:
            dest = QFileDialog.getExistingDirectory(self, 'Select Folder')
            self.buoy.copyMainConfigFileToSDCard(dest)
        else: 
            self.validateConfig()
            dest = QFileDialog.getExistingDirectory(self, 'Select Folder')
            self.buoy.copyMainConfigFileToSDCard(dest)
    
    def checkConfig(self):
        """ Assert configuration matches all requirements. 

        Returns:
            bool: True if ok, False otherwise
        """
        wifiIsValid = self.checkWifi()
        accessPointIsValid = self.checkAccessPoint()
        return wifiIsValid & accessPointIsValid

    def checkWifi(self):
        """ Assert wifi configuration matches requirements.

        Returns:
            bool: True if ok, False otherwise
        """
        ssidIsValid = self.checkWifi_SSID()
        pskIsValid = self.checkWifi_PSK()
        pskConfirm = self.confirmWifiPSK()
        return ssidIsValid & pskIsValid & pskConfirm

    def checkAccessPoint(self):
        """ Assert access point configuration matches requirements.

        Returns:
            bool: True if ok, False otherwise
        """
        ssidIsValid = self.checkAccessPoint_SSID()
        pwdIsValid = self.checkAccessPoint_PWD()
        pwdConfirm = self.confirmAccessPointPWD()
        return ssidIsValid & pwdIsValid & pwdConfirm

    def getConfig(self):
        """ Get configuration written in GUI. """
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

    def update_status(self):
        """ Update connection status. 
        Status bar set to green if connected to buoy AP.
        Status bar set to red if not connected to buoy AP.
        """
        if self.ap_is_connected:
            self.statusBar.showMessage("Status: connected to buoy")
            self.statusBar.setStyleSheet("background-color : green")
        else:
            self.statusBar.showMessage("Status: not connected to buoy")
            self.statusBar.setStyleSheet("background-color : red")
        
    def showMsgBox(self, MsgType, title, text):
        """Display a custom pop up message box to inform user.

        Args:
            MsgType (string): type of message box to display ('Information' or 'Warning')
            title (string): message box title
            text (string): text to display in the message box
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
        """ Display dialog UI to select location to save file. 

        Returns:
            str: full path to location selected
        """
        fileName, _ = QFileDialog.getSaveFileName(self, "Save configuration", "", "Text Files (*.txt)")
        return fileName

    def openFileDialog(self):
        """ Open dialog UI 

        Returns:
            str: path of the file to load.
        """
        fileName, _ = QFileDialog.getOpenFileName(self, "Load configuration", "", "Text Files (*.txt)")
        return fileName

    def stop_gnssLive(self):
        """ Interupt real time plot of the GNSS data. """
        if self.gnss_livePlot_initialised:
            self.timer_gnss.stop()
            cmd = f"rm {self.nmea_tmpfile}"
            stdin, stdout, stderr = self.client_GNSS.exec_command(cmd)
            self.client_GNSS.close()
            self.gnss_livePlot_initialised = False
        
    def stop_meteoLive(self):
        """ Interupt real time plot of the meteo data. """
        if self.meteo_livePlot_initialised:
            self.timer_meteo.stop()
            self.client_METEO.close()
            self.meteo_livePlot_initialised = False

    def closeEvent(self, event):
        """ Assert user realy desire to close app. 

        Args:
            event (closevent)
        """
        reply = QMessageBox.question(self, 'Window Close', 'Do you want to close app ?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.stop_gnssLive()
            self.stop_meteoLive()
            event.accept()
            print('BuoyApp closed')
        else:
            event.ignore()

    ################################################
    #######    Connection to access point    #######
    ################################################
    def show_connection_window(self):
        """ Open connection window. """
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
