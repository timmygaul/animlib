import maya.cmds as cmds
import animlib.export
import animlib.apply

def selected():
    # Get all the selected referenced nodes channels.
    selection = cmds.ls(selection=True, referencedNodes = True)
    publish_channels = []
    namespaces = []
    for node in [x for x in selection if ":" in x]:
        attrs = cmds.listAttr(node,
                              settable=True,
                              keyable=True)
        for attr in attrs:
            publish_channels.append(node+"."+attr)
    
    data = animlib.export.channels(publish_channels)
    result = animlib.apply.build(data)