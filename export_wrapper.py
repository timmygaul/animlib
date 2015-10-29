

#====================================
def export_namespace(namespace,
                     name,
                     export_category="export",
                     export_identifier="unknown",
                     node_filter="*_ctrl",
                     node_selected=False,
                     keyable = True,
                     nonkeyable = True,
                     connections = True,
                     anim_curves = True,
                     constraints = True,
                     export_type="pose",):
    """
    """

    # Check the namespace exists and is not empty.
    if not cmds.namespace(exists=namespace):
        cmds.error("Cannot export namespace {0}, it does not exist.".format(
                                                                     namespace))
    if not cmds.namespaceInfo(namespace, listNamespace=True):
        cmds.error("Cannot export namespace {0}, it is empty.".format(
                                                                     namespace))

    # Build a list of nodes in the namespace that match the filter. Recursive
    # allows us to query child namespaces as well.
    nodes = cmds.ls(namespace+":*"+node_filter, recursive = True)

    # Build a list of channels to process.
    channels = get_channels_from_nodes(nodes, keyable=True, nonkeyable=True)

    # Get the channel data for the list of channels.
    channel_data = channel.get_channel_list_input(namespace, channels)

    # Export the channel data.
    export_data(export_category,
                export_identifier,
                namespace,
                name,
                channel_data)


#====================================
def get_channels_from_nodes(nodes, keyable=True, nonkeyable=True):
    """Receives a list of nodes and returns a list of channels that match the
    arguments.
    """
    channels = []
    for node in nodes:
        node_channels = []
        if keyable:
            channels_key = cmds.listAttr(node, keyable=True)
            if channels_key:
                node_channels = node_channels + channels_key
        if nonkeyable:
            channels_cb = cmds.listAttr(node, channelBox=True)
            if channels_cb:
                node_channels = node_channels + channels_cb
        if node_channels:
            node_channels = [node+"."+x for x in node_channels]
            channels = channels + node_channels
    return channels
    

#====================================
def get_user():
    """Returns the user file for the current account.
    """
    USERFILE = "/home/pukeko/user.txt"

    user_name = None
    file = open(USERFILE, "r")
    user_name = file.readline()
    file.close()
    if user_name[-1] == "\n":
        user_name = user_name[:-1]
    user_name = user_name.lower()
    return user_name
