import matlab.engine
import time

eng = matlab.engine.start_matlab()
#eng.RSTD_Interface_Exeng.quit()ample(nargout=0)
for i in range(3):
	eng.Init_DataCaptureDemo(nargout=0)

	time.sleep(1)
	time_start = time.time()

	input()
	eng.start_frame(nargout=0)
	time_use = time.time() - time_start
	print(time_use)
	time.sleep(40)

