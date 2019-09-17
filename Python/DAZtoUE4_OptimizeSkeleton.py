import maya.cmds as cmds
import time
import libHazardMayaUtils as mayaUtils
import libHazardDazUtils as dazUtils

reload(mayaUtils)
reload(dazUtils)

def test():
    mayaUtils.ParentAllGeometryToWorld()
    mayaUtils.ResetBindPoseForAllSkinClusters()
    mayaUtils.SetSkinMethodForAllSkinClusters(0)  # set skinning type to linear
    dazUtils.RenameSkeletonJoints()
    oldJoints = mayaUtils.GetHierarchy('Root')
    dazUtils.DuplicateSkeletonJoints('Root', 'DAZ_')
    dazUtils.FixNewJointsOrientation()
    dazUtils.RecreateHierarchy('Root', 'DAZ_')

    cmds.delete(oldJoints)
    dazUtils.RenameNewSkeleton()




#
#   MAIN
#
def OptimizeSkeleton():
    print 'Starting skeleton and mesh optimization'
    start = time.clock()
    cmds.currentTime(0, edit=True)#set skeleton to 'reference' position

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

    dazUtils.AddEndJoints()
    dazUtils.AddCameraJoint()
    mayaUtils.FixMaxInfluencesForAllSkinClusters(4)
    dazUtils.MakeBendCorrectiveJoints()
    dazUtils.CreateIkJoints()

    dazUtils.SetJointsVisualProperties()

    dazUtils.OptimizeBodyMaterials()

    mayaUtils.FixMaxInfluencesForAllSkinClusters(4)

    print 'FINISHED skeleton and mesh optimization: time taken %.02f seconds' % (time.clock()-start)
    mayaUtils.NotifyWithSound()
