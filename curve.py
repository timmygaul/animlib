"""Exports and rebuilds animation curves using the curve dictionary
format."""

import maya.cmds as cmds

#=======================================================================
def export(anim_curve):
    """Creates a dictionary of all the data necessary to rebuild the
    curve."""
    
    # Check the curve exists and is an animation curve.
    if not cmds.objExists(anim_curve):
        cmds.error("Failed to find anim curve {0}".format(anim_curve))
        
    type = cmds.nodeType(anim_curve)
    if not is_type_exportable(type):
        cmds.error("Node {0} is not an anim curve".format(anim_curve))
    
    # Get the keys on the curve.
    keys = cmds.keyframe(anim_curve, query=True)
    key_count = cmds.keyframe(anim_curve,
                              keyframeCount=True,
                              query=True)
                              
    # Gather the value and in/out tangent type, and x,y coordinates of
    # each key.
    data = {'name':anim_curve,'type':type}
    data['key_data'] = [key_info_by_index(anim_curve, i)
                        for i in range(key_count)]
    
    # Get infinity values
    data['pre'] = cmds.getAttr("{0}.preInfinity".format(anim_curve))
    data['post'] = cmds.getAttr("{0}.postInfinity".format(anim_curve))
                
    # Get curve colour values
    data['useColor'] = cmds.getAttr("{0}.useCurveColor".format(
                                                            anim_curve))
    data['color'] = cmds.getAttr("{0}.curveColor".format(anim_curve))[0]
    
    return data 
    
#=======================================================================
def build(data):
    # Create and name the anim curve.
    anim_curve = cmds.createNode(data['type'],
                                 name=data['name'],
                                 skipSelect=True)
    
    # Set curve-wide attributes.
    cmds.setAttr("{0}.preInfinity".format(anim_curve), data['pre'])
    cmds.setAttr("{0}.postInfinity".format(anim_curve), data['post'])
    cmds.setAttr("{0}.useCurveColor".format(anim_curve),
                 data['useColor'])
    color = (float(data['color'][0]),
             float(data['color'][1]),
             float(data['color'][2]),)
    cmds.setAttr("{0}.curveColorR".format(anim_curve), color[0])
    cmds.setAttr("{0}.curveColorR".format(anim_curve), color[1])
    cmds.setAttr("{0}.curveColorR".format(anim_curve), color[2])
                      
    # Create the keys using the time, value and tangency in key_data.             
    for key_data in data['key_data']:
        add_keyframe(anim_curve, key_data)

    return anim_curve
    
    
    
#=======================================================================
def add_keyframe(anim_curve, key_data):
    """Adds a keyframe to an anim_curve based on a data set in the form
    key_time, key_value, key_intan (type,x,y), key_outtan (type,x,y)"""
    
    # Unpack the values.
    key_time = key_data['key_time']
    key_value = key_data['key_value']
    
    # Check type: if it is a driven curve then we need to add keyframes
    # by float instead of by time.
    type = cmds.nodeType(anim_curve)
    if type.startswith('animCurveT'):
        # Create the keyframe. Default to linear to allow tangency info 
        # to be applied.
        cmds.setKeyframe(anim_curve,
                         time=key_time,
                         value=key_value,
                         inTangentType = 'linear',
                         outTangentType = 'linear',)
                         
        # Before we adjust any tangents ensure the weight tangents 
        # setting is correct.
        if 'tan_weighted' in key_data:
            cmds.keyTangent(anim_curve,
                            edit=True,
                            weightedTangents=True,)
                        
        # Set the tangents weights and angles. This will set the type to
        # 'fixed'.
        if 'in_angle' in key_data:
            cmds.keyTangent(anim_curve,
                            edit=True,
                            time=(key_time,),
                            absolute=True,
                            inAngle=key_data['in_angle'],
                            inWeight=key_data['in_weight'],
                            outAngle=key_data['out_angle'],
                            outWeight=key_data['out_weight'],
                            lock=key_data['tan_locked'],)
                            
        # Apply the tangency types if they aren't 'fixed'.
        if 'in_type' in key_data and key_data['in_type'] != 'fixed':
            result = cmds.keyTangent(anim_curve,
                             time=(key_time,),
                             inTangentType = key_data['in_type'],)
                
        if 'out_type' in key_data and key_data['out_type'] != 'fixed':
            result = cmds.keyTangent(anim_curve,
                             outTangentType = key_data['out_type'],
                             time=(key_time,),)
    else:
        # Create the keyframe. Default to linear to allow tangency info 
        # to be applied.
        cmds.setKeyframe(anim_curve,
                         float=key_time,
                         value=key_value,
                         inTangentType = 'linear',
                         outTangentType = 'linear',)
                         
        # Before we adjust any tangents ensure the weight tangents 
        # setting is correct.
        if 'tan_weighted' in key_data:
            cmds.keyTangent(anim_curve,
                            edit=True,
                            weightedTangents=True,)
                        
        # Set the tangents weights and angles. This will set the type to
        # 'fixed'.
        if 'in_angle' in key_data:
            cmds.keyTangent(anim_curve,
                            edit=True,
                            float=(key_time,),
                            absolute=True,
                            inAngle=key_data['in_angle'],
                            inWeight=key_data['in_weight'],
                            outAngle=key_data['out_angle'],
                            outWeight=key_data['out_weight'],
                            lock=key_data['tan_locked'],)
                            
        # Apply the tangency types if they aren't 'fixed'.
        if 'in_type' in key_data and key_data['in_type'] != 'fixed':
            result = cmds.keyTangent(anim_curve,
                             float=(key_time,),
                             inTangentType = key_data['in_type'],)
                
        if 'out_type' in key_data and key_data['out_type'] != 'fixed':
            result = cmds.keyTangent(anim_curve,
                             outTangentType = key_data['out_type'],
                             float=(key_time,),)
        
                        



