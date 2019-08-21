import matlab.engine
import time

# time1 = time.time()
eng = matlab.engine.start_matlab()
# time2 = time.time() - time1
# print(time2)

# testing
for i in range(3):
	eng.Init_DataCaptureDemo(nargout=0)

	time.sleep(1)
	time_start = time.time()

	input()
	eng.start_frame(nargout=0)
	time_use = time.time() - time_start
	print(time_use)
	time.sleep(40)

