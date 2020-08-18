import os
import maya.cmds as cmds
import maya.mel as mel
from shutil import copyfile

def MakeDirectoryIfNotExist(pDir):
    if not os.path.exists(pDir):
        os.makedirs(pDir)

def GetSubdirNames(pParentDir):
    return [dI for dI in os.listdir(pParentDir) if os.path.isdir(os.path.join(pParentDir, dI))]

def IsDirStartWithPrefixes(pDir, pPrefixList):
    return pDir.startswith(tuple(pPrefixList))

def CopyFile(pSrc, pDst):
    pSrc = GetFriendlyPath(pSrc)
    pDst = GetFriendlyPath(pDst)

    copyfile(pSrc, pDst)

#replace back slashes with forward slashes
#its important for mel.eval!!!
def GetFriendlyPath(pPath):
    return os.path.normpath(pPath).replace("\\", "/")

def ExportObj(pObj, pDir, pFileNameWithoutExtension):
    if not os.path.exists(pDir):
        os.makedirs(pDir)

    exportPath = os.path.join(pDir, pFileNameWithoutExtension + '.obj')
    exportOptions = "groups=1; ptgroups=1; materials=1; smoothing=1; normals=1"
    cmds.select(pObj)
    result = cmds.file(exportPath, exportSelected=True, type='OBJexport', force=True, op=exportOptions)
    print 'Exporting: {}'.format(result)
    cmds.select(clear=True)

    # No need for .mtl files if exists
    try:
        os.remove(os.path.join(pDir, pFileNameWithoutExtension + '.mtl'))
    except BaseException:
        pass

def ExportSelectionFBX(pDir, pFileNameWithoutExtension, pBakeAnimation):
    MakeDirectoryIfNotExist(pDir)
    exportPath = os.path.join(pDir, pFileNameWithoutExtension + '.fbx')

    exportPath = GetFriendlyPath(exportPath)

    # set settings

    #mel.eval('FBXConvertUnitString cm')
    mel.eval('FBXExportFileVersion FBX201800')
    mel.eval('FBXExportUpAxis "Y"')
    mel.eval("FBXExportSmoothingGroups -v true")
    mel.eval("FBXExportHardEdges -v false") #true only for motionbuilder
    mel.eval("FBXExportTangents -v false")
    mel.eval("FBXExportInstances -v false")
    mel.eval("FBXExportInAscii -v false")
    mel.eval("FBXExportSmoothMesh -v false")
    mel.eval('FBXExportTriangulate -v false')

    mel.eval("FBXExportShapes -v true")
    mel.eval("FBXExportSkins -v true")

    if pBakeAnimation:
        mel.eval("FBXExportBakeComplexAnimation -v true")
        mel.eval("FBXExportConstraints -v false")
        #cmds.FBXProperty('Export|IncludeGrp|Animation', '-v', 1)
    else:
        mel.eval("FBXExportBakeComplexAnimation -v false")
        mel.eval("FBXExportConstraints -v true")
        #cmds.FBXProperty('Export|IncludeGrp|Animation', '-v', 0)

    mel.eval('FBXExportQuaternion -v "resample"')
    mel.eval("FBXExportInputConnections -v false")# Connections
    mel.eval("FBXProperty Export|IncludeGrp|InputConnectionsGrp|IncludeChildren -v false")#should not include children otherwise 'end_' joint exported to ue4
    mel.eval("FBXExportCameras -v false")# Cameras
    mel.eval("FBXExportLights -v false")# Lights
    mel.eval("FBXExportEmbeddedTextures -v false")# Embed Media


    # export selection
    mel.eval("FBXExport -f \"" + exportPath + "\" -s")

    print 'Exporting: {}'.format(exportPath)
