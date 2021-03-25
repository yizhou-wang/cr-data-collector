#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Started on Mon. May 13th 2019

@author: Ryan Brazeal
@email: ryan.brazeal@ufl.edu

Program Name: livox_controller_demo.py
Version: 1.1.0
Last Updated: Fri. Sept. 11th 2020 (NEVER FORGET!)

Description: Python3 demo for controlling a single or multiple Livox sensor(s) using OpenPyLivox


"""

# openpylivox library import
import openpylivox.openpylivox.openpylivox as opl

# only used for this demo
import time
import sys


# operations for a single Livox Sensor
def singleSensor():
    lidar_only = False

    # create an openpylivox object
    sensor = opl.openpylivox(True)  # optional True/False, is used to have sensor messages printed to screen (default = False)

    # automatically discover if any Livox Sensors are available on the network
    # sensor.discover()

    # automatically discover if any Livox Sensors are available on the network, using a specific computer IP address
    # sensor.discover("192.168.1.23")

    # the sensor object's showMessages method can be used to turn on & off its information messages (example further down)
    sensor.showMessages(False)

    # sensor object's information messages can always be reset back to the initial state (on/off) as defined at the time of instantiation
    sensor.resetShowMessages()

    # easiest to try to automatically set the openpylivox sensor connection parameters and connect
    # connected = sensor.auto_connect()

    # or if your computer has multiple IP address you can force the computer IP to a manual address
    connected = sensor.auto_connect("192.168.1.50")

    # or manually define all IP addresses and ports (still need to properly configure your IP, Subnet, etc. on your computer)
    #                            computer IP       sensorIP    data port  command port  IMU port
    # connected = sensor.connect("192.168.1.23", "192.168.1.118",  60001,     50001,      40001)

    # make sure a sensor was connected
    if connected:

        # the sensor's connection parameters can be returned as a list of strings
        connParams = sensor.connectionParameters()

        # the sensor's firmware version can be returned as a list of strings
        firmware = sensor.firmware()

        # the sensor's serial number can be returned as a string
        serial = sensor.serialNumber()

        sensor.showMessages(True)

        # set the output coordinate system to Spherical
        # sensor.setSphericalCS()

        # set the output coordinate system to Cartesian (sensor default)
        # sensor.setCartesianCS()

        # read current extrinsic values from the sensor
        # sensor.readExtrinsic()

        # set all the sensor's extrinsic parameters equal to zero
        # (*** IMPORTANT: does not affect raw point cloud data stream, seems to only be used in Livox-Viewer? ***)
        sensor.setExtrinsicToZero()


        # set the sensor's extrinsic parameters to specific values
        # (*** IMPORTANT: does not affect raw point cloud data stream, seems to only be used in Livox-Viewer? ***)
        # sensor.setExtrinsicTo(x, y, z, roll, pitch, yaw)

        # the sensor's extrinsic parameters can be returned as a list of floats
        # extParams = sensor.extrinsicParameters()

        sensor.resetShowMessages()

        # make sure the lidar is spinning (ie., in normal mode), safe to call if the lidar is already spinning
        sensor.lidarSpinUp()

        ##########################################################################################

        # start data stream (real-time writing of point cloud data to a BINARY file)
        sensor.dataStart_RT_B()

        # send UTC time update (only works in conjunction with a hardware-based PPS pulse)
        sensor.updateUTC(2001, 1, 1, 1, 0)

        # set lidar return mode (0 = single 1st return, 1 = single strongest return, 2 = dual returns)
        sensor.setLidarReturnMode(0)

        # activate the IMU data stream (only for Horizon and Tele-15 sensors)
        sensor.setIMUdataPush(True)

        # turn on (True) or off (False) rain/fog suppression on the sensor
        sensor.setRainFogSuppression(True)

        # the sensor's lidar status codes can be returned as a list of integers (data stream needs to be started first)
        # status = sensor.lidarStatusCodes()

        # not exactly sure what this does as the fan does not respond to On(True) or Off(False) requests?
        # sensor.setFan(True)

        filePathAndName = "test.csv"  # file extension is NOT used to automatically determine if ASCII or Binary data is stored
        secsToWait = 0.0  # seconds, time delayed data capture start
        duration = 60.0  # seconds, zero (0) specifies an indefinite duration


        # (*** IMPORTANT: this command starts a new thread, so the current program (thread) needs to exist for the 'duration' ***)
        # capture the data stream and save it to a file (if applicable, IMU data stream will also be saved to a file)
        sensor.saveDataToFile(filePathAndName, secsToWait, duration, lidar_only)

        # simulate other operations being performed
        while True:

            # time.sleep(3)   #example of time < (duration + secsToWait), therefore early data capture stop

            # close the output data file, even if duration has not occurred (ideally used when duration = 0)
            # sensor.closeFile()
            # break

            # exit loop when capturing is complete (*** IMPORTANT: ignores (does not check) sensors with duration set to 0)
            if sensor.doneCapturing():
                break

        # NOTE: Any one of the following commands will also close the output data file (if still being written)

        # stop data stream
        sensor.dataStop()

        # if you want to put the lidar in stand-by mode, not sure exactly what this does, lidar still spins?
        # sensor.lidarStandBy()

        # if you want to stop the lidar from spinning (ie., lidar to power-save mode)
        sensor.lidarSpinDown()

        # if you want to reboot the sensor
        # sensor.reboot()

        # properly disconnect from the sensor
        sensor.disconnect()

        # convert BINARY point data to LAS file and IMU data (if applicable) to CSV file
        # only works in conjunction with .dataStart_RT_B()
        # designed so the efficiently collected binary point data can be converted to LAS at any time after data collection
        # opl.convertBin2LAS(filePathAndName, deleteBin=True)

        # convert BINARY point data and IMU data (if applicable) to CSV files
        # only works in conjunction with .dataStart_RT_B()
        # designed so the efficiently collected binary data can be converted to CSV at any time after data collection
        opl.convertBin2CSV(filePathAndName, deleteBin=True)

    else:
        print("\n***** Could not connect to a Livox sensor *****\n")



if __name__ == '__main__':

    singleSensor()
