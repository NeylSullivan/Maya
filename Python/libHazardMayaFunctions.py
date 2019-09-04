import maya.cmds as cmds
import maya.mel as mm

def CleanUnusedInfluenses(skinCluster):
    cmds.select(clear=True)
    weightedInfls = cmds.skinCluster(skinCluster, q=True, wi=True)
    print weightedInfls
    for wi in weightedInfls:
        cmds.skinCluster(skinCluster, e=True, selectInfluenceVerts=wi)
        selected = cmds.ls(sl=True)
        if len(selected)<=1:
            print wi + ' REMOVE'
            cmds.skinCluster(skinCluster, e=True, removeInfluence=wi)
            
def CleanUnusedInfluensesOnAllSkinClusters():
    cmds.select(clear=True)
    skinList = cmds.ls(type='skinCluster')
    for s in skinList:
        CleanUnusedInfluenses(s)
    cmds.select(clear=True)    

def GetSkinCluster(mesh):
    if cmds.nodeType(mesh) in ('mesh','nurbsSurface','nurbsCurve'):
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
    shapeMats = cmds.listConnections(cmds.listHistory(shape, f=1),type='lambert')
    if mat not in shapeMats:
        print 'GetFacesByMat: Material {0} not in shape {1}'.format(mat,shape)
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
        prefix = all_faces[0].split( '.' )[ 0 ] + '.f'
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
    cmds.select(cmds.polyListComponentConversion(tuv = True), r = True)
    cmds.polyEditUV(su=su, sv=sv)
    cmds.polyEditUV(u=u, v=v)
    cmds.select(clear=True)

def AppendShadingGroupByMat(shape, matTo, matFrom):
    targetShadingGroup = cmds.listConnections(matTo, type='shadingEngine')[0]
    fromFaces = GetFacesByMat(shape, matFrom)
    print 'AppendShadingGroupByMat shape={0} to={1} from={2}'.format(shape, matTo, matFrom)
    cmds.select(fromFaces)
    cmds.sets( e=True, forceElement=targetShadingGroup)
    cmds.select(clear=True)

def FindShapeByMat(mat):
    print 'Searching for shape with mat={0}'.format(mat)
    shapes = cmds.ls(geometry=True)
    #print shapes
    for shape in shapes:
        shapeMats = cmds.listConnections(cmds.listHistory(shape, f=1),type='lambert') or []
        if mat in shapeMats:
            return shape
        #print shapeMats
    print 'Could`nt find requested shape'
    return None


def DuplicateSkinnedMesh(shape, newMeshSuffix =''):
    shapeTransform = cmds.listRelatives(shape, parent = True, type='transform')[0]
    oldSkinCluster = GetSkinCluster(shapeTransform)
    oldJoints = cmds.skinCluster(oldSkinCluster, query=True, influence=True)
    #print oldJoints 

    newShape = cmds.duplicate(shape, name = shapeTransform + newMeshSuffix)[0]
    
    newSkinCluster = cmds.skinCluster(newShape, oldJoints, name=oldSkinCluster + newMeshSuffix)[0]
    #print newSkinCluster
    cmds.copySkinWeights (destinationSkin=newSkinCluster, sourceSkin=oldSkinCluster, noMirror=True, sa ="closestPoint", ia ="name")
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
    pass

def DetachSkinnedMeshByMat(shape, matList, newMeshSuffix=''):
    newShape = DuplicateSkinnedMesh(shape, newMeshSuffix)
    DeleteFacesByMat(shape, matList)
    DeleteFacesByMat(newShape, matList, True)
    #remove unused influences right now
    #skinCluster = GetSkinCluster(newShape)
    #Clean(skinCluster)
    return newShape


