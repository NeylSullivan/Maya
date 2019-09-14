import maya.cmds as cmds
import time
import libHazardMathUtils as hazMath
import libHazardMayaUtils as mayaUtils

reload(hazMath)
reload(mayaUtils)


def AddEndJoints():
    cmds.select(clear=True)
    srcJoints = ['HandThumb3_L', 'HandIndex3_L', 'HandMid3_L', 'HandRing3_L', 'HandPinky3_L']
    srcJoints.extend(['HandThumb3_R', 'HandIndex3_R', 'HandMid3_R', 'HandRing3_R', 'HandPinky3_R'])
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


def AddCameraJoint():
    cmds.select(clear=True)
    cmds.select(['Eye_L', 'Eye_R'])
    EyesPos = mayaUtils.GetAverageWorldTranslationOfSelected()
    EyesPos[0] = 0.0
    EyesPos[2] = 0.0

    cmds.select('Head')
    cmds.joint(name='FK_CAMERA_SOCKET')
    cmds.xform(worldSpace=True, translation=EyesPos)

    print 'Created camera joint FK_CAMERA_SOCKET with world pos {0}'.format(EyesPos)

def RenameSkeletonJoints():
    print 'Renaming skeleton joints'

    mayaUtils.RenameJoint('hip', 'Hips')
    mayaUtils.RenameJoint('abdomenLower', 'Spine_1')
    mayaUtils.RenameJoint('abdomenUpper', 'Spine_2')
    mayaUtils.RenameJoint('chestLower', 'Spine_3')
    mayaUtils.RenameJoint('chestUpper', 'Spine_4')

    mayaUtils.RenameJoint('neckLower', 'Neck_1')
    mayaUtils.RenameJoint('neckUpper', 'Neck_2')
    mayaUtils.RenameJoint('head', 'Head')

    mayaUtils.RenameJoint('lPectoral', 'Pectoral_L')
    mayaUtils.RenameJoint('rPectoral', 'Pectoral_R')
    # Arm Left
    mayaUtils.RenameJoint('lCollar', 'Clavicle_L')
    mayaUtils.RenameJoint('lShldrBend', 'ArmTop_L')
    mayaUtils.RenameJoint('lShldrTwist', 'ArmBottom_L')

    mayaUtils.RenameJoint('lForearmBend', 'ForeArmTop_L')
    mayaUtils.RenameJoint('lForearmTwist', 'ForeArmBottom_L')
    mayaUtils.RenameJoint('lHand', 'Hand_L')

    mayaUtils.RenameJoint('lThumb1', 'HandThumb1_L')
    mayaUtils.RenameJoint('lThumb2', 'HandThumb2_L')
    mayaUtils.RenameJoint('lThumb3', 'HandThumb3_L')

    mayaUtils.RenameJoint('lCarpal1', 'HandIndex0_L')
    mayaUtils.RenameJoint('lIndex1', 'HandIndex1_L')
    mayaUtils.RenameJoint('lIndex2', 'HandIndex2_L')
    mayaUtils.RenameJoint('lIndex3', 'HandIndex3_L')

    mayaUtils.RenameJoint('lCarpal2', 'HandMid0_L')
    mayaUtils.RenameJoint('lMid1', 'HandMid1_L')
    mayaUtils.RenameJoint('lMid2', 'HandMid2_L')
    mayaUtils.RenameJoint('lMid3', 'HandMid3_L')

    mayaUtils.RenameJoint('lCarpal3', 'HandRing0_L')
    mayaUtils.RenameJoint('lRing1', 'HandRing1_L')
    mayaUtils.RenameJoint('lRing2', 'HandRing2_L')
    mayaUtils.RenameJoint('lRing3', 'HandRing3_L')

    mayaUtils.RenameJoint('lCarpal4', 'HandPinky0_L')
    mayaUtils.RenameJoint('lPinky1', 'HandPinky1_L')
    mayaUtils.RenameJoint('lPinky2', 'HandPinky2_L')
    mayaUtils.RenameJoint('lPinky3', 'HandPinky3_L')

    # Arm Right
    mayaUtils.RenameJoint('rCollar', 'Clavicle_R')
    mayaUtils.RenameJoint('rShldrBend', 'ArmTop_R')
    mayaUtils.RenameJoint('rShldrTwist', 'ArmBottom_R')

    mayaUtils.RenameJoint('rForearmBend', 'ForeArmTop_R')
    mayaUtils.RenameJoint('rForearmTwist', 'ForeArmBottom_R')
    mayaUtils.RenameJoint('rHand', 'Hand_R')

    mayaUtils.RenameJoint('rThumb1', 'HandThumb1_R')
    mayaUtils.RenameJoint('rThumb2', 'HandThumb2_R')
    mayaUtils.RenameJoint('rThumb3', 'HandThumb3_R')

    mayaUtils.RenameJoint('rCarpal1', 'HandIndex0_R')
    mayaUtils.RenameJoint('rIndex1', 'HandIndex1_R')
    mayaUtils.RenameJoint('rIndex2', 'HandIndex2_R')
    mayaUtils.RenameJoint('rIndex3', 'HandIndex3_R')

    mayaUtils.RenameJoint('rCarpal2', 'HandMid0_R')
    mayaUtils.RenameJoint('rMid1', 'HandMid1_R')
    mayaUtils.RenameJoint('rMid2', 'HandMid2_R')
    mayaUtils.RenameJoint('rMid3', 'HandMid3_R')

    mayaUtils.RenameJoint('rCarpal3', 'HandRing0_R')
    mayaUtils.RenameJoint('rRing1', 'HandRing1_R')
    mayaUtils.RenameJoint('rRing2', 'HandRing2_R')
    mayaUtils.RenameJoint('rRing3', 'HandRing3_R')

    mayaUtils.RenameJoint('rCarpal4', 'HandPinky0_R')
    mayaUtils.RenameJoint('rPinky1', 'HandPinky1_R')
    mayaUtils.RenameJoint('rPinky2', 'HandPinky2_R')
    mayaUtils.RenameJoint('rPinky3', 'HandPinky3_R')

    # Leg Left
    mayaUtils.RenameJoint('lThighBend', 'UpLeg_L')
    mayaUtils.RenameJoint('lThighTwist', 'UpLegTwist_L')
    mayaUtils.RenameJoint('lShin', 'Leg_L')
    mayaUtils.RenameJoint('lFoot', 'Foot_L')
    #rename('lMetatarsals', 'Metatarsals_L')
    mayaUtils.RenameJoint('lToe', 'Toe_L')

    # Leg Right
    mayaUtils.RenameJoint('rThighBend', 'UpLeg_R')
    mayaUtils.RenameJoint('rThighTwist', 'UpLegTwist_R')
    mayaUtils.RenameJoint('rShin', 'Leg_R')
    mayaUtils.RenameJoint('rFoot', 'Foot_R')
    #rename('rMetatarsals', 'Metatarsals_R')
    mayaUtils.RenameJoint('rToe', 'Toe_R')

    # Face
    mayaUtils.RenameJoint('lEye', 'Eye_L')
    mayaUtils.RenameJoint('rEye', 'Eye_R')
    mayaUtils.RenameJoint('lEar', 'Ear_L')
    mayaUtils.RenameJoint('rEar', 'Ear_R')
    mayaUtils.RenameJoint('upperTeeth', 'UpperTeeth')
    mayaUtils.RenameJoint('lowerJaw', 'LowerJaw')
    mayaUtils.RenameJoint('lowerTeeth', 'LowerTeeth')
    mayaUtils.RenameJoint('tongue01', 'Tongue_1')
    mayaUtils.RenameJoint('tongue02', 'Tongue_2')
    mayaUtils.RenameJoint('tongue03', 'Tongue_3')
    mayaUtils.RenameJoint('tongue04', 'Tongue_4')

    mayaUtils.RenameJoint('lowerFaceRig', 'LowerFaceRig')
    mayaUtils.RenameChildren('LowerFaceRig')

    mayaUtils.RenameJoint('upperFaceRig', 'UpperFaceRig')
    mayaUtils.RenameChildren('UpperFaceRig')

    # Root
    mayaUtils.RenameJoint('Genesis8Female', 'Root')



