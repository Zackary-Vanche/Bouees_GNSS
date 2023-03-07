#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Menetrier Baptiste
# Created Date: 04/03/2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""
Package with basic functions for real time data visualisation. 
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import paramiko  # SSH package
from geodesy import getUTM_zone, utm_geod2map # Geodesy functions


##################stdin, stdout, stderr = client.exec_command(com)###########################################################
###########               Initialise ssh connection               ########### 
#############################################################################
def init_ssh_client(hostname, username, password):
    """Initialise ssh connection.

    Args:
        hostname (str): RaspberryPi IP (By default static IP '192.168.4.1') 
        username (str): RaspberryPi username ('pi' by default)
        password (str): RaspberryPi password ('hydro' by default)

    Returns:
        paramiko objects: client and channel associated to the ssh connection
    """
    # Initialize an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)

    # Open a channel to run the command
    channel = client.invoke_shell()
    return client, channel 


#############################################################################
###########                        Geodesy                        ###########
#############################################################################

def proj_to_UTM(lon, lat):
    """Project coordinates from WGS84 to UTM zone.

    Args:
        lon (float): Longitude in decimal degrees 
        lat (float): Latitue in decimal degrees

    Returns:
        float, float: x, y UTM zone coordinates
    """
    n = getUTM_zone(lon)
    x_utm, y_utm = utm_geod2map(n, lon, lat)
    return x_utm, y_utm, n

#############################################################################
###########         Assert NMEA sentences are valid               ###########
#############################################################################

def pre_process_sentence(sentence, verbose=False):
    """Pre-process NMEA sentences.

    Args:
        sentence (str): NMEA sentence
        verbose (bool, optional): Option to print information for invalid sentences. Defaults to False

    Returns:
        str, str: type of sentence, pre-processed sentence ((None, None) in case sentence is invalid)
    """
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
            if verbose:
                print('Checksum error')
                
            return None, None
        
    else:
        if verbose:
            print('Not a valid nmea sentence')
        return None, None
    
    
def check_sentence_is_nmea_sentence(sentence):
    """Check if NMEA sentence belongs to the list of known sentences.

    Args:
        sentence (str): NMEA sentence

    Returns:
        bool: True if NMEA sentence belongs to the known list, False otherwise
    """
    available_nmea_sentences = ["$GPGGA", "$GPGLL", "$GPGSA", "$GPGSV", "$GPVTG", "$GPRMC", '$GPDZDA']
    is_nmea_sentence = False
    for nmea_sentence in available_nmea_sentences:
        is_nmea_sentence = is_nmea_sentence or sentence.startswith(nmea_sentence)
    return is_nmea_sentence

def remove_unneeded_character_from_sentence(sentence):
    """Remove useless characters "\r", "\n".

    Args:
        sentence (str): NMEA sentence

    Returns:
        str: NMEA sentence without extra characters
    """
    # Split the sentence into a list of characters
    char_list = list(sentence)
    # Remove extra '\r' characters
    while char_list[-1] == '\r':
        char_list.pop()
        
    while char_list[0] == '\n':
        char_list.pop(0)
        
    # Join the characters back into a sentence string
    return ''.join(char_list)

def compute_nmea_checksum(sentence):
    """Derive NMEA checksum.

    Args:
        sentence (str): NMEA sentence

    Returns:
        str: 2-digit hexadecimal string representing the checksum
    """
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
    # read_nmea_ssh(hostname, username, password)
    # read_meteo_ssh(hostname, username, password)