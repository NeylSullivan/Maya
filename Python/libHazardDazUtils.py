import maya.cmds as cmds
import os
import libHazardMathUtils as hazMath
import libHazardMayaUtils as mayaUtils
import libHazardSelectionUtils as selUtils
import libHazardMorphTargetProcessing as hazMtp

reload(hazMath)
reload(mayaUtils)
reload(selUtils)
reload(hazMtp)

# konstants
#
k_LEFT_NIPPLE_UV = [0.7961298823356628, 0.8489649891853333]
k_RIGHT_NIPPLE_UV = [0.7028849720954895, 0.8489649891853333]

def GetSharedResourcesPath():
    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    return os.path.join(parentDir, 'Resources')

def TryLoadExternalMorphTargets():
    with mayaUtils.DebugTimer('TryLoadExternalMorphTargets'):
        mainMesh = mayaUtils.FindMeshByWildcard('Genesis8Female*', checkForMatWithName='Torso')

        if mainMesh is None:
            print 'Error! Can`t find body(Torso) mesh'
            return

        subDirs = [dI for dI in os.listdir(hazMtp.GetIntermediateFullPath()) if os.path.isdir(os.path.join(hazMtp.GetIntermediateFullPath(), dI))]

        blendShapeDeformer = None

        PREFIXES = ('MT_', 'MTD_', 'MTB_', 'MTTD_', 'MTTB_')

        for subDir in subDirs:

            if not subDir.startswith(PREFIXES):
                print 'SKIPPING directory {}. Reason - unresolved name (should starts with \'{}\')'.format(subDir, PREFIXES)
                continue

            fullSubdirPath = os.path.join(hazMtp.GetIntermediateFullPath(), subDir)
            morphMeshFile = os.path.join(fullSubdirPath, hazMtp.PROCESSED_BASE_MESH_NAME + '.obj')
            morphMeshExist = os.path.exists(morphMeshFile)
            print 'Dir: {} SubD mesh: {} Exist: {}'.format(subDir, morphMeshFile, morphMeshExist)
            if not morphMeshExist:
                print 'SKIPPING...'
                continue

            morphMesh = cmds.file(morphMeshFile, i=True, returnNewNodes=True)[0]
            morphMesh = cmds.rename(morphMesh, subDir) # name new blendshape as it folder
            cmds.xform(morphMesh, absolute=True, translation=[0, 0, 100])

            blendShapeDeformer = mayaUtils.GetBlendShape(mainMesh)

            if blendShapeDeformer is None:
                blendShapeDeformer = cmds.blendShape(mainMesh)[0]

            weightsCount = cmds.blendShape(blendShapeDeformer, q=True, weightCount=True) # Index for next added blendshape
            cmds.blendShape(blendShapeDeformer, edit=True, target=(mainMesh, weightsCount, morphMesh, 1.0))
            cmds.delete(morphMesh)



def TryLoadExternalBaseMeshBodyMorph():
    with mayaUtils.DebugTimer('TryLoadExternalBaseMeshBodyMorph'):
        mainMesh = mayaUtils.FindMeshByWildcard('Genesis8Female*', checkForMatWithName='Torso')

        if mainMesh is None:
            print 'Error! Can`t find body(Torso) mesh'
            return
        #Mesh unskinned on this stage so we can safely delete all history
        cmds.delete(mainMesh, constructionHistory=True)

        bodyMorphFile = os.path.join(hazMtp.GetIntermediateFullPath(), hazMtp.PROCESSED_BASE_MESH_NAME + '.obj')
        bodyMorphExist = os.path.exists(bodyMorphFile)
        print 'Body morph file: {} Exist: {}'.format(bodyMorphFile, bodyMorphExist)
        if not bodyMorphExist:
            print 'ABORTED: no body morph file found'
            return

        morphMesh = cmds.file(bodyMorphFile, i=True, returnNewNodes=True)[0]
        morphMesh = cmds.rename(morphMesh, 'BodyMorph')
        cmds.xform(morphMesh, absolute=True, translation=[0, 0, 100])

        bs = cmds.blendShape([morphMesh, mainMesh])
        cmds.blendShape(bs, edit=True, weight=[0, 1.0])

        cmds.delete(mainMesh, constructionHistory=True)
        cmds.delete(morphMesh)

def TryLoadExternalUVs():
    with mayaUtils.DebugTimer('TryLoadExternalUVs'):
        mainMesh = mayaUtils.FindMeshByWildcard('Genesis8Female*', checkForMatWithName='Torso')

        if mainMesh is None:
            print 'Error! Can`t find body(Torso) mesh'
            return

        cmds.delete(mainMesh, constructionHistory=True)

        BASE_MESH_WITH_UV_NAME = 'BaseFemale_UV1'

        uvMeshFile = os.path.join(hazMtp.GetIntermediateFullPath(), BASE_MESH_WITH_UV_NAME + '.obj')
        uvMeshFileExist = os.path.exists(uvMeshFile)

        print 'UV mesh file: {} Exist: {}'.format(uvMeshFile, uvMeshFileExist)
        if not uvMeshFileExist:
            print 'ABORTED: no uv mesh file found'
            return

        uvMesh = cmds.file(uvMeshFile, i=True, returnNewNodes=True)[0]
        uvMesh = cmds.rename(uvMesh, 'UV_Source')
        cmds.xform(uvMesh, absolute=True, translation=[0, 0, 100])

        cmds.polyUVSet(mainMesh, create=True, uvSet='Tesselation_UV')
        #transferAttributes -transferPositions 0 -transferNormals 0 -transferUVs 1 -sourceUvSet "map1" -targetUvSet "Tesselation_UV" -transferColors 0 -sampleSpace 5 -sourceUvSpace "map1" -targetUvSpace "Tesselation_UV" -searchMethod 3-flipUVs 0 -colorBorders 0
        cmds.transferAttributes(uvMesh, mainMesh, transferPositions=0, transferNormals=0, transferUVs=1, sourceUvSet='map1', targetUvSet='Tesselation_UV', sampleSpace=5)
        cmds.delete(mainMesh, constructionHistory=True)
        cmds.delete(uvMesh)


