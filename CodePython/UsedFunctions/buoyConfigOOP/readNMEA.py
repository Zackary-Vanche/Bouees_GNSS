import datetime  # module for working with time
import matplotlib.pyplot as plt  # for plotting
import paramiko  # library for SSH
import numpy as np 
import pandas as pd
import time
import pynmea2
from geodesy import getUTM_zone, utm_geod2map

def read_meteo_ssh(hostname, username, password):
    # Initialize an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)

    # Open a channel to run the command
    channel = client.invoke_shell()
    channel.send("tail -f /home/pi/data/METEO/logMETEO.txt\n") # command to read NMEA sentences
    
    # Initialise datafram
    data = pd.DataFrame({'time': [], 'temperature_C': [], 'pressure': [], 'humidity': []})
    
    # Initialise figure
    plt.ion()
    fig, axs = plt.subplots(3, 1, figsize=(10, 8))
    ax_temperature, ax_pressure, ax_humidity = axs[0], axs[1], axs[2]
    
    plt.subplots_adjust(left=0.1, 
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.7,
                    hspace=0.5)
        
    visu_range_temperature = 0.5
    visu_range_pressure = 0.5
    visu_range_humidity = 0.5
    
            
    start_time = time.time()
    init_time = 15 # To avoid first outputs 
    while time.time() - start_time < init_time:
        lines = channel.recv(1024).decode("utf-8")

    while True:
        lines = channel.recv(1024).decode("utf-8")
        
        lines = lines.split("\n")
        lines = [ lines[i] for i in range(len(lines)) if lines[i] != '']
        
        for line in lines:
            
            line = remove_unneeded_character_from_sentence(line)
            meteo_data = line.split(",") 
            
            
            data_to_append = pd.DataFrame({'time': [datetime.datetime.strptime(meteo_data[0], '%d%m%Y %H:%M:%S')], 
                                        'temperature_C': [float(meteo_data[1])], 
                                        'pressure': [float(meteo_data[2])], 
                                        'humidity': [float(meteo_data[3])]})
            data = pd.concat([data, data_to_append])
            
            ax_temperature.clear()
            ax_pressure.clear()
            ax_humidity.clear()
            
            ax_temperature.plot(data.time, data.temperature_C, marker='+')
            ax_pressure.plot(data.time, data.pressure, marker='+')
            ax_humidity.plot(data.time, data.humidity, marker='+')

            # ax_temperature.legend(loc='upper right')
            # ax_pressure.legend(loc='upper right')
            # ax_humidity.legend(loc='upper right')
                        
            ax_temperature.set_ylim([np.min(data.temperature_C) - visu_range_temperature, np.max(data.temperature_C) + visu_range_temperature])
            ax_pressure.set_ylim([np.min(data.pressure) - visu_range_pressure, np.max(data.pressure) + visu_range_pressure])
            ax_humidity.set_ylim([np.min(data.humidity) - visu_range_humidity, np.max(data.humidity) + visu_range_humidity])

            fig.autofmt_xdate(rotation=DATE_ROTATION)
            
            ax_temperature.ticklabel_format(axis='y', useOffset=False)
            ax_pressure.ticklabel_format(axis='y', useOffset=False)
            ax_humidity.ticklabel_format(axis='y', useOffset=False)
            
            ax_temperature.xaxis.set_minor_locator(plt.MaxNLocator(NB_DATES_TO_DISPLAY))
            ax_pressure.xaxis.set_minor_locator(plt.MaxNLocator(NB_DATES_TO_DISPLAY))
            ax_humidity.xaxis.set_minor_locator(plt.MaxNLocator(NB_DATES_TO_DISPLAY))
            
            ax_temperature.set_title('Temperature')
            ax_pressure.set_title('Pressure')
            ax_humidity.set_title('Humidity')
            
            ax_temperature.set_ylabel('T [°C]')
            ax_pressure.set_ylabel('P [hPa]')
            ax_humidity.set_ylabel('H [%]')
    
            plt.pause(9)
            plt.draw()      
                    
        # print(lines)
    
