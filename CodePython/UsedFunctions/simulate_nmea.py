import numpy as np 
from datetime import datetime
import time

PATH_GNSS = r'/home/pi/data/NMEA/logNMEA.txt'
# PATH_GNSS = r'C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Bouees_GNSS\CodePython\UsedFunctions\testsimu_gnss.txt'

def generate_sentence():
    sentence_types = ['GPGGA', 'GPGSA', 'GPGSV']
    sentence_type = np.random.choice(sentence_types)

    if sentence_type == 'GPGGA':
        time = datetime.now().strftime("%H%M%S.%f")
        latitude = np.random.uniform(0, 90)
        longitude = np.random.uniform(0, 180)
        fix_quality = np.random.randint(0, 1)
        num_satellites = np.random.randint(0, 12)
        hdop = np.random.uniform(0, 50)
        altitude = np.random.uniform(0, 9000)
        height_of_geoid = np.random.uniform(0, 9000)
        dgps_age = np.random.uniform(0, 9000)
        dgps_id = np.random.randint(0, 32)
        checksum = np.random.randint(0, 32)
        return f'$GPGGA,{time},{latitude},N,{longitude},E,{fix_quality},{num_satellites},{hdop},{altitude},M,{height_of_geoid},M,{dgps_age},{dgps_id},{checksum}*'
    
    elif sentence_type == 'GPGSA':
        mode = np.random.choice(['A', 'M'])
        fix_type = np.random.randint(1, 3)
        sats = [np.random.randint(0, 32) for _ in range(12)]
        pdop = np.random.uniform(0, 50)
        hdop = np.random.uniform(0, 50)
        vdop = np.random.uniform(0, 50)
        return f'$GPGSA,{mode},{fix_type},{",".join(str(sat) for sat in sats)},{pdop},{hdop},{vdop},*'
    
    elif sentence_type == 'GPGSV':
        num_sentences = np.random.randint(2, 3)
        sentence_num = np.random.randint(1, num_sentences)
        sats_in_view = np.random.randint(1, 12)
        sats = []
        for i in range(12):
            if i < sats_in_view:
                sat_id = np.random.randint(1, 32)
                elev = np.random.randint(0, 90)
                azimuth = np.random.randint(0, 359)
                snr = np.random.randint(0, 99)
                sats.append(f'{sat_id},{elev},{azimuth},{snr}')
            else:
                sats.append(",,")
        return f'$GPGSV,{num_sentences},{sentence_num},{sats_in_view},{",".join(sats)}'
    else:
        return None

# Create a file with np.random NMEA sentences
def simulate_GNSS():
    while True:
        with open(PATH_GNSS, 'a') as file:
            sentence = generate_sentence()
            if sentence:
                file.write(sentence + '\n')
                
        time.sleep(1)
            
if __name__ == '__main__':
    simulate_GNSS()