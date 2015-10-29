"""Reads and writes the .anim files into the library."""

import os
import os.path
import errno
import json
import pprint
import maya.cmds as cmds

EXT = '.anim'

#======================================================================
def write(filepath, data, overwrite=False):
    """Checks the filepath is fine to write to, converts the data using
    json and then writes the converted data to the filepath. Returns
    the filepath.
    """
    # Ensure the filepath ends with the extension.
    if not filepath.endswith(EXT):
        cmds.error("Filepath missing extension "
                   "{0}: {1}".format(EXT, filepath))
    
    # Ensure the directory structure exists.
    directory = os.path.dirname(filepath)
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    if not os.path.isdir(directory):
        cmds.error("{0} is not a directory: {1}".format(directory,
                                                        filepath,))
    
    # If the file exists and overwrite is False prompt the user.
    if os.path.exists(filepath):
        if os.path.isdir(filepath):
            cmds.error("Filepath is directory: {0}".format(filepath))
        elif not overwrite:
            result = cmds.confirmDialog(
                title='File exists',
                message='Overwrite existing anim file?',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
    
            if result != 'OK':
                cmds.error("User chose not to overwrite existing file.")

    # Pack and convert the data using json.
    output_data = json.dumps(data)
    
    # Write the anim data to the file.
    with open(filepath, 'w') as export_file:
        export_file.write(output_data)
        #export_file.write(pprint.pformat(data))
	return filepath
	
#======================================================================
def read(filepath):
    """Checks the filepath is fine to read from, reads the data, then
    converts it from json and returns the data for the export info, 
    the exported channels and the references, anim_curves and con-
    straints to rebuild.
    """
    # Check the file exists as a .anim file.
    if not filepath.endswith(EXT):
        cmds.error("Filepath missing extension "
                   "{0}: {1}".format(EXT, filepath))
        
    # Check the file exists.
    if not os.path.exists(filepath):
        cmds.error("Could not find anim file: {0}".format(filepath))

    # Read the file into a raw_data variable.
    with open(filepath, 'r') as anim_file:
        raw_data = anim_file.read()
        
    # Convert the raw_data using json.
    data = json.loads(raw_data)
    return data


