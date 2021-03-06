"""Rebuilds the exported references, curves, constraints and
connections in the Maya scene."""

import maya.cmds as cmds
import animlib.channel
import animlib.info
import animlib.reference
import animlib.curve
import animlib.constraint
import animlib.pairblend
import animlib.retime
import pprint

#======================================================================
def build(data,
          reference_filter=None,
          channel_filter=None,
          reference_unfound=True,
          reference_dependent=False,
          force_build=False,
          retime_filter=None,
          anim_blend_filter=None,
          ):
    """Rebuilds the given references, animation curves and constraints
    then uses the channel data to rebuild connections or set values.
    
    reference_filter: remaps the source data
    build_unfound: if a remapped namespace is empty, try to import a rig 
    """

    # Unpack the data.
    (info_data,
     dependency_data,
     reference_data,
     anim_curve_data,
     constraint_data,
     pairblend_data,
     channel_data,) = data

    #=== BUILD REFRENCES ===============================================
    # If there is no reference filter then populate a default filter 
    # with all namespaces, attempting to use source namespaces and to
    # build all inputs.
    if not reference_filter:
        reference_filter = {}
        for reference in reference_data.keys():
            source_namespace = reference_data[reference]['namespace']
            reference_filter[source_namespace]=(source_namespace,
                                                'connections')
            
    # Attempt to remap the source tokens to the namespaces in the 
    # reference filter.
    print 'Processing {0} References.'.format(len(reference_filter))
    remap = {}
    token_mode = {}
    scene_namespaces = ref_namespaces()
    for source_namespace in reference_filter.keys():
        token = info_data['references'][source_namespace]['token']
        dest_namespace = reference_filter[source_namespace][0]
        if not dest_namespace:
            continue
        if force_build:
            namespace = animlib.reference.build(reference_data[token],
                                         ref_namespace=dest_namespace)
            if namespace:
                remap[token] = namespace
        else:
            # If the namespace exists and belongs to a reference file  
            # then add it to the remap dictionary.
            if dest_namespace in scene_namespaces:
                remap[token] = dest_namespace
            
            # Else if build unfound is true attempt to import the 
            # original rig and remap to the resulting reference.  
            elif reference_unfound:
                namespace = animlib.reference.build(reference_data[token],
                                        ref_namespace=dest_namespace)
                if namespace:
                    remap[token] = namespace
        token_mode[token] = reference_filter[source_namespace][1]
          
    #=== BUILD DEPENDENT NODES =========================================
    # For the references that have successfully been remapped create a
    # set of curves, constraints and pair blends based on the dependency 
    # data and the reference filter apply settings.
    new = []
    for reference in remap.keys():
        # Retrieve the 'apply filter' for this reference.
        source_namespace = reference_data[reference]['namespace']
        filter = reference_filter[source_namespace][1]
        if filter == 'skip':
            continue
        if reference in dependency_data:
            # Apply the filter to the dependent nodes to determine which
            # should be built.
            dependencies = dependency_data[reference]
            if filter in ['connections', 'constraints']:
                nodes = []
                nodes+=[x for x in dependencies if x.startswith('@CON')]
                nodes+=[x for x in dependencies if x.startswith('@PRB')]
                new += nodes
                if filter == 'constraints':
                    for node in nodes:
                        token_mode[node]='constraints'
            if filter in ['connections', 'curves']:
                new +=  [x for x in dependencies if x.startswith('@CRV')]
                
            
    # Travel through the dependency tree to gather upstream nodes.
    processed = []
    while new:
        tokens = new[:]
        processed += tokens
        new = []
        for token in tokens:
            if token in dependency_data:
                dependencies = dependency_data[token]
                new += [x for x in dependencies if x not in processed]
                
    # Collate the dependencies into lists by type.
    pairblends = [x for x in processed if x.startswith('@PRB')]
    constraints = [x for x in processed if x.startswith('@CON')]
    curves = [x for x in processed if x.startswith('@CRV')]
            
    # Build the pairBlend curves, remapping the token to the new node.
    pairblends = list(set(pairblends))
    if pairblends:
        print 'Building {0} Pair Blends.'.format(len(pairblends))
        for pairblend in pairblends:
            new_prb = animlib.pairblend.build(pairblend_data[pairblend],
                                              remap)
            remap[pairblend] = new_prb
        print
        
    # Build the constraints, remapping the token to the new constraint.
    constraints = list(set(constraints))
    if constraints:
        print 'Building {0} Constraints.'.format(len(constraints))
        for constraint in constraints:
            new_con = animlib.constraint.build(
                                           constraint_data[constraint])
            remap[constraint] = new_con
        print
        
    # Build the anim curves, remapping the token to the new curve. Apply
    # any retime value.
    curves = list(set(curves))
    if curves:
        print 'Building {0} Curves.'.format(len(curves))
        for anim_curve in curves:
            new_curve = animlib.curve.build(anim_curve_data[anim_curve])
            remap[anim_curve] = new_curve
            if retime_filter:
                new_curve = animlib.retime.curve(new_curve, 
                                                 retime_filter)
    
    print token_mode
    
    # === CONNECT NODES / APPLY VALUES ON CHANNELS =====================
    # Apply the channel data.
    if channel_data:
        # Report the number of channels
        i = 0
        for token in channel_data:
            i += len(channel_data[token])
        print 'Applying data to {0} channels.'.format(i)
        
        # Process the channels by the token they belong to.
        for token in channel_data:
        
            # Figure out what data we're applying. If the mode is skip
            # or pass, we don't want to apply any data. If the mode is
            # constraints, we only want to do connections that start or
            # end in a pair blend or constraint. If the mode is 'curves'
            # 
            apply_mode = 'all'
            if token in token_mode:
                apply_mode = token_mode[token]
                if apply_mode in ['skip', 'pass']:
                    continue
            for channel in channel_data[token].keys():
                data = channel_data[token][channel]
                if apply_mode == 'values':
                    data = (None, data[1], data[2], data[3])
                elif apply_mode == 'constraints':
                    print '$$$'+str(data[0])
                    if data[0] and '@CRV' in data[0]:
                        data = (None, data[1], data[2], data[3])
                    else:
                        data = (remap_name(data[0], remap),
                                data[1], data[2], data[3])
                else:
                    data = (remap_name(data[0], remap),
                            data[1], data[2], data[3])
                        
                        
                # Apply the channel data.
                channel = remap_name(channel, remap)
                if '@' in channel:
                    continue
                animlib.channel.set(channel,
                                    data,
                                    skip_connected=False,
                                    blend_filter = anim_blend_filter)
        print
            
    # Clean up any constraints
    for constraint in list(set(constraints)):
        animlib.constraint.tidy_constraint_node(remap[constraint])
        
    return None

#======================================================================
def remap_name(name, remap):
    """Remaps the given name if it starts with a token."""
    old_name = name
    if name and name.startswith("@"):
            token = name.split('!')[0]+'!'
            if token in remap:
                new_value = remap[token]
                name = name.replace(token, new_value)
                if not cmds.objExists(name):
                    print (" > Remap failed",
                            old_name, '-', new_value, ':', name)
    return name
    
#======================================================================
def ref_namespaces():
    """Returns a list of namespaces of referenced files.
    """
    top_files = cmds.file(query=True, reference=True)
    top_nsp = [(cmds.file(x, query=True, namespace=True))    
               for x in top_files]
    namespaces = []
    def check_child(nsp):
        namespaces.append(':'+nsp)
        children = cmds.namespaceInfo(nsp, listOnlyNamespaces=True)
        if children:
            for child in children:
                check_child(child)
    for nsp in top_nsp:
        check_child(nsp)
    return namespaces
