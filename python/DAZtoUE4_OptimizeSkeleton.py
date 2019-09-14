import maya.cmds as cmds
import time
import libHazardMayaUtils as mayaUtils
import libHazardDazUtils as dazUtils

reload(mayaUtils)
reload(dazUtils)

#
#   MAIN
#
def OptymizeSkeleton():
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

    # export skinning
    for sd in skinData:
        #print sd
        fileName = sd[0] + '_WEIGHTS.xml'
        cmds.deformerWeights(fileName, ex=True, deformer=sd[2])

    dazUtils.DuplicateSkeletonJoints('Root', 'DAZ_')
    dazUtils.FixNewJointsOrientation()
    dazUtils.RecreateHierarchy('Root', 'DAZ_')


    cmds.delete(oldJoints)

    dazUtils.RenameNewSkeleton()

    #import skinning
    for sd in skinData:
        #print sd
        cmds.skinCluster(sd[3], sd[0], name=sd[2], tsb=True)
        fileName = sd[0] + '_WEIGHTS.xml'
        cmds.deformerWeights(fileName, im=True, deformer=sd[2], method='index')

    cmds.select(clear=True)

    dazUtils.AddEndJoints()
    dazUtils.AddCameraJoint()
    mayaUtils.FixMaxInfluencesForAllSkinClusters(4)
    dazUtils.MakeBendCorrectiveJoints()
    dazUtils.CreateIkJoints()

    dazUtils.OptimizeBodyMaterials()

    print 'FINISHED skeleton and mesh optimization: time taken %.02f seconds' % (time.clock()-start)
