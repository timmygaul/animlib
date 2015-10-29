"""Test Function."""
def test():
    print "Hello world."
    
    
    
#=======================================================================
def list_destination_channels(node):
    """Returns a list of channels that have incoming connections on a
    given node."""
    dest_channels = []
    connected_attrs = (cmds.listConnections(node,
                                            connections=True,
                                            source=True,
                                            destination=False,
                                            plugs=True,
                                            skipConversionNodes=True))
    if connected_attrs:
        for connected_attr in connected_attrs:
            if (source_node+".") in connected_attr:
                dest_channels.append(connected_attr)
    return dest_channels


#=======================================================================
def is_node_exportable(node):
    """Returns True if the node type is something we can export."""
    if cmds.referenceQuery(node, isNodeReferenced=True):
        return False
    return is_node_type_exportable(cmds.nodeType(node))
                           



#=======================================================================
def get_top_namespace(name):
    """Returns the first namespace.
    e.g. for "a:b:c:node" it will return "a"
    """
    return name[:-len(name.split(':')[-1])][:-1]