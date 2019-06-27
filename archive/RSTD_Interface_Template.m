addpath(genpath('.\'))

% Initialize Radarstudio .NET connection
RSTD_DLL_Path = 'C:\ti\mmwave_studio_01_00_00_00\mmWaveStudio\Clients\RtttNetClientController\RtttNetClientAPI.dll';

ErrStatus = Init_RSTD_Connection(RSTD_DLL_Path);
if (ErrStatus ~= 30000)
    disp('Error inside Init_RSTD_Connection');
    return;
end

% % Example Lua Command
% strFilename = 'C:\\ti\\mmwave_studio_01_00_00_00\\mmWaveStudio\\Scripts\\DataCaptureDemo_xWR.lua';
% Lua_String = sprintf('dofile("%s")',strFilename);
% ErrStatus =RtttNetClientAPI.RtttNetClient.SendCommand(Lua_String);
 