def PostprocessGenitaliaObject(genitaliaMeshWildcard):
    with mayaUtils.DebugTimer('PostprocessGenitaliaObject(genitaliaMeshWildcard={0})'.format(genitaliaMeshWildcard)):
        genitaliaMesh = mayaUtils.FindMeshByWildcard(genitaliaMeshWildcard)
        if not genitaliaMesh:
            print 'Genitalia mesh not found. Aborted'
            return

        print 'Processing {0}'.format(genitaliaMesh)

        genitaliaMesh = cmds.rename(genitaliaMesh, 'FemaleGenitalia') #rename to proper name

        #replace material with original torso mat
        facesWithTorsoMat = mayaUtils.GetFacesByMatsWildcard(genitaliaMesh, 'Torso*')
        mayaUtils.AssignObjectListToShader(facesWithTorsoMat, 'Body') #use new material name
        # mayaUtils.ArrangeUVByMat(genitaliaMesh, 'Body', su=0.5, sv=0.5, u=0.5, v=0.5)
        mayaUtils.AppendShadingGroupByMat(genitaliaMesh, 'Anus', 'Vagina')
        mayaUtils.RenameMaterial('Anus', 'BodyGenitalia')
        cmds.bakePartialHistory(genitaliaMesh, prePostDeformers=True)

        bodyMesh = mayaUtils.FindMeshByWildcard('FemaleBody'+'*', checkForMatWithName='Body')

        if not bodyMesh:
            print '{0} mesh not found. Aborted'
            return

        cmds.select(clear=True)
        borderVertsList = mayaUtils.GetBorderVertices(genitaliaMesh)
        borderVertsList = cmds.filterExpand(borderVertsList, sm=31, expand=True)

        bodySkinCluster = mayaUtils.GetSkinCluster(bodyMesh)
        genitaliaSkinCluster = mayaUtils.GetSkinCluster(genitaliaMesh)


        #transfer attributes manually
        for v in borderVertsList:
            pos = cmds.pointPosition(v, world=True)
            #print pos
            closestVert = mayaUtils.GetClosestVertex(bodyMesh, pos)
            closestVertPos = cmds.xform(closestVert, t=True, ws=True, q=True)
            closestVertNormal = cmds.polyNormalPerVertex(closestVert, query=True, xyz=True)

            # set position
            cmds.move(closestVertPos[0], closestVertPos[1], closestVertPos[2], v, absolute=True, worldSpace=True)
            # set normal
            cmds.polyNormalPerVertex(v, xyz=(closestVertNormal[0], closestVertNormal[1], closestVertNormal[2]))

            referenceVertInfluences = cmds.skinPercent(bodySkinCluster, closestVert, query=True, transform=None, ignoreBelow=0.00001)

            targetInfluences = cmds.skinCluster(genitaliaSkinCluster, query=True, influence=True)

            targetTransformValues = []

            for i in referenceVertInfluences:
                if i not in targetInfluences:
                    cmds.skinCluster(genitaliaSkinCluster, e=True, addInfluence=i, weight=0.0)
                    #print i
                referenceInfluenceValuePerVertex = cmds.skinPercent(bodySkinCluster, closestVert, query=True, transform=i, transformValue=True)
                targetTransformValues.append((i, referenceInfluenceValuePerVertex))

            #print targetTransformValues

            # set weight
            cmds.skinPercent(genitaliaSkinCluster, v, transformValue=targetTransformValues)

        cmds.bakePartialHistory(genitaliaMesh, prePostDeformers=True)


def DestroyUnusedJoints(pbDestroyToes):
    with mayaUtils.DebugTimer('DestroyUnusedJoints'):
        #mayaUtils.CleanUnusedInfluensesOnAllSkinClusters()
        mayaUtils.DestroyMiddleJoint('lMetatarsals')
        mayaUtils.DestroyMiddleJoint('rMetatarsals')
        #to match EPIC skeleton
        mayaUtils.DestroyMiddleJoint('pelvis')
        #spine1
        mayaUtils.TransferJointWeights('abdomenLower', 'abdomenUpper', 0.33)#transfer 33 persent to child
        mayaUtils.DestroyMiddleJoint('abdomenLower') # and 67 percent to parent then delete
        #Neck
        mayaUtils.TransferJointWeights('neckUpper', 'head', 0.33)#transfer 33 persent to child
        mayaUtils.DestroyMiddleJoint('neckUpper')
        
        mayaUtils.DestroyMiddleJoint('lCarpal1')
        mayaUtils.DestroyMiddleJoint('lCarpal2')
        mayaUtils.DestroyMiddleJoint('lCarpal3')
        mayaUtils.DestroyMiddleJoint('lCarpal4')
        mayaUtils.DestroyMiddleJoint('rCarpal1')
        mayaUtils.DestroyMiddleJoint('rCarpal2')
        mayaUtils.DestroyMiddleJoint('rCarpal3')
        mayaUtils.DestroyMiddleJoint('rCarpal4')
        #end to match EPIC skeleton
        if pbDestroyToes:
            mayaUtils.DestroyJointChildren('lToe')
            mayaUtils.DestroyJointChildren('rToe')


def MaskShellsEdgesForTesselation(shape, pUVtile):
    cmds.select(clear=True)
    print 'MaskShellsEdgesForTesselation shape: {0}, pUVtile: {1}'.format(shape, pUVtile)
    matched_faces = selUtils.GetFacesInUTile(shape, pUVtile)
    borderVerts = cmds.polyListComponentConversion(matched_faces, ff=True, tv=True, bo=True)
    borderFaces = cmds.polyListComponentConversion(borderVerts, fv=True, tf=True) #sort of grow extrude
    borderVerts = cmds.polyListComponentConversion(borderFaces, ff=True, tv=True) #we need wider row to mask tessellation in ue4
    #print borderVerts
    if borderVerts:
        mayaUtils.SetVertexColors(borderVerts, (0, 1, 1))
        #cmds.polyColorPerVertex(borderVerts, colorR=0.0, notUndoable=True) #fill verts red=0 color
    else:
        print 'No border verts detected. Skipping polyColorPerVertex'
    cmds.select(clear=True)

def SetVertexColorForBorderVertices():
    with mayaUtils.DebugTimer('SetVertexColorForBorderVertices'):
        skinList = cmds.ls(type='skinCluster')
        cmds.select(clear=True)

        for s in skinList:
            cmds.select(clear=True)
            mesh = mayaUtils.GetMeshFromSkinCluster(s)
            cmds.select(mesh)
            cmds.selectType(polymeshFace=True)
            cmds.polySelectConstraint(mode=3, type=8, where=1) # to get border vertices
            borderVerts = cmds.polyListComponentConversion(tv=True)
            cmds.polySelectConstraint(mode=0, sh=0, bo=0)
            cmds.select(clear=True)

            allVerts = cmds.polyListComponentConversion(mesh, tv=True)
            mayaUtils.SetVertexColors(allVerts, (1, 1, 1))
            mayaUtils.SetVertexColors(borderVerts, (0, 1, 1))

        cmds.select(clear=True)

        shape = mayaUtils.FindMeshByWildcard('FemaleBody*', checkForMatWithName='Body') #new name is 'Body'
        if shape:
            MaskShellsEdgesForTesselation(shape, 0)
            MaskShellsEdgesForTesselation(shape, 1)
            MaskShellsEdgesForTesselation(shape, 2)
            MaskShellsEdgesForTesselation(shape, 3)
            MaskShellsEdgesForTesselation(shape, 4)

