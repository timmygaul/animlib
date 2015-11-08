"""Analyses the Maya scene and returns node, channel and connection
data."""
import animlib.channel
import animlib.info
import animlib.reference
import animlib.curve
import animlib.constraint
import maya.cmds as cmds
import pprint

#======================================================================
def channels(channel_list):
    """Returns dictionaries of channel data, reference data, animation
    curve data and constraint node data that can be used to rebuild the
    incoming graph for the given channels.
    """
      
    # Process the channels first, and receive a dictionary of channel
    # data and dictionaries listing the reference nodes, curve nodes and
    # constraint nodes with their tokens as the dictionary keys.
    (channel_data,
     reference_nodes,
     anim_curve_nodes,
     constraint_nodes,
     pairblend_nodes,
     dependency_data,) = process_channels(channel_list)
     
    # Export the data for the nodes the channels are dependent upon.
    reference_data = process_references(reference_nodes)
    anim_curve_data = process_anim_curves(anim_curve_nodes)
    constraint_data = process_constraints(constraint_nodes)
    pairblend_data = process_pairblends(pairblend_nodes, channel_data)
    
    # Export information about the 
    info_data = animlib.info.export(channels, reference_data)
    
    return (info_data,
            dependency_data,
            reference_data,
            anim_curve_data,
            constraint_data,
            pairblend_data,
            channel_data,
            )
    
    
    
#======================================================================
def process_channels(channel_list):
    """ Cycles through a list of channels, recording channel data and
    the downstream nodes that can be exported.
    """
    processed_nodes = {}
    channel_data = {}
    node_list = {"@REF":{},
                 "@CRV":{},
                 "@CON":{},
                 "@PRB":{},}
    dependency_data = {}
    
    processed_channels = []
    while channel_list:
        new_channels = []
        channel_list = list(set(channel_list))
        for channel in channel_list:
            # If the channel data can't be retrieved, skip this channel.
            if not animlib.channel.is_gettable(channel):
                continue
                
            # Retrieve the channel data.
            source_attr, value, altered, type = animlib.channel.get(channel)
    
            # Tokenise the channel name, so the data can be applied if
            #  the name changes or is remapped at build time.
            (token,
             channel,
             node_list,
             processed_nodes,) = tokenise_attr(channel,
                                               node_list,
                                               processed_nodes,
                                               new_channels,)
    
            # Tokenise the source channel name if found, so the data can
            # be applied if the name changes or is remapped at build
            # time.
            if source_attr:
                (source_token,
                 source_attr,
                 node_list,
                 processed_nodes,) = tokenise_attr(source_attr,
                                                   node_list,
                                                   processed_nodes,
                                                   new_channels,)
                                                   
                # Add the source token to a list of dependencies for 
                # this token, so that we can selectively build based
                # on namespace later on.
                if source_token:
                    if not token in dependency_data:
                        dependency_data[token]=[]
                    if not source_token in dependency_data:
                        dependency_data[token].append(source_token)
                                            
            # Finally add the channel data to the channel data
            if not token in channel_data:
                channel_data[token]={}
            channel_data[token][channel] = (source_attr, value, altered, type)
        processed_channels += channel_list
        channel_list = [x for x in new_channels
                        if x not in processed_channels]
        
    # Tidy up the dependency data:
    for key in dependency_data:
        dependency_data[key] = list(set(dependency_data[key]))
        dependency_data[key].sort()
        
    return (channel_data,
            node_list["@REF"],
            node_list["@CRV"],
            node_list["@CON"],
            node_list["@PRB"],
            dependency_data,)
            
            
