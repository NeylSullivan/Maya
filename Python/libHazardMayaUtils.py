import os
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import time
import winsound
import fnmatch
from contextlib import contextmanager
import libHazardMathUtils as hazmath

reload(hazmath)

@contextmanager
def DebugTimer(pName):
    start = time.clock()
    try:
        print '\n\nSTART:      *******     {}      *******\n'.format(pName)
        yield
    finally:
        end = time.clock()
        print '\nFINISH:     *******     {}      *******\n      Time taken {:.2f} seconds\n\n'.format(pName, end - start)


def CleanUnusedMaterials():
    print 'CleanUnusedMaterials()'
    mel.eval('MLdeleteUnused;')


# Much faster than polyColorPerVertex
# but pVerts should be a verts of SAME mesh
def SetVertexColors(pVerts, pColor):
    if not pVerts:
        return
    indices = []
    for vertData in pVerts:
        dagObjectTupple = om2.MGlobal.getSelectionListByName(vertData).getComponent(0)
        nodeDagPath = dagObjectTupple[0]
        comp = om2.MFnSingleIndexedComponent(dagObjectTupple[1])
        indices.extend(comp.getElements())

    colors = [om2.MColor(pColor)] * len(indices)
    mfnMesh = om2.MFnMesh(nodeDagPath)
    mfnMesh.setVertexColors(colors, indices)


# Find closest vertex to given uv coordinates
def GetVertexFromUV(pShape, pUV):
    mfnMesh = om.MFnMesh(GetDagPath(pShape))
    numFaces = mfnMesh.numPolygons()

    uUtil = om.MScriptUtil()
    uUtil.createFromDouble(0.0)
    uPtr = uUtil.asFloatPtr()

    vUtil = om.MScriptUtil()
    vUtil.createFromDouble(0.0)
    vPtr = vUtil.asFloatPtr()

    closestFaceIdx = -1
    closestFaceVertIdx = -1
    minLength = None

    for faceIdx in range(numFaces):
        vtxCount = mfnMesh.polygonVertexCount(faceIdx)
        for vertIdx in range(vtxCount):
            mfnMesh.getPolygonUV(faceIdx, vertIdx, uPtr, vPtr)
            vertUV = [om.MScriptUtil(uPtr).asFloat(), om.MScriptUtil(vPtr).asFloat()]

            thisLength = hazmath.GetDistance2D(vertUV, pUV)
            if minLength is None or thisLength < minLength:
                minLength = thisLength
                closestFaceIdx = faceIdx
                closestFaceVertIdx = vertIdx

    # Finally convert to object relative vertex index
    if closestFaceIdx > -1:
        vertexList = om.MIntArray()

        mfnMesh.getPolygonVertices(closestFaceIdx, vertexList)
        meshVertIdx = vertexList[closestFaceVertIdx]
        return '{}.vtx[{}]'.format(pShape, meshVertIdx)

    return None



#https://gist.github.com/HamtaroDeluxe/67a97305ffbe284e5f104d8b4f9eb0f2
#returns the closest vertex given a mesh and a position [x,y,z] in world space.
#Uses om.MfnMesh.getClosestPoint() returned face ID and iterates through face's vertices.
def GetClosestVertex(mayaMesh, pos):
    doubleArray = om.MScriptUtil()
    doubleArray.createFromList(pos, 3)
    mVector = om.MVector(doubleArray.asDoublePtr())#using MVector type to represent position

    mMesh = om.MFnMesh(GetDagPath(mayaMesh))
    pointA = om.MPoint(mVector)
    pointB = om.MPoint()
    space = om.MSpace.kWorld

    util = om.MScriptUtil()
    util.createFromInt(0)
    idPointer = util.asIntPtr()


    mMesh.getClosestPoint(pointA, pointB, space, idPointer)
    idx = om.MScriptUtil(idPointer).asInt()

    faceVerts = cmds.ls(cmds.polyListComponentConversion(mayaMesh+'.f[' + str(idx) + ']', ff=True, tv=True), flatten=True)#face's vertices list
    closestVert = None
    minLength = None
    for v in faceVerts:
        thisLength = hazmath.GetDistance(pos, cmds.pointPosition(v, world=True))
        if minLength is None or thisLength < minLength:
            minLength = thisLength
            closestVert = v
    return closestVert

