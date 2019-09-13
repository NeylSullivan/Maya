import maya.cmds as cmds
import time

from libHazardMayaFunctions import *
import libHazardMayaFunctions
reload(libHazardMayaFunctions)

import libHazardMathUtils as math
reload(math)

def RenameSkeletonJoints():
    print 'Renaming skeleton joints'

    RenameJoint('hip', 'Hips')
    RenameJoint('abdomenLower', 'Spine_1')
    RenameJoint('abdomenUpper', 'Spine_2')
    RenameJoint('chestLower', 'Spine_3')
    RenameJoint('chestUpper', 'Spine_4')

    RenameJoint('neckLower', 'Neck_1')
    RenameJoint('neckUpper', 'Neck_2')
    RenameJoint('head', 'Head')

    RenameJoint('lPectoral', 'Pectoral_L')
    RenameJoint('rPectoral', 'Pectoral_R')
    # Arm Left
    RenameJoint('lCollar', 'Clavicle_L')
    RenameJoint('lShldrBend', 'ArmTop_L')
    RenameJoint('lShldrTwist', 'ArmBottom_L')

    RenameJoint('lForearmBend', 'ForeArmTop_L')
    RenameJoint('lForearmTwist', 'ForeArmBottom_L')
    RenameJoint('lHand', 'Hand_L')

    RenameJoint('lThumb1', 'HandThumb1_L')
    RenameJoint('lThumb2', 'HandThumb2_L')
    RenameJoint('lThumb3', 'HandThumb3_L')

    RenameJoint('lCarpal1', 'HandIndex0_L')
    RenameJoint('lIndex1', 'HandIndex1_L')
    RenameJoint('lIndex2', 'HandIndex2_L')
    RenameJoint('lIndex3', 'HandIndex3_L')

    RenameJoint('lCarpal2', 'HandMid0_L')
    RenameJoint('lMid1', 'HandMid1_L')
    RenameJoint('lMid2', 'HandMid2_L')
    RenameJoint('lMid3', 'HandMid3_L')

    RenameJoint('lCarpal3', 'HandRing0_L')
    RenameJoint('lRing1', 'HandRing1_L')
    RenameJoint('lRing2', 'HandRing2_L')
    RenameJoint('lRing3', 'HandRing3_L')

    RenameJoint('lCarpal4', 'HandPinky0_L')
    RenameJoint('lPinky1', 'HandPinky1_L')
    RenameJoint('lPinky2', 'HandPinky2_L')
    RenameJoint('lPinky3', 'HandPinky3_L')

    # Arm Right
    RenameJoint('rCollar', 'Clavicle_R')
    RenameJoint('rShldrBend', 'ArmTop_R')
    RenameJoint('rShldrTwist', 'ArmBottom_R')

    RenameJoint('rForearmBend', 'ForeArmTop_R')
    RenameJoint('rForearmTwist', 'ForeArmBottom_R')
    RenameJoint('rHand', 'Hand_R')

    RenameJoint('rThumb1', 'HandThumb1_R')
    RenameJoint('rThumb2', 'HandThumb2_R')
    RenameJoint('rThumb3', 'HandThumb3_R')

    RenameJoint('rCarpal1', 'HandIndex0_R')
    RenameJoint('rIndex1', 'HandIndex1_R')
    RenameJoint('rIndex2', 'HandIndex2_R')
    RenameJoint('rIndex3', 'HandIndex3_R')

    RenameJoint('rCarpal2', 'HandMid0_R')
    RenameJoint('rMid1', 'HandMid1_R')
    RenameJoint('rMid2', 'HandMid2_R')
    RenameJoint('rMid3', 'HandMid3_R')

    RenameJoint('rCarpal3', 'HandRing0_R')
    RenameJoint('rRing1', 'HandRing1_R')
    RenameJoint('rRing2', 'HandRing2_R')
    RenameJoint('rRing3', 'HandRing3_R')

    RenameJoint('rCarpal4', 'HandPinky0_R')
    RenameJoint('rPinky1', 'HandPinky1_R')
    RenameJoint('rPinky2', 'HandPinky2_R')
    RenameJoint('rPinky3', 'HandPinky3_R')

    # Leg Left
    RenameJoint('lThighBend', 'UpLeg_L')
    RenameJoint('lThighTwist', 'UpLegTwist_L')
    RenameJoint('lShin', 'Leg_L')
    RenameJoint('lFoot', 'Foot_L')
    #rename('lMetatarsals', 'Metatarsals_L')
    RenameJoint('lToe', 'Toe_L')

    # Leg Right
    RenameJoint('rThighBend', 'UpLeg_R')
    RenameJoint('rThighTwist', 'UpLegTwist_R')
    RenameJoint('rShin', 'Leg_R')
    RenameJoint('rFoot', 'Foot_R')
    #rename('rMetatarsals', 'Metatarsals_R')
    RenameJoint('rToe', 'Toe_R')

    # Face
    RenameJoint('lEye', 'Eye_L')
    RenameJoint('rEye', 'Eye_R')
    RenameJoint('lEar', 'Ear_L')
    RenameJoint('rEar', 'Ear_R')
    RenameJoint('upperTeeth', 'UpperTeeth')
    RenameJoint('lowerJaw', 'LowerJaw')
    RenameJoint('lowerTeeth', 'LowerTeeth')
    RenameJoint('tongue01', 'Tongue_1')
    RenameJoint('tongue02', 'Tongue_2')
    RenameJoint('tongue03', 'Tongue_3')
    RenameJoint('tongue04', 'Tongue_4')

    RenameJoint('lowerFaceRig', 'LowerFaceRig')
    RenameChildren('LowerFaceRig')

    RenameJoint('upperFaceRig', 'UpperFaceRig')
    RenameChildren('UpperFaceRig')

    # Root
    RenameJoint('Genesis8Female', 'Root')