def read_nmea_ssh(hostname, username, password):
    # Initialize an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)

    # Open a channel to run the command
    channel = client.invoke_shell()
    # channel.send("cat /dev/ttyS0\n") # command to read the ttyS0 where the GNSS module is connected
    channel.send("gpspipe -r\n") # command to read NMEA sentences

    # Initialize lists to store information
    times = []
    lats, lons = [], []
    x_utms, y_utms = [], []
    
    hdops = []
    vdops = []
    pdops = []
    satellites_in_view = []

    plt.ion()

    fig, axs = plt.subplots(1, 3, figsize=(14, 6))
    ax_dop, ax_pos, ax_snr = axs[0], axs[1], axs[2]


    plt.subplots_adjust(left=0.1, 
                        bottom=0.1, 
                        right=0.9, 
                        top=0.9, 
                        wspace=0.7,
                        hspace=0.5)

    start_time = time.time()
    init_time = 15 # To avoid first outputs 
    while time.time() - start_time < init_time:
        lines = channel.recv(1024).decode("utf-8")
        
    while True:
        # Read NMEA sentence
        lines = channel.recv(1024).decode("utf-8")
        # print(lines)
        
        lines = lines.split("\n")
        
        for sentence in lines:
            
            s_type, sentence = pre_process_sentence(sentence)
            if sentence:
                msg = pynmea2.parse(sentence, check=True)
                
                # sentence_type, nmea_sentence = pre_process_sentence(sentence)

                # Check if the line is a GPGGA sentence
                # if sentence_type == "$GPGGA":
                if msg.sentence_type == 'GGA':
                    
                    # Save time 
                    times.append(msg.timestamp)
                    
                    # parsed_sentence = parse_gpgga_sentence(nmea_sentence)
                    # x_utm, y_utm, n_utm = proj_to_UTM(np.array(parsed_sentence['lon']), np.array(parsed_sentence['lat']))
                    x_utm, y_utm, n_utm = proj_to_UTM(np.array(msg.longitude), np.array(msg.latitude))

                    
                    x_utms.append(x_utm)
                    y_utms.append(y_utm)
                    
                    # lats.append(parsed_sentence['lat'])
                    # lons.append(parsed_sentence['lon'])
                    # pdops.append(parsed_sentence['pdop'])
                    
                    # Keep only a constant number of values to plot
                    if len(x_utms) > NMEA_VALUES_TO_PLOT:
                        x_utms.pop(0)
                        y_utms.pop(0)
                        times.pop(0)
                        # lats.pop(0)
                        # lons.pop(0)
                        # pdops.pop(0)

                    # Plot the updated values
                    ax_pos.clear()
                    # ax_pos.scatter(lons, lats, label='lat')
                    ax_pos.scatter(x_utms, y_utms)
                    ax_pos.set_xlabel('E [m]')
                    ax_pos.set_ylabel('N [m]')
                    ax_pos.set_title(f'UTM zone n°{n_utm}')
                    ax_pos.ticklabel_format(useOffset=False)
                    ax_pos.grid()
                    ax_pos.tick_params(axis='x', labelrotation=20)

                    plt.pause(0.005)
                    plt.tight_layout()
                    plt.draw()      
                    
                # Check if the line is a GPGSV sentence
                elif msg.sentence_type == "GSA":
                        
                    # parsed_sentence = parse_gpgsa_sentence(nmea_sentence)
                    
                    # Append the hdop and vdop to the lists
                    # hdops.append(parsed_sentence['hdop'])
                    # vdops.append(parsed_sentence['vdop'])
                    # pdops.append(parsed_sentence['pdop'])
                    hdops.append(msg.hdop)
                    vdops.append(msg.vdop)
                    pdops.append(msg.pdop)
                    
                    # Keep only a constant number of values to plot
                    if len(hdops) > NMEA_VALUES_TO_PLOT:
                        hdops.pop(0)
                        vdops.pop(0)
                        pdops.pop(0)
        
                    # Plot the updated values
                    ax_dop.clear()
                    if len(hdops) ==  len(times):
                        times_label = [t.strftime("%H:%M:%S") for t in times]
                        ax_dop.plot(times_label, hdops, label='hdop')
                        ax_dop.plot(times_label, vdops, label='vdop')
                        ax_dop.plot(times_label, pdops, label='pdop')
                        ax_dop.tick_params(axis='x', labelrotation=20)
                    else:
                        ax_dop.plot(hdops, label='hdop')
                        ax_dop.plot(vdops, label='vdop')
                        ax_dop.plot(pdops, label='pdop')
                        
                    ax_dop.legend(loc='upper right')
                    plt.pause(0.005)
                    plt.draw()                      
                        
                
                elif msg.sentence_type == "GSV":
                    
                    # parsed_sentence = parse_gpgsv_sentence(nmea_sentence)
                    snr = np.empty((4))
                    ax_snr.clear()
                    for i in range(1, 4):
                        idx = msg.name_to_idx[f'snr_{i}']
                        if idx <= len(msg.data)-1:
                            snr[i-1] = msg.data[idx]
                        else:
                            snr[i] = np.nan
                    
                    x = np.arange(1, len(snr)+1, 1)
                    ax_snr.bar(x, snr, width=0.5)
                    ax_snr.set_ylim([0, 100])
                    ax_snr.set_ylabel('SNR')
                    ax_snr.set_xlabel('Sat')
                    
                    plt.pause(0.005)
                    plt.draw()  

                else: 
                    # print('No data')
                    pass
                        

                    
            # t += 1
            
    client.close()
    plt.show()
    # print(hdops)
    # print(vdops)
    print(lats)
    print(lons)


