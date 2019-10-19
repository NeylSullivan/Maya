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

def UpdateListWithAllThemParents(inOutJointsList):
    jointsUnique = list(set(inOutJointsList))
    allParentsSet = set()
    for j in jointsUnique:
        parents = GetAllParentsOfJoint(j)
        allParentsSet.update(parents)

    allParentsSet.update(jointsUnique)

    #inOutJointsList.clear()
    #python 2.x list has no clear() so use this instead
    del inOutJointsList [:]
    inOutJointsList.extend(list(allParentsSet))


def GetMeshesJoints(meshes):
    allJoints = []

    for m in meshes:
        skinCluster = mayaUtils.GetSkinCluster(m)
        if not skinCluster:
            continue

        weightedInfls = cmds.skinCluster(skinCluster, q=True, wi=True)
        allJoints.extend(weightedInfls)

    allJoints = list(set(allJoints))

    UpdateListWithAllThemParents(allJoints)
    RemoveJointsFromListByWildCard(allJoints, '*_END') # END joints not skinned but to be sure... they never should be exported to ue4

    return allJoints

def GetSpecialJoints():
    specialJoints = []

    sockets = cmds.ls('Camera', type='joint')
    if sockets:
        specialJoints.extend(sockets)

    nipples = cmds.ls('Nipple_?', type='joint')
    if nipples:
        specialJoints.extend(nipples)

    jiggles = cmds.ls('*_JIGGLE', type='joint')
    if jiggles:
        specialJoints.extend(jiggles)

    eyes = cmds.ls('Eye_?', type='joint')
    if eyes:
        specialJoints.extend(eyes)

    UpdateListWithAllThemParents(specialJoints)
    print specialJoints
    return specialJoints

def GetIKJoints(sourceJointsList):
    ikJoints = []

    for j in sourceJointsList:
        constraints = list(set(cmds.listConnections(j, type='parentConstraint') or []))
        if not constraints:
            continue
        #print j
        #print constraints
        for c in constraints:
            objects = list(set(cmds.listConnections(c, source=False, destination=True, exactType=True, type='joint') or []))
            if not objects:
                continue
            #print objects
            for o in objects:
                ikJoints.append(o)
                #print cmds.nodeType(o)


    ikJoints = fnmatch.filter(ikJoints, 'IK_*')
    UpdateListWithAllThemParents(ikJoints)

    return ikJoints


def SelectJointsForSelectedMeshes(bKeepSelection=True, bIncludeSpecialJoints=True, bIncludeIKJoints=True):
    allSelected = cmds.ls(selection=True)

    allShapes = cmds.ls(geometry=True)
    allMeshes = cmds.listRelatives(allShapes, parent=True, type='transform')
    allMeshes = list(set(allMeshes))

    allSelectedMeshes = []
    for m in allSelected:
        if m in allMeshes:
            allSelectedMeshes.append(m)

    jointsForSelection = GetMeshesJoints(allSelectedMeshes)

    if bKeepSelection:
        cmds.select(jointsForSelection, add=True)
    else:
        cmds.select(jointsForSelection)

    if bIncludeSpecialJoints:
        jointsForSelection.extend(GetSpecialJoints())
        jointsForSelection = list(set(jointsForSelection))
        cmds.select(jointsForSelection, add=True)

    if bIncludeIKJoints:
        #print 'bIncludeIKJoints = {0}'.format(bIncludeIKJoints)
        jointsForSelection.extend(GetIKJoints(jointsForSelection))
        jointsForSelection = list(set(jointsForSelection))
        cmds.select(jointsForSelection, add=True)

def SelectBodyAnimRelevantJoints():
    jointsToSelect = mayaUtils.GetHierarchy('Root')
    RemoveJointsFromListByWildCard(jointsToSelect, '*_END')
    RemoveJointsFromListByWildCard(jointsToSelect, '*_TWIST')
    RemoveJointsFromListByWildCard(jointsToSelect, '*_BEND')
    RemoveJointsFromListByWildCard(jointsToSelect, '*_JIGGLE')
    RemoveJointsFromListByWildCard(jointsToSelect, 'Nipple_?')

    if 'Head' in jointsToSelect:
        headChildren = cmds.listRelatives('Head', allDescendents=True, type="joint")
        if headChildren:
            for j in headChildren:
                if not j == 'Camera': #keep camera socket
                    RemoveJointFromList(jointsToSelect, j)

    jointsToSelect = list(set(jointsToSelect))
    UpdateListWithAllThemParents(jointsToSelect)
    cmds.select(jointsToSelect)