def GetDagPath(nodeName):
    sel = om.MSelectionList()
    om.MGlobal.getSelectionListByName(nodeName, sel)

    dp = om.MDagPath()

    sel.getDagPath(0, dp)
    return dp


def UvCoordToWorld(U, V, mesh):

    mfnMesh = om.MFnMesh(GetDagPath(mesh))
    numFaces = mfnMesh.numPolygons()

    WSpoint = om.MPoint(0.0, 0.0, 0.0)

    util2 = om.MScriptUtil()
    util2.createFromList((U, V), 2)
    float2ParamUV = util2.asFloat2Ptr()

    for i in range(numFaces):
        try:
            mfnMesh.getPointAtUV(i, WSpoint, float2ParamUV, om.MSpace.kWorld)
            break #point is in poly
        except BaseException:
            continue #point not found!

    return [WSpoint[0], WSpoint[1], WSpoint[2]]


def NotifyWithSound():
    for i in range(1, 5):
        winsound.Beep(1000 + i * 5, 150)

def GetBorderFaces(mesh):
    cmds.select(clear=True)
    borderVertsList = GetBorderVertices(mesh)
    borderFacesList = cmds.polyListComponentConversion(borderVertsList, tf=True)
    return borderFacesList

def ManualTransferAttributesForBorderVerts(targetMesh, srcMesh):
    cmds.select(clear=True)
    borderVertsList = GetBorderVertices(targetMesh)
    borderVertsList = cmds.filterExpand(borderVertsList, sm=31, expand=True)

    bodySkinCluster = GetSkinCluster(srcMesh)
    genitaliaSkinCluster = GetSkinCluster(targetMesh)

    #transfer attributes manually
    for v in borderVertsList:
        pos = cmds.pointPosition(v, world=True)
        #print pos
        closestVert = GetClosestVertex(srcMesh, pos)
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


    cmds.bakePartialHistory(targetMesh, prePostDeformers=True)


def GetBorderVertices(mesh):
    cmds.select(clear=True)
    borderVertsList = []

    cmds.select(mesh)
    cmds.selectType(polymeshEdge=True)
    cmds.polySelectConstraint(mode=3, type=0x8000, where=1) # to get border vertices
    borderVerts = cmds.polyListComponentConversion(tv=True)
    borderVertsList.extend(borderVerts)
    cmds.polySelectConstraint(mode=0, sh=0, bo=0)
    cmds.select(clear=True)
    return borderVertsList

def SetAverageNormalsForBorderVertices(mesh):
    print 'SetAverageNormalsForBorderVertices(mesh = {0})'.format(mesh)
    borderVertsList = GetBorderVertices(mesh)
    cmds.select(borderVertsList)
    cmds.polyAverageNormal(distance=0.2)
    cmds.select(clear=True)


def ParentAllGeometryToWorld():
    print 'Parenting geometry to world'

    skinList = cmds.ls(type='skinCluster')
    meshes = set(sum([cmds.skinCluster(c, q=1, g=1) for c in skinList], []))
    for mesh in meshes:
        transformList = cmds.listRelatives(mesh, parent=True)
        for tf in transformList:
            if cmds.listRelatives(tf, parent=True):
                cmds.parent(tf, world=True)

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