def GetAverageWorldTranslationOfSelected():
    sel = cmds.ls(sl=True, fl=True)
    count = len(sel)
    sums = [0, 0, 0]
    for item in sel:
        pos = cmds.xform(item, q=True, worldSpace=True, translation=True)
        sums[0] += pos[0]
        sums[1] += pos[1]
        sums[2] += pos[2]
    center = [sums[0]/count, sums[1]/count, sums[2]/count]
    return center


def AddCameraJoint():
    cmds.select(clear=True)
    cmds.select(['Eye_L', 'Eye_R'])
    EyesPos = GetAverageWorldTranslationOfSelected()
    EyesPos[0] = 0.0
    EyesPos[2] = 0.0

    cmds.select('Head')
    cmds.joint(name='FK_CAMERA_SOCKET')
    cmds.xform(worldSpace=True, translation=EyesPos)

    print 'Created camera joint FK_CAMERA_SOCKET with world pos {0}'.format(
        EyesPos)


def AddEndJoints():
    cmds.select(clear=True)
    srcJoints = ['HandThumb3_L', 'HandIndex3_L',
                 'HandMid3_L', 'HandRing3_L', 'HandPinky3_L']
    srcJoints.extend(['HandThumb3_R', 'HandIndex3_R',
                      'HandMid3_R', 'HandRing3_R', 'HandPinky3_R'])
    srcJoints.append('Tongue_4')

    for j in srcJoints:
        newJointName = j + '_END'
        relativeTranslation = cmds.xform(
            j, q=True, relative=True, translation=True)
        cmds.select(j)
        cmds.joint(name=newJointName)
        cmds.xform(relative=True, translation=relativeTranslation)
        print 'Created end joint {0} from {1} with offset {2}'.format(
            newJointName, j, relativeTranslation)


def CreateIkJoint(referenceJnt, parentJnt, ikJntName):
    cmds.select(clear=True)
    print 'Created IK joint "{0}" corresponding to "{1}" parented to "{2}"'.format(ikJntName, referenceJnt, parentJnt)
    cmds.select(referenceJnt)
    cmds.joint(name=ikJntName)
    if not parentJnt == referenceJnt:
        cmds.parent(ikJntName, parentJnt)





def DuplicateSkeletonJoints(oldSkeletonRoot, newJointsPrefix):
    print 'Duplicating skeleton'

    jointsList = GetHierarchy(oldSkeletonRoot)
    #print jointsList

    for j in jointsList:
        pos = cmds.joint(j, q=True, absolute=True)
        oldName = cmds.joint(j, q=True, name=True)
        oldOrientation = cmds.joint(j, q=True, orientation=True)

        newName = newJointsPrefix + oldName

        cmds.select(clear=True)
        newJoint = cmds.joint(p=pos, name=newName)
        cmds.xform(newJoint, r=True, ro=oldOrientation)


