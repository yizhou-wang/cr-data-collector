-- Get the file parameters
DUT_VERSION = ...

-- RT3 installation path
RSTD_PATH = RSTD.GetRstdPath()

-- Options for DUT Version
DUT_VER = {AR1xxx = 1}

-- Declare the loading function
dofile(RSTD_PATH .. "\\Scripts\\AR1xFunctions.lua")

-- Set the target device
DUT_VERSION = DUT_VERSION or DUT_VER.AR1xxx

-- Set automoation mode on/off (no message boxes)
local automation_mode = false

-- Display timestmaps in output/log
RSTD.SetAndTransmit ("/Settings/Scripter/Display DateTime" , "1")
RSTD.SetAndTransmit ("/Settings/Scripter/DateTime Format" , "HH:mm:ss")


Load_AR1x_Client(automation_mode)

TESTING = false
WriteToLog("TESTING = ".. tostring(TESTING) .. "\n", "green")

-- This command starts a listening server on port 2777 by default
RSTD.NetStart() 