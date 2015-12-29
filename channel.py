"""
Interacts with the values and connections of the channels.

The engine at the heart of the anim library, this script converts chan-
nels in Maya into a tuple (source channel, value, is_default, type) and 
then applies those values back into the Maya scene.
"""
import maya.cmds as cmds        
import pprint

#! Need to get it to support double3 and matrix.

#======================================================================
def get(channel):
    """Receives a channel and returns a tuple with a source attribute 
    (None if there is no connection), the current value, a boolean 
    which records if the attribute has been altered since the file was
    last opened (ie a reference edit) and the type of data.
    """
    # Set defaults.
    value = None
    source = None
    is_altered = False

    # Get the current value of the channel.
    value = cmds.getAttr(channel)

    # Get the current value of the channel.
    data_type = cmds.getAttr(channel, type=True)

    # If the channel is connected, get the name of the connected node.
    connections=cmds.listConnections(channel,
                                     source=True,
                                     destination=False,
                                     plugs=True,
                                     skipConversionNodes=True)
    if connections:
        source = connections[0]
        is_altered=True
        
    # If the channel is not connected but is referenced, query if the 
    # attribute has been changed.
    else:
        if cmds.referenceQuery(channel, isNodeReferenced=True):
            edit = cmds.listAttr(channel, changedSinceFileOpen=True)
            if edit:
            	is_altered=True
            
    return(source, value, is_altered, data_type)

#======================================================================
def set(channel, channel_input, override_unaltered=True):
    """Receives a channel and input data gathered from the get() func.
    If there is a source attribute this function will attempt to con-
    nect it, otherwise it will apply the value (unless it is the
    default value and override_unaltered is True)"""
    
    if '@' in channel:
        cmds.error(channel)
    
    # If the channel doesn't exist then return None.
    if not cmds.objExists(channel):
        print(" > Attribute does not exist: {0}".format(channel))
        return None
    
    if 'Constraint' in channel:
        override_unaltered=True
    
    # Parse the channel_input tuple into variables.
    source = channel_input[0]
    value = channel_input[1]
    was_altered = channel_input[2]
    data_type = channel_input[3]

    # If the channel has not been altered and we aren't overriding un-
    # altered values, then leave the attribute alone.
    if not source and not was_altered and not override_unaltered:
        return channel

    #! What if the channel already has an incoming connection?

    # If the channel has a source attribute, attempt to connect it.
    if source:
        if cmds.objExists(source):
            if cmds.isConnected(source,
                                channel,
                                ignoreUnitConversion=True):
                return channel  
            try:
                cmds.connectAttr(source, channel, force=True)
                return channel
            except:
                print((" > Failed to connect attr : "
                      "'{0}' - {1}, ").format(source, channel)),
                print(channel_input)
        else:
            print((' > Failed to find source attr : '
                      "'{0}' - {1}, ").format(source, channel))

    # Otherwise apply the recorded value.
    if cmds.getAttr(channel, settable=True):
        if is_type_numeric(data_type):
            cmds.setAttr(channel, value)
        else:
            print ' > Failed to set attr [type]:',
            print data_type, channel, value
    else:
		print(" > Failed to set attr [settable] {0}".format(channel)),
		print(channel_input)
    return channel
    
#======================================================================  
def is_gettable(channel, print_msg=True):
    """Returns True if the get() function will operate successfully on 
    the given channel."""
    if not channel:
        return False
    
    if not cmds.objExists(channel):
        print(" > Could not find channel: {0}".format(channel))
        return False
            
    if not is_type_exportable(cmds.getAttr(channel, type=True)):
        print(" > Skipping due to type "
              "{0}: {1}.".format(cmds.getAttr(channel, type=True), channel))
        return False
        
    return True
    
#======================================================================  
def is_settable(channel, print_msg=True):
    """Returns True if the set() function will operate successfully on 
    the given channel."""
    return check_gettable(channel)                 
                       
#=======================================================================
def is_type_exportable(channel_type):
    """Returns True if the attribute type is something we can export."""
    return True
    
#=======================================================================
def is_type_numeric(channel_type):
    """Returns True if the attribute type is something we can export."""
    return channel_type in [
                            "bool",
                            "long",
                            "short",
                            "byte",
                            "char",
                            "enum",
                            "float",
                            "double",
                            "doubleAngle",
                            "doubleLinear",
                           ]
