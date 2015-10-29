"""Encodes and reads an information dictionary that records various
data about the export."""

import time
import maya.cmds as cmds

#======================================================================
def export(channels, reference_data):
    """Records information about the export conditions.
    """
    info_data = {}
    
    # Record the export time.
    info_data['time'] = time.strftime("%c")
    
    # Record the user and filepath.
    
    # Record the first and last frame, and the frame rate.
    
    # Record the namespaces and references in the channel list.
    reference_info = {}
    for token in reference_data.keys():
        namespace = reference_data[token]['namespace']
        filename = reference_data[token]['filename']
        if not namespace in reference_info:
            reference_info[namespace]={'filename':filename,
                                       'token':token}
    info_data['references']=reference_info
    return info_data