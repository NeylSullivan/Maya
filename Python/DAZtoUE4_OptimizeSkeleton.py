import maya.cmds as cmds
import maya.mel as mel
import time
import libHazardMayaUtils as mayaUtils
import libHazardDazUtils as dazUtils


reload(mayaUtils)
reload(dazUtils)

def OptimizeBodyMeshForBaking():
    start = time.clock()
    shape = cmds.ls(selection=True)

    if not shape:
        print 'Mesh not selected'
        return
    shape = shape[0]
    print shape
    print 'bakePartialHistory'
    cmds.bakePartialHistory(shape, preCache=True)

    allSets = cmds.listSets(object=shape, extendToShape=True)
    renderingSets = cmds.listSets(object=shape, extendToShape=True, type=1)
    print allSets
    if allSets:
        for s in allSets:
            if s not in renderingSets:
                cmds.delete(s)

    unusedMatsList = ['*Mouth*', '*Teeth*', '*Pupils*', '*EyeMoisture*', '*Cornea*', '*Irises*', '*Sclera*']
    for mat in unusedMatsList:
        unusedFaces = mayaUtils.GetFacesByMatsWildcard(shape, mat)
        if unusedFaces:
            cmds.delete(unusedFaces)

    mayaUtils.CleanUnusedMaterials()

    mayaUtils.AppendShadingGroupByMatWildcard(shape, '*Face*', '*Lips*')
    mayaUtils.AppendShadingGroupByMatWildcard(shape, '*Face*', '*Ears*')
    mayaUtils.AppendShadingGroupByMatWildcard(shape, '*Face*', '*EyeSocket*')

    mayaUtils.AppendShadingGroupByMatWildcard(shape, '*Legs*', '*Toenails*')
    mayaUtils.AppendShadingGroupByMatWildcard(shape, '*Arms*', '*Fingernails*')


    mayaUtils.ArrangeUVByMatWildcard(shape, '*Torso*', su=0.5, sv=0.5, u=0.5, v=0.5)
    mayaUtils.ArrangeUVByMatWildcard(shape, '*Face*', su=0.5, sv=0.5, u=0.0, v=0.5)
    mayaUtils.ArrangeUVByMatWildcard(shape, '*Legs*', su=0.5, sv=0.5, u=0.5, v=0.0)
    mayaUtils.ArrangeUVByMatWildcard(shape, '*Arms*', su=0.5, sv=0.5, u=0.0, v=0.0)

    mayaUtils.AppendShadingGroupByMatWildcard(shape, '*Torso*', '*Legs*')
    mayaUtils.AppendShadingGroupByMatWildcard(shape, '*Torso*', '*Arms*')
    mayaUtils.AppendShadingGroupByMatWildcard(shape, '*Torso*', '*Face*')


    mayaUtils.RenameMaterial('*Torso*', 'Body')
    mayaUtils.CleanUnusedMaterials()
    print 'FINISHED OptimizeBodyMeshForBaking(): time taken %.02f seconds' % (time.clock()-start)
    mayaUtils.NotifyWithSound()

#
#   MAIN
#
def OptimizeSkeleton(pbCollapseToes=False, pLoadExternalBaseMesh=False, pLoadExternalMorphs=False, pLoadExternalUVs=False, pCreateIKConstraints=False):
    print 'Starting skeleton and mesh optimization'
    start = time.clock()
    cmds.currentTime(0, edit=True)#set skeleton to 'reference' position
    cmds.select(all=True)
    mel.eval('gotoBindPose')
    cmds.select(clear=True)

    dazUtils.RemoveObjectsByWildcard(['Fingernails_*'], 'transform')
    mayaUtils.ParentAllGeometryToWorld()
    mayaUtils.FixMaxInfluencesForAllSkinClusters(4)
    dazUtils.DestroyUnusedJoints(pbCollapseToes)
    mayaUtils.ResetBindPoseForAllSkinClusters()
    mayaUtils.SetSkinMethodForAllSkinClusters(0)  # set skinning type to linear

    #return

    dazUtils.RenameSkeletonJoints()
    oldJoints = mayaUtils.GetHierarchy('root')

    # collect data for skin export
    skinData = mayaUtils.GetSkinExportData()  # transform, shape, skincluster, jointsList

    mayaUtils.ExportSkinning(skinData)          # export skinning
    dazUtils.DuplicateSkeletonJoints('root', 'DAZ_')
    dazUtils.FixNewJointsOrientation()
    dazUtils.FixNewJointsAiming()
    dazUtils.RecreateHierarchy('root', 'DAZ_')
    dazUtils.AlighnTwistJoints()

    cmds.delete(oldJoints)
    dazUtils.RenameNewSkeleton()

    if pLoadExternalBaseMesh: # Do it when mesh unskinned
        dazUtils.TryLoadExternalBaseMeshBodyMorph()

    #load external secondary uv here
    if pLoadExternalUVs:
        dazUtils.TryLoadExternalUVs()

    mayaUtils.ImportSkinning(skinData, pDeleteFilesAfterImport=True)          # import skinning

    cmds.select(clear=True)

    dazUtils.AddBreastJoints() ################ should nipples need to be skinned or it just points for ue4 sockets?

    dazUtils.AddEndJoints()
    dazUtils.AddCameraJoint()
    mayaUtils.FixMaxInfluencesForAllSkinClusters(4)
    dazUtils.MakeBendCorrectiveJoints()
    dazUtils.CreateIkJoints(pCreateIKConstraints)

    dazUtils.SetJointsVisualProperties()


    if pLoadExternalMorphs:
        dazUtils.TryLoadExternalMorphTargets()

    dazUtils.OptimizeBodyMaterials() # Check this, try to extract blendshape before baking history, then readd it. Done 26102019

    mayaUtils.FixMaxInfluencesForAllSkinClusters(4)

    dazUtils.RenameAndCombineMeshes()

    #no need anymore, mask for tesselation now writen in secondary uv and loaded externally
    #dazUtils.SetVertexColorForBorderVertices() #for genitalia mesh also
    dazUtils.CollapseUVTiles() #use this instead

    dazUtils.PostprocessGenitaliaObject('HazardFemaleGenitalia*')

    mayaUtils.CleanUnusedMaterials()

    #dazUtils.SafeBakePartialHistoryKeepBlendShapes(shape)

    dazUtils.ReplaceEyesWithExternalMeshes()

    print 'FINISHED skeleton and mesh optimization: time taken %.02f seconds' % (time.clock()-start)
    mayaUtils.NotifyWithSound()

