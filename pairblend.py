"""Exports and rebuilds pairBlend nodes."""

import maya.cmds as cmds

#=======================================================================
def export(pairblend, object):
    """Creates a dictionary of all the data necessary to rebuild the
    curve."""
    # Check the node is a pairblend.
    if not is_type_exportable(cmds.nodeType(pairblend)):
        return None
        
    # Record the name of the pair blend attribute on the blended 
    # transform.
    if object:
        node, attr = object[0].split('.',1)
    else:
        node, attr = None
    print {'name': pairblend, 'object': node, 'attr': attr}
    # Return the data.
    return {'name': pairblend, 'object': node, 'attr': attr}
    
#=======================================================================
def build(data, remap):
    # Create and name the anim curve.
    pairblend = cmds.createNode('pairBlend',
                                 name=data['name'],
                                 skipSelect=True)
                                 
    # Create the attribute to drive the pair blend weight.
    # We need the name of the node in its tokenised form to rebuild it
    # on whatever the hell the rig may end up being.
    if data['object'] and data['attr']:
        object = remap_name(data['object'], remap)
        if cmds.objExists(object):
            if not cmds.objExists(object+'.'+data['attr']):
                cmds.addAttr(object,
                             longName = data['attr'],
                             keyable=True)
    
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
    
    
#======================================================================
def remap_name(name, remap):
    """Remaps the given name if it starts with a token."""
    old_name = name
    if name and name.startswith("@"):
            token = name.split('!')[0]+'!'
            if token in remap:
                new_value = remap[token]
                name = new_value + name[len(token):]
                if not cmds.objExists(name):
                    print " > Remap failed", old_name, new_value, name
    return name