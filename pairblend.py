"""Exports and rebuilds pairBlend nodes."""

import maya.cmds as cmds

#=======================================================================
def export(pairblend):
    """Creates a dictionary of all the data necessary to rebuild the
    curve."""
    # Check the node is a pairblend.
    if not is_type_exportable(cmds.nodeType(pairblend)):
        return None
    
    # Return the data.
    return {'name': pairblend,}
    
#=======================================================================
def build(data):
    # Create and name the anim curve.
    pairblend = cmds.createNode('pairBlend',
                                 name=data['name'],
                                 skipSelect=True)
    return pairblend
    
#=======================================================================
def is_type_exportable(node_type):
    """Returns True if the node type is something we can export."""
    return node_type == "pairBlend"

    
#======================================================================
def list_channels(pairblend):
    channels = ('.currentDriver',
                '.inTranslate1',
                '.inTranslateX1',
                '.inTranslateY1',
                '.inTranslateZ1',
                '.inRotate1',
                '.inRotateX1',
                '.inRotateY1',
                '.inRotateZ1',
                '.inTranslate2',
                '.inTranslateX2',
                '.inTranslateY2',
                '.inTranslateZ2',
                '.inRotate2',
                '.inRotateX2',
                '.inRotateY2',
                '.inRotateZ2',
                '.weight',
                '.rotateOrder',
                '.translateXMode',
                '.translateYMode',
                '.translateZMode',
                '.rotateMode',
                '.rotInterpolation',)
    return [pairblend+x for x in channels]