#
#   MAIN
#
def CreateOptimizedSkeletonOnlyAndRetargetAnim(bFilterCurves=True):
    print 'Starting skeleton optimization'
    start = time.clock()
    cmds.currentTime(0, edit=True)#set skeleton to 'reference' position

    dazUtils.RemoveObjectsByWildcard(['Fingernails_*'], 'transform')
    dazUtils.RemoveObjectsByWildcard(['HazardFemaleGenitalia_*Shape'], 'transform')

    mayaUtils.ParentAllGeometryToWorld()

    primaryMesh = mayaUtils.FindMeshByWildcard('Genesis8*', preferShapeWithMaxVertices=True, checkForMatWithName='Torso')

    if primaryMesh:
        cmds.select(primaryMesh)
    else:
        cmds.select(all=True)

    mel.eval('gotoBindPose')
    cmds.select(clear=True)

    #delete all meshes
    shapesToDelete = mayaUtils.GetMultipleShapesTransforms(cmds.ls(geometry=True, objectsOnly=True))
    if shapesToDelete:
        for s in shapesToDelete:
            cmds.delete(s)
            print 'Deleting {0}'.format(s)

    dazUtils.RenameSkeletonJoints()
    oldJoints = mayaUtils.GetHierarchy('root')

    dazUtils.DuplicateSkeletonJoints('root', 'DAZ_')
    dazUtils.FixNewJointsOrientation()
    dazUtils.FixNewJointsAiming()
    dazUtils.RecreateHierarchy('root', 'DAZ_')
    dazUtils.AlighnTwistJoints()

    #delete twist joints for animation retargetting/ they are procedurally animated in engine
    unusedJoints = cmds.ls('DAZ_*twist*')
    for j in unusedJoints:
        cmds.delete(j)
        print '\tDeleting {0}'.format(j)


    print 'Renaming OLD skeleton'
    oldJoints = mayaUtils.GetHierarchy('root')
    for j in oldJoints:
        mayaUtils.RenameJoint(j, 'OLD_' + j)

    dazUtils.RenameNewSkeleton() #remove DAZ_ prefix

    cmds.select(clear=True)
    #create constraint from old skeleton to new
    print 'Creating constraints'
    newJoints = mayaUtils.GetHierarchy('root')

    for j in newJoints:
        oldJoint = 'OLD_' + j
        print '\tCreating parentConstraint from {0} to {1}'.format(oldJoint, j)
        cmds.parentConstraint(oldJoint, j, maintainOffset=True)

    dazUtils.AddCameraJoint()
    dazUtils.CreateIkJoints() #create AFTER constraining new skeleton to old

    # No need to bake IK joints, they are auto baked during exporting to fbx

    print'\n'
    print "\t\t******** BAKING ANIMATION ********"
    print'\n'
    attributesToBake = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    timeRange = (cmds.playbackOptions(animationStartTime=True, query=True), cmds.playbackOptions(animationEndTime=True, query=True))
    print 'timeRange = {0}'.format(timeRange)
    cmds.bakeResults(newJoints, attribute=attributesToBake, time=timeRange, minimizeRotation=True, preserveOutsideKeys=True, simulation=True, disableImplicitControl=True)

    print'\n'
    print "\t\t******** Filtering curves ********"
    print'\n'

    if bFilterCurves:
        animNodes = cmds.listConnections(newJoints, type="animCurve")
        if animNodes:
            print 'Performing filtering for {0} anim curves'.format(len(animNodes))
            oldKeysCount = cmds.keyframe(animNodes, q=True, keyframeCount=True)
            cmds.filterCurve(animNodes,	filter='simplify', timeTolerance=0.01, tolerance=0.01)
            newKeysCount = cmds.keyframe(animNodes, q=True, keyframeCount=True)
            percent = float(newKeysCount) / float(oldKeysCount)  * 100.0
            print '{0} keys filtered to {1} keys ({2:.1f}%)'.format(oldKeysCount, newKeysCount, percent)
    else:
        print 'Filtering NOT requested'


    #clean scene after finishing
    print 'Deleting old skeleton'
    cmds.select(clear=True)
    cmds.select(mayaUtils.GetHierarchy('OLD_root'))
    cmds.delete()

    print 'FINISHED animation retargeting: time taken %.02f seconds' % (time.clock()-start)
    mayaUtils.NotifyWithSound()