##################################################################################
#############                     Preprocess data                   ##############
##################################################################################

def proj_to_UTM(lon, lat):
    n = getUTM_zone(lon)
    x_utm, y_utm = utm_geod2map(n, lon, lat)
    return x_utm, y_utm, n

##################################################################################
#############          Parse NMEA sentences to extract info         ##############
##################################################################################

def parse_gpgsv_sentence(sentence):
    """
    Parses a GPGSV sentence and returns its elements
    """
    # Split the line into fields
    fields = sentence.split(",")
    
    # Extract the number of satellites in view
    if fields[3]:
        num_sats = int(fields[3])
    else:
        num_sats = None
        
    # Extract satellite information
    sats = []
    for i in range(4, len(fields) - 3, 4):
        sat_id = fields[i]
        if sat_id:
            sat_id = int(sat_id)
        else:
            sat_id = None
        
        elevation = fields[i + 1]
        if elevation:
            elevation = int(elevation)
        else:
            elevation = None
        
        azimuth = fields[i + 2]
        if azimuth:
            azimuth = int(azimuth)
        else:
            azimuth = None
        
        snr = fields[i + 3]
        if snr:
            snr = int(snr)
        else:
            snr = None
            
        sat = {'id': sat_id,
               'elevation': elevation,
               'azimuth': azimuth,
               'snr': snr}
        sats.append(sat)
    
    parsed_sentence = {'num_sats': num_sats,
                       'sats': sats}
    
    return parsed_sentence


