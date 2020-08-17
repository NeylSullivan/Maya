import os
import maya.cmds as cmds
import libHazardMayaUtils
from libHazardMayaUtils import DebugTimer
import libHazardSelectionUtils
import libHazardSkeletonSelectionUtils as skelUtils
import DAZtoUE4_OptimizeSkeleton as dazToUe
import libHazardFileUtils as fileUtils
import libHazardEnvironment as env
reload(libHazardMayaUtils)
reload(libHazardSelectionUtils)
reload(skelUtils)
reload(fileUtils)
reload(env)
#reload(dazToUe)

def ShouldProcessAssets(pSrc, pDst, pForceFullRebuild, pPrintReason=True):
    if pPrintReason:
        print '\nShouldProcessAssets: pSrc={} pDst={}'.format(pSrc, pDst)

    #cannot process without source
    if not os.path.exists(pSrc):
        if pPrintReason:
            print 'ShouldProcessAssets:False, Src File Not Exist\n'
        return False

    #we requested full reprocessing
    if pForceFullRebuild:
        if pPrintReason:
            print 'ShouldProcessAssets:True, Forced Full Reprocessing\n'
        return True

    #destination file not exist. we need to create it!
    if not os.path.exists(pDst):
        if pPrintReason:
            print 'ShouldProcessAssets:True, Dest File Not Exist\n'
        return True

    #now compare modification time for both files
    srcModificationTime = os.path.getmtime(pSrc)
    dstModificationTime = os.path.getmtime(pDst)
    if srcModificationTime > dstModificationTime:
        if pPrintReason:
            print 'ShouldProcessAssets:True, Dest File Outdated\n'
        return True

    if pPrintReason:
        print 'ShouldProcessAssets:False, Dest File Is Exist and Up-to-date\n'
    return False

def PreprocessMorphTargets(pForceFullRebuild=True, inBeepAfterComplete=True):
    with DebugTimer('Processing directory: {}'.format(env.GetSrcFullPath())):
        baseMeshFile = os.path.join(env.GetSrcFullPath(), env.SRC_BASE_MESH_NAME + '.obj')
        baseMeshExist = os.path.exists(baseMeshFile)
        print 'Base mesh: {} Exist: {}'.format(baseMeshFile, baseMeshExist)

        if not baseMeshExist:
            print 'ABORTED: no base mesh found '
            return

        subdMeshFile = os.path.join(env.GetSrcFullPath(), env.SRC_SUBD_MESH_NAME + '.obj')
        subdMeshExist = os.path.exists(subdMeshFile)

        print 'SubD mesh: {} Exist: {}'.format(subdMeshFile, subdMeshExist)

        if subdMeshExist:
            checkedOutputFile = os.path.join(env.GetIntermediateFullPath(), env.PROCESSED_BASE_MESH_NAME + '.obj')
            
            if ShouldProcessAssets(subdMeshFile, checkedOutputFile, pForceFullRebuild):
                ProcessMeshesPair(baseMeshFile, subdMeshFile, env.GetIntermediateFullPath())

        print ''
        print '          **************          Processing subdirectories          **************'
        print ''

        subDirs = fileUtils.GetSubdirNames(env.GetSrcFullPath())

        for subDir in subDirs:
            if not fileUtils.IsDirStartWithPrefixes(subDir, env.MORPH_TARGET_PREFIXES):
                print 'Skipping Dir: {} as it not Morph Target directory (checked for prefixes: {})'.format(subDir, env.MORPH_TARGET_PREFIXES)
                continue

            fullSubdirPath = os.path.join(env.GetSrcFullPath(), subDir)
            subdMeshFile = os.path.join(fullSubdirPath, env.SRC_SUBD_MESH_NAME + '.obj')
            subdMeshExist = os.path.exists(subdMeshFile)
            print 'Dir: {} SubD mesh: {} Exist: {}'.format(subDir, subdMeshFile, subdMeshExist)
            if not subdMeshExist:
                print 'SKIPPING...'
            else:
                fullOutputPath = os.path.join(env.GetIntermediateFullPath(), subDir)
                checkedOutputFile=os.path.join(fullOutputPath, env.PROCESSED_BASE_MESH_NAME + '.obj')
                
                if ShouldProcessAssets(subdMeshFile, checkedOutputFile, pForceFullRebuild):
                    ProcessMeshesPair(baseMeshFile, subdMeshFile, fullOutputPath)

    print 'Done'
    if inBeepAfterComplete:
        libHazardMayaUtils.NotifyWithSound()

