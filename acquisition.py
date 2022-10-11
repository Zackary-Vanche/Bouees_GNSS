import os
import time
import shutil
from datetime import datetime
time.sleep(120)
#print(os.getcwd())

c = 0
path = './'
#folder_exists = os.path.exists(path + 'acquisition')

os.system('rm -r ./acquisition')

os.system('mkdir ./acquisition')
    
while True:
    now = datetime.now()
    current_time = now.strftime("%d_%m_%Y_%H:%M:%S")

    name = str(c)
    os.system(('gpspipe -o ~/acquisition/{}_{}.txt -r -R -n 15000').format(name, current_time))
    c+=1
    

 
