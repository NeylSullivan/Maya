import os
import maya.cmds as cmds
import libHazardMayaUtils
from libHazardMayaUtils import DebugTimer
reload(libHazardMayaUtils)


SRC_DIR = 'e:\\blackops\\__MODELS\\Characters\\Female\\Base\\SRC\\'

SRC_BASE_MESH_NAME = 'DAZ_Base'
SRC_SUBD_MESH_NAME = 'DAZ_SubD1'

PROCESSED_BASE_MESH_NAME = 'MAYA_Base'
PROCESSED_SUBD_MESH_NAME = 'MAYA_SubD1'

def ProcessSrcDir():
    print 'Processing directory: {}'.format(SRC_DIR)
    baseMeshFile = os.path.join(SRC_DIR, SRC_BASE_MESH_NAME + '.obj')
    baseMeshExist = os.path.exists(baseMeshFile)
    print 'Base mesh: {} Exist: {}'.format(baseMeshFile, baseMeshExist)

    if not baseMeshExist:
        print 'ABORTED: no base mesh found '
        return

    subdMeshFile = os.path.join(SRC_DIR, SRC_SUBD_MESH_NAME + '.obj')
    subdMeshExist = os.path.exists(subdMeshFile)

    print 'SubD mesh: {} Exist: {}'.format(subdMeshFile, subdMeshExist)

    if subdMeshExist:
        ProcessMeshesPair(baseMeshFile, subdMeshFile, SRC_DIR)


    print ''
    print '          **************          Processing subdirectories          **************'
    print ''

    subDirs = [dI for dI in os.listdir(SRC_DIR) if os.path.isdir(os.path.join(SRC_DIR, dI))]

    for subDir in subDirs:
        fullSubdirPath = os.path.join(SRC_DIR, subDir)
        subdMeshFile = os.path.join(fullSubdirPath, SRC_SUBD_MESH_NAME + '.obj')
        subdMeshExist = os.path.exists(subdMeshFile)
        print 'Dir: {} SubD mesh: {} Exist: {}'.format(subDir, subdMeshFile, subdMeshExist)
        if not subdMeshExist:
            print 'SKIPPING...'
        else:
            ProcessMeshesPair(baseMeshFile, subdMeshFile, fullSubdirPath)


    print 'Done'



def ProcessMeshesPair(pBaseFile, pSubdFile, pOutputDir):

    cmds.file(newFile=True, force=True)
    baseMesh = cmds.file(pBaseFile, i=True, returnNewNodes=True)[0]
    baseMesh = cmds.rename(baseMesh, 'BaseMesh')

    subdMesh = cmds.file(pSubdFile, i=True, returnNewNodes=True)[0]
    subdMesh = cmds.rename(subdMesh, 'SubdMesh')
    cmds.xform(subdMesh, absolute=True, translation=[0, 0, 100])

    with DebugTimer('Processing base resolution'):
        cmds.transferAttributes(subdMesh, baseMesh, transferPositions=1, transferNormals=0, sampleSpace=3)
        cmds.delete(baseMesh, constructionHistory=True)

    #Export baseMesh Here
    ExportObj(baseMesh, pOutputDir, PROCESSED_BASE_MESH_NAME)

    with DebugTimer('Processing SubD 1 resolution'):
        # Settings are important for keeping same vertex order
        # ch=1, ost=0, khe=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1, \sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=1, kb=1, c=1, ocr=0, dpe=1, sl=1
        cmds.polySmooth(baseMesh, ost=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1,\
             sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=1, kb=1, c=1, ocr=0, dpe=1, sl=1)
        cmds.delete(baseMesh, constructionHistory=True)
        cmds.transferAttributes(subdMesh, baseMesh, transferPositions=1, transferNormals=0, sampleSpace=3)
        cmds.delete(baseMesh, constructionHistory=True)

    ExportObj(baseMesh, pOutputDir, PROCESSED_SUBD_MESH_NAME)

def ExportObj(pObj, pDir, pFileNameWithoutExtension):
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
