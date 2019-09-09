import maya.cmds as cmds
import time

def GetSkinExportData():
    skinData = []  # transform, shape, skincluster, jointsList
    skinList = cmds.ls(type='skinCluster')
    meshes = set(sum([cmds.skinCluster(c, q=1, g=1) for c in skinList], []))
    #print meshes
    for mesh in meshes:
        transformList = cmds.listRelatives(mesh, parent=True)
        #print transformList
        for tf in transformList:
            shapes = cmds.listRelatives(tf, shapes=True)
            for shape in shapes:
                history = cmds.listHistory(shape, groupLevels=True, pruneDagObjects=True)
                skins = cmds.ls(history, type='skinCluster')
                #print skins
                for skin in skins:
                    joints = cmds.skinCluster(skin, query=True, influence=True)
                    skinData.append([tf, shape, skin, joints])
                    #print joints
    return skinData


def SetSkinMethodForAllSkinClusters(skinMethod):
    skinList = cmds.ls(type='skinCluster')
    for s in skinList:
        cmds.skinCluster(s, e=True, skinMethod=skinMethod)

def RenameMaterial(originalName, newName):
    print 'Renaming material {0} to {1}'.format(originalName, newName)
    shaders = cmds.ls(type="lambert")
    for mat in shaders:
        if mat == originalName:
            cmds.rename(mat, newName)
            return
    print 'Can`t find material {0}'.format(originalName)

def ResetBindPose(sel):
    for each in sel:
        shapes = cmds.listRelatives(each, shapes=True)

        for shape in shapes:
            # get skin cluster
            history = cmds.listHistory(
                shape, groupLevels=True, pruneDagObjects=True)
            skins = cmds.ls(history, type='skinCluster')

            for skin in skins:
                joints = cmds.skinCluster(skin, query=True, influence=True)

                cmds.setAttr(skin+'.envelope', 0)
                cmds.skinCluster(skin, edit=True, unbindKeepHistory=True)

                # delete bindPose
                dagPose = cmds.dagPose(each, query=True, bindPose=True)
                if dagPose:
                    cmds.delete(dagPose)
                dagPose = cmds.listConnections(
                    skin+'.bindPose', d=False, type='dagPose')
                if dagPose:
                    cmds.delete(dagPose)

                cmds.skinCluster(joints, shape, toSelectedBones=True)
                cmds.setAttr(skin+'.envelope', 1)

def ResetBindPoseForAllSkinClusters():
    skinList = cmds.ls(type='skinCluster')
    print 'Resetting bind pose'
    meshes = set(sum([cmds.skinCluster(c, q=1, g=1) for c in skinList], []))
    for mesh in meshes:
        transformList = cmds.listRelatives(mesh, parent=True)
        ResetBindPose(transformList)
    print 'Resetting bind pose: Done'


def GetHierarchy(rootJoint):
    root = cmds.ls(rootJoint, type="joint")
    if len(root) == 1:
        allHierarchy = cmds.listRelatives(root[0], allDescendents=True)
        allHierarchy.append(root[0])
        return allHierarchy
    else:
        return None

def RotateJoint(jointName, x=0, y=0, z=0):
    if cmds.objExists(jointName):
        if cmds.nodeType(jointName) == 'joint':
            cmds.rotate(x, y, z, jointName, relative=True, objectSpace=True)
            print 'RotateJoint: {0} to [{1}, {2}, {3}]'.format(jointName, x, y, z)
        else:
            print 'RotateJoint: {0} is not joint. Aborting!'.format(jointName)
    else:
        print 'RotateJoint: {0} is not exist. Aborting!'.format(jointName)


def RenameJoint(oldName, newName):
    if cmds.objExists(oldName):
        if cmds.nodeType(oldName) == 'joint':
            cmds.rename(oldName, newName)
            print 'RenameJoint: {0} to {1}'.format(oldName, newName)
        else:
            print 'RenameJoint: {0} is not joint. Aborting renaming to {1}!'.format(oldName, newName)
    else:
        print 'RenameJoint: {0} is not exist. Aborting renaming to {1}!'.format(oldName, newName)

