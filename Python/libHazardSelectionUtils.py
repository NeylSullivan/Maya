import maya.cmds as cmds
import maya.api.OpenMaya as om
import libHazardMayaUtils as mayaUtils

reload(mayaUtils)

# Deprecated
def GetFaceUVCenter(face):
    uvs = cmds.filterExpand(cmds.polyListComponentConversion(face, toUV=True, border=True), sm=35, expand=True)
    uList = []
    vList = []
    for uv in uvs:
        UVValues = cmds.polyEditUV(uv, query=True)
        uList.append(UVValues[0])
        vList.append(UVValues[1])
        #print UVValues
    u = sum(uList) / len(uList)
    v = sum(vList) / len(vList)

    return [u, v]

 # Deprecated
def GetFacesByBitmapMask(shape, bitmapMaskPath):
    file_node = cmds.shadingNode("file", asTexture=True)
    cmds.setAttr('%s.fileTextureName' % file_node, bitmapMaskPath, type="string")
    cmds.select(clear=True)

    all_faces = cmds.filterExpand(cmds.polyListComponentConversion(shape, toFace=True), sm=34, expand=True)
    matched_faces = []

    for f in all_faces:
        center = GetFaceUVCenter(f) # !!! VERY SLOW !!! Can be optimized with maya.OpenMaya
        alpha = 0.0
        try:
            alpha = cmds.colorAtPoint(file_node, u=center[0], v=center[1]) #return array with one element
            alpha = alpha[0]
            #print alpha
        except BaseException:
            pass

        if alpha > 0.6:
            matched_faces.append(f)
    cmds.delete(file_node)
    cmds.select(clear=True)
    return matched_faces


def IsUvInRange(pInUV, pFrom, pTo):
    if pInUV[0] < pFrom[0]:
        return False
    if pInUV[1] < pFrom[1]:
        return False

    if pInUV[0] > pTo[0]:
        return False
    if pInUV[1] > pTo[1]:
        return False

    return True

#def GetFacesInUVRange(pShape, pFrom=[0, 0], pTo=[1, 1]):
def GetFacesInUVRange(pShape, pFrom, pTo, pInvertResult=False):
    nodeDagPath = om.MGlobal.getSelectionListByName(pShape).getDagPath(0)
    mfnMesh = om.MFnMesh(nodeDagPath)

    numFaces = mfnMesh.numPolygons

    matched_faces = []

    for faceIdx in range(numFaces):
        center = [0.0, 0.0]
        vtxCount = mfnMesh.polygonVertexCount(faceIdx)
        for vertIdx in range(vtxCount):
            vertUV = mfnMesh.getPolygonUV(faceIdx, vertIdx)
            center[0] += vertUV[0]
            center[1] += vertUV[1]

        # Find average
        center[0] /= vtxCount
        center[1] /= vtxCount

        if (IsUvInRange(center, pFrom, pTo) and not pInvertResult) or (not IsUvInRange(center, pFrom, pTo) and pInvertResult):
            matched_faces.append('{}.f[{}]'.format(pShape, faceIdx))

    return matched_faces

def GetFacesInUTile(pShape, pTileIndex):
    uvFrom = [0 + pTileIndex, 0]
    uvTo = [1 + pTileIndex, 1]
    matched_faces = GetFacesInUVRange(pShape, uvFrom, uvTo)
    cmds.select(matched_faces)
    return matched_faces

def GetFacesOutsideCenterUVRange(pShape):
    return GetFacesInUVRange(pShape, pFrom=[0.0, 0.0], pTo=[1.0, 1.0], pInvertResult=True)
