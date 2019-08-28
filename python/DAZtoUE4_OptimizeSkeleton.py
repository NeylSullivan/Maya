import maya.cmds as cmds

def RenameSkeletonJoints():
    print 'Renaming skeleton joints'
       
    rename('hip', 'Hips')
    rename('abdomenLower', 'Spine_1')
    rename('abdomenUpper', 'Spine_2')
    rename('chestLower', 'Spine_3')
    rename('chestUpper', 'Spine_4')

    rename('neckLower', 'Neck_1')
    rename('neckUpper', 'Neck_2')
    rename('head', 'Head')

    rename('lPectoral', 'Pectoral_L')
    rename('rPectoral', 'Pectoral_R')
    #Arm Left
    rename('lCollar', 'Clavicle_L')
    rename('lShldrBend', 'ArmTop_L')
    rename('lShldrTwist', 'ArmBottom_L')

    rename('lForearmBend', 'ForeArmTop_L')
    rename('lForearmTwist', 'ForeArmBottom_L')
    rename('lHand', 'Hand_L')

    rename('lThumb1', 'HandThumb1_L')
    rename('lThumb2', 'HandThumb2_L')
    rename('lThumb3', 'HandThumb3_L')

    rename('lCarpal1', 'HandIndex0_L')
    rename('lIndex1', 'HandIndex1_L')
    rename('lIndex2', 'HandIndex2_L')
    rename('lIndex3', 'HandIndex3_L')

    rename('lCarpal2', 'HandMid0_L')
    rename('lMid1', 'HandMid1_L')
    rename('lMid2', 'HandMid2_L')
    rename('lMid3', 'HandMid3_L')

    rename('lCarpal3', 'HandRing0_L')
    rename('lRing1', 'HandRing1_L')
    rename('lRing2', 'HandRing2_L')
    rename('lRing3', 'HandRing3_L')

    rename('lCarpal4', 'HandPinky0_L')
    rename('lPinky1', 'HandPinky1_L')
    rename('lPinky2', 'HandPinky2_L')
    rename('lPinky3', 'HandPinky3_L')

    #Arm Right
    rename('rCollar', 'Clavicle_R')
    rename('rShldrBend', 'ArmTop_R')
    rename('rShldrTwist', 'ArmBottom_R')

    rename('rForearmBend', 'ForeArmTop_R')
    rename('rForearmTwist', 'ForeArmBottom_R')
    rename('rHand', 'Hand_R')

    rename('rThumb1', 'HandThumb1_R')
    rename('rThumb2', 'HandThumb2_R')
    rename('rThumb3', 'HandThumb3_R')

    rename('rCarpal1', 'HandIndex0_R')
    rename('rIndex1', 'HandIndex1_R')
    rename('rIndex2', 'HandIndex2_R')
    rename('rIndex3', 'HandIndex3_R')

    rename('rCarpal2', 'HandMid0_R')
    rename('rMid1', 'HandMid1_R')
    rename('rMid2', 'HandMid2_R')
    rename('rMid3', 'HandMid3_R')

    rename('rCarpal3', 'HandRing0_R')
    rename('rRing1', 'HandRing1_R')
    rename('rRing2', 'HandRing2_R')
    rename('rRing3', 'HandRing3_R')

    rename('rCarpal4', 'HandPinky0_R')
    rename('rPinky1', 'HandPinky1_R')
    rename('rPinky2', 'HandPinky2_R')
    rename('rPinky3', 'HandPinky3_R')

    #Leg Left
    rename('lThighBend', 'UpLeg_L')
    rename('lThighTwist', 'UpLegTwist_L')
    rename('lShin', 'Leg_L')
    rename('lFoot', 'Foot_L')
    #rename('lMetatarsals', 'Metatarsals_L')
    rename('lToe', 'Toe_L')

    #Leg Right
    rename('rThighBend', 'UpLeg_R')
    rename('rThighTwist', 'UpLegTwist_R')
    rename('rShin', 'Leg_R')
    rename('rFoot', 'Foot_R')
    #rename('rMetatarsals', 'Metatarsals_R')
    rename('rToe', 'Toe_R')


    #Face
    rename('lEye', 'Eye_L')
    rename('rEye', 'Eye_R')
    rename('lEar', 'Ear_L')
    rename('rEar', 'Ear_R')
    rename('upperTeeth', 'UpperTeeth')
    rename('lowerJaw', 'LowerJaw')
    rename('lowerTeeth', 'LowerTeeth')
    rename('tongue01', 'Tongue_1')
    rename('tongue02', 'Tongue_2')
    rename('tongue03', 'Tongue_3')
    rename('tongue04', 'Tongue_4')

    rename('lowerFaceRig', 'LowerFaceRig')
    renameChildren('LowerFaceRig')

    rename('upperFaceRig', 'UpperFaceRig')
    renameChildren('UpperFaceRig')

    #Root
    rename('Genesis8Female', 'Root')

