import maya.cmds as cmds
import pprint
import animlib.curve as crv

#=======================================================================
def curve(anim_curve, time_filter, skip_cycle=True, trim=False):

    if not cmds.objExists(anim_curve):
        print "Could not find {0}".format(anim_curve)

    if cmds.nodeType(anim_curve) not in ("animCurveTL",
                                         "animCurveTA",
                                         "animCurveTT",
                                         "animCurveTU",):
        print 'Skipping non-time-based curve {0}'.format(anim_curve)
        return anim_curve

    # If a trim hasn't been specified then treat simple retimes as
    # global offsets or scales.
    if not trim:
        # If the time filter is a single value pair we calculate the 
        # offset and apply it to the entire framerange and return the 
        # anim_curve.
        if len(time_filter) == 1:
            offset = time_filter[0][0] - time_filter[0][1]
            src_keys = cmds.keyframe(anim_curve, query=True)
            new_start = min(src_keys)+offset
            new_end = max(src_keys)+offset
            cmds.scaleKey(anim_curve,
                          time=(min(src_keys),max(src_keys)),
                          newStartTime=new_start,
                          newEndTime=new_end,)
            return anim_curve
    
        # If there are only two values then it is a simple scale. 
        # Calculate the scale and apply it to the entire key range. If 
        # it is a held frame then treat it as a complex retime.
        if len(time_filter) == 2:
            new_start, src_start = time_filter[0]
            new_end, src_end = time_filter[1]
            if src_start != src_end:
                scale = (float(new_end) - new_start)/(src_end-src_start)
                offset = new_start-(src_start*scale)
                src_keys = cmds.keyframe(anim_curve, query=True)
                if not src_keys:
                    cmds.select(anim_curve)
                new_start = min(src_keys)*scale+offset
                new_end = max(src_keys)*scale+offset
                cmds.scaleKey(anim_curve,
                              time=(min(src_keys),max(src_keys)),
                              newStartTime=new_start,
                              newEndTime=new_end,)
                return anim_curve
            

    # If the curve has a cycle on it then a complex retime will be
    # unpredictable. So if the skip_cycle value is true we just return
    # the curve unchanged.
    pre_inf = cmds.getAttr("{0}.preInfinity".format(anim_curve))
    post_inf = cmds.getAttr("{0}.postInfinity".format(anim_curve))
    if pre_inf > 2 or post_inf > 2:
        print 'No retime applied to cycling curve {0}'.format(anim_curve)
        return anim_curve
    
    # Convert the remap frame pairs (old frame/new frame) into time
    # blocks (old start, old end, new start, new end) so we can manage
    # regions instead of points.
    time_blocks = []
    floor_frame = "Initialised."
    for x in range(len(time_filter)-1):
        # Unpack the current and next time values.
        new_start, src_start = time_filter[x]
        new_end, src_end = time_filter[x+1]
        time_blocks.append((src_start, src_end, new_start, new_end,))
        
        # Ensure the time blocks don't overlap.
        if floor_frame == "Initialised.":
            floor_frame = new_start
        if new_end <= floor_frame:
            cmds.error("Time filter overlaps: {0}".format(time_filter))
        else:
            floor_frame = new_end
            
        
    # Add a keyframe at each remap point, if one does not already exist,
    # and unlock the tangents so they can be remapped independently.
    for frame, new_frame in time_filter:
        if not cmds.keyframe(anim_curve, time=(new_frame,), query=True):
            cmds.setKeyframe(anim_curve, insert=True, time=(new_frame,))
        cmds.keyTangent(anim_curve, 
                        edit=True,
                        time=(frame,),
                        lock=False)
        
    # Create a temporary curve to transcribe the remap data to and a
    # buffer curve to hold the keys from each time block while we scale
    # them.
    node_type = cmds.nodeType(anim_curve)
    temp_curve = cmds.createNode(node_type,
                                 name=anim_curve+'remap_temp',
                                 skipSelect=True)
    
    # Transcribe the remapped keys onto the temporary curve using the
    # data in the time_blocks list.
    for time_block in time_blocks:
        src_start, src_end, new_start, new_end = time_block
        
        # If the time block uses the same source frame for the whole
        # time block then we need to treat it as a held frame.
        if src_end == src_start:
            # Add a duplicate key at the start and end of the time block.
            keys = cmds.keyframe(anim_curve,
                                 time=(src_start,),
                                 query=True)
            key_data = crv.key_info_by_time(anim_curve, keys[0])
            key_data['key_time'] = new_end
            crv.add_keyframe(temp_curve, key_data)
            key_data['key_time'] = new_start
            key_data['out_type'] = 'step'
            key_data['out_angle'] = 0
            key_data['out_weight'] = 0
            crv.add_keyframe(temp_curve, key_data) 
        
        # If the time block uses different source frames at the start
        # and end of the time block then we need to scale the region
        # between those frames.
        else:
            # If we're scaling backwards then shuffle the values
            # to work with the scaleKey script
            if src_start > src_end:
                (src_start, src_end) = (src_end, src_start)
                (new_start, new_end) = (new_end, new_start)
                reverse=True
            else:
                reverse=False

            # Copy those key in the time block to a buffer curve.
            buffer_curve = cmds.createNode(node_type,
                                         name=anim_curve+'buffer_temp',
                                         skipSelect=True)
            keys = cmds.keyframe(anim_curve,
                                 time=(src_start,src_end,),
                                 query=True)
            for key in keys:
                key_data = crv.key_info_by_time(anim_curve, key)
                crv.add_keyframe(buffer_curve, key_data)
                
            # Scale the keys on the buffer curve.
            cmds.scaleKey(buffer_curve,
                          time=(src_start,src_end),
                          newStartTime=new_start,
                          newEndTime=new_end,)

            # Stepped keys break if they're reversed, so this is a fix
            # for that.
            if reverse:
                for key_index in range(0, len(keys)-1):
                    if cmds.keyTangent(anim_curve,
                              outTangentType=True,
                              index=(key_index, key_index),
                              query=True)[0] == 'step':
                        new_index = len(keys)-key_index-2
                        cmds.keyTangent(buffer_curve,
                                        index=(new_index,),
                                        outTangentType = 'stepnext')
                    if cmds.keyTangent(anim_curve,
                              outTangentType=True,
                              index=(key_index, key_index),
                              query=True)[0] == 'stepnext':
                        new_index = len(keys)-key_index-2
                        cmds.keyTangent(buffer_curve,
                                        index=(new_index,),
                                        outTangentType = 'step')

            # Transcribe the keys to the temp curve.
            buffer_keys = cmds.keyframe(buffer_curve, query=True)
            temp_keys = cmds.keyframe(temp_curve, query=True)
            for key_index in range(0, len(buffer_keys)):
                key_data = crv.key_info_by_index(buffer_curve,
                                                 key_index)
                # If the start/end keys already exist on the curve we
                # don't want to overwrite the tangents before or after
                # the time block.
                if temp_keys and key_index == 0:
                    if key_data['key_time'] in temp_keys:
                        old_data = crv.key_info_by_time(temp_curve,
                                                key_data['key_time'])
                        key_data['in_type'] = old_data['in_type']
                        key_data['in_angle'] = old_data['in_angle']
                        key_data['in_weight'] = old_data['in_weight']
                        
                if temp_keys and key_index == len(buffer_keys)-1:
                    if key_data['key_time'] in temp_keys:
                        old_data = crv.key_info_by_time(temp_curve,
                                                key_data['key_time'])
                        key_data['out_type'] = old_data['out_type']
                        key_data['out_angle'] = old_data['out_angle']
                        key_data['out_weight'] = old_data['out_weight']

                crv.add_keyframe(temp_curve, key_data)
            cmds.delete(buffer_curve)

    # Transfer the keys from the temp curve to the original curve.
    src_keys = cmds.keyframe(anim_curve, query=True)
    temp_keys = cmds.keyframe(temp_curve, query=True)
    
    # Add a placeholder keyframe below the range of either curve. (If
    # we delete all the keyframes on a curve it will delete the curve
    # node as well.)
    min_key = min(src_keys) - min(temp_keys)-1
    cmds.setKeyframe(anim_curve,
                     time=min_key,
                     value=0,
                     inTangentType = 'linear',
                     outTangentType = 'linear',)

    # Delete all other keys on the source curve.
    cmds.cutKey(anim_curve,
                time=(min(src_keys),max(src_keys)),
                option='keys')

    # Copy the keys from the temp curve.
    for key in temp_keys:
        key_data = crv.key_info_by_time(temp_curve, key)
        crv.add_keyframe(anim_curve, key_data)
    cmds.delete(temp_curve)

    # Delete the placeholder key.
    cmds.cutKey(anim_curve, time=(min_key,), option='keys')
    return anim_curve


