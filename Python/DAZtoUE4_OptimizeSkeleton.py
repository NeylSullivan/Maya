import maya.cmds as cmds
import maya.mel as mel
import time
import libHazardMayaUtils as mayaUtils
import libHazardDazUtils as dazUtils


reload(mayaUtils)
reload(dazUtils)




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

    mayaUtils.SetVertexColorForBorderVertices()

    dazUtils.RenameAndCombineMeshes()

    dazUtils.CutMeshAndOffsetUVs()

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
