from pymouse import PyMouse
from pykeyboard import PyKeyboard
import time
import os
import shutil

m = PyMouse()
k = PyKeyboard()
x_dim, y_dim = m.screen_size()

# click DCA1000RAM
m.click(x_dim//2-150, y_dim//2-120, 1)
## record the click time and click trigger
m.click(x_dim//2-70, y_dim//2-100, 1)

t1 = time.time()
## save time t1

print('Finished Recording Data? Y/N')
# if yes, continue

time_modif = os.path.getmtime('C:/ti/mmwave_studio_01_00_00_00/mmWaveStudio/PostProc/adc_data_Raw_0.bin')
print('The creation time of this radar data is ',time_modif,'. Is this correct?')
# if yes, continue
## then packet reorder and zero fill
os.system('cd C:/ti/mmwave_studio_01_00_00_00/mmWaveStudio/PostProc')
os.system('Packet_Reorder_Zerofill.exe adc_data_Raw_0.bin adc_data.bin')
## is success, then copy file to destimation; otherwise, print error
