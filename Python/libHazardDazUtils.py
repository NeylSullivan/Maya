import maya.cmds as cmds
import time
import libHazardMathUtils as hazMath
import libHazardMayaUtils as mayaUtils
import libHazardSelectionUtils as selUtils

reload(hazMath)
reload(mayaUtils)
reload(selUtils)

def CutAndMoveUVForBodyPartsHiding(shape, mask, uOffset):
    cmds.select(clear=True)
    print 'CutAndMoveUVForBodyPartsHiding shape{0}, mask "{1}", uOffset {2}'.format(shape, mask, uOffset)
    matched_faces = selUtils.GetFacesByBitmapMask(shape, mask)
    cmds.polyChipOff(matched_faces, dup=False)
    cmds.polyEditUV(matched_faces, u=uOffset)
    cmds.bakePartialHistory(shape, prePostDeformers=True)
    cmds.select(clear=True)


def CutMeshAndOffsetUVs():
    cmds.select(clear=True)
    shape = mayaUtils.FindShapeByMat('Body') #new name is 'Body'
    CutAndMoveUVForBodyPartsHiding(shape, r'e:\blackops\__WorkFlow\Maya\Resources\head_mask.tga', 1.0)
    CutAndMoveUVForBodyPartsHiding(shape, r'e:\blackops\__WorkFlow\Maya\Resources\hands_mask.tga', 2.0)
    CutAndMoveUVForBodyPartsHiding(shape, r'e:\blackops\__WorkFlow\Maya\Resources\feet_mask.tga', 3.0)

    mayaUtils.SetVertexColorForBorderVertices()
    mayaUtils.SetAverageNormalsForBorderVertices(shape)
    cmds.bakePartialHistory(shape, prePostDeformers=True)

def RenameAndCombineMeshes():
    print 'RenameAndCombineMeshes()'
    #Main
    bodyList = cmds.ls('Genesis8FemaleFBX*Shape', type='transform', objectsOnly=True, long=True)
    if bodyList:
        cmds.rename(bodyList[0], 'FemaleBody')

    #
    #EYES
    #
    eyesList = cmds.ls('HazardEyes*', type='transform', objectsOnly=True, long=True)

    if eyesList and len(eyesList) > 1:
        print '\tCombining {0}'.format(eyesList)
        cmds.polyUniteSkinned(eyesList, ch=False)
        cmds.rename('FemaleEyes')
        cmds.select(clear=True)
        #clear orphane transforms if exist
        for o in eyesList:
            if cmds.objExists(o):
                cmds.delete(o)
    else:
        print '\t No EYES meshes to combine'

    #
    #MOUTH
    #
    mouthList = cmds.ls('*_MOUTH', type='transform', objectsOnly=True, long=True)
    print mouthList

    teethList = cmds.ls('Teeth*', type='transform', objectsOnly=True, long=True)
    print teethList
    mayaUtils.AssignObjectListToShader(teethList, 'Mouth')

    teethMouthList = []
    if mouthList:
        teethMouthList.extend(mouthList)
    if teethList:
        teethMouthList.extend(teethList)


    if teethMouthList and len(teethMouthList) > 1:
        print '\tCombining {0}'.format(teethMouthList)
        cmds.polyUniteSkinned(teethMouthList, ch=False)
        cmds.rename('FemaleMouth')
        cmds.select(clear=True)

        #clear orphane transforms if exist
        for o in teethMouthList:
            if cmds.objExists(o):
                cmds.delete(o)

    else:
        print '\t No MOUTH meshes to combine'



def RemoveObjectsByWildcard(objectsList, objectType, rootOnly=True):
    print 'RemoveObjectsByWildcard ({0} objects, type={1}, rootOnly={2})'.format(len(objectsList), objectType, rootOnly)

    for o in objectsList:
        result = cmds.ls(objectsList, type=objectType, objectsOnly=True, long=True) or []
        print '\tWildcard "{0}" found {1} object'.format(o, len(result))
        for r in result:
            if cmds.objExists(r): #still use prefix
                print '\t\tDeleting object{0}'.format(r)
                cmds.delete(r)

def AddBreastJoints():
    print 'AddBreastJoints()'
    cmds.select(clear=True)
    srcJointslist = ['Pectoral_L', 'Pectoral_R']
    for j in srcJointslist:
        newJointName = j + '_JIGGLE'
        cmds.select(j)
        cmds.joint(name=newJointName)
        cmds.xform(relative=True, translation=[3, 0, 0])
        skinList = cmds.ls(type='skinCluster')
        for skinClusterName in skinList:
            cmds.select(clear=True)
            influences = cmds.skinCluster(skinClusterName, query=True, influence=True)
            if j in influences:
                cmds.skinCluster(skinClusterName, e=True, addInfluence=newJointName, weight=0.0)
                continue
        mayaUtils.TransferJointWeights(j, newJointName)