def CollapseUVTiles():
    cmds.select(clear=True)
    shape = mayaUtils.FindMeshByWildcard('FemaleBody*', checkForMatWithName='Body') #new name is 'Body'
    if shape:
        #CollapseUVTile(shape, 0)
        CollapseUVTile(shape, 1)
        CollapseUVTile(shape, 2)
        CollapseUVTile(shape, 3)
        CollapseUVTile(shape, 4)

def CollapseUVTile(shape, pUVtile):
    cmds.select(clear=True)
    print 'CollapseUVTile shape: {0}, pUVtile: {1}'.format(shape, pUVtile)
    matched_faces = selUtils.GetFacesInUTile(shape, pUVtile)
    cmds.polyEditUV(matched_faces, relative=True, uValue=(-1.0*pUVtile))
    cmds.select(clear=True)

def RenameAndCombineMeshes():
    with mayaUtils.DebugTimer('RenameAndCombineMeshes'):
        #Main
        bodyList = cmds.ls('Genesis8FemaleFBX*Shape', type='transform', objectsOnly=True, long=True)
        if bodyList:
            cmds.rename(bodyList[0], 'FemaleBody')

        #
        #EYES
        #
        eyesList = cmds.ls('*Eyes', type='transform', objectsOnly=True, long=True)

        if eyesList and len(eyesList) > 1:
            print '\tCombining {0}'.format(eyesList)
            cmds.polyUniteSkinned(eyesList, ch=False)
            cmds.rename('FemaleEyes')
            cmds.select(clear=True)
            #clear orphane transforms if exist
            for o in eyesList:
                if cmds.objExists(o):
                    cmds.delete(o)
        elif eyesList and len(eyesList) == 1:
            cmds.rename(eyesList[0], 'FemaleEyes')
            print '\t Renaming SINGLE EYES object'
        else:
            print '\t No EYES meshes to combine'

        #Main
        eyelashesList = cmds.ls('*Eyelashes*Shape', type='transform', objectsOnly=True, long=True)
        if eyelashesList:
            cmds.rename(eyelashesList[0], 'FemaleEyelashes')


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
    with mayaUtils.DebugTimer('AddBreastJoints'):
        cmds.select(clear=True)
        srcJointslist = ['breast_l', 'breast_r']
        for j in srcJointslist:
            newJointName = j[:-2] + '_jiggle_' + j[-1]
            cmds.select(j)
            cmds.joint(name=newJointName)
            cmds.xform(relative=True, translation=[3, 0, 0])

        shape = mayaUtils.FindShapeByMat('Torso')#temp shape for finding nipples coordinates

        AddNippleJointAndRealighnBreast('nipple_l', 'breast_jiggle_l', k_LEFT_NIPPLE_UV, shape)
        AddNippleJointAndRealighnBreast('nipple_r', 'breast_jiggle_r', k_RIGHT_NIPPLE_UV, shape)

        #cmds.delete(tempShape)

        #transfer weights to new jiggle joints
        for j in srcJointslist:
            newJointName = j[:-2] + '_jiggle_' + j[-1]
            mayaUtils.TransferJointWeights(j, newJointName)

def ReplaceEyesWithExternalMeshes():
    oldEyes = mayaUtils.FindMeshByWildcard('FemaleEyes')
    jointLeft = cmds.ls('eye_l', type='joint')[0]
    jointRight = cmds.ls('eye_r', type='joint')[0]
    print oldEyes
    print jointLeft
    print jointRight

    #get old eyes mesh vertical (Y) size
    oldSizeY = mayaUtils.GetBoundingBox(oldEyes)[1]
    print oldSizeY
    cmds.delete(oldEyes)
    mayaUtils.CleanUnusedMaterials()

    print GetSharedResourcesPath()

    leftEyeFilePath = os.path.join(GetSharedResourcesPath(), 'Eye_Left.obj')
    print leftEyeFilePath
    leftEyeMesh = cmds.ls(cmds.file(leftEyeFilePath, i=True, returnNewNodes=True), transforms=True)[0]
    externalSizeY = mayaUtils.GetBoundingBox(leftEyeMesh)[1]
    print externalSizeY

    rightEyeFilePath = os.path.join(GetSharedResourcesPath(), 'Eye_Right.obj')
    rightEyeMesh = cmds.ls(cmds.file(rightEyeFilePath, i=True, returnNewNodes=True), transforms=True)[0]

    scaleFactor = oldSizeY / externalSizeY
    print 'Scale factor = {}'.format(scaleFactor)

    #scale and move new eyes
    cmds.scale( scaleFactor, scaleFactor, scaleFactor, leftEyeMesh, relative=True )
    cmds.matchTransform(leftEyeMesh, jointLeft, position=True, rotation=True)
    cmds.rotate( 0, '90deg', 0, leftEyeMesh, relative=True )
    cmds.makeIdentity(leftEyeMesh, apply=True, translate=True, rotate=True, scale=True, normal=1)
    cmds.delete(leftEyeMesh, constructionHistory=True)

    cmds.scale( scaleFactor, scaleFactor, scaleFactor, rightEyeMesh, relative=True )
    cmds.matchTransform(rightEyeMesh, jointRight, position=True, rotation=True)
    cmds.rotate( 0, '90deg', 0, rightEyeMesh, relative=True )
    cmds.makeIdentity(rightEyeMesh, apply=True, translate=True, rotate=True, scale=True, normal=1)
    cmds.delete(rightEyeMesh, constructionHistory=True)

    #binding
    cmds.skinCluster(jointLeft, leftEyeMesh,tsb=True)
    cmds.select(clear=True)

    cmds.skinCluster(jointRight, rightEyeMesh,tsb=True)
    cmds.select(clear=True)

    cmds.polyUniteSkinned([leftEyeMesh,rightEyeMesh], ch=False)
    cmds.rename('FemaleEyes')
    cmds.select(clear=True)

    sha = cmds.shadingNode('lambert', asShader=True, name='Eyes')
    sg = cmds.sets(empty=True, renderable=True, noSurfaceShader=True,  name='Eyes_sg')
    cmds.connectAttr( sha+'.outColor', sg+'.surfaceShader', f=True)
    cmds.sets('FemaleEyes', e=True, forceElement=sg)