def GetAllSkinClustersInfluencedByJoints(jointsList, bAllJointsRequired=False):
    if (jointsList is None) or (jointsList == ''):
        return []

    #convert argument to list if it's not
    if not isinstance(jointsList, list):
        jointsList = [jointsList]

    jointsSet = set(jointsList)

    outSkinList = []

    skinList = cmds.ls(type='skinCluster') or []
    for s in skinList:
        influencesSet = set(cmds.skinCluster(s, query=True, influence=True))
        if jointsSet.isdisjoint(influencesSet):
            continue #no shared elements

        if bAllJointsRequired and (not jointsSet.issubset(influencesSet)):
            continue #want all joints but not all presented in influencesSet
        outSkinList.append(s)

    return outSkinList

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


def ExportSkinning(skinData):
    with DebugTimer('Export skinning'):
        for sd in skinData:
            #print sd
            fileName = sd[0] + '_WEIGHTS.xml'
            cmds.deformerWeights(fileName, ex=True, deformer=sd[2])

def ImportSkinning(skinData, pDeleteFilesAfterImport=False):
    with DebugTimer('Import skinning'):
        xmlFilePaths = []
        for sd in skinData:
            #print sd
            cmds.skinCluster(sd[3], sd[0], name=sd[2], tsb=True)
            fileName = sd[0] + '_WEIGHTS.xml'
            filePath = cmds.deformerWeights(fileName, im=True, deformer=sd[2], method='index')
            if filePath:
                xmlFilePaths.append(filePath)

        if pDeleteFilesAfterImport:
            for filePath in xmlFilePaths:
                try:
                    os.remove(filePath)
                except BaseException:
                    print("Error while deleting file ", filePath)


def SetSkinMethodForAllSkinClusters(skinMethod):
    skinList = cmds.ls(type='skinCluster')
    for s in skinList:
        cmds.skinCluster(s, e=True, skinMethod=skinMethod)

def FindMatByWildcard(wildcard):
    shaders = cmds.ls(type="lambert")
    for mat in shaders:
        if fnmatch.fnmatch(mat, wildcard):
            return mat
    print 'Can`t find material {0}'.format(wildcard)
    return None

#by wildcard. only first matched material renamed
def RenameMaterial(originalName, newName):
    print 'Renaming material {0} to {1}'.format(originalName, newName)
    shaders = cmds.ls(type="lambert")
    for mat in shaders:
        #if mat == originalName:
        if fnmatch.fnmatch(mat, originalName):
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
                dagPose = cmds.listConnections(skin+'.bindPose', d=False, type='dagPose')
                if dagPose:
                    cmds.delete(dagPose)

                cmds.skinCluster(joints, shape, toSelectedBones=True)
                cmds.setAttr(skin+'.envelope', 1)

def ResetBindPoseForAllSkinClusters():
    with DebugTimer('Resetting bind pose'):
        skinList = cmds.ls(type='skinCluster')
        meshes = set(sum([cmds.skinCluster(c, q=1, g=1) for c in skinList], []))
        for mesh in meshes:
            transformList = cmds.listRelatives(mesh, parent=True)
            ResetBindPose(transformList)

def GetMeshFromSkinCluster(skinClusterName):
    shape = cmds.skinCluster(skinClusterName, q=True, geometry=True)[0]
    mesh = cmds.listRelatives(shape, parent=True)[0]
    return mesh

def GetHierarchy(rootJoint):
    root = cmds.ls(rootJoint, type="joint")
    if len(root) == 1:
        allHierarchy = cmds.listRelatives(root[0], allDescendents=True, type="joint")
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
            print '\tRenameJoint: {0} to {1}'.format(oldName, newName)
        else:
            print 'RenameJoint: {0} is not joint. Aborting renaming to {1}!'.format(oldName, newName)
    else:
        print 'RenameJoint: {0} is not exist. Aborting renaming to {1}!'.format(oldName, newName)


def FixMaxInfluencesForAllSkinClusters(maxInfluences):
    with DebugTimer('FixMaxInfluencesForAllSkinClusters'):
        cmds.select(clear=True)
        skinList = cmds.ls(type='skinCluster')
        for s in skinList:
            FixMaxInfluencesForSkinCluster(s, maxInfluences)
        cmds.select(clear=True)


