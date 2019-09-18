import maya.cmds as cmds
import maya.mel as mel
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


def SetVertexColorForBorderVertices():
    skinList = cmds.ls(type='skinCluster')
    cmds.select(clear=True)
    borderVertsList = []

    for s in skinList:
        cmds.select(clear=True)
        mesh = mayaUtils.GetMeshFromSkinCluster(s)
        cmds.select(mesh)
        cmds.selectType(polymeshFace=True)
        cmds.polySelectConstraint(mode=3, type=8, where=1) # to get border vertices
        borderVerts = cmds.polyListComponentConversion(tv=True)
        borderVertsList.extend(borderVerts)
        cmds.polySelectConstraint(mode=0, sh=0, bo=0)
        cmds.select(clear=True)

        allVerts = cmds.polyListComponentConversion(mesh, tv=True)
        cmds.polyColorPerVertex(allVerts, rgb=(1.0, 1.0, 1.0))

    cmds.select(borderVertsList)
    cmds.polyColorPerVertex(borderVertsList, rgb=(0.0, 1.0, 1.0))

#
#   MAIN
#
def OptimizeSkeleton():
    print 'Starting skeleton and mesh optimization'
    start = time.clock()
    cmds.currentTime(0, edit=True)#set skeleton to 'reference' position
    mel.eval('gotoBindPose')

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


#
#   MAIN
#
def CreateOptimizedSkeletonOnlyAndRetargetAnim():
    print 'Starting skeleton optimization'
    start = time.clock()
    cmds.currentTime(0, edit=True)#set skeleton to 'reference' position
    mel.eval('gotoBindPose')

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