def FixNewJointsOrientation():
    print 'Fixing joint orientation'

    # Root
    RotateJoint("DAZ_Root", 90, 0, 90)

    # Spine
    RotateJoint("DAZ_Hips", 90, 0, 90)
    RotateJoint("DAZ_Spine_1", 90, 0, 90)
    RotateJoint("DAZ_Spine_2", 90, 0, 90)
    RotateJoint("DAZ_Spine_3", 90, 0, 90)
    RotateJoint("DAZ_Spine_4", 90, 0, 90)

    RotateJoint("DAZ_Pectoral_L", 90, 0, 90)
    RotateJoint("DAZ_Pectoral_R", 90, 0, 90)

    RotateJoint("DAZ_Neck_1", 90, 0, 90)
    RotateJoint("DAZ_Neck_2", 90, 0, 90)
    RotateJoint("DAZ_Head", 90, 0, 90)

    # Leg Left
    RotateJoint("DAZ_UpLeg_L", 90, 0, -90)
    RotateJoint("DAZ_UpLegTwist_L", 90, 0, -90)
    RotateJoint("DAZ_Leg_L", 90, 0, -90)
    # copy rotation from Leg
    cmds.xform('DAZ_Foot_L', absolute=True, rotation=cmds.xform('DAZ_Leg_L', q=True, absolute=True, rotation=True))
    RotateJoint("DAZ_Toe_L", 0, -90, 0)

    # Leg Right
    RotateJoint("DAZ_UpLeg_R", 90, 0, -90)
    RotateJoint("DAZ_UpLegTwist_R", 90, 0, -90)
    RotateJoint("DAZ_Leg_R", 90, 0, -90)
    # copy rotation from Leg
    cmds.xform('DAZ_Foot_R', absolute=True, rotation=cmds.xform('DAZ_Leg_R', q=True, absolute=True, rotation=True))
    RotateJoint("DAZ_Toe_R", 0, -90, 0)

    # Arm Left

    RotateJoint("DAZ_Clavicle_L", 90)
    RotateJoint("DAZ_ArmTop_L", 90)
    RotateJoint("DAZ_ArmBottom_L", 90)
    RotateJoint("DAZ_ForeArmTop_L", 90)
    RotateJoint("DAZ_ForeArmBottom_L", 90)
    RotateJoint("DAZ_Hand_L", 90)

    RotateJoint('DAZ_HandThumb1_L', 180)
    RotateJoint('DAZ_HandThumb2_L', 180)
    RotateJoint('DAZ_HandThumb3_L', 180)

    RotateJoint('DAZ_HandIndex0_L', 90)
    RotateJoint('DAZ_HandIndex1_L', 90)
    RotateJoint('DAZ_HandIndex2_L', 90)
    RotateJoint('DAZ_HandIndex3_L', 90)

    RotateJoint('DAZ_HandMid0_L', 90)
    RotateJoint('DAZ_HandMid1_L', 90)
    RotateJoint('DAZ_HandMid2_L', 90)
    RotateJoint('DAZ_HandMid3_L', 90)

    RotateJoint('DAZ_HandRing0_L', 90)
    RotateJoint('DAZ_HandRing1_L', 90)
    RotateJoint('DAZ_HandRing2_L', 90)
    RotateJoint('DAZ_HandRing3_L', 90)

    RotateJoint('DAZ_HandPinky0_L', 90)
    RotateJoint('DAZ_HandPinky1_L', 90)
    RotateJoint('DAZ_HandPinky2_L', 90)
    RotateJoint('DAZ_HandPinky3_L', 90)

    # Arm Right

    RotateJoint("DAZ_Clavicle_R", -90, 180)
    RotateJoint("DAZ_ArmTop_R", -90, 180)
    RotateJoint("DAZ_ArmBottom_R", -90, 180)
    RotateJoint("DAZ_ForeArmTop_R", -90, 180)
    RotateJoint("DAZ_ForeArmBottom_R", -90, 180)
    RotateJoint("DAZ_Hand_R", -90, 180)

    RotateJoint('DAZ_HandThumb1_R', -180, 180)
    RotateJoint('DAZ_HandThumb2_R', -180, 180)
    RotateJoint('DAZ_HandThumb3_R', -180, 180)

    RotateJoint('DAZ_HandIndex0_R', -90, 180)
    RotateJoint('DAZ_HandIndex1_R', -90, 180)
    RotateJoint('DAZ_HandIndex2_R', -90, 180)
    RotateJoint('DAZ_HandIndex3_R', -90, 180)

    RotateJoint('DAZ_HandMid0_R', -90, 180)
    RotateJoint('DAZ_HandMid1_R', -90, 180)
    RotateJoint('DAZ_HandMid2_R', -90, 180)
    RotateJoint('DAZ_HandMid3_R', -90, 180)

    RotateJoint('DAZ_HandRing0_R', -90, 180)
    RotateJoint('DAZ_HandRing1_R', -90, 180)
    RotateJoint('DAZ_HandRing2_R', -90, 180)
    RotateJoint('DAZ_HandRing3_R', -90, 180)

    RotateJoint('DAZ_HandPinky0_R', -90, 180)
    RotateJoint('DAZ_HandPinky1_R', -90, 180)
    RotateJoint('DAZ_HandPinky2_R', -90, 180)
    RotateJoint('DAZ_HandPinky3_R', -90, 180)

    # facial rig
    RotateJoint("DAZ_Tongue_1", 0, -90, 0)
    RotateJoint("DAZ_Tongue_2", 0, -90, 0)
    RotateJoint("DAZ_Tongue_3", 0, -90, 0)
    RotateJoint("DAZ_Tongue_4", 0, -90, 0)

    # selecting original joints
    children = cmds.listRelatives('Head', allDescendents=True)

    for child in children:
        if child.startswith('Tongue_'):
            continue  # skip already rotated
        RotateJoint('DAZ_' + child, 90, 0, 90)  # but rotating skeleton copy

    cmds.select(clear=True)
    print 'Fixing joint orientation: Done'