def AddNippleJointAndRealighnBreast(newJointName, parentName, uvPos, referenceShape):
    cmds.select(clear=True)
    cmds.select(parentName)
    newJointName = cmds.joint(name=newJointName) #not final nipple joint!

    f = mayaUtils.UvCoordToWorld(uvPos[0], uvPos[1], referenceShape)
    print 'AddNippleJointAndRealighnBreast(): {} position is {}'.format(newJointName, f)
    cmds.move(f[0], f[1], f[2], newJointName, absolute=True)
    cmds.parent(newJointName, world=True)
    constraint = cmds.aimConstraint(newJointName, parentName, worldUpType='vector', worldUpVector=[0, 1, 0])
    cmds.delete(constraint)
    cmds.delete(newJointName) #delete temp nipple joint

    cmds.select(parentName) #again
    newJointName = cmds.joint(name=newJointName) #create new joint, properly aligned with parent
    cmds.move(f[0], f[1], f[2], newJointName, absolute=True)

def AddEndJoints():
    cmds.select(clear=True)
    srcJoints = []

    for joint in ['thumb_03', 'index_03', 'middle_03', 'pinky_03', 'toebig_02', 'toeindex_02', 'toemid_02', 'toering_02', 'toepinky_02']:
        for sideSuffix in ['_l', '_r']:
            srcJoints.append(joint + sideSuffix)

    srcJoints.append('tongue_04')


    for j in srcJoints:
        
        #newJointName = j + '_end'
        newJointName = j[:-5] + '_end_' + j[-4:]
        relativeTranslation = cmds.xform(j, q=True, relative=True, translation=True)
        cmds.select(j)
        cmds.joint(name=newJointName)
        cmds.xform(relative=True, translation=relativeTranslation)
        print 'Created end joint {0} from {1} with offset {2}'.format(newJointName, j, relativeTranslation)


def AddCameraJoint():
    cmds.select(clear=True)
    cmds.select(['eye_l', 'eye_r'])
    EyesPos = mayaUtils.GetAverageWorldTranslationOfSelected()
    EyesPos[0] = 0.0
    EyesPos[2] = 0.0

    cmds.select('head')
    cmds.joint(name='camera')
    cmds.xform(worldSpace=True, translation=EyesPos)
    cmds.xform(worldSpace=True, rotation=[0, -90, -90])

    print 'Created camera joint with world pos {0}'.format(EyesPos)

def GetRenamingDict():
    dictionary = {
        'hip': 'pelvis',
        #'abdomenLower': 'Spine_1',
        'abdomenUpper': 'spine_01',
        'chestLower': 'spine_02',
        'chestUpper': 'spine_03',

        'neckLower': 'neck_01',
        #'neckUpper': 'Neck_2',
        'head': 'head',

        'lPectoral': 'breast_l', #Pectoral_L
        'rPectoral': 'breast_r', #Pectoral_R
        # Arm Left
        'lCollar': 'clavicle_l',
        'lShldrBend': 'upperarm_l',
        'lShldrTwist': 'upperarm_twist_01_l',

        'lForearmBend': 'lowerarm_l',
        'lForearmTwist': 'lowerarm_twist_01_l',
        'lHand': 'hand_l',

        'lThumb1': 'thumb_01_l',
        'lThumb2': 'thumb_02_l',
        'lThumb3': 'thumb_03_l',

        #'lCarpal1': 'HandIndex0_L',
        'lIndex1': 'index_01_l',
        'lIndex2': 'index_02_l',
        'lIndex3': 'index_03_l',

        #'lCarpal2': 'HandMid0_L',
        'lMid1': 'middle_01_l',
        'lMid2': 'middle_02_l',
        'lMid3': 'middle_03_l',

        #'lCarpal3': 'HandRing0_L',
        'lRing1': 'ring_01_l',
        'lRing2': 'ring_02_l',
        'lRing3': 'ring_03_l',

        #'lCarpal4': 'HandPinky0_L',
        'lPinky1': 'pinky_01_l',
        'lPinky2': 'pinky_02_l',
        'lPinky3': 'pinky_03_l',

        # Arm Right
        'rCollar': 'clavicle_r',
        'rShldrBend': 'upperarm_r',
        'rShldrTwist': 'upperarm_twist_01_r',

        'rForearmBend': 'lowerarm_r',
        'rForearmTwist': 'lowerarm_twist_01_r',
        'rHand': 'hand_r',

        'rThumb1': 'thumb_01_r',
        'rThumb2': 'thumb_02_r',
        'rThumb3': 'thumb_03_r',

        #'rCarpal1': 'HandIndex0_R',
        'rIndex1': 'index_01_r',
        'rIndex2': 'index_02_r',
        'rIndex3': 'index_03_r',

        #'rCarpal2': 'HandMid0_R',
        'rMid1': 'middle_01_r',
        'rMid2': 'middle_02_r',
        'rMid3': 'middle_03_r',

        #'rCarpal3': 'HandRing0_R',
        'rRing1': 'ring_01_r',
        'rRing2': 'ring_02_r',
        'rRing3': 'ring_03_r',

        #'rCarpal4': 'HandPinky0_R',
        'rPinky1': 'pinky_01_r',
        'rPinky2': 'pinky_02_r',
        'rPinky3': 'pinky_03_r',

        # Leg Left
        'lThighBend': 'thigh_l',#UpLeg_L
        'lThighTwist': 'thigh_twist_01_l',
        'lShin': 'calf_l',
        'lFoot': 'foot_l',
        #rename'lMetatarsals': 'Metatarsals_L',
        'lToe': 'ball_l',

        # Leg Right
        'rThighBend': 'thigh_r',
        'rThighTwist': 'thigh_twist_01_r',
        'rShin': 'calf_r',
        'rFoot': 'foot_r',
        #rename'rMetatarsals': 'Metatarsals_R',
        'rToe': 'ball_r',

        # Toes
        'lBigToe' : 'toebig_01_l',
        'lBigToe_2' : 'toebig_02_l',
        'lSmallToe1' : 'toeindex_01_l',
        'lSmallToe1_2' : 'toeindex_02_l',
        'lSmallToe2' : 'toemid_01_l',
        'lSmallToe2_2' : 'toemid_02_l',
        'lSmallToe3' : 'toering_01_l',
        'lSmallToe3_2' : 'toering_02_l',
        'lSmallToe4' : 'toepinky_01_l',
        'lSmallToe4_2' : 'toepinky_02_l',

        'rBigToe' : 'toebig_01_r',
        'rBigToe_2' : 'toebig_02_r',
        'rSmallToe1' : 'toeindex_01_r',
        'rSmallToe1_2' : 'toeindex_02_r',
        'rSmallToe2' : 'toemid_01_r',
        'rSmallToe2_2' : 'toemid_02_r',
        'rSmallToe3' : 'toering_01_r',
        'rSmallToe3_2' : 'toering_02_r',
        'rSmallToe4' : 'toepinky_01_r',
        'rSmallToe4_2' : 'toepinky_02_r',

        # Face
        'lEye': 'eye_l',
        'rEye': 'eye_r',
        'lEar': 'ear_l',
        'rEar': 'ear_r',
        'upperTeeth': 'upperteeth',
        'lowerJaw': 'lowerjaw',
        'lowerTeeth': 'lowerteeth',
        'tongue01': 'tongue_01',
        'tongue02': 'tongue_02',
        'tongue03': 'tongue_03',
        'tongue04': 'tongue_04',

        'lowerFaceRig': 'lowerface',
        'upperFaceRig': 'upperface',
        # Root
        'Genesis8Female': 'root'}
    return dictionary

