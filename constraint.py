"""Exports and rebuilds constraint nodes using the constraint diction-
ary format."""
import maya.cmds as cmds

SINGLE_ATTRS = {'pointConstraint':  ('constraintParentInverseMatrix',
                                     'constraintRotatePivotX',
                                     'constraintRotatePivotY',
                                     'constraintRotatePivotZ',
                                     'constraintRotateTranslateX',
                                     'constraintRotateTranslateY',
                                     'constraintRotateTranslateZ',
                                     'offsetX',
                                     'offsetY',
                                     'offsetZ',
                                     'constraintOffsetPolarity',
                                     'restTranslateX',
                                     'restTranslateY',
                                     'restTranslateZ',),
                 'aimConstraint':   ('constraintParentInverseMatrix',
                                     'aimVectorX',
                                     'aimVectorY',
                                     'aimVectorZ',
                                     'upVectorX',
                                     'upVectorY',
                                     'upVectorZ',
                                     'worldUpVectorX',
                                     'worldUpVectorY',
                                     'worldUpVectorZ',
                                     'worldUpMatrix',
                                     'worldUpType',
                                     'scaleCompensate',
                                     'inverseScaleX',
                                     'inverseScaleY',
                                     'inverseScaleZ',
                                     'offsetX',
                                     'offsetY',
                                     'offsetZ',
                                     'restRotateX',
                                     'restRotateY',
                                     'restRotateZ',),
                 'orientConstraint':('constraintParentInverseMatrix',
                                     'constraintRotateOrder',
                                     'constraintJointOrientX',
                                     'constraintJointOrientY',
                                     'constraintJointOrientZ',
                                     'scaleCompensate',
                                     'inverseScaleX',
                                     'inverseScaleY',
                                     'inverseScaleZ',
                                     'offsetX',
                                     'offsetY',
                                     'offsetZ',
                                     'restRotateX',
                                     'restRotateY',
                                     'restRotateZ',
                                     'interpType',
                                     'interpCache',
                                     'useOldOffsetCalculation',),
                 'scaleConstraint': ('constraintParentInverseMatrix',
                                     'offsetX',
                                     'offsetY',
                                     'offsetZ',
                                     'restScaleX',
                                     'restScaleY',
                                     'restScaleZ',),
                 'parentConstraint':('constraintParentInverseMatrix',
                                     'lastTargetRotate',
                                     'lastTargetRotateX',
                                     'lastTargetRotateY',
                                     'lastTargetRotateZ',
                                     'constraintRotatePivot',
                                     'constraintRotatePivotX',
                                     'constraintRotatePivotY',
                                     'constraintRotatePivotZ',
                                     'constraintRotateTranslate',
                                     'constraintRotateTranslateX',
                                     'constraintRotateTranslateY',
                                     'constraintRotateTranslateZ',
                                     'restTranslate',
                                     'restTranslateX',
                                     'restTranslateY',
                                     'restTranslateZ',
                                     'constraintRotateOrder',
                                     'constraintJointOrient',
                                     'constraintJointOrientX',
                                     'constraintJointOrientY',
                                     'constraintJointOrientZ',
                                     'restRotate',
                                     'restRotateX',
                                     'restRotateY',
                                     'restRotateZ',
                                     'interpType',
                                     'interpCache',),}
                                     