def GetAverageWorldTranslationOfSelected():
    sel = cmds.ls(sl=True, fl=True)
    count = len(sel)
    sums = [0,0,0]
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
    
    print 'Created camera joint FK_CAMERA_SOCKET with world pos {0}'.format(EyesPos)

def AddEndJoints ():
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

def CreateIkJoint( referenceJnt, parentJnt, ikJntName):
    cmds.select(clear=True) 
    print 'Created IK joint "{0}" corresponding to "{1}" parented to "{2}"'.format(ikJntName, referenceJnt, parentJnt)
    cmds.select(referenceJnt)
    cmds.joint(name=ikJntName)
    if not parentJnt==referenceJnt:
        cmds.parent(ikJntName, parentJnt)

def ResetBindPose(sel):
    for each in sel:
        shapes = cmds.listRelatives(each, shapes=True)

        for shape in shapes:
            #get skin cluster
            history = cmds.listHistory(shape, groupLevels=True, pruneDagObjects=True)
            skins = cmds.ls(history, type='skinCluster')

            for skin in skins:
                joints = cmds.skinCluster(skin, query=True, influence=True)

                cmds.setAttr(skin+'.envelope', 0)
                cmds.skinCluster(skin, edit=True, unbindKeepHistory=True)

                #delete bindPose
                dagPose = cmds.dagPose(each, query=True, bindPose=True)
                if dagPose:
                    cmds.delete(dagPose)
                dagPose = cmds.listConnections(skin+'.bindPose', d=False, type='dagPose')
                if dagPose:
                    cmds.delete(dagPose)

                cmds.skinCluster(joints, shape, toSelectedBones=True)
                cmds.setAttr(skin+'.envelope', 1)

def rotate (jointName, x=0, y=0, z=0):
    try:
        cmds.select( jointName )
        cmds.rotate( x, y, z, relative=True, objectSpace=True)
    except Exception:
        print('Это что ещё такое?')

def rename (oldName, newName):
    try:
        cmds.rename(oldName, newName)
    except Exception:
        print('WTF? ' + oldName)

def renameChildren (name):
    children = cmds.listRelatives (name)
    for child in children:
        if child[0] == 'r':
            rename (child, child[1:] + '_R')
        elif child[0] == 'l':
            rename (child, child[1:] + '_L')

def transferJointWeights (oldJointName, newJointName):
    cmds.select(clear=True)
    skinList = cmds.ls(type='skinCluster')
    print('')
    print 'TransferJointWeights: Transfering weights from {0} to {1}'.format(oldJointName, newJointName)
    for skinClusterName in skinList:
        cmds.select(clear=True)
        print 'TransferJointWeights: Processing ' + skinClusterName
        influences = cmds.skinCluster( skinClusterName, query=True, influence=True)
        if oldJointName not in influences:
            print 'TransferJointWeights: ' + skinClusterName + ' is NOT influenced by SOURCE joint ' + oldJointName + ' Skipping...'
            continue
        elif newJointName not in influences:
            print 'TransferJointWeights: ' + skinClusterName + ' is NOT influenced by TARGET joint ' + newJointName + ' Skipping...'
            continue
        else:
            print 'TransferJointWeights: ' + skinClusterName + ' is influenced by joint ' + oldJointName + ' Processing...'

        cmds.skinCluster( skinClusterName, e=True, selectInfluenceVerts=oldJointName)
        sel = cmds.ls( selection=True, flatten=True )
        onlyVertices = cmds.filterExpand(sel, sm=31)
        
        if onlyVertices is None:
            print 'TransferJointWeights: No binded vertices. Skipping...'
        else:
            for v in onlyVertices:
                oldJointWeight = cmds.skinPercent( skinClusterName, v, transform=oldJointName, query=True)
                newJointWeight = cmds.skinPercent( skinClusterName, v, transform=newJointName, query=True)
                finalNewJointWeight = min(1.0, newJointWeight + oldJointWeight)
                
                #print 'TransferJointWeights: Processing vertex {0} with old weight {1} new weight {2}'.format(v, oldJointWeight, finalNewJointWeight)
                #set weight
                cmds.skinPercent(skinClusterName, v, transformValue=[(oldJointName, 0), (newJointName, finalNewJointWeight)])
            
        print 'TransferJointWeights: Removing {0} from influences of {1}'.format(oldJointName, skinClusterName)
        cmds.skinCluster( skinClusterName, e=True, removeInfluence=oldJointName)
    
    print 'TransferJointWeights: Done'
        
     