def FixMaxInfluencesForSkinCluster(skinClusterName, maxInfluences):
    k_EPSILON = 0.001

    shape = cmds.skinCluster(skinClusterName, q=True, geometry=True)[0]
    mesh = cmds.listRelatives(shape, parent=True)[0]
    vertsNum = cmds.polyEvaluate(mesh, v=1)


    cmds.skinPercent(skinClusterName, mesh, pruneWeights=k_EPSILON)

    fixedCounter = 0

    for i in range(0, vertsNum):
        vertexName = mesh+'.vtx['+str(i)+']' #current vertex
        Weights = cmds.skinPercent(skinClusterName, vertexName, q=True, value=True, ignoreBelow=k_EPSILON)
        if(len(Weights)) > maxInfluences: # If (number of influences > max number of influences)
            fixedCounter += 1
            sortedWeights = sorted(Weights, reverse=True)
            PruneValue = sortedWeights[maxInfluences] + k_EPSILON
            cmds.skinPercent(skinClusterName, vertexName, pruneWeights=PruneValue)
    if fixedCounter > 0:
        resultMessage = 'Fixed {} vertices'.format(fixedCounter)
    else:
        resultMessage = 'No vertices to fix'

    print 'Skincluster "{}". Mesh: {} Target max influense: {} Verts num: {}. {}'.format(skinClusterName, mesh, maxInfluences, vertsNum, resultMessage)

def TransferJointWeights(oldJointName, newJointName):
    cmds.select(clear=True)
    skinList = cmds.ls(type='skinCluster')
    print ''
    print 'TransferJointWeights: Transfering weights from \'{}\' to \'{}\''.format(oldJointName, newJointName)
    for skinClusterName in skinList:
        cmds.select(clear=True)

        influences = cmds.skinCluster(skinClusterName, query=True, influence=True)
        if oldJointName not in influences:
            print 'TransferJointWeights: \'{}\' is NOT influenced by SOURCE joint \'{}\'. Skipping...'.format(skinClusterName, oldJointName)
            continue
        elif newJointName not in influences: #S hould be added to influences instead
            print 'TransferJointWeights: \'{}\' is NOT influenced by TARGET joint \'{}\'. Skipping...'.format(skinClusterName, newJointName)
            continue
        else:
            print 'TransferJointWeights: \'{}\' is influenced by joint \'{}\' Processing...'.format(skinClusterName, oldJointName)

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


        #print 'TransferJointWeights: Removing \'{}\' from influences of \'{}\''.format(oldJointName, skinClusterName)
        cmds.skinCluster(skinClusterName, e=True, removeInfluence=oldJointName)

    print 'TransferJointWeights: Done'



def DestroyMiddleJoint(jointName):
    print ''

    if not cmds.objExists(jointName):
        print 'DestroyMiddleJoint: joint \'{}\' is not exist: Aborting'.format(jointName)
        return

    parents = cmds.listRelatives(jointName, parent=True)
    if parents is None:
        print 'DestroyMiddleJoint: Joint \'{}\' parent is None. Aborting'.format(jointName)
        return
    parent = parents[0]

    print 'DestroyMiddleJoint: Processing joint \'{}\' with parent \'{}\''.format(jointName, parent)
    TransferJointWeights(jointName, parent)

    children = cmds.listRelatives(jointName)
    if children is not None:
        for child in children:
            print 'DestroyMiddleJoint: parenting \'{}\' to \'{}\''.format(child, parent)
            cmds.parent(child, parent)

    print 'DestroyMiddleJoint: unparenting and destroying \'{}\''.format(jointName)
    cmds.parent(jointName, world=True)
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