def OptimizeBodyMaterials():
    print 'Starting body materials optimization'
    start = time.clock()

    shape = mayaUtils.FindShapeByMat('Torso')

    if shape is None:
        print 'Error! Can`t find body(Torso) shape'
        return

    mayaUtils.AppendShadingGroupByMat(shape, 'Mouth', 'Teeth')
    mouthShape = mayaUtils.DetachSkinnedMeshByMat(shape, ['Mouth'], '_MOUTH')

    eyesShape = mayaUtils.DetachSkinnedMeshByMat(shape, ['Pupils', 'EyeMoisture', 'Cornea', 'Irises', 'Sclera'], '_Eyes')

    mayaUtils.AppendShadingGroupByMat(shape, 'Face', 'Lips')
    mayaUtils.AppendShadingGroupByMat(shape, 'Face', 'Ears')
    mayaUtils.AppendShadingGroupByMat(shape, 'Face', 'EyeSocket')

    mayaUtils.AppendShadingGroupByMat(shape, 'Legs', 'Toenails')
    mayaUtils.AppendShadingGroupByMat(shape, 'Arms', 'Fingernails')

    mayaUtils.ArrangeUVByMat(shape, 'Torso', su=0.5, sv=0.5, u=0.5, v=0.5)
    mayaUtils.ArrangeUVByMat(shape, 'Face', su=0.5, sv=0.5, u=0.0, v=0.5)
    mayaUtils.ArrangeUVByMat(shape, 'Legs', su=0.5, sv=0.5, u=0.5, v=0.0)
    mayaUtils.ArrangeUVByMat(shape, 'Arms', su=0.5, sv=0.5, u=0.0, v=0.0)

    mayaUtils.AppendShadingGroupByMat(shape, 'Torso', 'Legs')
    mayaUtils.AppendShadingGroupByMat(shape, 'Torso', 'Arms')
    mayaUtils.AppendShadingGroupByMat(shape, 'Torso', 'Face')

    mayaUtils.RenameMaterial('Torso', 'Body')

    print 'Baking history'
    cmds.bakePartialHistory(shape, prePostDeformers=True)
    cmds.bakePartialHistory(mouthShape, prePostDeformers=True)
    cmds.bakePartialHistory(eyesShape, prePostDeformers=True)

    mayaUtils.CleanUnusedInfluensesOnAllSkinClusters()

    print 'Finished body materials optimization: time taken %.02f seconds' % (time.clock()-start)