#=======================================================================
def tokenise_attr(attr,
                  node_list,
                  processed_nodes,
                  new_channels):
    """Checks the node of the given attribute to see if it has been
    processed. If it hasn't and it is an exportable type it associates
    it with a token and adds the node to the various nodes-to-export
    lists. The attribute name is then 
    """
    # Trim the attribute from the name to find the node it belongs to.
    node = attr.split('.')[0]
    
    # Retrieve or create the node's token.
    if node in processed_nodes:
        token = processed_nodes[node]
    else:
        # If the node is referenced create a 'REF#' token and add the  
        # node to the anim curve node dictionary.
        if cmds.referenceQuery(node, isNodeReferenced=True):
            ref_node = cmds.referenceQuery(node,referenceNode=True)
            if ref_node in node_list['@REF']:
                token = node_list['@REF'][ref_node]
            else:
                token = "@REF{0}!".format(len(node_list['@REF']))
                node_list['@REF'][ref_node] = token
        else:
            # If the node is exportable as an anim curve create a 'CRV#' 
            # token and add the node to the anim curve node dictionary.
            node_type = cmds.nodeType(node)
            if animlib.curve.is_type_exportable(node_type):
                token = "@CRV{0}!".format(len(node_list['@CRV']))
                node_list['@CRV'][token] = node
                new_channels +=  animlib.curve.list_channels(node)
            
            # If the node is exportable as an anim curve create a 'CRV#' 
            # token and add the node to the anim curve node dictionary.
            elif animlib.constraint.is_type_exportable(node_type):
                token = "@CON{0}!".format(len(node_list['@CON']))
                node_list['@CON'][token] = node
                new_channels +=  animlib.constraint.list_channels(node)
                
            
            # If the node is exportable as an pair blend create a 'PRB#' 
            # token and add the node to the pair blend node dictionary.
            elif animlib.pairblend.is_type_exportable(node_type):
                token = "@PRB{0}!".format(len(node_list['@PRB']))
                node_list['@PRB'][token] = node
                new_channels +=  animlib.pairblend.list_channels(node)
                
            # Otherwise the node is not exportable.
            else:
                token=None
        
        # Add the node and token to the processed nodes dictionary.
        processed_nodes[node] = token
            
    if token:
        # If the token starts with REF, the node is referenced. Replace 
        # the top level of the namespace.
        if "@REF" in token:
            attr = token + attr[len(attr.split(':')[0]):]
            
            
        # If it is an animation curve or a constraint. Replace the
        # entire name of the node, leaving only the channel name.
        if "@CRV" in token or "@CON" in token or "@PRB" in token:
            attr = token + attr[len(attr.split('.')[0]):]

    return (token, attr, node_list, processed_nodes,)
    


#======================================================================
def process_references(reference_nodes):
    """Cycles through the list of reference nodes and gathers the data
    needed to recreate the reference at build time.
    """
    reference_data = {}
    for reference_node in reference_nodes.keys():
        token = reference_nodes[reference_node]
        data = animlib.reference.export(reference_node)
        reference_data[token] = data
        
    return reference_data
    
#======================================================================
def process_anim_curves(anim_curve_nodes):
    """Cycles through the list of anim curve nodes and gathers the data
    needed to recreate the curve at build time.
    """
    anim_curve_data = {}
    for token in anim_curve_nodes.keys():
        anim_curve = anim_curve_nodes[token]
        data = animlib.curve.export(anim_curve)
        anim_curve_data[token] = data
        
    return anim_curve_data
    
#======================================================================
def process_constraints(constraint_nodes):
    """Cycles through the list of constraint nodes and gathers the data
    needed to recreate the constraint at build time.
    """
    constraints_data = {}
    for token in constraint_nodes.keys():
        constraint_node = constraint_nodes[token]
        data = animlib.constraint.export(constraint_node)
        constraints_data[token] = data
        
    return constraints_data
    
#======================================================================
def process_pairblends(pairblend_nodes, channel_data):
    """Cycles through the list of pairBlend nodes and gathers the data
    needed to recreate the pairBlend at build time.
    """
    pairblends_data = {}
    for token in pairblend_nodes.keys():
        pairblend_node = pairblend_nodes[token]
        try:
            pairblend_object = channel_data[token][token+'.weight']
        except KeyError:
            pairblend_object = None
        data = animlib.pairblend.export(pairblend_node,
                                        pairblend_object)
        pairblends_data[token] = data
        
    return pairblends_data

