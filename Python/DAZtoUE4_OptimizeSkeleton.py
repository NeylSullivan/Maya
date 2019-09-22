import maya.cmds as cmds
import maya.mel as mel
import time
import libHazardMayaUtils as mayaUtils
import libHazardDazUtils as dazUtils

reload(mayaUtils)
reload(dazUtils)


def test():
    cmds.select(clear=True)
    shape = mayaUtils.FindShapeByMat('Body') #new name is 'Body'
    all_faces = cmds.filterExpand(cmds.polyListComponentConversion(shape, toFace=True), sm=34, expand=True)
    matched_faces = []

    file_node = cmds.shadingNode("file", asTexture=True)
    filePath = (r'e:\blackops\__WorkFlow\Maya\Resources\head_mask.tga')
    cmds.setAttr('%s.fileTextureName' % file_node, filePath, type="string")
    cmds.select(clear=True)

    for f in all_faces:
        alpha = 0.0
        uvs = cmds.filterExpand(cmds.polyListComponentConversion(f, toUV=True, border=True), sm=35, expand=True)
        #print uvs
        uList =[]
        vList =[]
        for uv in uvs:
            UVValues = cmds.polyEditUV(uv, query=True )
            uList.append(UVValues[0])
            vList.append(UVValues[1])
            #print UVValues
        uCoord = sum(uList) / len(uList)
        vCoord = sum(vList) / len(vList)

        try:
            alpha = cmds.colorAtPoint(file_node, u=uCoord, v=vCoord)[0] #[0.2499994933605194, 0.80069500207901]
            print alpha
        except:
            pass

        if(alpha > 0.6):
            
            matched_faces.append(f)
    cmds.delete(file_node)
    cmds.select(matched_faces)

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

    dazUtils.AddBreastJoints() ################
    dazUtils.AddNippleJoints() ################

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
