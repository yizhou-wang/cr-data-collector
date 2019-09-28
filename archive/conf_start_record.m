addpath(genpath('.\'))

Lua_String = 'ar1.CaptureCardConfig_StartRecord("C:\\ti\\mmwave_studio_02_00_00_02\\mmWaveStudio\\PostProc\\adc_data.bin", 1)';
ErrStatus = RtttNetClientAPI.RtttNetClient.SendCommand(Lua_String);