def AddNippleJoints():
    shape = mayaUtils.FindShapeByMat('Torso')
    newShape = cmds.duplicate(shape)[0]
    newShape = cmds.rename(newShape, 'TEMP_TORSO')
    mayaUtils.DeleteFacesByMat(newShape, ['Torso'], bInvert=True)
    cmds.bakePartialHistory(newShape, preCache=True)

    AddNippleJoint('Nipple_L', 'Pectoral_L_JIGGLE', [0.5732300281524658, 0.5203400254249573], newShape)
    AddNippleJoint('Nipple_R', 'Pectoral_R_JIGGLE', [0.4267699718475342, 0.5203400254249573], newShape)

    cmds.delete(newShape)


def AddNippleJoint(newJointName, parentName, uvPos, referenceShape):
    cmds.select(clear=True)
    cmds.select(parentName)
    newJointName = cmds.joint(name=newJointName)

    f = mayaUtils.UvCoordToWorld(uvPos[0], uvPos[1], referenceShape)
    print [f[0], f[1], f[2]]
    cmds.move(f[0], f[1], f[2], newJointName, absolute=True)


def AddEndJoints():
    cmds.select(clear=True)
    srcJoints = ['HandThumb3_L', 'HandIndex3_L', 'HandMid3_L', 'HandRing3_L', 'HandPinky3_L']
    srcJoints.extend(['HandThumb3_R', 'HandIndex3_R', 'HandMid3_R', 'HandRing3_R', 'HandPinky3_R'])
    srcJoints.append('Tongue_4')

    for j in srcJoints:
        newJointName = j + '_END'
        relativeTranslation = cmds.xform(j, q=True, relative=True, translation=True)
        cmds.select(j)
        cmds.joint(name=newJointName)
        cmds.xform(relative=True, translation=relativeTranslation)
        print 'Created end joint {0} from {1} with offset {2}'.format(newJointName, j, relativeTranslation)


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

def GetRenamingDict():
    dictionary = {
        'hip': 'Hips',
        'abdomenLower': 'Spine_1',
        'abdomenUpper': 'Spine_2',
        'chestLower': 'Spine_3',
        'chestUpper': 'Spine_4',

        'neckLower': 'Neck_1',
        'neckUpper': 'Neck_2',
        'head': 'Head',

        'lPectoral': 'Pectoral_L',
        'rPectoral': 'Pectoral_R',
        # Arm Left
        'lCollar': 'Clavicle_L',
        'lShldrBend': 'Arm_L',
        'lShldrTwist': 'Arm_L_TWIST',

        'lForearmBend': 'ForeArm_L',
        'lForearmTwist': 'ForeArm_L_TWIST',
        'lHand': 'Hand_L',

        'lThumb1': 'HandThumb1_L',
        'lThumb2': 'HandThumb2_L',
        'lThumb3': 'HandThumb3_L',

        'lCarpal1': 'HandIndex0_L',
        'lIndex1': 'HandIndex1_L',
        'lIndex2': 'HandIndex2_L',
        'lIndex3': 'HandIndex3_L',

        'lCarpal2': 'HandMid0_L',
        'lMid1': 'HandMid1_L',
        'lMid2': 'HandMid2_L',
        'lMid3': 'HandMid3_L',

        'lCarpal3': 'HandRing0_L',
        'lRing1': 'HandRing1_L',
        'lRing2': 'HandRing2_L',
        'lRing3': 'HandRing3_L',

        'lCarpal4': 'HandPinky0_L',
        'lPinky1': 'HandPinky1_L',
        'lPinky2': 'HandPinky2_L',
        'lPinky3': 'HandPinky3_L',

        # Arm Right
        'rCollar': 'Clavicle_R',
        'rShldrBend': 'Arm_R',
        'rShldrTwist': 'Arm_R_TWIST',

        'rForearmBend': 'ForeArm_R',
        'rForearmTwist': 'ForeArm_R_TWIST',
        'rHand': 'Hand_R',

        'rThumb1': 'HandThumb1_R',
        'rThumb2': 'HandThumb2_R',
        'rThumb3': 'HandThumb3_R',

        'rCarpal1': 'HandIndex0_R',
        'rIndex1': 'HandIndex1_R',
        'rIndex2': 'HandIndex2_R',
        'rIndex3': 'HandIndex3_R',

        'rCarpal2': 'HandMid0_R',
        'rMid1': 'HandMid1_R',
        'rMid2': 'HandMid2_R',
        'rMid3': 'HandMid3_R',

        'rCarpal3': 'HandRing0_R',
        'rRing1': 'HandRing1_R',
        'rRing2': 'HandRing2_R',
        'rRing3': 'HandRing3_R',

        'rCarpal4': 'HandPinky0_R',
        'rPinky1': 'HandPinky1_R',
        'rPinky2': 'HandPinky2_R',
        'rPinky3': 'HandPinky3_R',

        # Leg Left
        'lThighBend': 'UpLeg_L',
        'lThighTwist': 'UpLeg_L_TWIST',
        'lShin': 'Leg_L',
        'lFoot': 'Foot_L',
        #rename'lMetatarsals': 'Metatarsals_L',
        'lToe': 'Toe_L',

        # Leg Right
        'rThighBend': 'UpLeg_R',
        'rThighTwist': 'UpLeg_R_TWIST',
        'rShin': 'Leg_R',
        'rFoot': 'Foot_R',
        #rename'rMetatarsals': 'Metatarsals_R',
        'rToe': 'Toe_R',

        # Face
        'lEye': 'Eye_L',
        'rEye': 'Eye_R',
        'lEar': 'Ear_L',
        'rEar': 'Ear_R',
        'upperTeeth': 'UpperTeeth',
        'lowerJaw': 'LowerJaw',
        'lowerTeeth': 'LowerTeeth',
        'tongue01': 'Tongue_1',
        'tongue02': 'Tongue_2',
        'tongue03': 'Tongue_3',
        'tongue04': 'Tongue_4',

        'lowerFaceRig': 'LowerFaceRig',
        'upperFaceRig': 'UpperFaceRig',
        # Root
        'Genesis8Female': 'Root'}
    return dictionary