def TransferAttributesManuallyUVSpace(pSourceShape, pTargetFaces):
    cmds.select(clear=True)
    targetFacesUvVerts = cmds.ls(cmds.polyListComponentConversion(pTargetFaces, ff=True, toUV=True, uvShell=True), flatten=True)

    for mapVert in targetFacesUvVerts:
        uv = cmds.polyEditUV(mapVert, query=True)
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
    fileUtils.ExportObj(baseMesh, pOutputDir, env.PROCESSED_BASE_MESH_NAME)

    # SubD mesh can be used to create very detailed LOD0 mesh
    # or to bake animated normal maps (wrinkle maps)
    # but right now we dont use it so stop exporting to save processing time

    # with DebugTimer('Processing SubD resolution'):
    #     # Settings are important for keeping same vertex order
    #     # ch=1, ost=0, khe=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1, \
    #     # sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=1, kb=1, c=1, ocr=0, dpe=1, sl=1
    #     cmds.polySmooth(baseMesh, ost=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1,\
    #          sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=1, kb=1, c=1, ocr=0, dpe=1, sl=1)
    #     cmds.delete(baseMesh, constructionHistory=True)
    #     cmds.transferAttributes(subdMesh, baseMesh, transferPositions=1, transferNormals=0, sampleSpace=3)
    #     #should manually transfer eye sockets here like at base resolution
    #     cmds.delete(baseMesh, constructionHistory=True)

    # fileUtils.ExportObj(baseMesh, pOutputDir, env.PROCESSED_SUBD_MESH_NAME)