def DestroyUnusedJoints(pbDestroyToes):
    with DebugTimer('DestroyUnusedJoints'):
        DestroyMiddleJoint('lMetatarsals')
        DestroyMiddleJoint('rMetatarsals')
        DestroyMiddleJoint('pelvis')
        if pbDestroyToes:
            DestroyJointChildren('lToe')
            DestroyJointChildren('rToe')

def CleanUnusedInfluenses(skinCluster):
    cmds.select(clear=True)
    weightedInfls = cmds.skinCluster(skinCluster, q=True, wi=True)
    #print weightedInfls
    unusedList = []
    for wi in weightedInfls:
        cmds.skinCluster(skinCluster, e=True, selectInfluenceVerts=wi)
        sel = cmds.ls(selection=True, flatten=True)
        onlyVertices = cmds.filterExpand(sel, sm=31)
        #print onlyVertices
        if not onlyVertices:
            #print wi + ' REMOVE'
            cmds.skinCluster(skinCluster, e=True, removeInfluence=wi)
            unusedList.append(wi)

    resultMessage = ''
    if len(unusedList) > 10:
        resultMessage = '{}... + {} joints'.format(unusedList[:10], len(unusedList) - 10)
    elif unusedList:
        resultMessage = unusedList
    print '\tFor {0} removed {1} joints {2}'.format(skinCluster, len(unusedList), resultMessage)

def CleanUnusedInfluensesOnAllSkinClusters():
    cmds.select(clear=True)
    skinList = cmds.ls(type='skinCluster')
    print 'Clening unused influenses for {0} skinclusters'.format(len(skinList))
    for s in skinList:
        CleanUnusedInfluenses(s)
    cmds.select(clear=True)

def GetBlendShape(mesh):
    if cmds.nodeType(mesh) in ('mesh', 'nurbsSurface', 'nurbsCurve'):
        shapes = [mesh]
    else:
        shapes = cmds.listRelatives(mesh, shapes=True, path=True)

    for shape in shapes:
        history = cmds.listHistory(shape, groupLevels=True, pruneDagObjects=True)
        if not history:
            continue
        blendShapes = cmds.ls(history, type='blendShape')
        if blendShapes:
            return blendShapes[0]
    return None

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

def GetSGfromShader(shader=None):
    if shader:
        if cmds.objExists(shader):
            sgq = cmds.listConnections(shader, d=True, et=True, t='shadingEngine')
            if sgq:
                return sgq[0]

    return None

def AssignObjectListToShader(objList=None, shader=None):
    """
    Assign the shader to the object list
    arguments:
        objList: list of objects or faces
    """
    # assign selection to the shader
    shaderSG = GetSGfromShader(shader)
    if objList:
        if shaderSG:
            cmds.sets(objList, e=True, forceElement=shaderSG)
        else:
            print 'The provided shader didn\'t returned a shaderSG'
    else:
        print 'Please select one or more objects'

def GetFacesByMatsWildcard(shape, matWildcard):
    shapeMats = cmds.listConnections(cmds.listHistory(shape, f=1), type='lambert')

    if not shapeMats:
        return []

    faces_list = []

    matchingMats = fnmatch.filter(shapeMats, matWildcard)
    for mat in matchingMats:
        faces_list.extend(GetFacesByMat(shape, mat))

    return faces_list


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

def ArrangeUVByMatWildcard(shape, mat, su=1.0, sv=1.0, u=0.0, v=0.0):
    newMat = FindMatByWildcard(mat)
    if newMat:
        ArrangeUVByMat(shape, newMat, su, sv, u, v)

def ArrangeUVByMat(shape, mat, su=1.0, sv=1.0, u=0.0, v=0.0):
    print 'ArrangeUVByMat shape={0} mat={1} scale=[{2}, {3}], translate=[{4}, {5}]'.format(shape, mat, su, sv, u, v)
    faces = GetFacesByMat(shape, mat)
    cmds.select(faces)
    cmds.select(cmds.polyListComponentConversion(tuv=True), r=True)
    cmds.polyEditUV(su=su, sv=sv)
    cmds.polyEditUV(u=u, v=v)
    cmds.select(clear=True)