#=======================================================================
def is_type_exportable(node_type):
    """Returns True if the node type is something we can export."""
    return node_type in [
                            "animCurveTL",
                            "animCurveTA",
                            "animCurveTT",
                            "animCurveTU",
                            "animCurveUL",
                            "animCurveUA",
                            "animCurveUT",
                            "animCurveUU",
                           ]




    
#======================================================================
def key_info_by_index(anim_curve, key_index):
    """Returns a list of the time, value and tangency values (type,
    x and y coordinates) for both in and out tangents"""

    # Record key time and value.    
    key_data = {}
    
    # Check type: if it is a driven curve then we need to add keyframes
    # by float instead of by time.
    type = cmds.nodeType(anim_curve)
    if type.startswith('animCurveT'):
        key, value = cmds.keyframe(anim_curve,
                              index=(key_index, key_index),
                              absolute=True,
                              timeChange=True,
                              valueChange=True,
                              query=True)
    else:
        key, value = cmds.keyframe(anim_curve,
                              index=(key_index, key_index),
                              absolute=True,
                              floatChange=True,
                              valueChange=True,
                              query=True)
    key_data['key_time'] = key
    key_data['key_value'] = value

    # Record tangent information.
    key_data['in_type'] = cmds.keyTangent(anim_curve,
                                          index=(key_index, key_index),
                                          inTangentType=True,
                                          query=True)[0]
                              
    key_data['in_angle'] = cmds.keyTangent(anim_curve,
                                           index=(key_index, key_index),
                                           inAngle=True,
                                           query=True)[0]
                         
    key_data['in_weight'] = cmds.keyTangent(anim_curve,
                                            index=(key_index,
                                                   key_index),
                                            inWeight=True,
                                            query=True)[0]
    
    key_data['out_type'] = cmds.keyTangent(anim_curve,
                                           index=(key_index, key_index),
                                           outTangentType=True,
                                           query=True)[0]
 
    key_data['out_angle'] = cmds.keyTangent(anim_curve,
                                            index=(key_index,key_index),
                                            outAngle=True,
                                            query=True)[0]
                         
    key_data['out_weight'] = cmds.keyTangent(anim_curve,
                                             index=(key_index,
                                                    key_index),
                                            outWeight=True,
                                            query=True)[0]
                         
                          
    key_data['tan_weighted'] = cmds.keyTangent(anim_curve,
                                               index=(key_index, 
                                                     key_index),
                                               weightedTangents=True,
                                               query=True)[0]
                         
                          
    key_data['tan_locked'] = cmds.keyTangent(anim_curve,
                                             index=(key_index,
                                                    key_index),
                                             lock=True,
                                             query=True)[0]
        
    return key_data
            


#======================================================================
def key_info_by_time(anim_curve, time):
    """Wrapper script for key_info_by_index if you only know the frame.
    """
    
    index = cmds.keyframe(anim_curve,
                          indexValue=True,
                          time=(time,),
                          query=True)[0]
                          
    return key_info_by_index(anim_curve, index)
    
    
    
    
#======================================================================
def list_channels(anim_curve):
    type = cmds.nodeType(anim_curve)
    if type.startswith('animCurveU'):
        return [anim_curve+'.input']
    else:
        return []