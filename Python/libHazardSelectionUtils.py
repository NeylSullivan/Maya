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