def parse_gpgga_sentence(sentence):
    """
    Parses a GPGGA sentence and returns its elements
    """
    # Split the line into fields
    fields = sentence.split(",")
    
    # Extract the latitude 
    if fields[2]:
        lat = float(fields[2])
        lat_dir = fields[3]
        
        # Convert the latitude to decimal degrees
        lat_degrees = int(lat / 100)
        lat_minutes = lat - (lat_degrees * 100)
        lat_decimal = lat_degrees + (lat_minutes / 60)
        if lat_dir == "S":
            lat_decimal *= -1
    else:
        lat_decimal = None
    
    # Extract the longitude 
    if fields[4]:
        lon = float(fields[4])
        lon_dir = fields[5]
        
        # Convert the latitude to decimal degrees
        lon_degrees = int(lon / 100)
        lon_minutes = lon - (lon_degrees * 100)
        lon_decimal = lon_degrees + (lon_minutes / 60)
        if lon_dir == "W":
            lon_decimal *= -1
    else:
        lon_decimal = None
    
    # Extract the time
    if fields[1]:
        time = fields[1]
        hour = int(time[0:2])
        minute = int(time[2:4])
        second = int(time[4:6])
        time = datetime.time(hour,minute,second)
    else:
        time = None
    
    parsed_sentence = {'time': time,
                       'lat': lat_decimal,
                       'lon': lon_decimal}
    
    return parsed_sentence


def parse_gpgsa_sentence(sentence):
    """
    Parses a GPGSA sentence and returns its elements
    """
    # Split the sentence into fields
    fields = sentence.split(",")
    
    # Extract the elements from the fields
    selection_mode = fields[1] if fields[1] else None
    fix_mode = int(fields[2]) if fields[2] else None
    svid = [int(fields[i]) for i in range(3, 15) if fields[i]]
    pdop = float(fields[-3]) if fields[-3] else None
    hdop = float(fields[-2]) if fields[-2] else None
    vdop = float(fields[-1]) if fields[-1] else None
    
    parsed_sentence = {'selection_mode': selection_mode,
                       'fix_mode': fix_mode,
                       'svid': svid,
                       'pdop': pdop,
                       'hdop': hdop,
                       'vdop': vdop}
    
    return parsed_sentence


##################################################################################
#############          Assert NMEA sentences are valid          ##################
##################################################################################

def pre_process_sentence(sentence):
    
    # Assert sentence is an NMEA sentence
    if check_sentence_is_nmea_sentence(sentence):
        
        nmea_sentence = remove_unneeded_character_from_sentence(sentence)
        
        # Assert sentence is valid
        computed_checksum = compute_nmea_checksum(nmea_sentence[1:-3])
        received_checksum = nmea_sentence[-2:]
        
        if computed_checksum.upper() == received_checksum.upper():
            
            sentence_type = nmea_sentence[:6]   # Get type of sentence 
            # nmea_sentence = nmea_sentence[:-3]  # Get rid of checksum 
            
            return sentence_type, nmea_sentence
        else:
            return None, None
        
    else:
        return None, None
    
    
def check_sentence_is_nmea_sentence(sentence):
    available_nmea_sentences = ["$GPGGA", "$GPGLL", "$GPGSA", "$GPGSV", "$GPVTG", "$GPRMC"]
    is_nmea_sentence = False
    for nmea_sentence in available_nmea_sentences:
        is_nmea_sentence = is_nmea_sentence or sentence.startswith(nmea_sentence)
    return is_nmea_sentence

def remove_unneeded_character_from_sentence(sentence):
    # Split the sentence into a list of characters
    char_list = list(sentence)
    # Remove extra '\r' characters
    while char_list[-1] == '\r':
        char_list.pop()
    # Join the characters back into a sentence string
    return ''.join(char_list)

def compute_nmea_checksum(sentence):
    # Convert the sentence into a list of hexadecimal values
    hex_list = [format(ord(c), 'x').zfill(2) for c in sentence]
    # XOR the values in the list
    checksum = 0
    for h in hex_list:
        checksum ^= int(h, 16)
    # Return the checksum as a 2-digit hexadecimal string
    return format(checksum, 'x').zfill(2)




if __name__ == '__main__':
    hostname = '192.168.4.1'
    username = 'pi'
    password = 'hydro'
    
    METEO_VALUES_TO_PLOT = 20
    NMEA_VALUES_TO_PLOT = 10
    DATE_ROTATION = 20
    NB_DATES_TO_DISPLAY = 5
    POS_ON_MAP = True # Plot lon lat on map 
    read_nmea_ssh(hostname, username, password)
    # read_meteo_ssh(hostname, username, password)