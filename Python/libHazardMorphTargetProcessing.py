import os
import maya.cmds as cmds
import maya.mel as mel
import libHazardMayaUtils
import libHazardSelectionUtils
import libHazardSkeletonSelectionUtils as skelUtils
import DAZtoUE4_OptimizeSkeleton as dazToUe
from shutil import copyfile
from libHazardMayaUtils import DebugTimer
reload(libHazardMayaUtils)
reload(libHazardSelectionUtils)
reload(skelUtils)
#reload(dazToUe)

ROOT_DIR = 'e:\\blackops\\__MODELS\\Characters\\Female\\Base\\AUTOMATION'
SRC_DIR = 'SRC'
INTERMEDIATE_DIR = 'INTERMEDIATE'
OUTPUT_DIR = 'OUT'

SRC_BASE_MESH_NAME = 'Base'
SRC_SUBD_MESH_NAME = 'SubD'

PROCESSED_BASE_MESH_NAME = 'Base'
PROCESSED_SUBD_MESH_NAME = 'SubD'

ANIM_PREFIXES = ['PROPANIM_']

def GetSrcFullPath(inRootDirectory):
    if inRootDirectory is None:
        inRootDirectory = ROOT_DIR
    return os.path.join(inRootDirectory, SRC_DIR)

def GetIntermediateFullPath(inRootDirectory):
    if inRootDirectory is None:
        inRootDirectory = ROOT_DIR
    return os.path.join(inRootDirectory, INTERMEDIATE_DIR)

def ProcessSrcDir(inRootDirectory=None, inBeepAfterComplete=True):
    if inRootDirectory is None:
        print 'ProcessSrcDir: inRootDirectory is None. Using Default: {}'.format(ROOT_DIR)
    srcFullPath = GetSrcFullPath(inRootDirectory)
    with DebugTimer('Processing directory: {}'.format(srcFullPath)):
        baseMeshFile = os.path.join(srcFullPath, SRC_BASE_MESH_NAME + '.obj')
        baseMeshExist = os.path.exists(baseMeshFile)
        print 'Base mesh: {} Exist: {}'.format(baseMeshFile, baseMeshExist)

        if not baseMeshExist:
            print 'ABORTED: no base mesh found '
            return

        subdMeshFile = os.path.join(srcFullPath, SRC_SUBD_MESH_NAME + '.obj')
        subdMeshExist = os.path.exists(subdMeshFile)

        print 'SubD mesh: {} Exist: {}'.format(subdMeshFile, subdMeshExist)

        if subdMeshExist:
            ProcessMeshesPair(baseMeshFile, subdMeshFile, GetIntermediateFullPath(inRootDirectory))


        print ''
        print '          **************          Processing subdirectories          **************'
        print ''

        subDirs = [dI for dI in os.listdir(srcFullPath) if os.path.isdir(os.path.join(srcFullPath, dI))]

        for subDir in subDirs:
            #MTD_ Morph Target Dynamic
            #MTB_ Morph Target Baked
            #MTTD_ Morph Target Transformed Dynamic
            #MTTB_ Morph Target Transformed Baked
            morphTargetPrefixes = ['MTD_', 'MTB_', 'MTTD_', 'MTTB_']
            dirStartsWithPrefix = subDir.startswith(tuple(morphTargetPrefixes)) 
            if not dirStartsWithPrefix:
                print 'Skipping Dir: {} as it not Morph Target directory (checked for prefixes: {})'.format(subDir, morphTargetPrefixes)
                continue

            fullSubdirPath = os.path.join(srcFullPath, subDir)
            subdMeshFile = os.path.join(fullSubdirPath, SRC_SUBD_MESH_NAME + '.obj')
            subdMeshExist = os.path.exists(subdMeshFile)
            print 'Dir: {} SubD mesh: {} Exist: {}'.format(subDir, subdMeshFile, subdMeshExist)
            if not subdMeshExist:
                print 'SKIPPING...'
            else:
                fullOutputPath = os.path.join(GetIntermediateFullPath(inRootDirectory), subDir)
                ProcessMeshesPair(baseMeshFile, subdMeshFile, fullOutputPath)

    print 'Done'
    if inBeepAfterComplete:
        libHazardMayaUtils.NotifyWithSound()