def RenameChildren(name):
    print 'Rename Children for {0}'.format(name)
    children = cmds.listRelatives(name)
    for child in children:
        if child[0] == 'r':
            mayaUtils.RenameJoint(child, child[1:].lower() + '_r')
        elif child[0] == 'l':
            mayaUtils.RenameJoint(child, child[1:].lower() + '_l')
        else:
            mayaUtils.RenameJoint(child, child.lower() + '_m')


def RenameSkeletonJoints():
    with mayaUtils.DebugTimer('RenameSkeletonJoints'):
        #first rename original pevis joint if exist (for animation retargetting mode) as it has same name 'pelvis' as our new joint
        mayaUtils.RenameJoint('pelvis', 'original_pelvis_to_delete') 
        renamingDictionary = GetRenamingDict()
        for oldName, newName in renamingDictionary.iteritems():
            mayaUtils.RenameJoint(oldName, newName)

        RenameChildren('lowerface')
        RenameChildren('upperface')


def OptimizeBodyMaterials():
    with mayaUtils.DebugTimer('OptimizeBodyMaterials'):
        shape = mayaUtils.FindMeshByWildcard('Genesis8Female*', checkForMatWithName='Torso')

        if shape is None:
            print 'Error! Can`t find body(Torso) shape'
            return

        mayaUtils.AppendShadingGroupByMat(shape, 'Face', 'Lips')
        mayaUtils.AppendShadingGroupByMat(shape, 'Face', 'Ears')
        mayaUtils.AppendShadingGroupByMat(shape, 'Face', 'EyeSocket')

        mayaUtils.AppendShadingGroupByMat(shape, 'Legs', 'Toenails')
        mayaUtils.AppendShadingGroupByMat(shape, 'Arms', 'Fingernails')

        mayaUtils.AppendShadingGroupByMat(shape, 'Torso', 'Legs')
        mayaUtils.AppendShadingGroupByMat(shape, 'Torso', 'Arms')
        mayaUtils.AppendShadingGroupByMat(shape, 'Torso', 'Face')

        mayaUtils.AppendShadingGroupByMat(shape, 'Mouth', 'Teeth')

        mayaUtils.AppendShadingGroupByMat(shape, 'EyeMoisture', 'Cornea') # useful eyes
        mayaUtils.AppendShadingGroupByMat(shape, 'Pupils', 'Irises') # not used
        mayaUtils.AppendShadingGroupByMat(shape, 'Pupils', 'Sclera') # not used

        eyesShape = mayaUtils.DetachSkinnedMeshByMat(shape, ['EyeMoisture', 'Pupils'], '_Eyes')

        mayaUtils.DeleteFacesByMat(eyesShape, ['Pupils'])
        unusedEyesFaces = selUtils.GetFacesOutsideCenterUVRange(eyesShape)
        cmds.delete(unusedEyesFaces)

        mayaUtils.RenameMaterial('Torso', 'Body')
        mayaUtils.RenameMaterial('EyeMoisture', 'Eyes')

        mayaUtils.RenameMaterial('EyeLashes*', 'FemaleEyeLashes')

        SafeBakePartialHistoryKeepBlendShapes(shape)

        if eyesShape:
            cmds.bakePartialHistory(eyesShape, prePostDeformers=True)

        mayaUtils.CleanUnusedInfluensesOnAllSkinClusters()


def SafeBakePartialHistoryKeepBlendShapes(pShape):
    print 'SafeBakePartialHistoryKeepBlendShapes(pShape=\'{}\')'.format(pShape)
    bs = mayaUtils.GetBlendShape(pShape)
    if not bs:
        print 'No blendshape detected. Performing standart baking partial history'
        #cmds.bakePartialHistory(shape, prePostDeformers=True)
    else:
        print 'Detected blendshape \'{}\'. Performing ajustments'.format(bs)
        weightCount = cmds.blendShape(bs, q=True, weightCount=True)
        names = cmds.listAttr(bs + '.w', m=True)

        tempTargetObjects = []

        # Extract every blendshape to separate mesh
        for i in range(weightCount):
            # Set current index weight to 1.0, all others to 0.0
            for x in range(weightCount):
                weight = 0.0
                if i == x:
                    weight = 1.0
                cmds.blendShape(bs, edit=True, weight=[x, weight])
            newShape = cmds.duplicate(pShape, name=names[i])[0]
            cmds.setAttr(newShape+'.tz', lock=0)
            cmds.bakePartialHistory(newShape)
            cmds.xform(newShape, absolute=True, translation=[0, 0, 50.0*(i+1)])
            tempTargetObjects.append(newShape)


        # Reset all weights to zero
        for i in range(weightCount):
            cmds.blendShape(bs, edit=True, weight=[i, 0.0])

        cmds.delete(bs)
        cmds.bakePartialHistory(pShape, prePostDeformers=True)



        argsList = []
        argsList.extend(tempTargetObjects)
        argsList.append(pShape) # LAST add initial object to list
        cmds.blendShape(argsList)

        cmds.delete(tempTargetObjects) # delete temporary objects



