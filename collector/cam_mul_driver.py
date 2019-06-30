# coding=utf-8
import PySpin
import os
import time

from .cam_driver import display_chunk_data_from_image
from .cam_driver import display_chunk_data_from_nodemap
from .radar_driver import run_radar
from .radar_driver import init_radar


# Use the following class and global variable to select whether
# chunk data is displayed from the image or the nodemap.
class ChunkDataTypes:
    IMAGE = 1
    NODEMAP = 2


CHOSEN_CHUNK_DATA_TYPE = ChunkDataTypes.NODEMAP


def acquire_images(cam_list, seq_dir, frame_rate, num_img):
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
        timestamp_txt = [None] * len(cam_list)

        # Prepare each camera to acquire images
        #
        # *** NOTES ***
        # For pseudo-simultaneous streaming, each camera is prepared as if it
        # were just one, but in a loop. Notice that cameras are selected with
        # an index. We demonstrate pseduo-simultaneous streaming because true
        # simultaneous streaming would require multiple process or threads,
        # which is too complex for an example.
        #
        # Serial numbers are the only persistent objects we gather in this
        # example, which is why a vector is created.
        for i, cam in enumerate(cam_list):

            # Set acquisition mode to continuous
            node_acquisition_mode = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (node retrieval; camera %d). Aborting... \n' % i)
                return False

            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry \'continuous\' retrieval %d). \
                Aborting... \n' % i)
                return False
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
            print('Camera %d acquisition mode set to continuous...' % i)

            # Set trigger mode to Off
            node_trigger_mode = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('TriggerMode'))
            if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsWritable(node_trigger_mode):
                print('Unable to set trigger mode to off (node retrieval). Aborting...')
                return False
            node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
            if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
                print('Unable to set trigger mode to off (entry retrieval). Aborting...')
                return False
            trigger_mode_off = node_trigger_mode_off.GetValue()
            node_trigger_mode.SetIntValue(trigger_mode_off)
            print('Camera %d trigger mode set to off...' % i)

            # Set acquisition frame rate enable to true
            acquisition_frame_rate_active = PySpin.CBooleanPtr(cam.GetNodeMap().GetNode('AcquisitionFrameRateEnable'))
            if PySpin.IsAvailable(acquisition_frame_rate_active) and PySpin.IsWritable(acquisition_frame_rate_active):
                acquisition_frame_rate_active.SetValue(True)
            print('Camera %d acquisition frame rate activated...' % i)

            # Set frame rate to the given value
            node_acquisition_frame_rate = PySpin.CFloatPtr(cam.GetNodeMap().GetNode('AcquisitionFrameRate'))
            if not PySpin.IsAvailable(node_acquisition_frame_rate) or not PySpin.IsWritable(
                    node_acquisition_frame_rate):
                print('Unable to set frame rate (node retrieval). Aborting...')
                return False
            node_acquisition_frame_rate.SetValue(frame_rate)
            print('Camera %d acquisition frame rate set to %d...\n' % (i, frame_rate))

            timestamp_txt[i] = open(os.path.join(seq_dir, 'timestamps_%d.txt' % i), 'w')

        # pause
        # input("Initialization finished! Press Enter to continue ...")

        # Init radar
        engine = init_radar()
        # Run radar
        run_radar(engine)

        # record start time
        start_time = time.time()
        # print(start_time)

        for i, cam in enumerate(cam_list):
            # Begin acquiring images
            cam.BeginAcquisition()
            print('Camera %d started acquiring images...' % i)

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
        for n in range(num_img):
            for i, cam in enumerate(cam_list):
                try:
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
                        filename = os.path.join(seq_dir, 'images_' % i, '%010d.jpg' % n)
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

                            if i == 0:
                                FIRST_TS = int(ts_str)
                            value_new = (int(ts_str) - FIRST_TS) * 1e-9
                            timestamp_txt[i].write("%.10f\n" % value_new)

                    # Release image
                    image_result.Release()
                    print()

                except PySpin.SpinnakerException as ex:
                    print('Error: %s' % ex)
                    result = False

            for i, cam in enumerate(cam_list):
                timestamp_txt[i].close()

        with open(os.path.join(seq_dir, 'start_time.txt'), 'w') as start_time_txt:
            start_time_txt.write("%s" % start_time)
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


def print_device_info(nodemap, cam_num):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :param cam_num: Camera number.
    :type nodemap: INodeMap
    :type cam_num: int
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('Printing device information for camera %d... \n' % cam_num)

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not available.')
        print()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def run_multiple_cameras(cam_list):
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
            result &= print_device_info(nodemap_tldevice, i)

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

        # Acquire images on all cameras
        result &= acquire_images(cam_list)

        # Deinitialize each camera
        #
        # *** NOTES ***
        # Again, each camera must be deinitialized separately by first
        # selecting the camera and then deinitializing it.
        for cam in cam_list:

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
