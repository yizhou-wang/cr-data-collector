addpath(genpath('.\'))

% Initialize Radarstudio .NET connection
RSTD_DLL_Path = 'C:\ti\mmwave_studio_01_00_00_00\mmWaveStudio\Clients\RtttNetClientController\RtttNetClientAPI.dll';
ErrStatus = Init_RSTD_Connection(RSTD_DLL_Path);

if (ErrStatus ~= 30000)
    disp('Error inside Init_RSTD_Connection');
    return;
end

Lua_String = 'ar1.CaptureCardConfig_StartRecord("C:\\ti\\mmwave_studio_01_00_00_00\\mmWaveStudio\\PostProc\\adc_data.bin", 1)';
ErrStatus =RtttNetClientAPI.RtttNetClient.SendCommand(Lua_String);

