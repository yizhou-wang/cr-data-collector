# coding=utf-8
try:
    import PySpin
except:
    print("Warning: PySpin is not installed!")

import os
import time

from .cam_config import ChunkDataTypes, CHOSEN_CHUNK_DATA_TYPE
from .cam_config import configure_chunk_data, disable_chunk_data, \
    display_chunk_data_from_image, display_chunk_data_from_nodemap
from .cam_config import configure_buffer, configure_trigger
from .cam_config import print_device_info
from .radar_driver import run_radar
from .radar_driver import init_radar
from .radar_driver import check_datetime


def acquire_images(cam, nodemap, nodemap_tldevice, seq_dir, frame_rate, num_img, radar=True, interval=0):
    """
    This function acquires and saves 10 images from a device.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    # TODO: remove input frame_rate if not needed.

    print('\n*** IMAGE ACQUISTION ***\n')

    try:
        result = True

        # Set acquisition mode to continuous
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (node retrieval). Aborting...')
            return False
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
        print('Acquisition mode set to continuous...')

        # Set acquisition frame rate enable to true
        acquisition_frame_rate_active = PySpin.CBooleanPtr(nodemap.GetNode('AcquisitionFrameRateEnable'))
        if PySpin.IsAvailable(acquisition_frame_rate_active) and PySpin.IsWritable(acquisition_frame_rate_active):
            acquisition_frame_rate_active.SetValue(True)
        print('Acquisition frame rate activated...')

        # Set frame rate to the given value
        node_acquisition_frame_rate = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionFrameRate'))
        if not PySpin.IsAvailable(node_acquisition_frame_rate) or not PySpin.IsWritable(node_acquisition_frame_rate):
            print('Unable to set frame rate (node retrieval). Aborting...')
            return False
        node_acquisition_frame_rate.SetValue(frame_rate)
        print('Acquisition frame rate set to %d...\n' % frame_rate)

        timestamp_txt = open(os.path.join(seq_dir, 'timestamps.txt'), 'w')

        # pause
        # input("Initialization finished! Press Enter to continue ...")

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

        # Begin acquiring images
        #
        # *** NOTES ***
        # What happens when the camera begins acquiring images depends on the
        # acquisition mode. Single frame captures only a single image, multi
        # frame captures a set number of images, and continuous captures a
        # continuous stream of images. As the example calls for the
        # retrieval of 10 images, continuous mode has been set.
        #
        # *** LATER ***
        # Image acquisition must be ended when no more images are needed.
        cam.BeginAcquisition()

        # # record start time
        # start_time = time.time()
        # print(start_time)

        print('Acquiring images...')

        # Retrieve device serial number for filename
        #
        # *** NOTES ***
        # The device serial number is retrieved in order to keep cameras from
        # overwriting one another. Grabbing image IDs could also accomplish
        # this.
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)

        # Retrieve, convert, and save images
        for i in range(num_img):
            try:
                # Retrieve next received image
                #
                # *** NOTES ***
                # Capturing an image houses images on the camera buffer. Trying
                # to capture an image that does not exist will hang the camera.
                #
                # *** LATER ***
                # Once an image from the buffer is saved and/or no longer
                # needed, the image must be released in order to keep the
                # buffer from filling up.
                image_result = cam.GetNextImage()

                # Ensure image completion
                #
                # *** NOTES ***
                # Images can be easily checked for completion. This should be
                # done whenever a complete image is expected or required.
                # Further, check image status for a little more insight into
                # why an image is incomplete.
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
                else:

                    # Print image information
                    #
                    # *** NOTES ***
                    # Images have quite a bit of available metadata including
                    # things such as CRC, image status, and offset values, to
                    # name a few.
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                    print('Grabbed Image %d, width = %d, height = %d' % (i, width, height))

                    # Convert image to mono 8
                    #
                    # *** NOTES ***
                    # Images can be converted between pixel formats by using
                    # the appropriate enumeration value. Unlike the original
                    # image, the converted one does not need to be released as
                    # it does not affect the camera buffer.
                    #
                    # When converting images, color processing algorithm is an
                    # optional parameter.
                    # image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)

                    
                    # Create a unique filename
                    # filename = '%s/images/%010d.jpg' % (seq_dir, i)
                    filename = os.path.join(seq_dir, 'images', '%010d.jpg' % i)

                    # Save image
                    #
                    # *** NOTES ***
                    # The standard practice of the examples is to use device
                    # serial numbers to keep images of one device from
                    # overwriting those of another.
                    # print('TEST1')
                    # image_converted.Save(filename)
                    image_result.Save(filename)
                    print('Image saved at %s' % filename)
                    

                    # Display chunk data
                    if CHOSEN_CHUNK_DATA_TYPE == ChunkDataTypes.IMAGE:
                        result &= display_chunk_data_from_image(image_result)
                    elif CHOSEN_CHUNK_DATA_TYPE == ChunkDataTypes.NODEMAP:
                        result, ts_str = display_chunk_data_from_nodemap(nodemap)

                        if i == 0:
                            FIRST_TS = int(ts_str)
                        value_new = (int(ts_str) - FIRST_TS) * 1e-9
                        timestamp_txt.write("%.10f\n" % value_new)

                    # Release image
                    #
                    # *** NOTES ***
                    # Images retrieved directly from the camera (i.e. non-converted
                    # images) need to be released in order to keep from filling the
                    # buffer.
                    image_result.Release()
                    print('')

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

        timestamp_txt.close()

        with open(os.path.join(seq_dir, 'start_time.txt'), 'w') as start_time_txt:
            start_time_txt.write("%s" % start_time)
            # TODO: transform time format to readable

        # End acquisition
        #
        # *** NOTES ***
        # Ending acquisition appropriately helps ensure that devices clean up
        # properly and do not need to be power-cycled to maintain integrity.
        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def run_single_camera(cam, seq_dir, frame_rate, num_img, radar=True, interval=0):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()
        # Retrieve Stream Parameters device nodemap
        s_node_map = cam.GetTLStreamNodeMap()

        if configure_trigger(nodemap) is False:
            return False
        # Configure chunk data
        if configure_chunk_data(nodemap) is False:
            return False
        if configure_buffer(s_node_map) is False:
            return False

        # Acquire images and display chunk data
        result &= acquire_images(cam, nodemap, nodemap_tldevice, seq_dir, frame_rate, num_img, radar, interval)

        # Disable chunk data
        if disable_chunk_data(nodemap) is False:
            return False

        # De-initialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result
