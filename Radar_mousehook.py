from pymouse import PyMouse
from pykeyboard import PyKeyboard
import time
import os

m = PyMouse()
k = PyKeyboard()
x_dim, y_dim = m.screen_size()

# click DCA1000RAM
m.click(x_dim//2-150, y_dim//2-120, 1)
## record the click time and click trigger
t0 = time.clock()
m.click(x_dim//2-70, y_dim//2-100, 1)

t1 = time.time()
## save time t1

print('Finished?')
## then packet reorder and zero fill
## then copy file to destimation