def RenameChildren(name):
    print 'Rename Children for {0}'.format(name)
    children = cmds.listRelatives(name)
    for child in children:
        if child[0] == 'r':
            RenameJoint(child, child[1:] + '_R')
        elif child[0] == 'l':
            RenameJoint(child, child[1:] + '_L')

def FixMaxInfluencesForAllSkinClusters(maxInfluences):
    print 'Starting FixMaxInfluencesForAllSkinClusters'
    start = time.clock()
    cmds.select(clear=True)
    skinList = cmds.ls(type='skinCluster')
    for s in skinList:
        FixMaxInfluencesForSkinCluster(s, maxInfluences)
    cmds.select(clear=True)
    print 'Finished FixMaxInfluencesForAllSkinClusters: time taken %.02f seconds' % (time.clock()-start)

def FixMaxInfluencesForSkinCluster(skinClusterName, maxInfluences):
    k_EPSILON = 0.0001

    shape = cmds.skinCluster(skinClusterName, q=True, geometry=True)[0]
    mesh = cmds.listRelatives(shape, parent=True)[0]
    vertsNum = cmds.polyEvaluate(mesh, v=1)
    print 'Fixing max influences for skincluster "{0}". Mesh: {1} Target max influense: {2} Verts num: {3}'.format(skinClusterName, mesh, maxInfluences, vertsNum)

    cmds.skinPercent(skinClusterName, mesh, pruneWeights=k_EPSILON)

    fixedCounter = 0

    for i in range(0, vertsNum):
        vertexName = mesh+'.vtx['+str(i)+']' #current vertex
        Weights = cmds.skinPercent(skinClusterName, vertexName, q=True, value=True, ignoreBelow=k_EPSILON)
        if(len(Weights)) > maxInfluences: # If (number of influences > max number of influences)
            fixedCounter += 1
            sortedWeights = sorted(Weights, reverse=True)
            PruneValue = sortedWeights[maxInfluences] + k_EPSILON
            #print vertexName
            #print sortedWeights
            #print PruneValue
            cmds.skinPercent(skinClusterName, vertexName, pruneWeights=PruneValue)
    if fixedCounter > 0:
        print 'Fixed {0} vertices'.format(fixedCounter)
    else:
        print 'No vertices found'

def TransferJointWeights(oldJointName, newJointName):
    cmds.select(clear=True)
    skinList = cmds.ls(type='skinCluster')
    print ''
    print 'TransferJointWeights: Transfering weights from {0} to {1}'.format(oldJointName, newJointName)
    for skinClusterName in skinList:
        cmds.select(clear=True)
        print 'TransferJointWeights: Processing ' + skinClusterName
        influences = cmds.skinCluster(
            skinClusterName, query=True, influence=True)
        if oldJointName not in influences:
            print 'TransferJointWeights: ' + skinClusterName + ' is NOT influenced by SOURCE joint ' + oldJointName + ' Skipping...'
            continue
        elif newJointName not in influences:
            print 'TransferJointWeights: ' + skinClusterName + ' is NOT influenced by TARGET joint ' + newJointName + ' Skipping...'
            continue
        else:
            print 'TransferJointWeights: ' + skinClusterName + ' is influenced by joint ' + oldJointName + ' Processing...'

        cmds.skinCluster(skinClusterName, e=True, selectInfluenceVerts=oldJointName)
        sel = cmds.ls(selection=True, flatten=True)
        onlyVertices = cmds.filterExpand(sel, sm=31)

        if onlyVertices is None:
            print 'TransferJointWeights: No binded vertices. Skipping...'
        else:
            for v in onlyVertices:
                oldJointWeight = cmds.skinPercent(skinClusterName, v, transform=oldJointName, query=True)
                newJointWeight = cmds.skinPercent(skinClusterName, v, transform=newJointName, query=True)
                finalNewJointWeight = min(1.0, newJointWeight + oldJointWeight)

                #print 'TransferJointWeights: Processing vertex {0} with old weight {1} new weight {2}'.format(v, oldJointWeight, finalNewJointWeight)
                # set weight
                cmds.skinPercent(skinClusterName, v, transformValue=[(oldJointName, 0), (newJointName, finalNewJointWeight)])

        print 'TransferJointWeights: Removing {0} from influences of {1}'.format(oldJointName, skinClusterName)
        cmds.skinCluster(skinClusterName, e=True, removeInfluence=oldJointName)

    print 'TransferJointWeights: Done'