def CreateIkJoints(pCreateConstraint=True):
    with mayaUtils.DebugTimer('CreateIkJoints'):
        CreateIkJoint('camera', 'root', 'ik_camera', pCreateConstraint)
        CreateIkJoint('root', 'root', 'ik_foot_root')
        CreateIkJoint('foot_r', 'ik_foot_root', 'ik_foot_r', pCreateConstraint)
        CreateIkJoint('foot_l', 'ik_foot_root', 'ik_foot_l', pCreateConstraint)

        CreateIkJoint('root', 'root', 'ik_hand_root', False)
        CreateIkJoint('hand_r', 'ik_hand_root', 'ik_hand_gun', pCreateConstraint)
        CreateIkJoint('hand_r', 'ik_hand_gun', 'ik_hand_r', pCreateConstraint)
        CreateIkJoint('hand_l', 'ik_hand_gun', 'ik_hand_l', pCreateConstraint)

        #CreateIkJoint('pelvis', 'root', 'IK_pelvis', pCreateConstraint)


def CreateIkJoint(referenceJnt, parentJnt, ikJntName, bCreateConstraint=False):
    cmds.select(clear=True)
    print 'Created IK joint "{0}" corresponding to "{1}" parented to "{2}"'.format(ikJntName, referenceJnt, parentJnt)
    if not cmds.objExists(referenceJnt):
        print 'Reference joint not found. Aborting'
        return
    if not cmds.objExists(parentJnt):
        print 'Parent joint not found. Aborting'
        return
    cmds.select(referenceJnt)
    cmds.joint(name=ikJntName)
    if not parentJnt == referenceJnt:
        cmds.parent(ikJntName, parentJnt)

    if bCreateConstraint:
        cmds.parentConstraint(referenceJnt, ikJntName)





def DuplicateSkeletonJoints(oldSkeletonRoot, newJointsPrefix):
    with mayaUtils.DebugTimer('Duplicating skeleton'):
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
    with mayaUtils.DebugTimer('FixNewJointsOrientation'):
        # Root
        mayaUtils.RotateJoint("DAZ_root", 0, 0, 0)

        # Spine
        mayaUtils.RotateJoint("DAZ_pelvis", -90, 0, 90)
        #mayaUtils.RotateJoint("DAZ_Spine_1", 90, 0, 90)
        mayaUtils.RotateJoint("DAZ_spine_01", -90, 0, 90)
        mayaUtils.RotateJoint("DAZ_spine_02", -90, 0, 90)
        mayaUtils.RotateJoint("DAZ_spine_03", -90, 0, 90)

        mayaUtils.RotateJoint("DAZ_breast_l", 0, -90, 0)
        mayaUtils.RotateJoint("DAZ_breast_r", 0, -90, 0)

        mayaUtils.RotateJoint("DAZ_neck_01", -90, 0, 90)
        #mayaUtils.RotateJoint("DAZ_Neck_2", 90, 0, 90)
        mayaUtils.RotateJoint("DAZ_head", -90, 0, 90)

        # Leg Left
        mayaUtils.RotateJoint("DAZ_thigh_l", -90, 0, 90)
        mayaUtils.RotateJoint("DAZ_thigh_twist_01_l", -90, 0, 90)
        mayaUtils.RotateJoint("DAZ_calf_l", -90, 0, 90)
        # copy rotation from Leg
        cmds.xform('DAZ_foot_l', absolute=True, rotation=cmds.xform('calf_l', q=True, absolute=True, rotation=True))
        mayaUtils.RotateJoint("DAZ_foot_l", -90, 0, 90)
        mayaUtils.RotateJoint("DAZ_ball_l", 0, -90, 0) #TODO near but not ideal

        # Leg Right
        mayaUtils.RotateJoint("DAZ_thigh_r", 90, 0, -90)
        mayaUtils.RotateJoint("DAZ_thigh_twist_01_r", 90, 0, -90)
        mayaUtils.RotateJoint("DAZ_calf_r", 90, 0, -90)
        # copy rotation from Leg
        cmds.xform('DAZ_foot_r', absolute=True, rotation=cmds.xform('calf_r', q=True, absolute=True, rotation=True))
        mayaUtils.RotateJoint("DAZ_foot_r", 90, 0, -90)
        mayaUtils.RotateJoint("DAZ_ball_r", 180, 90, 0)

        # Arm Left

        mayaUtils.RotateJoint("DAZ_clavicle_l", -90)
        mayaUtils.RotateJoint("DAZ_upperarm_l", -90)
        mayaUtils.RotateJoint("DAZ_upperarm_twist_01_l", -90)
        mayaUtils.RotateJoint("DAZ_lowerarm_l", -90)
        mayaUtils.RotateJoint("DAZ_lowerarm_twist_01_l", -90)
        mayaUtils.RotateJoint("DAZ_hand_l", -180)

        mayaUtils.RotateJoint('DAZ_thumb_01_l', -90)
        mayaUtils.RotateJoint('DAZ_thumb_02_l', -90)
        mayaUtils.RotateJoint('DAZ_thumb_03_l', -90)

        #mayaUtils.RotateJoint('DAZ_HandIndex0_L', 90)
        mayaUtils.RotateJoint('DAZ_index_01_l', 180)
        mayaUtils.RotateJoint('DAZ_index_02_l', 180)
        mayaUtils.RotateJoint('DAZ_index_03_l', 180)

        #mayaUtils.RotateJoint('DAZ_HandMid0_L', 90)
        mayaUtils.RotateJoint('DAZ_middle_01_l', 180)
        mayaUtils.RotateJoint('DAZ_middle_02_l', 180)
        mayaUtils.RotateJoint('DAZ_middle_03_l', 180)

        #mayaUtils.RotateJoint('DAZ_HandRing0_L', 90)
        mayaUtils.RotateJoint('DAZ_ring_01_l', 180)
        mayaUtils.RotateJoint('DAZ_ring_02_l', 180)
        mayaUtils.RotateJoint('DAZ_ring_03_l', 180)

        #mayaUtils.RotateJoint('DAZ_HandPinky0_L', 90)
        mayaUtils.RotateJoint('DAZ_pinky_01_l', 180)
        mayaUtils.RotateJoint('DAZ_pinky_02_l', 180)
        mayaUtils.RotateJoint('DAZ_pinky_03_l', 180)

        # Arm Right

        mayaUtils.RotateJoint("DAZ_clavicle_r", 90)
        mayaUtils.RotateJoint("DAZ_upperarm_r", 90)
        mayaUtils.RotateJoint("DAZ_upperarm_twist_01_r", 90)
        mayaUtils.RotateJoint("DAZ_lowerarm_r", 90)
        mayaUtils.RotateJoint("DAZ_lowerarm_twist_01_r", 90)
        mayaUtils.RotateJoint("DAZ_hand_r", 0)

        mayaUtils.RotateJoint('DAZ_thumb_01_r', 90)
        mayaUtils.RotateJoint('DAZ_thumb_02_r', 90)
        mayaUtils.RotateJoint('DAZ_thumb_03_r', 90)

        #mayaUtils.RotateJoint('DAZ_HandIndex0_R', -90, 180)
        mayaUtils.RotateJoint('DAZ_index_01_r', 0)
        mayaUtils.RotateJoint('DAZ_index_02_r', 0)
        mayaUtils.RotateJoint('DAZ_index_03_r', 0)

        #mayaUtils.RotateJoint('DAZ_HandMid0_R', -90, 180)
        mayaUtils.RotateJoint('DAZ_middle_01_r', 0)
        mayaUtils.RotateJoint('DAZ_middle_02_r', 0)
        mayaUtils.RotateJoint('DAZ_middle_03_r', 0)

        #mayaUtils.RotateJoint('DAZ_HandRing0_R', -90, 180)
        mayaUtils.RotateJoint('DAZ_ring_01_r', 0)
        mayaUtils.RotateJoint('DAZ_ring_02_r', 0)
        mayaUtils.RotateJoint('DAZ_ring_03_r', 0)

        #mayaUtils.RotateJoint('DAZ_HandPinky0_R', -90, 180)
        mayaUtils.RotateJoint('DAZ_pinky_01_r', 0)
        mayaUtils.RotateJoint('DAZ_pinky_02_r', 0)
        mayaUtils.RotateJoint('DAZ_pinky_03_r', 0)

        #Toes
        for t in ['toebig_01', 'toebig_02', 'toeindex_01', 'toeindex_02', 'toemid_01', 'toemid_02', 'toering_01', 'toering_02', 'toepinky_01', 'toepinky_02']:
            mayaUtils.RotateJoint('DAZ_'+t+'_l', 0, 90)
            mayaUtils.RotateJoint('DAZ_'+t+'_r', 0, -90)


        # facial rig
        mayaUtils.RotateJoint("DAZ_tongue_01", 0, -90, 0)
        mayaUtils.RotateJoint("DAZ_tongue_02", 0, -90, 0)
        mayaUtils.RotateJoint("DAZ_tongue_03", 0, -90, 0)
        mayaUtils.RotateJoint("DAZ_tongue_04", 0, -90, 0)

        mayaUtils.RotateJoint("DAZ_eye_l", 0, -90, 180)
        mayaUtils.RotateJoint("DAZ_eye_r", 0, -90, 180)

        # selecting original joints of face rig
        children = cmds.listRelatives('DAZ_head', allDescendents=True) or []

        for child in children:
            if child in ['DAZ_eye_l', 'DAZ_eye_r'] or child.startswith('DAZ_tongue_'):
                continue  # skip already rotated
            mayaUtils.RotateJoint('DAZ_' + child, 0, -90, 0)  # but rotating skeleton copy

        cmds.select(clear=True)

