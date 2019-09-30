import maya.cmds as cmds
#import maya.mel as mel
import DAZtoUE4_OptimizeSkeleton as DAZtoUE4
import libHazardMayaUtils as mayaUtils
import libHazardDazUtils as dazUtils
import libHazardSkeletonSelectionUtils as skelUtils

reload(DAZtoUE4)
reload(mayaUtils)
reload(dazUtils)
reload(skelUtils)


class DAZtoUE4_UI(object):
    def __init__(self):
        if cmds.window("hazardDAZtoUE4", exists=True):
            cmds.deleteUI("hazardDAZtoUE4")
        self.win = cmds.window('hazardDAZtoUE4', title="DAZ to UE4 Tools", widthHeight=(200, 200))

        cmds.columnLayout(rowSpacing=10, adjustableColumn=True)
        cmds.frameLayout(label='Skeletal mesh')
        cmds.columnLayout(rowSpacing=5, adjustableColumn=True)
        self.btnOptimizeSkeleton = cmds.button(label="Optimize Skeleton and Mesh", command=self.OptimizeSkeleton)
        self.btnRetargetAnim = cmds.button(label="Create Skeleton and Retarget Anim", command=self.CreateOptimizedSkeletonOnlyAndRetargetAnim)
        cmds.setParent('..')
        cmds.setParent('..')

        cmds.frameLayout(label='Joints Selection Utils')
        cmds.columnLayout(rowSpacing=5, adjustableColumn=True)
        cmds.button(label="Select Face Rig", command=self.SelectFaceRig)
        cmds.button(label="Select Body Anim Relevant Joints", command=self.SelectBodyAnimRelevantJoints)
        cmds.button(label="Select Joints for Selected Meshes", command=self.SelectJointsForSelectedMeshes)
        cmds.setParent('..')
        cmds.setParent('..')

        cmds.showWindow(self.win)


    def OptimizeSkeleton(self, _unused):
        reload(DAZtoUE4)
        DAZtoUE4.OptimizeSkeleton()

    def CreateOptimizedSkeletonOnlyAndRetargetAnim(self, _unused):
        reload(DAZtoUE4)
        DAZtoUE4.CreateOptimizedSkeletonOnlyAndRetargetAnim()

    def SelectFaceRig(self, _unused):
        reload(skelUtils)
        skelUtils.SelectFaceRig()

    def SelectBodyAnimRelevantJoints(self, _unused):
        reload(skelUtils)
        #skelUtils.SelectJointsForSelectedMeshes()

    def SelectJointsForSelectedMeshes(self, _unused):
        reload(skelUtils)
        skelUtils.SelectJointsForSelectedMeshes()