def DestroyMiddleJoint(jointName):
    print''

    if not cmds.objExists(jointName):
        print 'DestroyMiddleJoint: joint {0} is not exist: Aborting'.format(jointName)
        return

    print 'DestroyMiddleJoint: Processing joint: ' + jointName
    parent = cmds.listRelatives(jointName, parent=True)
    if parent is None:
        print 'DestroyMiddleJoint: Joint parent is None. Aborting'
        return

    print 'DestroyMiddleJoint: Joint parent is ' + parent[0]
    TransferJointWeights(jointName, parent[0])

    children = cmds.listRelatives(jointName)
    if children is not None:
        for child in children:
            print 'DestroyMiddleJoint: parenting {0} to {1}'.format(child, parent[0])
            cmds.parent(child, parent[0])

    print 'DestroyMiddleJoint: unparenting {0}'.format(jointName)
    cmds.parent(jointName, world=True)
    print 'DestroyMiddleJoint: destroying {0}'.format(jointName)
    cmds.delete(jointName)

    print 'DestroyMiddleJoint: Done'


def DestroyJointChildren(jointName):
    print''

    if not cmds.objExists(jointName):
        print 'DestroyJointChildren: joint {0} is not exist: Aborting'.format(jointName)
        return

    print 'DestroyJointChildren: Processing joint: ' + jointName

    children = cmds.listRelatives(jointName, allDescendents=True)
    if children is None:
        print 'DestroyJointChildren: joint {0} does not has children: Aborting'.format(jointName)
        return

    for child in children:
        TransferJointWeights(child, jointName)

    for child in children:
        print 'DestroyJointChildren: unparenting {0}'.format(child)
        cmds.parent(child, world=True)
        print 'DestroyJointChildren: destroying {0}'.format(child)
        cmds.delete(child)

    print 'DestroyJointChildren: Done'


def CleanUnusedInfluenses(skinCluster):
    cmds.select(clear=True)
    weightedInfls = cmds.skinCluster(skinCluster, q=True, wi=True)
    print weightedInfls
    for wi in weightedInfls:
        cmds.skinCluster(skinCluster, e=True, selectInfluenceVerts=wi)
        selected = cmds.ls(sl=True)
        if len(selected) <= 1:
            print wi + ' REMOVE'
            cmds.skinCluster(skinCluster, e=True, removeInfluence=wi)

def CleanUnusedInfluensesOnAllSkinClusters():
    cmds.select(clear=True)
    skinList = cmds.ls(type='skinCluster')
    for s in skinList:
        CleanUnusedInfluenses(s)
    cmds.select(clear=True)

def GetSkinCluster(mesh):
    if cmds.nodeType(mesh) in ('mesh', 'nurbsSurface', 'nurbsCurve'):
        shapes = [mesh]
    else:
        shapes = cmds.listRelatives(mesh, shapes=True, path=True)

    for shape in shapes:
        history = cmds.listHistory(shape, groupLevels=True, pruneDagObjects=True)
        if not history:
            continue
        skins = cmds.ls(history, type='skinCluster')
        if skins:
            return skins[0]
    return None