def AimJointForUnreal(joint, target, inAimVector=[1.0, 0.0, 0.0]):
    constraint = cmds.aimConstraint(target, joint, worldUpType='vector', aimVector=inAimVector, worldUpVector=[0, 0, 1])
    print '\tAimJoint {0} to {1}'.format(joint, target)
    cmds.delete(constraint)

def AimJoint(joint, target, inAimVector=[1.0, 0.0, 0.0]):
    constraint = cmds.aimConstraint(target, joint, worldUpType='vector', aimVector=inAimVector, worldUpVector=[0, 0, 1])
    print '\tAimJoint {0} to {1}'.format(joint, target)
    cmds.delete(constraint)

# Custom aiming for foot joints (aim Y, keep X)
def AimFootJoint(footJoint, toeTarget):
    footPos = cmds.xform(footJoint, t=True, ws=True, q=True)
    toePos = cmds.xform(toeTarget, t=True, ws=True, q=True)

    locatorPos = toePos
    locatorPos[1] = footPos[1] # Set Y from foot

    locator = cmds.spaceLocator()
    cmds.xform(locator, ws=True, translation=locatorPos)

    constraint = cmds.aimConstraint(locator, footJoint, aimVector=[0, 1, 0], worldUpType='Vector', upVector=[1, 0, 0], worldUpVector=[0, -1, 0], skip='y')
    cmds.delete(constraint)
    cmds.delete(locator)


def FixNewJointsAiming(prefix='DAZ_'):
    with mayaUtils.DebugTimer('FixNewJointsAiming'):
        #AimJoint(prefix + 'Spine_1', prefix + 'Spine_2')
        AimJoint(prefix + 'spine_01', prefix + 'spine_02')
        AimJoint(prefix + 'spine_02', prefix + 'spine_03')
        AimJoint(prefix + 'spine_03', prefix + 'neck_01')
        AimJoint(prefix + 'neck_01', prefix + 'head')
        #AimJoint(prefix + 'Neck_2', prefix + 'Head')

        AimJoint(prefix + 'clavicle_l', prefix + 'upperarm_l')
        AimJoint(prefix + 'upperarm_l', prefix + 'lowerarm_l')
        AimJoint(prefix + 'lowerarm_l', prefix + 'hand_l')

        AimJoint(prefix + 'clavicle_r', prefix + 'upperarm_r')
        AimJoint(prefix + 'upperarm_r', prefix + 'lowerarm_r')
        AimJoint(prefix + 'lowerarm_r', prefix + 'hand_r')

        AimJoint(prefix + 'thigh_l', prefix + 'calf_l', inAimVector=[-1.0, 0.0, 0.0])
        AimJoint(prefix + 'calf_l', 'foot_l')
        AimJoint(prefix + 'thigh_r', prefix + 'calf_r')
        AimJoint(prefix + 'calf_r', 'foot_r')

        AimFootJoint(prefix + 'foot_l', prefix + 'ball_l')
        AimFootJoint(prefix + 'foot_r', prefix + 'ball_r')

def AlighnTwistJoints(prefix='DAZ_'):
    with mayaUtils.DebugTimer('AlighnTwistJoints'):
        twistJoints = cmds.ls(prefix + '*_twist*', type='joint')
        for j in twistJoints:
            oldPos = cmds.joint(j, q=True, position=True, relative=True)
            newPos = [oldPos[0], 0.0, 0.0]
            print '\tAlighning joint {0} oldPos={1}, newPos ={2}'.format(j, oldPos, newPos)
            cmds.joint(j, e=True, position=newPos, relative=True)
            cmds.joint(j, e=True, orientation=[0.0, 0.0, 0.0])
            cmds.xform(j, rotation=[0.0, 0.0, 0.0])


