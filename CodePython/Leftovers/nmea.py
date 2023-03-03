import random
import matplotlib.pyplot as plt

# List of NMEA sentence types
# sentence_types = ['$GPGSA', '$GPGSV']
# sentence_types = ['$GPGSA']



# def parse_nmea_sentence(sentence):
#     parts = sentence.split(',')
#     sentence_type = parts[0]
#     if sentence_type == '$GPGSA':
#         mode = parts[1]
#         fix_type = parts[2]
#         sats = [int(x) if x else None for x in parts[3:15]]
#         pdop = float(parts[15])
#         hdop = float(parts[16])
#         vdop = float(parts[17])
#         return {
#             'sentence_type': sentence_type,
#             'mode': mode,
#             'fix_type': fix_type,
#             'sats': sats,
#             'pdop': pdop,
#             'hdop': hdop,
#             'vdop': vdop
#         }
#     elif sentence_type == '$GPGSV':
#         num_sentences = int(parts[1])
#         sentence_num = int(parts[2])
#         sats_in_view = int(parts[3])
#         sats = []
#         for i in range(4, len(parts)-3, 4):
#             if parts[i]:
#                 sat_id = int(parts[i])
#                 elev = int(parts[i+1]) if parts[i+1] else None
#                 azimuth = int(parts[i+2]) if parts[i+2] else None
#                 snr = int(parts[i+3]) if parts[i+3] else None
#                 sats.append({'id': sat_id, 'elevation': elev, 'azimuth': azimuth, 'snr': snr})
#         return {
#             'sentence_type': sentence_type,
#             'num_sentences': num_sentences,
#             'sentence_num': sentence_num,
#             'sats_in_view': sats_in_view,
#             'sats': sats
#         }
#     else:
#         return None

# def read_nmea_from_file(file_path):
#     data = []
#     with open(file_path, 'r') as f:
#         for line in f:
#             sentence = line.strip()
#             if sentence:
#                 data.append(parse_nmea_sentence(sentence))
#     return data

                
# def plot_nmea_data(data):
#     for sentence in data:
#         if sentence['sentence_type'] == '$GPGSA':
#             x = range(12)
#             y = sentence['sats']
#             plt.scatter(x, y)
#             plt.xlabel('Satellite Number')
#             plt.ylabel('PRN')
#             plt.title('GPGSA - Satellite IDs')
#             # plt.show()
            
#             x = range(3)
#             y = [sentence['pdop'], sentence['hdop'], sentence['vdop']]
#             plt.scatter(x, y)
#             plt.xlabel('DOP Type')
#             plt.ylabel('Value')
#             plt.title('GPGSA - DOP values')
#             # plt.show()
            
#             x = range(3)
#             y = [sentence['fix_type'] == '1', sentence['fix_type'] == '2', sentence['fix_type'] == '3']
#             plt.scatter(x, y)
#             plt.xlabel('Fix Type')
#             plt.ylabel('Value')
#             plt.title('GPGSA - Fix Type')
#             # plt.show()
#         elif sentence['sentence_type'] == '$GPGSV':
#             x = [sat['azimuth'] for sat in sentence['sats']]
#             y = [sat['elevation'] for sat in sentence['sats']]
#             plt.scatter(x, y)
#             plt.xlabel('Azimuth')
#             plt.ylabel('Elevation')
#             plt.title('GPGSV - Satellite Positions')
#             plt.show()


# def read_nmea_from_file(file_path):
#     plt.figure(1)
#     plt.subplot(311)
#     plt.title('GPGSA - Satellite IDs')
#     plt.xlabel('Satellite Number')
#     plt.ylabel('PRN')
#     plt.subplot(312)
#     plt.title('GPGSA - DOP values')
#     plt.xlabel('Time')
#     plt.ylabel('Value')
#     plt.subplot(313)
#     plt.title('GPGSA - Fix Type')
#     plt.xlabel('Time')
#     plt.ylabel('Value')
#     plt.show(block=False)
#     plt.figure(2)
#     plt.title('GPGSV - Satellite Positions')
#     plt.xlabel('Azimuth')
#     plt.ylabel('Elevation')
#     plt.show(block=False)
#     time = 0
#     with open(file_path, 'r') as f:
#         for line in f:
#             sentence = line.strip()
#             if sentence:
#                 data = parse_nmea_sentence(sentence)
#                 plot_nmea_data(data, time)
#                 time += 1
#                 plt.pause(0.05)

