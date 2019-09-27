# coding=utf-8
try:
    import PySpin
except:
    print("Warning: PySpin is not installed!")

import os
import time
import datetime
import numpy as np

from .cam_config import ChunkDataTypes, CHOSEN_CHUNK_DATA_TYPE
from .cam_config import configure_chunk_data, disable_chunk_data, \
    display_chunk_data_from_image, display_chunk_data_from_nodemap
from .cam_config import configure_buffer, configure_trigger_multi, grab_next_image_by_trigger
from .cam_config import print_device_info_multi
from .radar_driver import run_radar
from .radar_driver import init_radar
from .radar_driver import check_datetime


def acquire_images(cam_list, seq_dir, frame_rate, num_img, radar, interval=0):
    """
    This function acquires and saves 10 images from each device.

    :param cam_list: List of cameras
    :type cam_list: CameraList
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***\n')
    try:
        result = True
        timestamp_txt = []

        # set config for primary camera
        cam = cam_list[0]
        # Set acquisition mode to continuous
        node_acquisition_mode = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (node retrieval). Aborting... \n')
            return False
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry \'continuous\' retrieval). \
            Aborting... \n')
            return False
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
        print('Camera acquisition mode set to continuous...')
        ####################
        # Framerate
        ####################
        # Set acquisition frame rate enable to true
        acquisition_frame_rate_active = PySpin.CBooleanPtr(cam.GetNodeMap().GetNode('AcquisitionFrameRateEnable'))
        if PySpin.IsAvailable(acquisition_frame_rate_active) and PySpin.IsWritable(acquisition_frame_rate_active):
            acquisition_frame_rate_active.SetValue(True)
        print('Camera acquisition frame rate activated...')
        # Set frame rate to the given value
        node_acquisition_frame_rate = PySpin.CFloatPtr(cam.GetNodeMap().GetNode('AcquisitionFrameRate'))
        if not PySpin.IsAvailable(node_acquisition_frame_rate) or not PySpin.IsWritable(
                node_acquisition_frame_rate):
            print('Unable to set frame rate (node retrieval). Aborting...')
            return False
        node_acquisition_frame_rate.SetValue(frame_rate)
        print('Camera acquisition frame rate set to %d...\n' % frame_rate)

        for i in range(2):
            f = open(os.path.join(seq_dir, 'timestamps_%d.txt' % i), 'w')
            timestamp_txt.append(f)

        if radar:
            # Init radar
            engine = init_radar()
        if radar and interval != 0:
            assert check_datetime(interval) is True
        if radar:
            # Run radar
            run_radar(engine)

        # record start time
        start_time = time.time()
        # print(start_time)

        # for i, cam in enumerate(cam_list):
        #     # Begin acquiring images
        #     # ts_tmp = time.time()
        #     cam.BeginAcquisition()
        #     start_time_cam.append(time.time())
        #     # print('begin acq %s' % (time.time() - ts_tmp))
        #     print('Camera %d started acquiring images...' % i)

        cam_list[1].BeginAcquisition()
        cam_list[0].BeginAcquisition()
        # record start time
        start_time_cam = time.time()

        print('Camera started acquiring images...')

        for i, cam in enumerate(cam_list):
            # Retrieve device serial number for filename0
            node_device_serial_number = PySpin.CStringPtr(cam.GetTLDeviceNodeMap().GetNode('DeviceSerialNumber'))

            if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                device_serial_number = node_device_serial_number.GetValue()
                print('Camera %d serial number set to %s...' % (i, device_serial_number))

            print()

        # Retrieve, convert, and save images for each camera
        #
        # *** NOTES ***
        # In order to work with simultaneous camera streams, nested loops are
        # needed. It is important that the inner loop be the one iterating
        # through the cameras; otherwise, all images will be grabbed from a
        # single camera before grabbing any images from another.

        FIRST_TS_list = np.zeros((len(cam_list), ))
        for n in range(num_img):
            for i, cam in enumerate(cam_list):
                try:
                    # #  Retrieve the next image from the trigger
                    # result &= grab_next_image_by_trigger(cam.GetNodeMap())
                    # Retrieve next received image and ensure image completion
                    image_result = cam.GetNextImage()

                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ... \n' % image_result.GetImageStatus())
                    else:
                        # Print image information
                        width = image_result.GetWidth()
                        height = image_result.GetHeight()
                        print('Camera %d grabbed image %d, width = %d, height = %d' % (i, n, width, height))

                        # Convert image to mono 8
                        # image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)

                        # Create a unique filename
                        filename = os.path.join(seq_dir, 'images_%d' % i, '%010d.jpg' % n)
                        # TODO: check order of left/right cameras

                        # if device_serial_number:
                        #     filename = 'AcquisitionMultipleCamera-%s-%d.jpg' % (device_serial_number, n)
                        # else:
                        #     filename = 'AcquisitionMultipleCamera-%d-%d.jpg' % (i, n)

                        # Save image
                        image_result.Save(filename)
                        print('Image saved at %s' % filename)

                        # Display chunk data
                        if CHOSEN_CHUNK_DATA_TYPE == ChunkDataTypes.IMAGE:
                            result &= display_chunk_data_from_image(image_result)
                        elif CHOSEN_CHUNK_DATA_TYPE == ChunkDataTypes.NODEMAP:
                            result, ts_str = display_chunk_data_from_nodemap(cam.GetNodeMap())

                            if n == 0:
                                FIRST_TS_list[i] = int(ts_str)
                            value_new = (int(ts_str) - FIRST_TS_list[i]) * 1e-9
                            # timestamp_txt[i].write("%.10f\n" % value_new)
                            f = open(os.path.join(seq_dir, 'timestamps_%d.txt' % i), 'a+')
                            f.write("%.10f\n" % value_new)

                    # Release image
                    image_result.Release()
                    print()

                except PySpin.SpinnakerException as ex:
                    print('Error: %s' % ex)
                    result = False

            for i, cam in enumerate(cam_list):
                timestamp_txt[i].close()

        with open(os.path.join(seq_dir, 'start_time.txt'), 'w') as start_time_txt:
            time_str = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')
            start_time_txt.write("%s\n" % time_str)
            # for cam_st in start_time_cam:
            #     time_str = datetime.datetime.fromtimestamp(cam_st).strftime('%Y-%m-%d %H:%M:%S.%f')
            #     start_time_txt.write("%s\n" % time_str)
            time_str = datetime.datetime.fromtimestamp(start_time_cam).strftime('%Y-%m-%d %H:%M:%S.%f')
            start_time_txt.write("%s\n" % time_str)
            start_time_txt.write("\n")
            
            for ff in FIRST_TS_list:
                start_time_txt.write("%d\n" % ff)
                
            # TODO: transform time format to readable

        # End acquisition for each camera
        #
        # *** NOTES ***
        # Notice that what is usually a one-step process is now two steps
        # because of the additional step of selecting the camera. It is worth
        # repeating that camera selection needs to be done once per loop.
        #
        # It is possible to interact with cameras through the camera list with
        # GetByIndex(); this is an alternative to retrieving cameras as
        # CameraPtr objects that can be quick and easy for small tasks.
        for cam in cam_list:

            # End acquisition
            cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def run_multiple_cameras(cam_list, seq_dir, frame_rate, num_img, radar=True, interval=0):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam_list: List of cameras
    :type cam_list: CameraList
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve transport layer nodemaps and print device information for
        # each camera
        # *** NOTES ***
        # This example retrieves information from the transport layer nodemap
        # twice: once to print device information and once to grab the device
        # serial number. Rather than caching the nodem#ap, each nodemap is
        # retrieved both times as needed.
        print('*** DEVICE INFORMATION ***\n')

        for i, cam in enumerate(cam_list):

            # Retrieve TL device nodemap
            nodemap_tldevice = cam.GetTLDeviceNodeMap()

            # Print device information
            result &= print_device_info_multi(nodemap_tldevice, i)

        # Initialize each camera
        #
        # *** NOTES ***
        # You may notice that the steps in this function have more loops with
        # less steps per loop; this contrasts the AcquireImages() function
        # which has less loops but more steps per loop. This is done for
        # demonstrative purposes as both work equally well.
        #
        # *** LATER ***
        # Each camera needs to be deinitialized once all images have been
        # acquired.
        for i, cam in enumerate(cam_list):

            # Initialize camera
            cam.Init()

            # Retrieve GenICam nodemap
            nodemap = cam.GetNodeMap()
            # Retrieve Stream Parameters device nodemap
            s_node_map = cam.GetTLStreamNodeMap()

            # Configure chunk data
            if configure_chunk_data(nodemap) is False:
                return False
            if configure_buffer(s_node_map) is False:
                return False

        if configure_trigger_multi(cam_list, sync=True) is False:
            return False

        # Acquire images on all cameras
        result &= acquire_images(cam_list, seq_dir, frame_rate, num_img, radar, interval)

        # Deinitialize each camera
        #
        # *** NOTES ***
        # Again, each camera must be deinitialized separately by first
        # selecting the camera and then deinitializing it.
        for cam in cam_list:

            # Disable chunk data
            if disable_chunk_data(cam.GetNodeMap()) is False:
                return False

            # Deinitialize camera
            cam.DeInit()

        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        del cam

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result
