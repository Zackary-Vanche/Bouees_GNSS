from buoy import * 

FLAG_DEPLOYED = '/boot/userConfigIsDeployed.txt'
def main():
    # Change permission 
    cmd =  f'sudo chmod +rw {FLAG_DEPLOYED}'
    os.system(cmd) 

    with open(FLAG_DEPLOYED, 'r') as f:
        configIsDeployed = int(f.read())    # Get status 

    with open(FLAG_DEPLOYED, 'w') as f:
        if not configIsDeployed:    # Update config
            buoy = Buoy(parent='RPI')
            buoy.updateConfig()
            f.write('1')
            # Reboot with new config
            os.system('sudo reboot')
        else:
            f.write('1')    

if __name__ == '__main__':
    main()