def DestroyMiddleJoint (jointName):
    print''
    
    if not cmds.objExists(jointName):
        print 'DestroyMiddleJoint: joint {0} is not exist: Aborting'.format(jointName)
        return
    
    print 'DestroyMiddleJoint: Processing joint: ' + jointName
    parent = cmds.listRelatives (jointName, parent=True)
    if parent is None:
        print('DestroyMiddleJoint: Joint parent is None. Aborting')
        return

    print('DestroyMiddleJoint: Joint parent is ' + parent[0])
    transferJointWeights(jointName, parent[0])
    
    children = cmds.listRelatives (jointName)
    if children is not None:
        for child in children:
            print 'DestroyMiddleJoint: parenting {0} to {1}'.format(child, parent[0])
            cmds.parent(child, parent[0])

    print 'DestroyMiddleJoint: unparenting {0}'.format(jointName)
    cmds.parent(jointName, world=True)
    print 'DestroyMiddleJoint: destroying {0}'.format(jointName)
    cmds.delete(jointName)
    
    print 'DestroyMiddleJoint: Done'

def DestroyJointChildren (jointName):
    print''

    if not cmds.objExists(jointName):
        print 'DestroyJointChildren: joint {0} is not exist: Aborting'.format(jointName)
        return
        
    print 'DestroyJointChildren: Processing joint: ' + jointName
    
    children = cmds.listRelatives (jointName, allDescendents=True)
    if children is None:
        print 'DestroyJointChildren: joint {0} does not has children: Aborting'.format(jointName)
        return
        
    for child in children:
        transferJointWeights(child, jointName)

    for child in children:
        print 'DestroyJointChildren: unparenting {0}'.format(child)
        cmds.parent(child, world=True)
        print 'DestroyJointChildren: destroying {0}'.format(child)
        cmds.delete(child)

    print 'DestroyJointChildren: Done'

    
def DuplicateSkeletonJoints():
    print 'Duplicating skeleton'

    jointsList = cmds.ls(type="joint")

    for j in jointsList:
        pos = cmds.joint(j, q=True, absolute=True)
        oldName = cmds.joint(j, q=True, name=True)
        oldOrientation = cmds.joint(j, q=True, orientation=True)

        newName = "DAZ_" + oldName
        
        cmds.select(clear=True) 
        newJoint = cmds.joint(p=pos, name=newName)
        cmds.xform( r=True, ro=oldOrientation )

        
