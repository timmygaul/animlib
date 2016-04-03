"""Exports and rebuilds file references using the reference dictionary
format."""

"""
ref_namespace = (get_top_namespace(channel))
        if not ref_namespace in nsp_tokens:
            token = "@nsp" + str(len(nsp_tokens)+1)
            filepath = cmds.referenceQuery(channel, filename=True)
            nsp_tokens[ref_namespace]=(token,filepath)
        channel = channel.replace(ref_namespace, token, 1);
"""
import os.path
import maya.cmds as cmds

#======================================================================
def export(ref_node):
    """
    """
    data = {}
    data['filename'] = cmds.referenceQuery(ref_node, filename=True)
    data['namespace'] = cmds.referenceQuery(ref_node, namespace=True)
    data['parents'] = get_parents(data['namespace'])
    return data
    
    
    
    
    

#======================================================================
def build(data, ref_namespace=None):
    """
    """
    
    # Parse the data into variables.
    data_filepath = data['filename']
    if not ref_namespace:
        ref_namespace = data['namespace']

    # Trim the filepath in case it was a duplicate and would thus have
    # a '{n}' suffix.
    data_filepath = trim_path(data_filepath)

    # Return None as namespace if the filepath is not a maya file.
    if not is_maya_file(data_filepath):
        return None
        
    # Create the new reference.
    filepath = cmds.file(data_filepath,
                         reference=True,
                         type="mayaAscii",
                         mergeNamespacesOnClash=False,
                         namespace=ref_namespace,
                         options= "v=0;")
    namespace = cmds.referenceQuery(filepath, namespace=True)
    
    # Attempt to rename the reference node.
    expected_name = namespace + 'RN'
    if not cmds.objExists(expected_name):
        ref_node = cmds.referenceQuery(filepath, referenceNode=True)
        if not ref_node == expected_name:
            cmds.lockNode(ref_node, lock=False )
            ref_node = cmds.rename(ref_node, expected_name)
            cmds.lockNode(ref_node)

    
    # Attempt to rename the reference node.
    expected_name = namespace + 'RN'
    if not cmds.objExists(expected_name):
        ref_node = cmds.referenceQuery(filepath, referenceNode=True)
        if not ref_node == expected_name:
            cmds.lockNode(ref_node, lock=False )
            ref_node = cmds.rename(ref_node, expected_name)
            cmds.lockNode(ref_node)


    # Attempt to reparent anything that we can.
    set_parents(namespace, data['parents'])
    
    # Return the namespace of the reference to be used.
    return namespace
    
    
#======================================================================
def is_maya_file(filepath):
    """Returns True if the file exists and has the suffix .ma or .mb.
    """
    if os.path.isfile(filepath):
        if filepath.endswith('.ma') or filepath.endswith('.mb'):
            return True
    print '>> File read failed: {0}'.format(filepath)   
    return False
    
    
#======================================================================
def trim_path(filepath):
    """Removes any '{n}' suffix that Maya uses to differentiate between
    references using the same path.
    """
    return filepath.split('{')[0]
    
    
#======================================================================
def top_nodes(namespace):
    """Returns a list of the top-level nodes in the namespace (i.e. 
    DAG nodes that are not parented to any other node in the same 
    namespace) - this isn't a very efficient method but I don't know
    any better way to do it
    """
    if namespace.startswith(':'):
        namespace = namespace.split(':')[1]
    else:
        namespace = namespace.split(':')[0]

    all_nodes = set(cmds.ls('*{0}:*'.format(namespace),
                        long=True,
                        recursive=True,
                        dagObjects=True))

    hierarchy = '|'+namespace+':'
    parent_nodes = [x for x in all_nodes if x.count(hierarchy) == 1]
    return parent_nodes
    
#======================================================================
def get_parents(namespace):
    """
    """
    parent_data = {}
    top_level_nodes = top_nodes(namespace)
    for node in top_level_nodes:
        parent = cmds.listRelatives(node, parent=True)
        if parent:
            node = node.split('|')[-1]
            if namespace.startswith(':'):
                namespace = namespace.split(':')[1]
            token_name = node.replace(namespace, '#nsp!')
            parent_data[token_name] = parent[0]
    return parent_data
    
#======================================================================
def set_parents(namespace, parent_data):
    """
    """
    for key in parent_data:
        rig_obj = key.replace('#nsp!', namespace)
        if not cmds.objExists(rig_obj):
            print '  >> Could not reparent unfound node: ', rig_obj
            continue
        if not cmds.objExists(parent_data[key]):
            print '  >> Could not find parent node: ',
            print rig_obj, parent_data[key]
            continue
            
        try:
            cmds.parent(rig_obj, parent_data[key])
        except:
            print '  >> Reparenting failed: '
            print rig_obj, parent_data[key]
    
#======================================================================
def trim_namespace(namespace):
    """
    """
    if namespace.startswith(':'):
        return namespace.split(':')[1]
    else:
        return namespace.split(':')[0]
    