def RenameChildren(name):
    print 'Rename Children for {0}'.format(name)
    children = cmds.listRelatives(name)
    for child in children:
        if child[0] == 'r':
            mayaUtils.RenameJoint(child, child[1:] + '_R')
        elif child[0] == 'l':
            mayaUtils.RenameJoint(child, child[1:] + '_L')


def RenameSkeletonJoints():
    print 'Renaming skeleton joints'

    renamingDictionary = GetRenamingDict()

    for oldName, newName in renamingDictionary.iteritems():
        mayaUtils.RenameJoint(oldName, newName)

    RenameChildren('LowerFaceRig')
    RenameChildren('UpperFaceRig')


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
    mayaUtils.RenameMaterial('HazardEyes', 'Eyes')

    print 'Baking history'
    cmds.bakePartialHistory(shape, prePostDeformers=True)
    if mouthShape:
        cmds.bakePartialHistory(mouthShape, prePostDeformers=True)
    if eyesShape:
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
        #print j
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
    mayaUtils.RotateJoint("DAZ_Root", 00, 0, 0)

    # Spine
    mayaUtils.RotateJoint("DAZ_Hips", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Spine_1", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Spine_2", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Spine_3", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Spine_4", 90, 0, 90)

    mayaUtils.RotateJoint("DAZ_Pectoral_L", 0, -90, 0)
    mayaUtils.RotateJoint("DAZ_Pectoral_R", 0, -90, 0)

    mayaUtils.RotateJoint("DAZ_Neck_1", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Neck_2", 90, 0, 90)
    mayaUtils.RotateJoint("DAZ_Head", 90, 0, 90)

    # Leg Left
    mayaUtils.RotateJoint("DAZ_UpLeg_L", 90, 0, -90)
    mayaUtils.RotateJoint("DAZ_UpLeg_L_TWIST", 90, 0, -90)
    mayaUtils.RotateJoint("DAZ_Leg_L", 90, 0, -90)
    # copy rotation from Leg
    cmds.xform('DAZ_Foot_L', absolute=True, rotation=cmds.xform('DAZ_Leg_L', q=True, absolute=True, rotation=True))
    mayaUtils.RotateJoint("DAZ_Toe_L", 0, -90, 0)

    # Leg Right
    mayaUtils.RotateJoint("DAZ_UpLeg_R", 90, 0, -90)
    mayaUtils.RotateJoint("DAZ_UpLeg_R_TWIST", 90, 0, -90)
    mayaUtils.RotateJoint("DAZ_Leg_R", 90, 0, -90)
    # copy rotation from Leg
    cmds.xform('DAZ_Foot_R', absolute=True, rotation=cmds.xform('DAZ_Leg_R', q=True, absolute=True, rotation=True))
    mayaUtils.RotateJoint("DAZ_Toe_R", 0, -90, 0)

    # Arm Left

    mayaUtils.RotateJoint("DAZ_Clavicle_L", 90)
    mayaUtils.RotateJoint("DAZ_Arm_L", 90)
    mayaUtils.RotateJoint("DAZ_Arm_L_TWIST", 90)
    mayaUtils.RotateJoint("DAZ_ForeArm_L", 90)
    mayaUtils.RotateJoint("DAZ_ForeArm_L_TWIST", 90)
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
    mayaUtils.RotateJoint("DAZ_Arm_R", -90, 180)
    mayaUtils.RotateJoint("DAZ_Arm_R_TWIST", -90, 180)
    mayaUtils.RotateJoint("DAZ_ForeArm_R", -90, 180)
    mayaUtils.RotateJoint("DAZ_ForeArm_R_TWIST", -90, 180)
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

    jointsList = cmds.listRelatives(oldSkeletonRoot, allDescendents=True, type="joint")#Root is already unparrented, we dont need it

    for j in jointsList:
        parent = cmds.listRelatives(j, parent=True, type='joint')
        if not parent:
            continue
        oldName = cmds.joint(j, q=True, name=True)
        oldParentName = cmds.joint(parent, q=True, name=True)
        newName = newJointsPrefix + oldName
        newParentName = newJointsPrefix + oldParentName
        if oldName == 'UpLeg_L' or oldName == 'UpLeg_R': #connect legs to Hips, not to pelvis
            newParentName = newJointsPrefix + 'Hips'
        elif oldName == 'Toe_L':
            newParentName = newJointsPrefix + 'Foot_L' #not to lMetatarsals
        elif oldName == 'Toe_R':
            newParentName = newJointsPrefix + 'Foot_R' #not to rMetatarsals

        #print newParentName
        cmds.parent(newName, newParentName)

        print 'Parenting {0} to {1}'.format(newName, newParentName)

    twistJoints = cmds.ls(newJointsPrefix+'*_TWIST')
    for j in twistJoints:
        parent = cmds.listRelatives(j, parent=True)
        children = cmds.listRelatives(j)
        if children is not None:
            for child in children:
                print 'Reparenting twist joint {0} child {1} to {2}'.format(j, child, parent[0])
                cmds.parent(child, parent[0])

    #Remove unused bones if exists (for animation retarheting mode)
    unusedList = ['pelvis', 'lMetatarsals', 'rMetatarsals']
    for j in unusedList:
        if cmds.objExists(newJointsPrefix + j): #still use prefix
            cmds.delete(newJointsPrefix + j)
            print 'Deleting joint {0}'.format(newJointsPrefix + j)

    orphanParentsList = ['Toe_L', 'Toe_R']
    for j in orphanParentsList:
        if cmds.objExists(newJointsPrefix + j): #still use prefix
            childrenList = cmds.listRelatives(newJointsPrefix + j, allDescendents=True) or []
            for c in childrenList:
                cmds.delete(c)
                print 'Deleting {0} - child joint of {1} '.format(c, newJointsPrefix + j)


def SetJointsVisualProperties():
    joints = cmds.ls('*_TWIST')
    joints += cmds.ls('*_BEND')
    for j in joints:
        cmds.setAttr(j + '.radius', 3)

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
    MakeBendCorrectiveJoint('Knee_L_BEND', 'Leg_L', 'UpLeg_L', ['UpLeg_L_TWIST', 'Leg_L'])
    MakeBendCorrectiveJoint('Knee_R_BEND', 'Leg_R', 'UpLeg_R', ['UpLeg_R_TWIST', 'Leg_R'])

    MakeBendCorrectiveJoint('Butt_L_BEND', 'UpLeg_L', 'Hips')
    MakeBendCorrectiveJoint('Butt_R_BEND', 'UpLeg_R', 'Hips')

    MakeBendCorrectiveJoint('Shoulder_L_BEND', 'Arm_L', 'Clavicle_L')
    MakeBendCorrectiveJoint('Shoulder_R_BEND', 'Arm_R', 'Clavicle_R')

    MakeBendCorrectiveJoint('Elbow_L_BEND', 'ForeArm_L', 'Arm_L', ['Arm_L_TWIST', 'ForeArm_L'])
    MakeBendCorrectiveJoint('Elbow_R_BEND', 'ForeArm_R', 'Arm_R', ['Arm_R_TWIST', 'ForeArm_R'])