def AppendShadingGroupByMatWildcard(shape, matTo, matFrom):
    matTo = FindMatByWildcard(matTo)
    matFrom = FindMatByWildcard(matFrom)
    if matTo and matFrom:
        AppendShadingGroupByMat(shape, matTo, matFrom)


def AppendShadingGroupByMat(shape, matTo, matFrom):
    shapeMats = cmds.listConnections(cmds.listHistory(shape, f=1), type='lambert') or []
    if matTo not in shapeMats:
        print 'AppendShadingGroupByMat: material={} not in shape={}. Aborting.'.format(matTo, shape)
        return

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

def GetShapeTransform(meshTransformOrShape):
    if cmds.nodeType(meshTransformOrShape) == 'transform':
        return meshTransformOrShape
    else:
        #probably shape
        return cmds.listRelatives(meshTransformOrShape, parent=True, type='transform')[0]

def GetMultipleShapesTransforms(meshTransformOrShapesList):
    if not meshTransformOrShapesList:
        print 'WARNING: GetMultipleShapesTransforms() meshTransformOrShapesList is None'
        return None
    transformsSet = set()
    for s in meshTransformOrShapesList:
        transformsSet.add(GetShapeTransform(s))

    return list(transformsSet)


def DuplicateSkinnedMesh(shape, newMeshSuffix=''):
    shapeTransform = GetShapeTransform(shape)
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

def IsShapeContainAnyMat(shape, matList):
    for m in matList:
        faces = GetFacesByMat(shape, m)
        if faces: #not empty
            return True #one material is enought
    return False

def DetachSkinnedMeshByMat(shape, matList, newMeshSuffix=''):
    print 'Detaching from skinned mesh {0} materials {1} with new name {0}{2}'.format(shape, matList, newMeshSuffix)
    if IsShapeContainAnyMat(shape, matList):
        newShape = DuplicateSkinnedMesh(shape, newMeshSuffix)
        DeleteFacesByMat(shape, matList)
        DeleteFacesByMat(newShape, matList, True)
        return newShape
    print 'Aborted - no materials in shape'
    return None

def FindMeshByWildcard(wildcard, preferShapeWithMaxVertices=False, checkForMatWithName=None):
    print 'FindMeshByWildcard(wildcard={0}, preferShapeWithMaxVertices={1}, checkForMatWithName={2})'.format(wildcard, preferShapeWithMaxVertices, checkForMatWithName)
    shapes = cmds.ls(wildcard, shapes=True, objectsOnly=True, long=False)
    if not shapes: #wildcard can be exact transform name
        transforms = cmds.ls(wildcard, transforms=True, objectsOnly=True, long=False) #try to find transforms with shapes
        if transforms:
            shapes = cmds.listRelatives(transforms, type='shape')

    if not shapes:
        return None
    meshes = cmds.listRelatives(shapes, parent=True, type='transform')


    result = None

    if meshes:
        result = meshes[0] #if no special check, set (and return at end of function) first finded from list


    meshes = list(set(meshes)) #unique only

    if checkForMatWithName:
        meshesWithMat = []
        for m in meshes:
            shapeMats = cmds.listConnections(cmds.listHistory(m, f=1), type='lambert') or []
            if checkForMatWithName in shapeMats:
                meshesWithMat.append(m)
        meshes = meshesWithMat

    if meshes:
        result = meshes[0]

    if result and meshes and preferShapeWithMaxVertices:
        for m in meshes:
            resultVertexNum = cmds.polyEvaluate(result, vertex=True)
            currentVertexNum = cmds.polyEvaluate(m, vertex=True)
            if currentVertexNum > resultVertexNum:
                result = m

    return result
