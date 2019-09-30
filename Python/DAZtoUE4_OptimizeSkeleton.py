import maya.cmds as cmds
import maya.mel as mel
import time
import libHazardMayaUtils as mayaUtils
import libHazardDazUtils as dazUtils


reload(mayaUtils)
reload(dazUtils)

def OptimizeBodyMeshForBaking():
    shape = cmds.ls(selection=True)

    if not shape:
        print 'Mesh not selected'
        return
    shape = shape[0]
    print shape

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
    mayaUtils.NotifyWithSound()

#
#   MAIN
#
def OptimizeSkeleton():
    print 'Starting skeleton and mesh optimization'
    start = time.clock()
    cmds.currentTime(0, edit=True)#set skeleton to 'reference' position
    cmds.select(all=True)
    mel.eval('gotoBindPose')
    cmds.select(clear=True)

    dazUtils.RemoveObjectsByWildcard(['Fingernails_*'], 'transform')



    mayaUtils.FixMaxInfluencesForAllSkinClusters(4)
    mayaUtils.DestroyUnusedJoints()
    mayaUtils.ParentAllGeometryToWorld()
    mayaUtils.ResetBindPoseForAllSkinClusters()
    mayaUtils.SetSkinMethodForAllSkinClusters(0)  # set skinning type to linear
    dazUtils.RenameSkeletonJoints()
    oldJoints = mayaUtils.GetHierarchy('Root')

    # collect data for skin export
    skinData = mayaUtils.GetSkinExportData()  # transform, shape, skincluster, jointsList

    mayaUtils.ExportSkinning(skinData)          # export skinning
    dazUtils.DuplicateSkeletonJoints('Root', 'DAZ_')
    dazUtils.FixNewJointsOrientation()
    dazUtils.RecreateHierarchy('Root', 'DAZ_')

    cmds.delete(oldJoints)
    dazUtils.RenameNewSkeleton()

    mayaUtils.ImportSkinning(skinData)          # import skinning

    cmds.select(clear=True)

    dazUtils.AddBreastJoints() ################ TODO reallign to nipples?
    dazUtils.AddNippleJoints() ################ TODO should be skinned?

    dazUtils.AddEndJoints()
    dazUtils.AddCameraJoint()
    mayaUtils.FixMaxInfluencesForAllSkinClusters(4)
    dazUtils.MakeBendCorrectiveJoints()
    dazUtils.CreateIkJoints()

    dazUtils.SetJointsVisualProperties()

    dazUtils.OptimizeBodyMaterials()

    mayaUtils.FixMaxInfluencesForAllSkinClusters(4)

    mayaUtils.SetVertexColorForBorderVertices() #for genitalia mesh also

    dazUtils.RenameAndCombineMeshes()

    dazUtils.CutMeshAndOffsetUVs()

    dazUtils.PostprocessGenitaliaObject('HazardFemaleGenitalia*')

    mayaUtils.CleanUnusedMaterials()

    print 'FINISHED skeleton and mesh optimization: time taken %.02f seconds' % (time.clock()-start)
    mayaUtils.NotifyWithSound()

#
#   MAIN
#
def CreateOptimizedSkeletonOnlyAndRetargetAnim():
    print 'Starting skeleton optimization'
    start = time.clock()
    cmds.currentTime(0, edit=True)#set skeleton to 'reference' position
    cmds.select(all=True)
    mel.eval('gotoBindPose')
    cmds.select(clear=True)

    dazUtils.RemoveObjectsByWildcard(['Fingernails_*'], 'transform')

    #mayaUtils.FixMaxInfluencesForAllSkinClusters(4)
    #mayaUtils.DestroyUnusedJoints()
    mayaUtils.ParentAllGeometryToWorld()
    #mayaUtils.ResetBindPoseForAllSkinClusters()
    mayaUtils.SetSkinMethodForAllSkinClusters(0)  # set skinning type to linear
    dazUtils.RenameSkeletonJoints()
    oldJoints = mayaUtils.GetHierarchy('Root')

    # collect data for skin export
    #skinData = mayaUtils.GetSkinExportData()  # transform, shape, skincluster, jointsList

    #mayaUtils.ExportSkinning(skinData)          # export skinning
    dazUtils.DuplicateSkeletonJoints('Root', 'DAZ_')
    dazUtils.FixNewJointsOrientation()
    dazUtils.RecreateHierarchy('Root', 'DAZ_')

    #cmds.delete(oldJoints)
    print 'Renaming OLD skeleton'
    oldJoints = mayaUtils.GetHierarchy('Root')
    for j in oldJoints:
        mayaUtils.RenameJoint(j, 'OLD_' + j)

    dazUtils.RenameNewSkeleton() #remove DAZ_ prefix

    #mayaUtils.ImportSkinning(skinData)          # import skinning

    cmds.select(clear=True)

    #create constraint from old skeleton to new

    newJoints = mayaUtils.GetHierarchy('Root')

    for j in newJoints:
        oldJoint = 'OLD_' + j
        print 'Creating parentConstraint from {0} to {1}'.format(oldJoint, j)
        cmds.parentConstraint(oldJoint, j, maintainOffset=True)


    #dazUtils.AddEndJoints()
    #dazUtils.AddCameraJoint()
    #mayaUtils.FixMaxInfluencesForAllSkinClusters(4)
    #dazUtils.MakeBendCorrectiveJoints()
    #dazUtils.CreateIkJoints()

    #dazUtils.SetJointsVisualProperties()

    #dazUtils.OptimizeBodyMaterials()

    #mayaUtils.FixMaxInfluencesForAllSkinClusters(4)

    print 'FINISHED animation retarheting: time taken %.02f seconds' % (time.clock()-start)
    mayaUtils.NotifyWithSound()