TARGET_ATTRS = {'pointConstraint':  ('target[{0}].targetTranslate',
                                     'target[{0}].targetTranslateX',
                                     'target[{0}].targetTranslateY',
                                     'target[{0}].targetTranslateZ',
                                     'target[{0}].targetRotatePivot',
                                     'target[{0}].targetRotatePivotX',
                                     'target[{0}].targetRotatePivotY',
                                     'target[{0}].targetRotatePivotZ',
                                     'target[{0}].targetRotateTranslate',
                                     'target[{0}].targetRotateTranslateX',
                                     'target[{0}].targetRotateTranslateY',
                                     'target[{0}].targetRotateTranslateZ',
                                     'target[{0}].targetParentMatrix',
                                     'target[{0}].targetWeight',),
                 'aimConstraint':   ('target[{0}].targetTranslate',
                                     'target[{0}].targetTranslateX',
                                     'target[{0}].targetTranslateY',
                                     'target[{0}].targetTranslateZ',
                                     'target[{0}].targetRotatePivot',
                                     'target[{0}].targetRotatePivotX',
                                     'target[{0}].targetRotatePivotY',
                                     'target[{0}].targetRotatePivotZ',
                                     'target[{0}].targetRotateTranslate',
                                     'target[{0}].targetRotateTranslateX',
                                     'target[{0}].targetRotateTranslateY',
                                     'target[{0}].targetRotateTranslateZ',
                                     'target[{0}].targetParentMatrix',
                                     'target[{0}].targetWeight'),
                 'orientConstraint':('target[{0}].targetRotate',
                                     'target[{0}].targetRotateX',
                                     'target[{0}].targetRotateY',
                                     'target[{0}].targetRotateZ',
                                     'target[{0}].targetRotateOrder',
                                     'target[{0}].targetJointOrient',
                                     'target[{0}].targetJointOrientX',
                                     'target[{0}].targetJointOrientY',
                                     'target[{0}].targetJointOrientZ',
                                     'target[{0}].targetParentMatrix',
                                     'target[{0}].targetWeight',),
                 'scaleConstraint': ('target[{0}].targetScale',
                                     'target[{0}].targetScaleX',
                                     'target[{0}].targetScaleY',
                                     'target[{0}].targetScaleZ',
                                     'target[{0}].targetParentMatrix',
                                     'target[{0}].targetWeight'),
                 'parentConstraint':('target[{0}].targetParentMatrix',
                                     'target[{0}].targetWeight',
                                     'target[{0}].targetTranslate',
                                     'target[{0}].targetTranslateX',
                                     'target[{0}].targetTranslateY',
                                     'target[{0}].targetTranslateZ',
                                     'target[{0}].targetRotatePivot',
                                     'target[{0}].targetRotatePivotX',
                                     'target[{0}].targetRotatePivotY',
                                     'target[{0}].targetRotatePivotZ',
                                     'target[{0}].targetRotateTranslate',
                                     'target[{0}].targetRotateTranslateX',
                                     'target[{0}].targetRotateTranslateY',
                                     'target[{0}].targetRotateTranslateZ',
                                     'target[{0}].targetOffsetTranslate',
                                     'target[{0}].targetOffsetTranslateX',
                                     'target[{0}].targetOffsetTranslateY',
                                     'target[{0}].targetOffsetTranslateZ',
                                     'target[{0}].targetRotate',
                                     'target[{0}].targetRotateX',
                                     'target[{0}].targetRotateY',
                                     'target[{0}].targetRotateZ',
                                     'target[{0}].targetRotateOrder',
                                     'target[{0}].targetJointOrient',
                                     'target[{0}].targetJointOrientX',
                                     'target[{0}].targetJointOrientY',
                                     'target[{0}].targetJointOrientZ',
                                     'target[{0}].targetOffsetRotate',
                                     'target[{0}].targetOffsetRotateX',
                                     'target[{0}].targetOffsetRotateY',
                                     'target[{0}].targetOffsetRotateZ',
                                     'target[{0}].targetScale',
                                     'target[{0}].targetScaleX',
                                     'target[{0}].targetScaleY',
                                     'target[{0}].targetScaleZ'),}

#=======================================================================
def export(constraint_node):
    """Returns the data necessary to rebuild the constraint node so it
    is ready to receive channel data.
    """
    # Determine the type of constraint.
    node_type = cmds.nodeType(constraint_node)
    if not is_type_exportable(node_type):
        return None
    
    # Record the names of the custom weight attrs (the ones that the
    # users interact with that are named after the target object).
    weight_attrs = get_custom_weight_attrs(constraint_node)
    
    # Return the data.
    return {'name': constraint_node,
            'type': node_type,
            'weight_attrs':weight_attrs,}
    
    
#=======================================================================
def build(constraint_data):
    """Uses the constraint data to rebuild the constraint node ready to
    receive channel data.
    """    
    # Create the constraint node.
    node = cmds.createNode(constraint_data['type'],
                           name=constraint_data['name'],
                           skipSelect=True)
    
    # Add the custom weight attrs to receive the channel data.
    for attr in constraint_data['weight_attrs']:
        cmds.addAttr(node,
                     longName = attr.split('.')[1],
                     attributeType='float',)
    return node


#=======================================================================
def is_type_exportable(node_type):
    """Returns True if the node type is something we can export."""
    exportable_types = ['pointConstraint',
                        'aimConstraint',
                        'orientConstraint',
                        'scaleConstraint',
                        'parentConstraint',]
    return node_type in exportable_types
    
