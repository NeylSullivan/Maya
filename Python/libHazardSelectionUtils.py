import maya.cmds as cmds

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

def GetFacesByBitmapMask(shape, bitmapMaskPath):
    file_node = cmds.shadingNode("file", asTexture=True)
    cmds.setAttr('%s.fileTextureName' % file_node, bitmapMaskPath, type="string")
    cmds.select(clear=True)

    all_faces = cmds.filterExpand(cmds.polyListComponentConversion(shape, toFace=True), sm=34, expand=True)
    matched_faces = []

    for f in all_faces:
        center = GetFaceUVCenter(f)
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

def GetFacesOutsideCenterUVRange(pShape):
    cmds.select(clear=True)

    all_faces = cmds.filterExpand(cmds.polyListComponentConversion(pShape, toFace=True), sm=34, expand=True)
    matched_faces = []

    UVfrom = [0, 0]
    UVto = [1, 1]

    for f in all_faces:
        center = GetFaceUVCenter(f)

        if IsUvInRange(center, UVfrom, UVto): # Skip if in range
            continue
        matched_faces.append(f)

    return matched_faces

#def GetFacesInUVRange(pShape, pFrom=[0, 0], pTo=[1, 1]):
def GetFacesInUVRange(pShape, pFrom, pTo):
    cmds.select(clear=True)

    all_faces = cmds.filterExpand(cmds.polyListComponentConversion(pShape, toFace=True), sm=34, expand=True)
    matched_faces = []

    for f in all_faces:
        center = GetFaceUVCenter(f)

        if IsUvInRange(center, pFrom, pTo):
            matched_faces.append(f)

    return matched_faces

def GetFacesInUTile(pShape, pTileIndex):
    uvFrom = [0 + pTileIndex, 0]
    uvTo = [1 + pTileIndex, 1]
    matched_faces = GetFacesInUVRange(pShape, uvFrom, uvTo)
    cmds.select(matched_faces)
    return matched_faces