#=======================================================================
def curve_list(anim_curve_list, time_filter, skip_cycle=True):

    # Setup the progress window:
    num_curves = len(anim_curve_list)
    progress_step = 100.0 / num_curves
    progress = 0.0
    cmds.progressWindow(title='Retime Curves!',
                        progress=0, minValue=0, maxValue=100,
                        status='Not started yet...',
                        isInterruptable=True )

    # Start looping
    for anim_curve in anim_curve_list:
        # Update our progress window, quit if the user has hit escape:
        if cmds.progressWindow( query=True, isCancelled=True ):
            break
        cmds.progressWindow(edit=True,
                            progress=int(progress),
                            status='%.1f%%'%progress)
        progress += progress_step
        curve(anim_curve, time_filter, skip_cycle)
        
    # Exit the progress window:
    cmds.progressWindow(endProgress=1)




#=======================================================================
def scene(time_filter, skip_cycle=True):
    all_anim_curves = cmds.ls(type=('animCurveTL',
                                    'animCurveTA',
                                    'animCurveTT',
                                    'animCurveTU',))
    curve_list(all_anim_curves, time_filter, skip_cycle)


#=======================================================================
def selected(time_filter, skip_cycle=True):
    selection = cmds.ls(selection=True)
    anim_curves = []
    for node in selection:
        if cmds.nodeType(node) in ("animCurveTL",
                                   "animCurveTA",
                                   "animCurveTT",
                                   "animCurveTU",):
            anim_curves.append(node)
        else:
            curves = cmds.ls(cmds.listHistory(node, leaf=False),
                             type=('animCurveTL',
                                   'animCurveTA',
                                   'animCurveTT',
                                   'animCurveTU',))
            anim_curves += curves
    pprint.pprint(anim_curves)
    curve_list(anim_curves, time_filter, skip_cycle)


#=======================================================================
def ui():
    result = cmds.promptDialog(
		title='Retime Animation Curves',
		message=('Enter new_frame/src_frame separated by a space.'+
                 '\n\nOn Frame X I want to see Frame Y = X/Y'),
		button=['Selected', 'Scene', 'Cancel'],
		defaultButton='Selected',
		cancelButton='Cancel',
		dismissString='Cancel')

    if result == 'Cancel':
        return
    
    text = cmds.promptDialog(query=True, text=True)
    print text
    time_filter=[]
    value_pairs = text.split(' ')
    for value_pair in value_pairs:
        values = value_pair.split('/')
        pair = (float(values[0]),float(values[1]))
        time_filter.append(pair)
    
    if result == 'Selected':
        selected(time_filter)
    else:
        scene(time_filter)