#=======================================================================
def list_channels(constraint_node):
    """Returns a list of channels that need values/connections published
    to later rebuild the constraint.
    """
    # Determine the type of constraint and the number of targets.
    node_type = cmds.nodeType(constraint_node)
    if not is_type_exportable(node_type):
        return None
    indices = cmds.getAttr(constraint_node+'.target', multiIndices=True)
    
    # Return a list of attributes to export, including custom weight
    # attributes that plug into the actual target weight attrs.
    attrs = [constraint_node+'.'+x for x in SINGLE_ATTRS[node_type]]
    for i in indices:
        attrs += [constraint_node+'.'+x.format(i)
                  for x in TARGET_ATTRS[node_type]]
    attrs += get_custom_weight_attrs(constraint_node)
    return attrs
                           
                           
#=======================================================================
def get_custom_weight_attrs(constraint_node):
    """Returns a dictionary of the custom weight attributes--the
    attrs that users interact with like 'ani01:hand_ctrlW0'--and the
    internal target weight attr that it links to.
    """
    # Get a list of target weight attributes.
    indices = cmds.getAttr(constraint_node+'.target', multiIndices=True)
    weight_attrs = [constraint_node+'.target['+str(x)+'].targetWeight'
                                                       for x in indices]
    
    # Check each target weight attribute for an upstream custom attr
    custom_weight_attrs = []
    for weight_attr in weight_attrs:
        custom_weight_attrs += cmds.listConnections(
                                             weight_attr,
                                             source=True,
                                             destination=False,
                                             plugs=True,
                                             skipConversionNodes=True)            
    return custom_weight_attrs
    
#=======================================================================
def get_first_constrained_object(constraint_node):
    """Finds the first object linked to the output of the constraint
    output channels.
    """
    attrs = ('.constraintTranslate',
             '.constraintTranslateX',
             '.constraintTranslateY',
             '.constraintTranslateZ',
             '.constraintRotate',
             '.constraintRotateX',
             '.constraintRotateY',
             '.constraintRotateZ',
             '.constraintScale',
             '.constraintScaleX',
             '.constraintScaleY',
             '.constraintScaleZ',)
    for attr in attrs:
        if cmds.objExists(constraint_node+attr):
            nodes = cmds.listConnections(constraint_node+attr)
            if nodes:
                if cmds.nodeType(nodes[0]) == 'pairBlend':
                    pairblend = nodes[0]
                    for x in ('.outRotate',
                              '.outRotateX',
                              '.outRotateY',
                              '.outRotateZ',
                              '.outTranslate',
                              '.outTranslateX',
                              '.outTranslateY',
                              '.outTranslateZ',):
                        nodes = cmds.listConnections(pairblend+x)
                        if nodes:
                            for node in nodes:
                                if cmds.nodeType(node) == 'transform':
                                    return node
                            
                else:
                    return nodes[0]
    return None
    
#=======================================================================
def tidy_constraint_node(constraint_node):
    """The custom weight attrs may refer to non-existant nodes, i.e.
    'ani01:hand_ctrlW0' when ani01 has been swapped out with tim01. This
    script matches their name to the name of the current target objects.
    """
    # Hide the transform channels from the channel box
    for ch in ('.tx',
               '.ty',
               '.tz',
               '.rx',
               '.ry',
               '.rz',
               '.sx',
               '.sy',
               '.sz',
               '.v'):
        cmds.setAttr(constraint_node+ch,
                     keyable=False,
                     channelBox=False)
        
    # Parent the node under the the constrained transform.
    object = get_first_constrained_object(constraint_node)
    if object:
        print constraint_node, object
        cmds.parent(constraint_node, object)
    
    # Create new custom weight attributes with the target names, and
    # transfer the connections.
    if not cmds.objExists(constraint_node+'.target'):
        print(' >>> No targets found for constraint {0}'.format(constraint_node))
        return
    indices = cmds.getAttr(constraint_node+'.target', multiIndices=True)
    for i in indices:
        pm_attr = '.target[{0}].targetParentMatrix'.format(str(i))
        target = cmds.listConnections(constraint_node+pm_attr)
        weight_attr = '.target[{0}].targetWeight'.format(str(i))
        weight = cmds.listConnections(constraint_node+weight_attr,
                                      plugs=True)
        if target and weight:
            cmds.setAttr(weight[0], keyable=True)
            attr_name = target[0].split(':')[-1]+'W'+str(i)
            if not cmds.objExists(constraint_node+'.'+attr_name):
                cmds.renameAttr(weight[0], attr_name)
    
    
    
    return
