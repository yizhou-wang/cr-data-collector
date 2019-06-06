addpath(genpath('.\'))

Lua_String = 'ar1.StartFrame()';
ErrStatus = RtttNetClientAPI.RtttNetClient.SendCommand(Lua_String);