def FixNewJointsOrientation():
    print 'Fixing joint orientation'
        
    #Root
    rotate("DAZ_Root", 90, 0, 90)
        
    #Spine
    rotate("DAZ_Hips", 90, 0, 90)
    rotate("DAZ_Spine_1", 90, 0, 90)
    rotate("DAZ_Spine_2", 90, 0, 90)
    rotate("DAZ_Spine_3", 90, 0, 90)
    rotate("DAZ_Spine_4", 90, 0, 90)

    rotate("DAZ_Pectoral_L", 90, 0, 90)
    rotate("DAZ_Pectoral_R", 90, 0, 90)

    rotate("DAZ_Neck_1", 90, 0, 90)
    rotate("DAZ_Neck_2", 90, 0, 90)
    rotate("DAZ_Head", 90, 0, 90)

    #Leg Left
    rotate("DAZ_UpLeg_L", 90, 0, -90)
    rotate("DAZ_UpLegTwist_L", 90, 0, -90)
    rotate("DAZ_Leg_L", 90, 0, -90)
    #copy rotation from Leg
    cmds.xform( 'DAZ_Foot_L', absolute=True, rotation=cmds.xform( 'DAZ_Leg_L', q=True, absolute=True, rotation=True ) )
    rotate("DAZ_Toe_L", 0, -90, 0)

    #Leg Right
    rotate("DAZ_UpLeg_R", 90, 0, -90)
    rotate("DAZ_UpLegTwist_R", 90, 0, -90)
    rotate("DAZ_Leg_R", 90, 0, -90)
    #copy rotation from Leg
    cmds.xform( 'DAZ_Foot_R', absolute=True, rotation=cmds.xform( 'DAZ_Leg_R', q=True, absolute=True, rotation=True ) )
    rotate("DAZ_Toe_R", 0, -90, 0)

    #Arm Left

    rotate("DAZ_Clavicle_L", 90)
    rotate("DAZ_ArmTop_L", 90)
    rotate("DAZ_ArmBottom_L", 90)
    rotate("DAZ_ForeArmTop_L", 90)
    rotate("DAZ_ForeArmBottom_L", 90)
    rotate("DAZ_Hand_L", 90)

    rotate('DAZ_HandThumb1_L', 180)
    rotate('DAZ_HandThumb2_L', 180)
    rotate('DAZ_HandThumb3_L', 180)

    rotate('DAZ_HandIndex0_L', 90)
    rotate('DAZ_HandIndex1_L', 90)
    rotate('DAZ_HandIndex2_L', 90)
    rotate('DAZ_HandIndex3_L', 90)

    rotate('DAZ_HandMid0_L', 90)
    rotate('DAZ_HandMid1_L', 90)
    rotate('DAZ_HandMid2_L', 90)
    rotate('DAZ_HandMid3_L', 90)

    rotate('DAZ_HandRing0_L', 90)
    rotate('DAZ_HandRing1_L', 90)
    rotate('DAZ_HandRing2_L', 90)
    rotate('DAZ_HandRing3_L', 90)

    rotate('DAZ_HandPinky0_L', 90)
    rotate('DAZ_HandPinky1_L', 90)
    rotate('DAZ_HandPinky2_L', 90)
    rotate('DAZ_HandPinky3_L', 90)

    #Arm Right

    rotate("DAZ_Clavicle_R",  -90, 180)
    rotate("DAZ_ArmTop_R",  -90, 180)
    rotate("DAZ_ArmBottom_R",  -90, 180)
    rotate("DAZ_ForeArmTop_R",  -90, 180)
    rotate("DAZ_ForeArmBottom_R",  -90, 180)
    rotate("DAZ_Hand_R",  -90, 180)

    rotate('DAZ_HandThumb1_R',  -180, 180)
    rotate('DAZ_HandThumb2_R',  -180, 180)
    rotate('DAZ_HandThumb3_R',  -180, 180)

    rotate('DAZ_HandIndex0_R',  -90, 180)
    rotate('DAZ_HandIndex1_R',  -90, 180)
    rotate('DAZ_HandIndex2_R',  -90, 180)
    rotate('DAZ_HandIndex3_R',  -90, 180)

    rotate('DAZ_HandMid0_R',  -90, 180)
    rotate('DAZ_HandMid1_R',  -90, 180)
    rotate('DAZ_HandMid2_R',  -90, 180)
    rotate('DAZ_HandMid3_R',  -90, 180)

    rotate('DAZ_HandRing0_R',  -90, 180)
    rotate('DAZ_HandRing1_R',  -90, 180)
    rotate('DAZ_HandRing2_R',  -90, 180)
    rotate('DAZ_HandRing3_R',  -90, 180)

    rotate('DAZ_HandPinky0_R',  -90, 180)
    rotate('DAZ_HandPinky1_R',  -90, 180)
    rotate('DAZ_HandPinky2_R',  -90, 180)
    rotate('DAZ_HandPinky3_R',  -90, 180)

    #facial rig
    rotate("DAZ_Tongue_1", 0, -90, 0)
    rotate("DAZ_Tongue_2", 0, -90, 0)
    rotate("DAZ_Tongue_3", 0, -90, 0)
    rotate("DAZ_Tongue_4", 0, -90, 0)

    children = cmds.listRelatives ('Head', allDescendents=True) #selecting original joints

    for child in children:
        if child.startswith('Tongue_'):
            continue #skip
        rotate('DAZ_' + child, 90, 0, 90) #but rotating skeleton copy


    cmds.select(clear=True) 

def RecreateHierarchy():
    print 'Recreating hierarchy'

    jointsList = cmds.listRelatives ('Root', allDescendents=True, type="joint")
    #jointsList.append ('Root') #Root is already unparrented
        
    for j in jointsList:
        parent = cmds.listRelatives( j, parent=True, type='joint' )
        if not parent:
            continue
        oldName = cmds.joint(j, q=True, name=True)
        oldParentName = cmds.joint(parent, q=True, name=True)
        
        newName = "DAZ_" + oldName
        newParentName = "DAZ_" + oldParentName
        #print newParentName
        cmds.parent(newName, newParentName)
    
def RenameNewSkeleton():
    print 'Renaming new skeleton'
    newRoot = cmds.ls('DAZ_Root', type="joint")
    newJoints = cmds.listRelatives( newRoot, allDescendents=True)
    newJoints.append(newRoot[0])

    for j in newJoints:
        newName = j[4:]
        print newName
        rename(j, newName)