def GetFacesByMat(shape, mat):
    shapeMats = cmds.listConnections(cmds.listHistory(shape, f=1), type='lambert')
    if mat not in shapeMats:
        print 'GetFacesByMat: Material {0} not in shape {1}'.format(mat, shape)
        return []
    else:
        sg_list = cmds.listConnections(mat, type='shadingEngine')
        faces_list = []
        for sg in sg_list:
            faces = cmds.filterExpand(cmds.sets(sg, q=True), sm=34, expand=False) or []
            #print "[faces]",mat, shape, sg, faces
            faces_list.extend(faces)

        all_faces = cmds.filterExpand(cmds.polyListComponentConversion(shape, toFace=True), sm=34, expand=False)
        #print "[all_faces]", all_faces
        prefix = all_faces[0].split('.')[0] + '.f'
        #print prefix

        filtered_faces = []

        for f in faces_list:
            #print f
            if f.startswith(prefix):
                filtered_faces.append(f)

        return filtered_faces

def ArrangeUVByMat(shape, mat, su=1.0, sv=1.0, u=0.0, v=0.0):
    print 'ArrangeUVByMat shape={0} mat={1} scale=[{2}, {3}], translate=[{4}, {5}]'.format(shape, mat, su, sv, u, v)
    faces = GetFacesByMat(shape, mat)
    cmds.select(faces)
    cmds.select(cmds.polyListComponentConversion(tuv=True), r=True)
    cmds.polyEditUV(su=su, sv=sv)
    cmds.polyEditUV(u=u, v=v)
    cmds.select(clear=True)

def AppendShadingGroupByMat(shape, matTo, matFrom):
    targetShadingGroup = cmds.listConnections(matTo, type='shadingEngine')[0]
    fromFaces = GetFacesByMat(shape, matFrom)
    print 'AppendShadingGroupByMat shape={0} to={1} from={2}'.format(shape, matTo, matFrom)
    cmds.select(fromFaces)
    cmds.sets(e=True, forceElement=targetShadingGroup)
    cmds.select(clear=True)

def FindShapeByMat(mat):
    print 'Searching for shape with mat={0}'.format(mat)
    shapes = cmds.ls(geometry=True)
    #print shapes
    for shape in shapes:
        shapeMats = cmds.listConnections(cmds.listHistory(shape, f=1), type='lambert') or []
        if mat in shapeMats:
            return shape
        #print shapeMats
    print 'Could`nt find requested shape'
    return None


def DuplicateSkinnedMesh(shape, newMeshSuffix=''):
    shapeTransform = cmds.listRelatives(shape, parent=True, type='transform')[0]
    oldSkinCluster = GetSkinCluster(shapeTransform)
    oldJoints = cmds.skinCluster(oldSkinCluster, query=True, influence=True)
    #print oldJoints

    newShape = cmds.duplicate(shape, name=shapeTransform + newMeshSuffix)[0]

    newSkinCluster = cmds.skinCluster(newShape, oldJoints, name=oldSkinCluster + newMeshSuffix)[0]
    #print newSkinCluster
    cmds.copySkinWeights(destinationSkin=newSkinCluster, sourceSkin=oldSkinCluster, noMirror=True, sa="closestPoint", ia="name")
    return newShape

def DeleteFacesByMat(shape, matList, bInvert=False):
    faces_list = []
    for m in matList:
        faces = GetFacesByMat(shape, m) or []
        faces_list.extend(faces)

    if not bInvert:
        cmds.delete(faces_list)
    else:
        #print['TEST1'],faces_list
        faces_list = cmds.filterExpand(faces_list, sm=34, expand=True)
        #print['TEST2'],faces_list

        all_faces = cmds.filterExpand(cmds.polyListComponentConversion(shape, toFace=True), sm=34, expand=True)

        difference = list(set(all_faces)-set(faces_list))
        cmds.delete(difference)
    #cmds.bakePartialHistory(shape, prePostDeformers=True)


def DetachSkinnedMeshByMat(shape, matList, newMeshSuffix=''):
    newShape = DuplicateSkinnedMesh(shape, newMeshSuffix)
    DeleteFacesByMat(shape, matList)
    DeleteFacesByMat(newShape, matList, True)
    return newShape