def RecreateHierarchy(oldSkeletonRoot, newJointsPrefix):
    print 'Recreating hierarchy'

    jointsList = cmds.listRelatives(oldSkeletonRoot, allDescendents=True, type="joint")#Root is already unparrented

    for j in jointsList:
        parent = cmds.listRelatives(j, parent=True, type='joint')
        if not parent:
            continue
        oldName = cmds.joint(j, q=True, name=True)
        oldParentName = cmds.joint(parent, q=True, name=True)

        newName = newJointsPrefix + oldName
        newParentName = newJointsPrefix + oldParentName
        #print newParentName
        cmds.parent(newName, newParentName)
        print 'Parenting {0} to {1}'.format(newName, newParentName)


def RenameNewSkeleton():
    print 'Renaming new skeleton'
    newRoot = cmds.ls('DAZ_Root', type="joint")
    newJoints = cmds.listRelatives(newRoot, allDescendents=True)
    newJoints.append(newRoot[0])

    for j in newJoints:
        newName = j[4:]
        RenameJoint(j, newName)

def ParentAllGeometryToWorld():
    print 'Parenting geometry to world'

    skinList = cmds.ls(type='skinCluster')
    meshes = set(sum([cmds.skinCluster(c, q=1, g=1) for c in skinList], []))
    for mesh in meshes:
        transformList = cmds.listRelatives(mesh, parent=True)
        for tf in transformList:
            if cmds.listRelatives(tf, parent=True):
                cmds.parent(tf, world=True)

