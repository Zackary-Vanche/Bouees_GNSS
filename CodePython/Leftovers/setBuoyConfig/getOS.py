import os 

def getOS():
    if os.name == 'nt':
        os_sys = 'Windows'
    else:
        os_sys = 'Linux'
    return os_sys
