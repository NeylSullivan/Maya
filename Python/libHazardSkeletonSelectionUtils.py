import maya.cmds as cmds
import fnmatch
import libHazardMayaUtils as mayaUtils

reload(mayaUtils)

def FindJoint(jointName):
    joint = cmds.ls(jointName, type="joint")
    if not joint:
        print 'FindJoint: Can`t find joint {0}'.format(jointName)
        return None
    return joint[0]

def GetAllParentsOfJoint(jointName):
    parents = []

    currentParent = cmds.listRelatives(jointName, parent=True, type='joint')

    while currentParent:
        parents.append(currentParent[0])
        currentParent = cmds.listRelatives(currentParent, parent=True, type='joint')

    return parents

def RemoveJointsFromListByWildCard(inOutJointList, wildcard):
    if not inOutJointList:
        return

    matchingJoints = fnmatch.filter(inOutJointList, wildcard)
    for mj in matchingJoints:
        inOutJointList.remove(mj)


def RemoveJointFromList(inOutJointList, jointToRemove):
    if not inOutJointList:
        return
    if jointToRemove not in inOutJointList:
        return

    inOutJointList.remove(jointToRemove)

def GetFaceRig():
    rig = []

    head = FindJoint('Head')
    if not head:
        return
    rig.append(head)

    allChildren = cmds.listRelatives(head, allDescendents=True, type='joint')
    if allChildren:
        rig.extend(allChildren)

    allParents = GetAllParentsOfJoint(head)# cmds.listRelatives(head, parent=True, type='joint')
    if allParents:
        rig.extend(allParents)

    rig = list(set(rig))

    RemoveJointFromList(rig, 'FK_CAMERA_SOCKET')
    RemoveJointsFromListByWildCard(rig, '*_END')

    print rig
    return rig


def SelectFaceRig():
    cmds.select(clear=True)
    cmds.select(GetFaceRig())

def GetMeshesJoints(meshes):
    allJoints = []

    for m in meshes:
        skinCluster = mayaUtils.GetSkinCluster(m)
        if not skinCluster:
            continue

        weightedInfls = cmds.skinCluster(skinCluster, q=True, wi=True)
        allJoints.extend(weightedInfls)

    allJoints = list(set(allJoints))

    allParentsSet = set()

    for j in allJoints:
        parents = GetAllParentsOfJoint(j)
        allParentsSet.update(parents)

    allParentsSet.update(allJoints)

    allJoints = list(allParentsSet)

    RemoveJointsFromListByWildCard(allJoints, '*_END') # END joints not skinned but to be sure...

    return allJoints


def SelectJointsForSelectedMeshes():
    #cmds.select(clear=True)

    allSelected = cmds.ls(selection=True)

    allShapes = cmds.ls(geometry=True)
    allMeshes = cmds.listRelatives(allShapes, parent=True, type='transform')
    allMeshes = list(set(allMeshes))

    allSelectedMeshes = []
    for m in allSelected:
        if m in allMeshes:
            allSelectedMeshes.append(m)

    jointsForSelected = GetMeshesJoints(allSelectedMeshes)
    print jointsForSelected
    cmds.select(jointsForSelected)