#tempList = cmds.ls('DAZ_*', type="joint")
#cmds.delete(tempList)
    
DestroyMiddleJoint ('lMetatarsals')
DestroyMiddleJoint ('rMetatarsals')
DestroyMiddleJoint ('pelvis')
DestroyJointChildren ('lToe')
DestroyJointChildren ('rToe')
DestroyJointChildren ('lSmallToe2_2')

#set skinning type to linear
skinList = cmds.ls(type='skinCluster')
for s in skinList:
   cmds.skinCluster(s, e=True, skinMethod=0)

RenameSkeletonJoints()

DuplicateSkeletonJoints()

FixNewJointsOrientation()

RecreateHierarchy()

print 'Parenting geometry to world'

skinList = cmds.ls(type='skinCluster')
meshes = set(sum([cmds.skinCluster(c, q=1, g=1) for c in skinList], []))
for mesh in meshes:
    transformList = cmds.listRelatives(mesh, parent=True)
    for tf in transformList:
        if cmds.listRelatives( tf, parent=True):
            cmds.parent(tf, world=True)
            
oldRoot = cmds.ls('Root', type="joint")
oldJoints = cmds.listRelatives( oldRoot, allDescendents=True)
oldJoints.append(oldRoot[0])
skinList = cmds.ls(type='skinCluster')

print 'Resetting bind pose'
meshes = set(sum([cmds.skinCluster(c, q=1, g=1) for c in skinList], []))
for mesh in meshes:
    transformList = cmds.listRelatives(mesh, parent=True)
    ResetBindPose(transformList)

print 'Resetting bind pose: Done'


for oldJoint in oldJoints:
    newJoint = "DAZ_" + oldJoint
    if not cmds.objExists(newJoint):
        print "ERROR corresponding joint {0} not exist".format(newJoint)
        continue
        
    for skinClusterName in skinList:
        cmds.select(clear=True)
        
        print 'TransferJointWeights: Processing ' + skinClusterName
        influences = cmds.skinCluster( skinClusterName, query=True, influence=True)
        if oldJoint not in influences:
            print 'TransferJointWeights: ' + skinClusterName + ' is NOT influenced by SOURCE joint ' + oldJoint + ' Skipping...'
            continue
        else:
            print 'TransferJointWeights: ' + skinClusterName + ' is influenced by joint ' + oldJoint + ' Processing...'

        if newJoint not in influences:
            cmds.skinCluster( skinClusterName, e=True, addInfluence=newJoint, weight = 0.0)
        

        cmds.skinCluster( skinClusterName, e=True, selectInfluenceVerts=oldJoint)
        sel = cmds.ls( selection=True, flatten=True )
        onlyVertices = cmds.filterExpand(sel, sm=31)
        
        if onlyVertices is None:
            print 'TransferJointWeights: No binded vertices. Skipping...'
        else:
            for v in onlyVertices:
                oldJointWeight = cmds.skinPercent( skinClusterName, v, transform=oldJoint, query=True)
                newJointWeight = cmds.skinPercent( skinClusterName, v, transform=newJoint, query=True)
                finalNewJointWeight = min(1.0, newJointWeight + oldJointWeight)
                cmds.skinPercent(skinClusterName, v, transformValue=[(oldJoint, 0), (newJoint, finalNewJointWeight)])
            
        print 'TransferJointWeights: Removing {0} from influences of {1}'.format(oldJoint, skinClusterName)
        cmds.skinCluster( skinClusterName, e=True, removeInfluence=oldJoint)

print 'TransferJointWeights: Done'
print 'Deleting old skeleton'
cmds.delete(oldJoints)


RenameNewSkeleton()

AddEndJoints()
AddCameraJoint()

CreateIkJoint('FK_CAMERA_SOCKET', 'Root', 'IK_CAMERA')
CreateIkJoint('Root', 'Root', 'IK_Foot_Root')
CreateIkJoint('Foot_R', 'IK_Foot_Root', 'IK_Foot_R')
CreateIkJoint('Foot_L', 'IK_Foot_Root', 'IK_Foot_L')

CreateIkJoint('Root', 'Root', 'IK_Hands_Root')
CreateIkJoint('Hand_R', 'IK_Hands_Root', 'IK_Weapon_Root')
CreateIkJoint('Hand_R', 'IK_Weapon_Root', 'IK_Hand_R')
CreateIkJoint('Hand_L', 'IK_Weapon_Root', 'IK_Hand_L')

print 'All tasks DONE'