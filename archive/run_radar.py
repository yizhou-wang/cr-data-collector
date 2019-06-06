import matlab.engine

eng = matlab.engine.start_matlab()
#eng.RSTD_Interface_Example(nargout=0)
eng.Init_DataCaptureDemo(nargout=0)
eng.quit()