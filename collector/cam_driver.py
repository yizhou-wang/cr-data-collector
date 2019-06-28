# coding=utf-8
# =============================================================================
# Copyright © 2018 FLIR Integrated Imaging Solutions, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
#
# ChunkData.py shows how to get chunk data on an image, either from
# the nodemap or from the image itself. It relies on information provided in
# the Enumeration, Acquisition, and NodeMapInfo examples.
#
# It can also be helpful to familiarize yourself with the ImageFormatControl
# and Exposure samples. As they are somewhat shorter and simpler, either
# provides a strong introduction to camera customization.
#
# Chunk data provides information on various traits of an image. This includes
# identifiers such as frame ID, properties such as black level, and more. This
# information can be acquired from either the nodemap or the image itself.
#
# It may be preferable to grab chunk data from each individual image, as it
# can be hard to verify whether data is coming from the correct image when
# using the nodemap. This is because chunk data retrieved from the nodemap is
# only valid for the current image; when GetNextImage() is called, chunk data
# will be updated to that of the new current image.
#
import PySpin
import os
import time

from .radar_driver import run_radar
from .radar_driver import init_radar


# Use the following class and global variable to select whether
# chunk data is displayed from the image or the nodemap.
class ChunkDataTypes:
    IMAGE = 1
    NODEMAP = 2


CHOSEN_CHUNK_DATA_TYPE = ChunkDataTypes.NODEMAP


def configure_chunk_data(nodemap):
    """
    This function configures the camera to add chunk data to each image. It does
    this by enabling each type of chunk data before enabling chunk data mode.
    When chunk data is turned on, the data is made available in both the nodemap
    and each image.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :return: True if successful, False otherwise
    :rtype: bool
    """
    try:
        result = True
        print('\n*** CONFIGURING CHUNK DATA ***\n')

        # Activate chunk mode
        #
        # *** NOTES ***
        # Once enabled, chunk data will be available at the end of the payload
        # of every image captured until it is disabled. Chunk data can also be
        # retrieved from the nodemap.
        chunk_mode_active = PySpin.CBooleanPtr(nodemap.GetNode('ChunkModeActive'))

        if PySpin.IsAvailable(chunk_mode_active) and PySpin.IsWritable(chunk_mode_active):
            chunk_mode_active.SetValue(True)

        print('Chunk mode activated...')

        # Enable all types of chunk data
        #
        # *** NOTES ***
        # Enabling chunk data requires working with nodes: "ChunkSelector"
        # is an enumeration selector node and "ChunkEnable" is a boolean. It
        # requires retrieving the selector node (which is of enumeration node
        # type), selecting the entry of the chunk data to be enabled, retrieving
        # the corresponding boolean, and setting it to be true.
        #
        # In this example, all chunk data is enabled, so these steps are
        # performed in a loop. Once this is complete, chunk mode still needs to
        # be activated.
        chunk_selector = PySpin.CEnumerationPtr(nodemap.GetNode('ChunkSelector'))

        if not PySpin.IsAvailable(chunk_selector) or not PySpin.IsReadable(chunk_selector):
            print('Unable to retrieve chunk selector. Aborting...\n')
            return False

        # Retrieve entries
        #
        # *** NOTES ***
        # PySpin handles mass entry retrieval in a different way than the C++
        # API. Instead of taking in a NodeList_t reference, GetEntries() takes
        # no parameters and gives us a list of INodes. Since we want these INodes
        # to be of type CEnumEntryPtr, we can use a list comprehension to
        # transform all of our collected INodes into CEnumEntryPtrs at once.
        entries = [PySpin.CEnumEntryPtr(chunk_selector_entry) for chunk_selector_entry in chunk_selector.GetEntries()]

        print('Enabling entries...')

        # Iterate through our list and select each entry node to enable
        for chunk_selector_entry in entries:
            # Go to next node if problem occurs
            if not PySpin.IsAvailable(chunk_selector_entry) or not PySpin.IsReadable(chunk_selector_entry):
                continue

            chunk_selector.SetIntValue(chunk_selector_entry.GetValue())

            chunk_str = '\t {}:'.format(chunk_selector_entry.GetSymbolic())

            # Retrieve corresponding boolean
            chunk_enable = PySpin.CBooleanPtr(nodemap.GetNode('ChunkEnable'))

            # Enable the boolean, thus enabling the corresponding chunk data
            if not PySpin.IsAvailable(chunk_enable):
                print('{} not available'.format(chunk_str))
                result = False
            elif chunk_enable.GetValue() is True:
                print('{} enabled'.format(chunk_str))
            elif PySpin.IsWritable(chunk_enable):
                chunk_enable.SetValue(True)
                print('{} enabled'.format(chunk_str))
            else:
                print('{} not writable'.format(chunk_str))
                result = False

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def display_chunk_data_from_nodemap(nodemap):
    """
    This function displays all available chunk data by looping through the
    chunk data category node on the nodemap.

    :param nodemap: Device nodemap to retrieve images from.
    :type nodemap: INodeMap
    :return: True if successful, False otherwise
    :rtype: bool
    """
    print('Printing chunk data from nodemap...')

    try:
        result = True
        # Retrieve chunk data information nodes
        #
        # *** NOTES ***
        # As well as being written into the payload of the image, chunk data is
        # accessible on the GenICam nodemap. When chunk data is enabled, it is
        # made available from both the image payload and the nodemap.
        chunk_data_control = PySpin.CCategoryPtr(nodemap.GetNode('ChunkDataControl'))
        if not PySpin.IsAvailable(chunk_data_control) or not PySpin.IsReadable(chunk_data_control):
            print('Unable to retrieve chunk data control. Aborting...\n')
            return False

        features = chunk_data_control.GetFeatures()

        # Iterate through children
        for feature in features:
            feature_node = PySpin.CNodePtr(feature)
            feature_display_name = '\t{}:'.format(feature_node.GetDisplayName())

            if not PySpin.IsAvailable(feature_node) or not PySpin.IsReadable(feature_node):
                print('{} node not available'.format(feature_display_name))
                result &= False
                continue
            # Print node type value
            #
            # *** NOTES ***
            # All nodes can be cast as value nodes and have their information
            # retrieved as a string using the ToString() method. This is much
            # easier than dealing with each individual node type.
            else:
                feature_value = PySpin.CValuePtr(feature)
                print('{} {}'.format(feature_display_name, feature_value.ToString()))

                if feature_node.GetDisplayName() == 'Chunk Timestamp':
                    ts_str = feature_value.ToString()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result, ts_str