def TransferAttributesManuallyUVSpace(pSourceShape, pTargetFaces):
    cmds.select(clear=True)
    targetFacesUvVerts = cmds.ls(cmds.polyListComponentConversion(pTargetFaces, ff=True, toUV=True, uvShell=True), flatten=True)

    for mapVert in targetFacesUvVerts:
        uv = cmds.polyEditUV(mapVert, query=True )
        targetVert = cmds.polyListComponentConversion(mapVert, fromUV=True, tv=True)
        sourceShapeVert = libHazardMayaUtils.GetVertexFromUV(pSourceShape, uv)
        sourcePos = cmds.pointPosition(sourceShapeVert, local=True)
        #print sourceShapeVert
        cmds.xform(targetVert, translation=sourcePos, objectSpace=True)

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

        #Transfer eyesockets vertices manually to fix 'spikes' error
        eyeSocketFaces = libHazardSelectionUtils.GetFacesInUVRange('BaseMesh', pFrom=[0.3, 0.9], pTo=[0.7, 1])
        tempShape = cmds.duplicate(subdMesh, name='Temp'+'SubdMesh')[0] #temp shape with high poly eye sockets only to speed up calculations
        cmds.xform(tempShape, absolute=True, translation=[0, 0, 150])
        subdEyeSocketFaces = libHazardSelectionUtils.GetFacesInUVRange(tempShape, pFrom=[0.3, 0.8], pTo=[0.7, 1], pInvertResult=True)
        cmds.delete(subdEyeSocketFaces)
        cmds.delete(tempShape, constructionHistory=True)
        TransferAttributesManuallyUVSpace(tempShape, eyeSocketFaces)
        cmds.delete(tempShape)

        cmds.delete(baseMesh, constructionHistory=True)

    #Export baseMesh Here
    ExportObj(baseMesh, pOutputDir, PROCESSED_BASE_MESH_NAME)

    with DebugTimer('Processing SubD resolution'):
        # Settings are important for keeping same vertex order
        # ch=1, ost=0, khe=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1, \sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=1, kb=1, c=1, ocr=0, dpe=1, sl=1
        cmds.polySmooth(baseMesh, ost=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1,\
             sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=1, kb=1, c=1, ocr=0, dpe=1, sl=1)
        cmds.delete(baseMesh, constructionHistory=True)
        cmds.transferAttributes(subdMesh, baseMesh, transferPositions=1, transferNormals=0, sampleSpace=3)
        cmds.delete(baseMesh, constructionHistory=True)

    ExportObj(baseMesh, pOutputDir, PROCESSED_SUBD_MESH_NAME)

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
    if not os.path.exists(pDir):
        os.makedirs(pDir)
    exportPath = os.path.join(pDir, pFileNameWithoutExtension + '.fbx')

    #replace back slashes with forward slashes
    #its important for mel.eval!!!
    exportPath = os.path.normpath(exportPath)
    if exportPath.partition("\\")[2] != "":
        exportPath = exportPath.replace("\\", "/")

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
    else:
        mel.eval("FBXExportBakeComplexAnimation -v false")
        mel.eval("FBXExportConstraints -v true")

    mel.eval('FBXExportQuaternion -v "resample"')
    mel.eval("FBXExportInputConnections -v false")# Connections
    mel.eval("FBXExportCameras -v false")# Cameras
    mel.eval("FBXExportLights -v false")# Lights
    mel.eval("FBXExportEmbeddedTextures -v false")# Embed Media
    
    
    # export selection
    mel.eval("FBXExport -f \"" + exportPath + "\" -s")

    print 'Exporting: {}'.format(exportPath)

