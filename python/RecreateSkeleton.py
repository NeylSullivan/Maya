import maya.cmds as cmds

jointsList = cmds.ls(type="joint")

for j in jointsList:
    pos = cmds.joint(j, q=True, absolute=True)
    oldName = cmds.joint(j, q=True, name=True)
    oldOrientation = cmds.joint(j, q=True, orientation=True)

    newName = "DAZ_" + oldName
#    print oldOrientation
    cmds.select(clear=True)
    newJoint = cmds.joint(p=pos, name=newName)
    cmds.xform(r=True, ro=oldOrientation)

cmds.select(clear=True)

for j in jointsList:
    parent = cmds.listRelatives(j, parent=True, type='joint')
    if not parent:
        continue
    oldName = cmds.joint(j, q=True, name=True)
    oldParentName = cmds.joint(parent, q=True, name=True)

    newName = "DAZ_" + oldName
    newParentName = "DAZ_" + oldParentName
    print newParentName
    cmds.parent(newName, newParentName)