def GenerateBendCorrectiveBones():
    newJoint = 'Knee_L_BCB'
    maxNewJointRatio = 1.0
    CreateIkJoint('Leg_L', 'UpLegTwist_L', newJoint)
    cmds.orientConstraint('Leg_L', 'UpLegTwist_L', newJoint, maintainOffset=True)

    cmds.select(newJoint)
    #return

    skinClusterName = 'skinCluster1'
    mesh = GetMeshFromSkinCluster(skinClusterName)
    srcJoints = ['Leg_L', 'UpLegTwist_L']

    cmds.select(clear=True)
    influences = cmds.skinCluster(skinClusterName, query=True, influence=True)
    #intersectedVerts = set(cmds.filterExpand(cmds.polyListComponentConversion(mesh, toVertex=True), sm=31, expand=True))
    #print intersectedVerts

    cmds.skinCluster(skinClusterName, e=True, selectInfluenceVerts=srcJoints[0])
    sel = cmds.ls(selection=True, flatten=True)
    onlyVertices = cmds.filterExpand(sel, sm=31, expand=True)
    intersectedVerts = []

    prune_value = 0.001

    for v in onlyVertices:
        if cmds.skinPercent(skinClusterName, v, transform=srcJoints[0], query=True) > prune_value:
            if cmds.skinPercent(skinClusterName, v, transform=srcJoints[1], query=True) > prune_value:
                intersectedVerts.append(v)
    #cmds.select(intersectedVerts)

    intersectedVertsList = list(intersectedVerts)
    #cmds.select(intersectedVertsList)
    cmds.skinCluster(skinClusterName, e=True, addInfluence=newJoint, weight=0.0)
    cmds.select(clear=True)
    for v in intersectedVertsList:
        sumNewWeight = 0
        transformValueList = []
        oldWeights = []

        for j in srcJoints:
            w = cmds.skinPercent(skinClusterName, v, transform=j, query=True)
            print 'skinPercent Vert: {0} j:{1} w:{2}'.format(v, j, w)
            oldWeights.append(w)

        totalWeight = oldWeights[0] + oldWeights[1]
        weightsDifference = abs(oldWeights[0] - oldWeights[1])
        print oldWeights
        print totalWeight

        for i in range(0, 2):
            bendJointTransferAlpha = math.SmoothStep01(math.Clamp01(oldWeights[i] / totalWeight))
            newWeight = oldWeights[i] * bendJointTransferAlpha
            sumNewWeight += newWeight
            transformValueList.append([srcJoints[i], newWeight])


        transformValueList.append([newJoint, min(totalWeight, max(0.0, totalWeight - sumNewWeight)) - prune_value])
        print 'Vert: {0} value:{1}'.format(v, sumNewWeight)
        cmds.skinPercent(skinClusterName, v, transformValue=transformValueList)

    #cmds.select(intersectedVertsList)

#
#
#   MAIN
#
#
def OptymizeSkeleton():
    print 'Starting skeleton and mesh optimization'
    start = time.clock()

    FixMaxInfluencesForAllSkinClusters(4)

    DestroyMiddleJoint('lMetatarsals')
    DestroyMiddleJoint('rMetatarsals')
    DestroyMiddleJoint('pelvis')
    DestroyJointChildren('lToe')
    DestroyJointChildren('rToe')

    ParentAllGeometryToWorld()

    ResetBindPoseForAllSkinClusters()

    SetSkinMethodForAllSkinClusters(0)  # set skinning type to linear

    RenameSkeletonJoints()

    oldJoints = GetHierarchy('Root')

    # collect data for skin export
    skinData = GetSkinExportData()  # transform, shape, skincluster, jointsList

    # export skinning
    for sd in skinData:
        #print sd
        fileName = sd[0] + '_WEIGHTS.xml'
        cmds.deformerWeights(fileName, ex=True, deformer=sd[2])

    DuplicateSkeletonJoints('Root', 'DAZ_')
    FixNewJointsOrientation()
    RecreateHierarchy('Root', 'DAZ_')


    cmds.delete(oldJoints)

    RenameNewSkeleton()

    #import skinning
    for sd in skinData:
        #print sd
        cmds.skinCluster(sd[3], sd[0], name=sd[2], tsb=True)
        fileName = sd[0] + '_WEIGHTS.xml'
        cmds.deformerWeights(fileName, im=True, deformer=sd[2], method='index')

    cmds.select(clear=True)

    AddEndJoints()
    AddCameraJoint()

    #FixMaxInfluencesForAllSkinClusters(4)

    CreateIkJoint('FK_CAMERA_SOCKET', 'Root', 'IK_CAMERA')
    CreateIkJoint('Root', 'Root', 'IK_Foot_Root')
    CreateIkJoint('Foot_R', 'IK_Foot_Root', 'IK_Foot_R')
    CreateIkJoint('Foot_L', 'IK_Foot_Root', 'IK_Foot_L')

    CreateIkJoint('Root', 'Root', 'IK_Hands_Root')
    CreateIkJoint('Hand_R', 'IK_Hands_Root', 'IK_Weapon_Root')
    CreateIkJoint('Hand_R', 'IK_Weapon_Root', 'IK_Hand_R')
    CreateIkJoint('Hand_L', 'IK_Weapon_Root', 'IK_Hand_L')

    print 'FINISHED skeleton and mesh optimization: time taken %.02f seconds' % (time.clock()-start)