def CreateIkJoints():
    CreateIkJoint('FK_CAMERA_SOCKET', 'Root', 'IK_CAMERA')
    CreateIkJoint('Root', 'Root', 'IK_Foot_Root')
    CreateIkJoint('Foot_R', 'IK_Foot_Root', 'IK_Foot_R')
    CreateIkJoint('Foot_L', 'IK_Foot_Root', 'IK_Foot_L')

    CreateIkJoint('Root', 'Root', 'IK_Hands_Root')
    CreateIkJoint('Hand_R', 'IK_Hands_Root', 'IK_Weapon_Root')
    CreateIkJoint('Hand_R', 'IK_Weapon_Root', 'IK_Hand_R')
    CreateIkJoint('Hand_L', 'IK_Weapon_Root', 'IK_Hand_L')


def CreateIkJoint(referenceJnt, parentJnt, ikJntName):
    cmds.select(clear=True)
    print 'Created IK joint "{0}" corresponding to "{1}" parented to "{2}"'.format(ikJntName, referenceJnt, parentJnt)
    cmds.select(referenceJnt)
    cmds.joint(name=ikJntName)
    if not parentJnt == referenceJnt:
        cmds.parent(ikJntName, parentJnt)





def DuplicateSkeletonJoints(oldSkeletonRoot, newJointsPrefix):
    print 'Duplicating skeleton'

    jointsList = mayaUtils.GetHierarchy(oldSkeletonRoot)
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
    mayaUtils.RotateJoint("DAZ_Root", 90, 0, 90)

    # Spine
    mayaUtils.RotateJoint("DAZ_Hips", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Spine_1", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Spine_2", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Spine_3", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Spine_4", 90, 0, 90)

    mayaUtils.RotateJoint("DAZ_Pectoral_L", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Pectoral_R", 90, 0, 90)

    mayaUtils.RotateJoint("DAZ_Neck_1", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Neck_2", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Head", 90, 0, 90)

    # Leg Left
    mayaUtils.RotateJoint("DAZ_UpLeg_L", 90, 0, -90)
    mayaUtils.RotateJoint("DAZ_UpLegTwist_L", 90, 0, -90)
    mayaUtils.RotateJoint("DAZ_Leg_L", 90, 0, -90)
    # copy rotation from Leg
    cmds.xform('DAZ_Foot_L', absolute=True, rotation=cmds.xform('DAZ_Leg_L', q=True, absolute=True, rotation=True))
    mayaUtils.RotateJoint("DAZ_Toe_L", 0, -90, 0)

    # Leg Right
    mayaUtils.RotateJoint("DAZ_UpLeg_R", 90, 0, -90)
    mayaUtils.RotateJoint("DAZ_UpLegTwist_R", 90, 0, -90)
    mayaUtils.RotateJoint("DAZ_Leg_R", 90, 0, -90)
    # copy rotation from Leg
    cmds.xform('DAZ_Foot_R', absolute=True, rotation=cmds.xform('DAZ_Leg_R', q=True, absolute=True, rotation=True))
    mayaUtils.RotateJoint("DAZ_Toe_R", 0, -90, 0)

    # Arm Left

    mayaUtils.RotateJoint("DAZ_Clavicle_L", 90)
    mayaUtils.RotateJoint("DAZ_ArmTop_L", 90)
    mayaUtils.RotateJoint("DAZ_ArmBottom_L", 90)
    mayaUtils.RotateJoint("DAZ_ForeArmTop_L", 90)
    mayaUtils.RotateJoint("DAZ_ForeArmBottom_L", 90)
    mayaUtils.RotateJoint("DAZ_Hand_L", 90)

    mayaUtils.RotateJoint('DAZ_HandThumb1_L', 180)
    mayaUtils.RotateJoint('DAZ_HandThumb2_L', 180)
    mayaUtils.RotateJoint('DAZ_HandThumb3_L', 180)

    mayaUtils.RotateJoint('DAZ_HandIndex0_L', 90)
    mayaUtils.RotateJoint('DAZ_HandIndex1_L', 90)
    mayaUtils.RotateJoint('DAZ_HandIndex2_L', 90)
    mayaUtils.RotateJoint('DAZ_HandIndex3_L', 90)

    mayaUtils.RotateJoint('DAZ_HandMid0_L', 90)
    mayaUtils.RotateJoint('DAZ_HandMid1_L', 90)
    mayaUtils.RotateJoint('DAZ_HandMid2_L', 90)
    mayaUtils.RotateJoint('DAZ_HandMid3_L', 90)

    mayaUtils.RotateJoint('DAZ_HandRing0_L', 90)
    mayaUtils.RotateJoint('DAZ_HandRing1_L', 90)
    mayaUtils.RotateJoint('DAZ_HandRing2_L', 90)
    mayaUtils.RotateJoint('DAZ_HandRing3_L', 90)

    mayaUtils.RotateJoint('DAZ_HandPinky0_L', 90)
    mayaUtils.RotateJoint('DAZ_HandPinky1_L', 90)
    mayaUtils.RotateJoint('DAZ_HandPinky2_L', 90)
    mayaUtils.RotateJoint('DAZ_HandPinky3_L', 90)

    # Arm Right

    mayaUtils.RotateJoint("DAZ_Clavicle_R", -90, 180)
    mayaUtils.RotateJoint("DAZ_ArmTop_R", -90, 180)
    mayaUtils.RotateJoint("DAZ_ArmBottom_R", -90, 180)
    mayaUtils.RotateJoint("DAZ_ForeArmTop_R", -90, 180)
    mayaUtils.RotateJoint("DAZ_ForeArmBottom_R", -90, 180)
    mayaUtils.RotateJoint("DAZ_Hand_R", -90, 180)

    mayaUtils.RotateJoint('DAZ_HandThumb1_R', -180, 180)
    mayaUtils.RotateJoint('DAZ_HandThumb2_R', -180, 180)
    mayaUtils.RotateJoint('DAZ_HandThumb3_R', -180, 180)

    mayaUtils.RotateJoint('DAZ_HandIndex0_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandIndex1_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandIndex2_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandIndex3_R', -90, 180)

    mayaUtils.RotateJoint('DAZ_HandMid0_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandMid1_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandMid2_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandMid3_R', -90, 180)

    mayaUtils.RotateJoint('DAZ_HandRing0_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandRing1_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandRing2_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandRing3_R', -90, 180)

    mayaUtils.RotateJoint('DAZ_HandPinky0_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandPinky1_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandPinky2_R', -90, 180)
    mayaUtils.RotateJoint('DAZ_HandPinky3_R', -90, 180)

    # facial rig
    mayaUtils.RotateJoint("DAZ_Tongue_1", 0, -90, 0)
    mayaUtils.RotateJoint("DAZ_Tongue_2", 0, -90, 0)
    mayaUtils.RotateJoint("DAZ_Tongue_3", 0, -90, 0)
    mayaUtils.RotateJoint("DAZ_Tongue_4", 0, -90, 0)

    # selecting original joints
    children = cmds.listRelatives('Head', allDescendents=True)

    for child in children:
        if child.startswith('Tongue_'):
            continue  # skip already rotated
        mayaUtils.RotateJoint('DAZ_' + child, 90, 0, 90)  # but rotating skeleton copy

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
        mayaUtils.RenameJoint(j, newName)



def MakeBendCorrectiveJoint(name, referenceJnt, parentJnt, donorJntsList=None):
    if donorJntsList is None:
        donorJntsList = [parentJnt, referenceJnt]

    skinClusters = mayaUtils.GetAllSkinClustersInfluencedByJoints(donorJntsList, True)
    print 'Creating bend corrective joint {0} parented: {1}, referenced: {2}, skins: {3}'.format(name, parentJnt, referenceJnt, skinClusters)

    cmds.select(clear=True)
    cmds.select(referenceJnt)
    cmds.joint(name=name)
    if not parentJnt == referenceJnt:
        cmds.parent(name, parentJnt)

    cmds.orientConstraint(donorJntsList, name, maintainOffset=True)

    cmds.select(clear=True)



    for skinClusterName in skinClusters:
        cmds.skinCluster(skinClusterName, e=True, selectInfluenceVerts=donorJntsList[0])
        sel = cmds.ls(selection=True, flatten=True)
        onlyVertices = cmds.filterExpand(sel, sm=31, expand=True)
        intersectedVerts = []

        prune_value = 0.001

        for v in onlyVertices:
            if cmds.skinPercent(skinClusterName, v, transform=donorJntsList[0], query=True) > prune_value:
                if cmds.skinPercent(skinClusterName, v, transform=donorJntsList[1], query=True) > prune_value:
                    intersectedVerts.append(v)

        cmds.skinCluster(skinClusterName, e=True, addInfluence=name, weight=0.0)
        cmds.select(clear=True)
        for v in intersectedVerts:
            sumNewWeight = 0
            transformValueList = []
            oldWeights = []
            jointsCount = len(donorJntsList)

            for j in donorJntsList:
                w = cmds.skinPercent(skinClusterName, v, transform=j, query=True)
                #print 'skinPercent Vert: {0} j:{1} w:{2}'.format(v, j, w)
                oldWeights.append(w)

            totalWeight = sum(oldWeights)

            for i in range(0, jointsCount):
                newWeight = oldWeights[i] * hazMath.SmoothStep01(hazMath.Clamp01(oldWeights[i] / totalWeight))
                sumNewWeight += newWeight
                transformValueList.append([donorJntsList[i], newWeight])

            totalWeight -= prune_value

            transformValueList.append([name, hazMath.Clamp(totalWeight - sumNewWeight, 0.0, totalWeight)])
            cmds.skinPercent(skinClusterName, v, transformValue=transformValueList)
            #print 'Vert: {0} value:{1}'.format(v, sumNewWeight)


        #cmds.select(intersectedVertsList)

def MakeBendCorrectiveJoints():
    print 'MakeBendCorrectiveJoints'
    MakeBendCorrectiveJoint('Knee_L_BEND', 'Leg_L', 'UpLegTwist_L')
    MakeBendCorrectiveJoint('Knee_R_BEND', 'Leg_R', 'UpLegTwist_R')

    MakeBendCorrectiveJoint('Butt_L_BEND', 'UpLeg_L', 'Hips')
    MakeBendCorrectiveJoint('Butt_R_BEND', 'UpLeg_R', 'Hips')

    MakeBendCorrectiveJoint('Shoulder_L_BEND', 'ArmTop_L', 'Clavicle_L')
    MakeBendCorrectiveJoint('Shoulder_R_BEND', 'ArmTop_R', 'Clavicle_R')

    MakeBendCorrectiveJoint('Elbow_L_BEND', 'ForeArmTop_L', 'ArmBottom_L')
    MakeBendCorrectiveJoint('Elbow_R_BEND', 'ForeArmTop_R', 'ArmBottom_R')