def ProcessAnimDir(inRootDirectory, subDir, fullOutputPath):
    srcFullPath = GetSrcFullPath(inRootDirectory)
    fullSubdirPath = os.path.join(srcFullPath, subDir)
    animFile = os.path.join(fullSubdirPath, 'Animation.fbx')
    animFileExist = os.path.exists(animFile)
    print 'Dir: {} Anim File: {} Exist: {}'.format(subDir, animFile, animFileExist)
    if not animFileExist:
        print 'SKIPPING...'
        return

    cmds.file(newFile=True, force=True)
    cmds.file(animFile, pr=1, rpr="Animation", ignoreVersion=1, i=1, type="FBX", importFrameRate=True, importTimeRange="override", ra=True, rdn=1, mergeNamespacesOnClash=False, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")
    dazToUe.CreateOptimizedSkeletonOnlyAndRetargetAnim(bFilterCurves=True, inBeepAfterComplete=False)
    #export
    outputFileName = subDir
    #strip prefix
    for prefix in ANIM_PREFIXES:
        if outputFileName.startswith(prefix):
            outputFileName = outputFileName[len(prefix):]

    cmds.select(all=True, hierarchy=True)
    ExportSelectionFBX(pDir=fullOutputPath, pFileNameWithoutExtension='A_'+outputFileName, pBakeAnimation=True)
    cmds.select(clear=True)

    #copy txt file with pose names iw exist
    descriptionFile = os.path.join(fullSubdirPath, 'ExportNames.txt')
    if(os.path.exists(descriptionFile)):
        descriptionFullOutputPath = os.path.join(fullOutputPath,  'A_' + outputFileName + '.txt')
        #print descriptionFile
        #print descriptionFullOutputPath
        copyfile(descriptionFile, descriptionFullOutputPath)


    intermediateDir = GetIntermediateFullPath(inRootDirectory)
    if not os.path.exists(intermediateDir):
        os.makedirs(intermediateDir)

    #save maya file for later use
    saveAnimPath = os.path.join(intermediateDir,  'A_' + outputFileName + '.mb')
    cmds.file( rename=saveAnimPath )
    cmds.file(save=1, options="v=0;", f=1)



def PerformFullBatchProcessing(inRootDirectory=None):
    if inRootDirectory is None:
        print 'PerformFullbatchProcessing: inRootDirectory is None. Using Default: {}'.format(ROOT_DIR)
        inRootDirectory = ROOT_DIR
    
    srcFullPath = GetSrcFullPath(inRootDirectory)
    with DebugTimer('PerformFullBatchProcessing: Processing directory: {}'.format(srcFullPath)):
        #process morphs
        ProcessSrcDir(inRootDirectory, inBeepAfterComplete=False)

        #create output directory
        fullOutputPath = os.path.join(inRootDirectory, OUTPUT_DIR)
        if not os.path.exists(fullOutputPath):
            os.makedirs(fullOutputPath)

        #process animations
        subDirs = [dI for dI in os.listdir(srcFullPath) if os.path.isdir(os.path.join(srcFullPath, dI))]

        for subDir in subDirs:
            dirStartsWithPrefix = subDir.startswith(tuple(ANIM_PREFIXES)) 
            if not dirStartsWithPrefix:
                print 'PerformFullBatchProcessing: Skipping Dir: {} as it not ANIMATION directory (checked for prefixes: {})'.format(subDir, ANIM_PREFIXES)
                continue
            
            ProcessAnimDir(inRootDirectory, subDir, fullOutputPath)
    
        #end animations processing

        #finally process main meshes
        baseFile = os.path.join(srcFullPath, 'Base.fbx')
        baseFileExist = os.path.exists(baseFile)
        print 'PerformFullBatchProcessing: Final Mesh processing Dir: {} Anim File: {} Exist: {}'.format(srcFullPath, baseFile, baseFileExist)
        if not baseFileExist:
            print 'SKIPPING...'
            return

        cmds.file(newFile=True, force=True)
        cmds.file(baseFile, pr=1, rpr="Animation", ignoreVersion=1, i=1, type="FBX", importFrameRate=True, importTimeRange="override", ra=True, rdn=1, mergeNamespacesOnClash=False, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")
        dazToUe.OptimizeSkeleton(pbCollapseToes=False, pLoadExternalBaseMesh=True, pLoadExternalMorphs=True, pLoadExternalUVs=True, pCreateIKConstraints=True, inBeepAfterComplete=False)


        #recognize gender
        baseMeshName = 'Generic'
        if libHazardMayaUtils.FindMeshByWildcard('Female*'):
            baseMeshName = 'Female'
        elif libHazardMayaUtils.FindMeshByWildcard('Male*'):
            baseMeshName = ('Male')

        
        #export rig for 3ds max, motionbuilder etc (with end bones)
        cmds.select(all=True, hierarchy=True)
        ExportSelectionFBX(pDir=fullOutputPath, pFileNameWithoutExtension='RIG_'+baseMeshName, pBakeAnimation=False)
        cmds.select(clear=True)


        #export mesh(meshes) for ue4 (without end bones)
        body = libHazardMayaUtils.FindMeshByWildcard(baseMeshName + 'Body')
        eyelashes = libHazardMayaUtils.FindMeshByWildcard(baseMeshName + 'Eyelashes')
        eyes = libHazardMayaUtils.FindMeshByWildcard(baseMeshName + 'Eyes')

        meshesToExport = []
        if body: meshesToExport.append(body)
        if eyes: meshesToExport.append(eyes)
        if eyelashes: meshesToExport.append(eyelashes)

        if meshesToExport:
            cmds.select(meshesToExport)
            skelUtils.SelectJointsForSelectedMeshes(bKeepSelection=True, bIncludeSpecialJoints=True, bIncludeIKJoints=True)
            ExportSelectionFBX(pDir=fullOutputPath, pFileNameWithoutExtension='SK_'+baseMeshName, pBakeAnimation=True)
            cmds.select(clear=True)
        else:
            print 'ERROR: Nothing to export as {}'.format(baseMeshName)
        

        #save maya file for later use
        intermediateDir = GetIntermediateFullPath(inRootDirectory)
        saveFilePath = os.path.join(intermediateDir,  'BaseProcessed.mb')
        cmds.file( rename=saveFilePath )
        cmds.file(save=1, options="v=0;", f=1)
        #end mesh processing
    
    libHazardMayaUtils.NotifyWithSound()