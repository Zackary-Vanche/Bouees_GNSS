from setBuoyConfig import *
from getOS import getOS


def main():
    config = readConfig(CONFIG_FILE)
    createEmptyConfigFiles()

    setUserWifi(config)
    setUserAP(config)

    
if __name__ == '__main__':
    main()