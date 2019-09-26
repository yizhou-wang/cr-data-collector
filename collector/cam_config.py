try:
    import PySpin
except:
    print("Warning: PySpin is not installed!")


serial_left_1   = '18384019'
serial_right_1  = '19325055'


# Use the following class and global variable to select whether
# chunk data is displayed from the image or the nodemap.
class ChunkDataTypes:
    IMAGE = 1
    NODEMAP = 2


class TriggerType:
    NULL = 0
    SOFTWARE = 1
    HARDWARE = 2
    HARDWARE_SEC = 3


CHOSEN_CHUNK_DATA_TYPE = ChunkDataTypes.NODEMAP
CHOSEN_TRIGGER = TriggerType.SOFTWARE


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


def display_chunk_data_from_nodemap(nodemap, verbose=False):
    """
    This function displays all available chunk data by looping through the
    chunk data category node on the nodemap.

    :param nodemap: Device nodemap to retrieve images from.
    :type nodemap: INodeMap
    :return: True if successful, False otherwise
    :rtype: bool
    """
    # print('Printing chunk data from nodemap...')

    try:
        result = True
        ts_str = None
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
                if verbose:
                    print('{} {}'.format(feature_display_name, feature_value.ToString()))

                if feature_node.GetDisplayName() == 'Chunk Timestamp':
                    ts_str = feature_value.ToString()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False
        ts_str = None

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


def print_device_info_multi(nodemap, cam_num):
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


def configure_buffer(s_node_map):

    try:
        result = True
        ####################
        # BufferHandling
        ####################

        # Retrieve Buffer Handling Mode Information
        handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
        if not PySpin.IsAvailable(handling_mode) or not PySpin.IsWritable(handling_mode):
            print('Unable to set Buffer Handling mode (node retrieval). Aborting...\n')
            return False

        handling_mode_entry = PySpin.CEnumEntryPtr(handling_mode.GetCurrentEntry())
        if not PySpin.IsAvailable(handling_mode_entry) or not PySpin.IsReadable(handling_mode_entry):
            print('Unable to set Buffer Handling mode (Entry retrieval). Aborting...\n')
            return False

        # Set stream buffer Count Mode to manual
        stream_buffer_count_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferCountMode'))
        if not PySpin.IsAvailable(stream_buffer_count_mode) or not PySpin.IsWritable(stream_buffer_count_mode):
            print('Unable to set Buffer Count Mode (node retrieval). Aborting...\n')
            return False

        stream_buffer_count_mode_manual = PySpin.CEnumEntryPtr(stream_buffer_count_mode.GetEntryByName('Manual'))
        if not PySpin.IsAvailable(stream_buffer_count_mode_manual) or not PySpin.IsReadable(stream_buffer_count_mode_manual):
            print('Unable to set Buffer Count Mode entry (Entry retrieval). Aborting...\n')
            return False

        stream_buffer_count_mode.SetIntValue(stream_buffer_count_mode_manual.GetValue())
        print('Stream Buffer Count Mode set to manual...')

        # Retrieve and modify Stream Buffer Count
        buffer_count = PySpin.CIntegerPtr(s_node_map.GetNode('StreamBufferCountManual'))
        if not PySpin.IsAvailable(buffer_count) or not PySpin.IsWritable(buffer_count):
            print('Unable to set Buffer Count (Integer node retrieval). Aborting...\n')
            return False

        # Display Buffer Info
        print('\nDefault Buffer Handling Mode: %s' % handling_mode_entry.GetDisplayName())
        print('Default Buffer Count: %d' % buffer_count.GetValue())
        print('Maximum Buffer Count: %d' % buffer_count.GetMax())

        buffer_count.SetValue(buffer_count.GetMax())
        print('Buffer count now set to: %d' % buffer_count.GetValue())

    except:
        result = False

    return result


def configure_trigger(nodemap, trigger_type=TriggerType.SOFTWARE):
    try:
        result = True
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

        # Select trigger source
        # The trigger source must be set to hardware or software while trigger
        # mode is off.
        node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
        if not PySpin.IsAvailable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
            print('Unable to get trigger source (node retrieval). Aborting...')
            return False

        if trigger_type == TriggerType.NULL:
            pass
        if trigger_type == TriggerType.SOFTWARE:
            node_trigger_source_software = node_trigger_source.GetEntryByName('Software')
            if not PySpin.IsAvailable(node_trigger_source_software) or not PySpin.IsReadable(
                    node_trigger_source_software):
                print('Unable to set trigger source (enum entry retrieval). Aborting...')
                return False
            node_trigger_source.SetIntValue(node_trigger_source_software.GetValue())

        elif trigger_type == TriggerType.HARDWARE:
            node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line0')
            if not PySpin.IsAvailable(node_trigger_source_hardware) or not PySpin.IsReadable(
                    node_trigger_source_hardware):
                print('Unable to set trigger source (enum entry retrieval). Aborting...')
                return False
            node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())

        elif trigger_type == TriggerType.HARDWARE_SEC:
            node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line3')
            if not PySpin.IsAvailable(node_trigger_source_hardware) or not PySpin.IsReadable(
                    node_trigger_source_hardware):
                print('Unable to set trigger source (enum entry retrieval). Aborting...')
                return False
            node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())

        if trigger_type != TriggerType.NULL:
            # Turn trigger mode on
            # Once the appropriate trigger source has been set, turn trigger mode
            # on in order to retrieve images using the trigger.
            node_trigger_mode_on = node_trigger_mode.GetEntryByName('On')
            if not PySpin.IsAvailable(node_trigger_mode_on) or not PySpin.IsReadable(node_trigger_mode_on):
                print('Unable to enable trigger mode (enum entry retrieval). Aborting...')
                return False

            node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())
            print('Trigger mode turned back on...')

    except:
        result = False

    return result


def configure_trigger_multi(cam_list, sync=False):
    try:
        result = True
        if sync:
            # cam_1 = cam_list.GetBySerial(serial_left_1)
            # cam_2 = cam_list.GetBySerial(serial_right_1)
            cam_1 = cam_list[0]
            cam_2 = cam_list[1]
            configure_trigger(cam_1.GetNodeMap(), trigger_type=TriggerType.NULL)
            configure_trigger(cam_2.GetNodeMap(), trigger_type=TriggerType.HARDWARE_SEC)

        else:
            for cam in cam_list:
                nodemap = cam.GetNodeMap()
                configure_trigger(nodemap)
    except:
        result = False

    return result


def grab_next_image_by_trigger(nodemap, trigger_type=TriggerType.SOFTWARE):
    """
    This function acquires an image by executing the trigger node.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        # Use trigger to capture image
        # The software trigger only feigns being executed by the Enter key;
        # what might not be immediately apparent is that there is not a
        # continuous stream of images being captured; in other examples that
        # acquire images, the camera captures a continuous stream of images.
        # When an image is retrieved, it is plucked from the stream.

        if trigger_type == TriggerType.SOFTWARE:
            # Execute software trigger
            node_softwaretrigger_cmd = PySpin.CCommandPtr(nodemap.GetNode('TriggerSoftware'))
            if not PySpin.IsAvailable(node_softwaretrigger_cmd) or not PySpin.IsWritable(node_softwaretrigger_cmd):
                print('Unable to execute trigger. Aborting...')
                return False

            # Get user input
            input('Press the Enter key to initiate software trigger.')

            node_softwaretrigger_cmd.Execute()

            # TODO: Blackfly and Flea3 GEV cameras need 2 second delay after software trigger

        elif trigger_type == TriggerType.HARDWARE:
            print('Use the hardware to trigger image acquisition.')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result