def ProcessAnimDir(subDir):
    fullSubdirPath = os.path.join(env.GetSrcFullPath(), subDir)
    animFile = os.path.join(fullSubdirPath, 'Animation.fbx')
    animFileExist = os.path.exists(animFile)
    print 'Dir: {} Anim File: {} Exist: {}'.format(subDir, animFile, animFileExist)
    if not animFileExist:
        print 'SKIPPING...'
        return

    cmds.file(newFile=True, force=True)
    cmds.file(animFile, pr=1, rpr="Animation", ignoreVersion=1, i=1, type="FBX", importFrameRate=True,\
         importTimeRange="override", ra=True, rdn=1, mergeNamespacesOnClash=False, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")
    dazToUe.CreateOptimizedSkeletonOnlyAndRetargetAnim(bFilterCurves=True, inBeepAfterComplete=False)
    #export
    outputFileName = subDir
    #strip prefix
    for prefix in env.ANIM_PREFIXES:
        if outputFileName.startswith(prefix):
            outputFileName = outputFileName[len(prefix):]

    cmds.select(all=True, hierarchy=True)
    fileUtils.ExportSelectionFBX(pDir=env.GetOutputFullPath(), pFileNameWithoutExtension='A_'+outputFileName, pBakeAnimation=True)
    cmds.select(clear=True)

    #copy txt file with pose names if exist
    descriptionFile = os.path.join(fullSubdirPath, 'ExportNames.txt')
    if os.path.exists(descriptionFile):
        descriptionFullOutputPath = os.path.join(env.GetOutputFullPath(), 'A_' + outputFileName + '.txt')
        #print descriptionFile
        #print descriptionFullOutputPath
        fileUtils.CopyFile(descriptionFile, descriptionFullOutputPath)


    intermediateDir = env.GetIntermediateFullPath()
    fileUtils.MakeDirectoryIfNotExist(intermediateDir)
    #save maya file for later use
    saveAnimPath = os.path.join(intermediateDir, 'A_' + outputFileName + '.mb')
    cmds.file(rename=saveAnimPath)
    cmds.file(save=1, options="v=0;", f=1)



def PerformFullBatchProcessing(pForceFullRebuild=True):
    with DebugTimer('PerformFullBatchProcessing: Processing directory: {}'.format(env.GetSrcFullPath())):
        #process morphs
        PreprocessMorphTargets(pForceFullRebuild=pForceFullRebuild, inBeepAfterComplete=False)

        #create output directory
        fileUtils.MakeDirectoryIfNotExist(env.GetOutputFullPath())

        #process animations
        subDirs = fileUtils.GetSubdirNames(env.GetSrcFullPath())

        for subDir in subDirs:
            if not fileUtils.IsDirStartWithPrefixes(subDir, env.ANIM_PREFIXES):
                print 'PerformFullBatchProcessing: Skipping Dir: {} as it not ANIMATION directory (checked for prefixes: {})'.format(subDir, env.ANIM_PREFIXES)
                continue

            ProcessAnimDir(subDir)

        #end animations processing

        #finally process main meshes
        baseFile = os.path.join(env.GetSrcFullPath(), 'Base.fbx')
        baseFileExist = os.path.exists(baseFile)
        print 'PerformFullBatchProcessing: Final Mesh processing Dir: {} Anim File: {} Exist: {}'.format(env.GetSrcFullPath(), baseFile, baseFileExist)
        if not baseFileExist:
            print 'SKIPPING...'
            return

        cmds.file(newFile=True, force=True)
        cmds.file(baseFile, pr=1, rpr="Animation", ignoreVersion=1, i=1, type="FBX", importFrameRate=True,\
             importTimeRange="override", ra=True, rdn=1, mergeNamespacesOnClash=False, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")
        dazToUe.OptimizeSkeleton(pbCollapseToes=False, pLoadExternalBaseMesh=True, pLoadExternalMorphs=True,\
             pLoadExternalUVs=True, pCreateIKConstraints=True, inBeepAfterComplete=False)


        #recognize gender
        baseMeshName = 'Generic'
        if libHazardMayaUtils.FindMeshByWildcard('Female*'):
            baseMeshName = 'Female'
        elif libHazardMayaUtils.FindMeshByWildcard('Male*'):
            baseMeshName = ('Male')


        #export rig for 3ds max, motionbuilder etc (with end bones)
        cmds.select(all=True, hierarchy=True)
        fileUtils.ExportSelectionFBX(pDir=env.GetOutputFullPath(), pFileNameWithoutExtension='RIG_'+baseMeshName, pBakeAnimation=False)
        cmds.select(clear=True)


        #export mesh(meshes) for ue4 (without end bones)
        body = libHazardMayaUtils.FindMeshByWildcard(baseMeshName + 'Body')
        eyelashes = libHazardMayaUtils.FindMeshByWildcard(baseMeshName + 'Eyelashes')
        eyes = libHazardMayaUtils.FindMeshByWildcard(baseMeshName + 'Eyes')

        meshesToExport = []
        if body:
            meshesToExport.append(body)
        if eyes:
            meshesToExport.append(eyes)
        if eyelashes:
            meshesToExport.append(eyelashes)

        if meshesToExport:
            cmds.select(meshesToExport)
            skelUtils.SelectJointsForSelectedMeshes(bKeepSelection=True, bIncludeSpecialJoints=True, bIncludeIKJoints=True)
            fileUtils.ExportSelectionFBX(pDir=env.GetOutputFullPath(), pFileNameWithoutExtension='SK_'+baseMeshName, pBakeAnimation=True)
            cmds.select(clear=True)
        else:
            print 'ERROR: Nothing to export as {}'.format(baseMeshName)


        #save maya file for later use
        saveFilePath = os.path.join(env.GetIntermediateFullPath(), 'BaseProcessed.mb')
        cmds.file(rename=saveFilePath)
        cmds.file(save=1, options="v=0;", f=1)
        #end mesh processing

    libHazardMayaUtils.NotifyWithSound()
    