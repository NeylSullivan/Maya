import maya.cmds as cmds
import time

import libHazardMayaFunctions
reload(libHazardMayaFunctions)
from libHazardMayaFunctions import *

def OptimizeBodyMaterials():
    print 'Starting body materials optimization'
    start = time.clock()

    shape = FindShapeByMat('Torso')
        
    if shape is None:
        print 'Error! Can`t find body(Torso) shape'
        return

    AppendShadingGroupByMat(shape, 'Mouth','Teeth')    
    mouthShape = DetachSkinnedMeshByMat(shape, ['Mouth'], '_MOUTH')
        
    eyesShape = DetachSkinnedMeshByMat(shape, ['Pupils', 'EyeMoisture', 'Cornea', 'Irises', 'Sclera'], '_Eyes')
    
    AppendShadingGroupByMat(shape, 'Face','Lips')
    AppendShadingGroupByMat(shape, 'Face','Ears')
    AppendShadingGroupByMat(shape, 'Face','EyeSocket')
    
    AppendShadingGroupByMat(shape, 'Legs','Toenails')
    AppendShadingGroupByMat(shape, 'Arms','Fingernails')
    
    ArrangeUVByMat(shape, 'Torso', su=0.5, sv=0.5, u=0.5, v=0.5)
    ArrangeUVByMat(shape, 'Face', su=0.5, sv=0.5, u=0.0, v=0.5)
    ArrangeUVByMat(shape, 'Legs', su=0.5, sv=0.5, u=0.5, v=0.0)
    ArrangeUVByMat(shape, 'Arms', su=0.5, sv=0.5, u=0.0, v=0.0)
    
    AppendShadingGroupByMat(shape, 'Torso','Legs')
    AppendShadingGroupByMat(shape, 'Torso','Arms')
    AppendShadingGroupByMat(shape, 'Torso','Face')
    
    print 'Baking history'
    cmds.bakePartialHistory(shape, prePostDeformers=True)
    cmds.bakePartialHistory(mouthShape, prePostDeformers=True)
    cmds.bakePartialHistory(eyesShape, prePostDeformers=True)


    print 'Finished body materials optimization: time taken %.02f seconds' % (time.clock()-start)