def RecreateHierarchy(oldSkeletonRoot, newJointsPrefix):
    with mayaUtils.DebugTimer('Recreating hierarchy'):
        jointsList = cmds.listRelatives(oldSkeletonRoot, allDescendents=True, type="joint")#Root is already unparrented, we dont need it

        for j in jointsList:
            parent = cmds.listRelatives(j, parent=True, type='joint')
            if not parent:
                continue
            oldName = cmds.joint(j, q=True, name=True)
            oldParentName = cmds.joint(parent, q=True, name=True)
            newName = newJointsPrefix + oldName
            newParentName = newJointsPrefix + oldParentName
            if oldName == 'thigh_l' or oldName == 'thigh_r': #connect legs to Hips, not to OLD pelvis
                newParentName = newJointsPrefix + 'pelvis'
            elif oldName == 'ball_l':
                newParentName = newJointsPrefix + 'foot_l' #not to lMetatarsals
            elif oldName == 'ball_r':
                newParentName = newJointsPrefix + 'foot_r' #not to rMetatarsals
            elif oldName == 'head':
                newParentName = newJointsPrefix + 'neck_01' #not to neckUpper
            elif oldName == 'spine_01':
                newParentName = newJointsPrefix + 'pelvis' #not to abdomenLower

            #print newParentName
            cmds.parent(newName, newParentName)

            print '\tParenting {0} to {1}'.format(newName, newParentName)

        twistJoints = cmds.ls(newJointsPrefix+'*_twist*')
        for j in twistJoints:
            parent = cmds.listRelatives(j, parent=True)
            children = cmds.listRelatives(j)
            if children is not None:
                for child in children:
                    print 'Reparenting twist joint {0} child {1} to {2}'.format(j, child, parent[0])
                    cmds.parent(child, parent[0])

        #Remove unused bones if exists (for animation retargeting mode)
        unusedList = ['lMetatarsals', 'rMetatarsals', 'abdomenLower', 'neckUpper', 'original_pelvis_to_delete']
        for j in unusedList:
            if cmds.objExists(newJointsPrefix + j): #still use prefix
                cmds.delete(newJointsPrefix + j)
                print 'Deleting joint {0}'.format(newJointsPrefix + j)

        # orphanParentsList = ['Toe_L', 'Toe_R']
        # for j in orphanParentsList:
        #     if cmds.objExists(newJointsPrefix + j): #still use prefix
        #         childrenList = cmds.listRelatives(newJointsPrefix + j, allDescendents=True) or []
        #         for c in childrenList:
        #             cmds.delete(c)
        #             print 'Deleting {0} - child joint of {1} '.format(c, newJointsPrefix + j)


def SetJointsVisualProperties():
    joints = cmds.ls('*_twist_*',type='joint')
    joints += cmds.ls('*_bend_*',type='joint')
    for j in joints:
        cmds.setAttr(j + '.radius', 3)

def RenameNewSkeleton():
    with mayaUtils.DebugTimer('RenameNewSkeleton'):
        newRoot = cmds.ls('DAZ_root', type='joint')
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
    with mayaUtils.DebugTimer('MakeBendCorrectiveJoints'):
        MakeBendCorrectiveJoint('knee_bend_l', 'calf_l', 'thigh_l', ['thigh_twist_01_l', 'calf_l'])
        MakeBendCorrectiveJoint('knee_bend_r', 'calf_r', 'thigh_r', ['thigh_twist_01_r', 'calf_r'])

        MakeBendCorrectiveJoint('butt_bend_l', 'thigh_l', 'pelvis')
        MakeBendCorrectiveJoint('butt_bend_r', 'thigh_r', 'pelvis')

        MakeBendCorrectiveJoint('shoulder_bend_l', 'upperarm_l', 'clavicle_l')
        MakeBendCorrectiveJoint('shoulder_bend_r', 'upperarm_r', 'clavicle_r')

        MakeBendCorrectiveJoint('elbow_bend_l', 'lowerarm_l', 'upperarm_l', ['upperarm_twist_01_l', 'lowerarm_l'])
        MakeBendCorrectiveJoint('elbow_bend_r', 'lowerarm_r', 'upperarm_r', ['upperarm_twist_01_r', 'lowerarm_r'])

def TriangulateAllSkinnedMeshes():
    with mayaUtils.DebugTimer('TriangulateAllSkinnedMeshes'):
        cmds.select(clear=True)
        skinList = cmds.ls(type='skinCluster') or []
        for s in skinList:
            mesh = mayaUtils.GetMeshFromSkinCluster(s)
            cmds.polyTriangulate(mesh)
            cmds.bakePartialHistory(mesh, prePostDeformers=True)
        cmds.select(clear=True)

def SubdivideImportantBodyParts():
    with mayaUtils.DebugTimer('SubdivideImportantBodyParts'):
        cmds.select(clear=True)
        bodyMesh = mayaUtils.FindMeshByWildcard('Genesis*Shape', preferShapeWithMaxVertices=True, checkForMatWithName='Torso')
        if bodyMesh:
            facesToSubdiv = []

            nipplesVerts = []
            leftNipple = mayaUtils.GetVertexFromUV(bodyMesh, k_LEFT_NIPPLE_UV)
            rightNipple = mayaUtils.GetVertexFromUV(bodyMesh, k_RIGHT_NIPPLE_UV)


            if leftNipple and rightNipple:
                nipplesVerts = [leftNipple, rightNipple]
                nipplesFaces = cmds.polyListComponentConversion(nipplesVerts, fv=True, tf=True)
                nipplesVerts = cmds.polyListComponentConversion(nipplesFaces, ff=True, tv=True)
                nipplesFaces = cmds.polyListComponentConversion(nipplesVerts, fv=True, tf=True)
                nipplesVerts = cmds.polyListComponentConversion(nipplesFaces, ff=True, tv=True)
                nipplesFaces = cmds.polyListComponentConversion(nipplesVerts, fv=True, tf=True)
                if nipplesFaces:
                    facesToSubdiv.extend(nipplesFaces)

            earsFaces = mayaUtils.GetFacesByMatsWildcard(bodyMesh, 'Ears')
            if earsFaces:
                facesToSubdiv.extend(earsFaces)

            handsFaces = selUtils.GetFacesInUTile(bodyMesh, 2)
            if handsFaces:
                facesToSubdiv.extend(handsFaces)

            feetFaces = selUtils.GetFacesInUTile(bodyMesh, 3)
            if feetFaces:
                facesToSubdiv.extend(feetFaces)


            if facesToSubdiv:
                cmds.polySmooth(facesToSubdiv)
                cmds.bakePartialHistory(bodyMesh, prePostDeformers=True)

        cmds.select(clear=True)