def display_chunk_data_from_image(image):
    """
    This function displays a select amount of chunk data from the image. Unlike
    accessing chunk data via the nodemap, there is no way to loop through all
    available data.

    :param image: Image to acquire chunk data from
    :type image: Image object
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    print('Printing chunk data from image...')
    try:
        result = True
        print(type(image))
        # Retrieve chunk data from image
        #
        # *** NOTES ***
        # When retrieving chunk data from an image, the data is stored in a
        # ChunkData object and accessed with getter functions.
        chunk_data = image.GetChunkData()

        # Retrieve exposure time (recorded in microseconds)
        exposure_time = chunk_data.GetExposureTime()
        print('\tExposure time: {}'.format(exposure_time))

        # Retrieve frame ID
        frame_id = chunk_data.GetFrameID()
        print('\tFrame ID: {}'.format(frame_id))

        # Retrieve gain; gain recorded in decibels
        gain = chunk_data.GetGain()
        print('\tGain: {}'.format(gain))

        # Retrieve height; height recorded in pixels
        height = chunk_data.GetHeight()
        print('\tHeight: {}'.format(height))

        # Retrieve offset X; offset X recorded in pixels
        offset_x = chunk_data.GetOffsetX()
        print('\tOffset X: {}'.format(offset_x))

        # Retrieve offset Y; offset Y recorded in pixels
        offset_y = chunk_data.GetOffsetY()
        print('\tOffset Y: {}'.format(offset_y))

        # Retrieve sequencer set active
        sequencer_set_active = chunk_data.GetSequencerSetActive()
        print('\tSequencer set active: {}'.format(sequencer_set_active))

        # Retrieve timestamp
        timestamp = chunk_data.GetTimestamp()
        print('\tTimestamp: {}'.format(timestamp))

        # Retrieve width; width recorded in pixels
        width = chunk_data.GetWidth()
        print('\tWidth: {}'.format(width))

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False
    return result


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('\n*** DEVICE INFORMATION ***\n')

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
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def acquire_images(cam, nodemap, nodemap_tldevice, seq_dir, frame_rate, num_img):
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

        # Set trigger mode to Off
        node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
        if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsWritable(node_trigger_mode):
            print('Unable to set trigger mode to off (node retrieval). Aborting...')
            return False
        node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
        if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
            print('Unable to set trigger mode to off (entry retrieval). Aborting...')
            return False
        trigger_mode_off = node_trigger_mode_off.GetValue()
        node_trigger_mode.SetIntValue(trigger_mode_off)
        print('Trigger mode set to off...')

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

        # Init radar
        engine = init_radar()
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


def disable_chunk_data(nodemap):
    """
    This function disables each type of chunk data before disabling chunk data mode.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :return: True if successful, False otherwise
    :rtype: bool
    """
    try:
        result = True

        # Retrieve the selector node
        chunk_selector = PySpin.CEnumerationPtr(nodemap.GetNode('ChunkSelector'))

        if not PySpin.IsAvailable(chunk_selector) or not PySpin.IsReadable(chunk_selector):
            print('Unable to retrieve chunk selector. Aborting...\n')
            return False

        # Retrieve entries
        #
        # *** NOTES ***
        # PySpin handles mass entry retrieval in a different way than the C++
        # API. Instead of taking in a NodeList_t reference, GetEntries() takes
        # no parameters and gives us a list of INodes. Since we want these INodes
        # to be of type CEnumEntryPtr, we can use a list comprehension to
        # transform all of our collected INodes into CEnumEntryPtrs at once.
        entries = [PySpin.CEnumEntryPtr(chunk_selector_entry) for chunk_selector_entry in chunk_selector.GetEntries()]

        print('Disabling entries...')

        for chunk_selector_entry in entries:
            # Go to next node if problem occurs
            if not PySpin.IsAvailable(chunk_selector_entry) or not PySpin.IsReadable(chunk_selector_entry):
                continue

            chunk_selector.SetIntValue(chunk_selector_entry.GetValue())

            chunk_symbolic_form = '\t {}:'.format(chunk_selector_entry.GetSymbolic())

            # Retrieve corresponding boolean
            chunk_enable = PySpin.CBooleanPtr(nodemap.GetNode('ChunkEnable'))

            # Disable the boolean, thus disabling the corresponding chunk data
            if not PySpin.IsAvailable(chunk_enable):
                print('{} not available'.format(chunk_symbolic_form))
                result = False
            elif not chunk_enable.GetValue():
                print('{} disabled'.format(chunk_symbolic_form))
            elif PySpin.IsWritable(chunk_enable):
                chunk_enable.SetValue(False)
                print('{} disabled'.format(chunk_symbolic_form))
            else:
                print('{} not writable'.format(chunk_symbolic_form))

        # Deactivate Chunk Mode
        chunk_mode_active = PySpin.CBooleanPtr(nodemap.GetNode('ChunkModeActive'))

        if not PySpin.IsAvailable(chunk_mode_active) or not PySpin.IsWritable(chunk_mode_active):
            print('Unable to deactivate chunk mode. Aborting...\n')
            return False

        chunk_mode_active.SetValue(False)

        print('Chunk mode deactivated...')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def run_single_camera(cam, seq_dir, frame_rate, num_img):
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

        # Configure chunk data
        if configure_chunk_data(nodemap) is False:
            return False

        # Acquire images and display chunk data
        result &= acquire_images(cam, nodemap, nodemap_tldevice, seq_dir, frame_rate, num_img)

        # Disable chunk data
        if disable_chunk_data(nodemap) is False:
            return False

        # De-initialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result
