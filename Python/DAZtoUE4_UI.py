import maya.cmds as cmds
import DAZtoUE4_OptimizeSkeleton as DAZtoUE4
import libHazardMayaUtils as mayaUtils
import libHazardDazUtils as dazUtils
import libHazardSkeletonSelectionUtils as skelUtils
import libHazardMayaUIExtension as uiExt

reload(DAZtoUE4)
reload(mayaUtils)
reload(dazUtils)
reload(skelUtils)
reload(uiExt)


class DAZtoUE4_UI(object):
    def __init__(self):

        self.WINDOW_NAME = 'hazardDAZtoUE4'
        self.WINDOW_TITLE = "DAZ to UE4 Tools"
        self.WINDOW_SIZE = (260, 450)

        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)
        self.WINDOW_NAME = cmds.window(self.WINDOW_NAME, title=self.WINDOW_TITLE, widthHeight=self.WINDOW_SIZE, maximizeButton=False)

        self.mainForm = cmds.formLayout(nd=100)

        self.mainColumn = cmds.columnLayout(rowSpacing=10, adjustableColumn=True)

        cmds.formLayout(self.mainForm, edit=True, attachForm=([self.mainColumn, 'left', 10], [self.mainColumn, 'right', 10], [self.mainColumn, 'top', 10]))

        with uiExt.FrameLayout(label='Skeletal mesh', collapsable=True, collapse=False, marginHeight=8, marginWidth=8):
            with uiExt.FrameLayout(labelVisible=False, borderVisible=True, marginHeight=4, marginWidth=4):
                with uiExt.ColumnLayout(rowSpacing=5, adjustableColumn=True):
                    self.btnOptimizeSkeleton = cmds.button(label="Optimize Skeleton and Mesh", command=self.OptimizeSkeleton)
                    self.chkbxPreSubdivideImportantParts = cmds.checkBox(label='Pre Subdivide Important Parts', align='left', value=True)
                    self.chkbxCollapseToes = cmds.checkBox(label='Collapse Toes', align='left', value=False)

            with uiExt.FrameLayout(labelVisible=False, borderVisible=True, marginHeight=4, marginWidth=4):
                with uiExt.ColumnLayout(rowSpacing=5, adjustableColumn=True):
                    self.btnTriangulateAllSkinnedMeshes = cmds.button(label="Triangulate all skinned meshes", command=self.TriangulateAllSkinnedMeshes)


            with uiExt.FrameLayout(labelVisible=False, borderVisible=True, marginHeight=4, marginWidth=4):
                with uiExt.ColumnLayout(rowSpacing=5, adjustableColumn=True):
                    self.btnRetargetAnim = cmds.button(label="Create Skeleton and Retarget Anim", command=self.CreateOptimizedSkeletonOnlyAndRetargetAnim)
                    self.chkbxFilterCurves = cmds.checkBox(label='Filter Curves', align='left', value=True)


        with uiExt.FrameLayout(label='Joints Selection Utils', collapsable=True, collapse=False, marginHeight=8, marginWidth=8):
            with uiExt.ColumnLayout(rowSpacing=5, adjustableColumn=True):
                cmds.button(label="Select Face Rig", enableBackground=False, command=self.SelectFaceRig)
                cmds.button(label="Select Body Anim Relevant Joints", command=self.SelectBodyAnimRelevantJoints)

                with uiExt.FrameLayout(labelVisible=False, borderVisible=True, marginHeight=4, marginWidth=4):
                    with uiExt.ColumnLayout(rowSpacing=5, adjustableColumn=True):
                        cmds.button(label="Select Joints for Selected Meshes", command=self.SelectJointsForSelectedMeshes)
                        self.chkbxKeepSelection = cmds.checkBox(label='Keep Selection', align='left', value=True)
                        self.chkbxIncludeSpecialJoints = cmds.checkBox(label='Include Special Joints', align='left', value=True)
                        self.chkbxIncludeIKjoints = cmds.checkBox(label='Include IK Joints', align='left', value=True)

        with uiExt.FrameLayout(label='Mesh optimization', collapsable=True, collapse=True, marginHeight=8, marginWidth=8):
            with uiExt.ColumnLayout(rowSpacing=5, adjustableColumn=True):
                self.btnOptimizeMeshForBaking = cmds.button(label="Optimize Mesh for Baking", command=self.OptimizeMeshForBaking)

        cmds.showWindow(self.WINDOW_NAME)
        cmds.window(self.WINDOW_NAME, e=True, widthHeight=self.WINDOW_SIZE)


    def OptimizeSkeleton(self, _unused):
        reload(DAZtoUE4)
        collapseToes = cmds.checkBox(self.chkbxCollapseToes, query=True, value=True)
        subdivide = cmds.checkBox(self.chkbxPreSubdivideImportantParts, query=True, value=True)
        DAZtoUE4.OptimizeSkeleton(collapseToes, subdivide)

    def CreateOptimizedSkeletonOnlyAndRetargetAnim(self, _unused):
        reload(DAZtoUE4)
        filterCurves = cmds.checkBox(self.chkbxFilterCurves, query=True, value=True)
        DAZtoUE4.CreateOptimizedSkeletonOnlyAndRetargetAnim(bFilterCurves=filterCurves)

    def SelectFaceRig(self, _unused):
        reload(skelUtils)
        skelUtils.SelectFaceRig()

    def SelectBodyAnimRelevantJoints(self, _unused):
        reload(skelUtils)
        skelUtils.SelectBodyAnimRelevantJoints()

    def SelectJointsForSelectedMeshes(self, _unused):
        reload(skelUtils)
        keepSelection = cmds.checkBox(self.chkbxKeepSelection, query=True, value=True)
        includeSpecialJoints = cmds.checkBox(self.chkbxIncludeSpecialJoints, query=True, value=True)
        includeIKjoints = cmds.checkBox(self.chkbxIncludeIKjoints, query=True, value=True)

        skelUtils.SelectJointsForSelectedMeshes(bKeepSelection=keepSelection, bIncludeSpecialJoints=includeSpecialJoints, bIncludeIKJoints=includeIKjoints)

    def OptimizeMeshForBaking(self, _unused):
        reload(DAZtoUE4)
        DAZtoUE4.OptimizeBodyMeshForBaking()

    def TriangulateAllSkinnedMeshes(self, _unused):
        reload(dazUtils)
        result = cmds.confirmDialog(title='Confirm', message='Triangulate All Skinned Meshes. Are you sure?',\
             button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if result == 'Yes':
            dazUtils.TriangulateAllSkinnedMeshes()