# def plot_nmea_data(data, time):
#     if data['sentence_type'] == '$GPGSA':
#         plt.figure(1)
#         plt.subplot(311)
#         x = range(12)
#         y = data['sats']
#         plt.scatter(x, y)
#         plt.subplot(312)
#         x = [time] * 3
#         y = [data['pdop'], data['hdop'], data['vdop']]
#         plt.scatter(x, y)
#         plt.subplot(313)
#         x = [time]
#         y = [data['fix_type']]
#         plt.scatter(x, y)
#         plt.draw()
#     elif data['sentence_type'] == '$GPGSV':
#         plt.figure(2)
#         x = [sat['azimuth'] for sat in data['sats']]
#         y = [sat['elevation'] for sat in data['sats']]
#         plt.scatter(x, y)
#         plt.draw()


import datetime

def parse_nmea_sentence(sentence):
    data = {}
    sentence_type = sentence[3:6]
    if sentence_type == 'GSA':
        data = parse_gsa_sentence(sentence)
    elif sentence_type == 'GSV':
        data = parse_gsv_sentence(sentence)
    elif sentence_type == 'GGA':
        data = parse_gga_sentence(sentence)
    data['sentence_type'] = sentence_type
    return data

def parse_gsa_sentence(sentence):
    data = {}
    sentence = sentence.split(',')
    if len(sentence) > 17:
        prn = [int(i) for i in sentence[3:14] if i]
        data["prn"] = prn
        data["pdop"] = float(sentence[15])
        data["hdop"] = float(sentence[16])
        data["vdop"] = float(sentence[17])
        data["fix_type"] = int(sentence[2])
    return data

def parse_gsv_sentence(sentence):
    data = {}
    sentence = sentence.split(',')
    if len(sentence) > 4:
        total_sentences = int(sentence[1])
        sentence_number = int(sentence[2])
        satellites_in_view = int(sentence[3])
        data["total_sentences"] = total_sentences
        data["sentence_number"] = sentence_number
        data["satellites_in_view"] = satellites_in_view
        satellite_data = []
        for i in range(4, len(sentence) - 3, 4):
            if sentence[i]:
                satellite_data.append({
                    "prn": int(sentence[i]),
                    "elevation": int(sentence[i + 1]),
                    "azimuth": int(sentence[i + 2]),
                    "snr": int(sentence[i + 3]),
                })
        data["satellite_data"] = satellite_data
    return data

def parse_gga_sentence(sentence):
    data = {}
    sentence = sentence.split(',')
    if len(sentence) > 9:
        time = datetime.datetime.strptime(sentence[1], "%H%M%S.%f")
        data["time"] = time
        data["latitude"] = float(sentence[2])
        data["latitude_direction"] = sentence[3]
        data["longitude"] = float(sentence[4])
        data["longitude_direction"] = sentence[5]
        data["fix_quality"] = int(sentence[6])
        data["satellites_tracked"] = int(sentence[7])
        data["hdop"] = float(sentence[8])
        data["altitude"] = float(sentence[9])
        data["altitude_unit"] = sentence[10]
        data["geoid_separation"] = float(sentence[11])
        data["geoid_separation_unit"] = sentence[12]
        data["dgps_age"] = float(sentence[13])
        data["dgps_ref_station_id"] = int(sentence[14])
    return data

def read_nmea_from_file(file_path):
    with open(file_path, 'r') as file:
        nmea_sentences = file.readlines()
    nmea_data = []
    for sentence in nmea_sentences:
        if sentence.startswith('$GPG'):
            nmea_data.append(parse_nmea_sentence(sentence))
    return nmea_data

def plot_nmea_data(nmea_data):
    time = []
    pdop = []
    hdop = []
    vdop = []
    fix_types = []
    for sentence in nmea_data:
        if sentence['sentence_type'] == 'GGA':
            time.append(sentence['time'])
            hdop.append(sentence['hdop'])

        if sentence['sentence_type'] == 'GSA':
            pdop.append(sentence['pdop'])
            # hdop.append(sentence['hdop'])
            vdop.append(sentence['vdop'])
            fix_types.append(sentence['fix_type'])

    # fig, axs = plt.subplots(3, 1)
    # axs[0].plot(time, pdop)
    # axs[0].set(xlabel='Time', ylabel='PDOP',title='PDOP vs Time')

    # axs[1].plot(time, hdop)
    # axs[1].set(xlabel='Time', ylabel='HDOP',title='HDOP vs Time')

    # axs[2].plot(time, vdop)
    # axs[2].set(xlabel='Time', ylabel='VDOP',title='VDOP vs Time')
    plt.figure()
    plt.plot(time, hdop)
    plt.show()
    

if __name__ == '__main__':
    # Example of usage
    create_nmea_file('nmea_sentences.txt', 150)
    parsed_data = read_nmea_from_file('nmea_sentences.txt')
    plot_nmea_data(parsed_data)
    plt.show()