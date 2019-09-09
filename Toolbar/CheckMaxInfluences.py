import maya.cmds as cmds

DEFAULT_MAXIMUM_INFULENCE = 4

def check_maximum_influence(maximum=DEFAULT_MAXIMUM_INFULENCE):
    res = []
    cmds.select(clear=True)

    outputMessage = 'Checked for max {0} influenses\n'.format(maximum)

    skin_clusters = cmds.ls(type="skinCluster")
    for cluster in skin_clusters:
        for mesh in cmds.skinCluster(cluster, q=True, geometry=True):
            currentRes = check_mesh(maximum, cluster, mesh)
            if currentRes:
                outputMessage += "Found {0} vertices in mesh {1}\n".format(len(currentRes), mesh)
            else:
                outputMessage += "NOT found vertices in mesh {0}\n".format(mesh)
            res += currentRes
    print outputMessage
    dialog = cmds.confirmDialog(title='Check maximum influences results', message=outputMessage, button=['Select', 'Cancel'], defaultButton='Select', cancelButton='Cancel')

    if dialog == 'Select':
        cmds.select(res)





def check_mesh(maximum, cluster, mesh):
    vertices = cmds.polyListComponentConversion(mesh, toVertex=True)
    vertices = cmds.filterExpand(vertices, selectionMask=31)  # polygon vertex

    res = []
    for vert in vertices:
        joints = cmds.skinPercent(cluster, vert, query=True, ignoreBelow=0.000001, transform=None)
        if len(joints) > maximum:
            res.append(vert)

    return res

check_maximum_influence()
