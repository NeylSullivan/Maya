import os
import maya.cmds as cmds

DAZ_TO_UE4_NAMESPACE = 'hazardDAZtoUE4'
BATCH_PROCESSING_DIR_OPTION_NAME = 'batchProcessingDir'

ANIM_PREFIXES = ['PROPANIM_']

#MTD_ Morph Target Dynamic
#MTB_ Morph Target Baked
#MTTD_ Morph Target Transformed Dynamic
#MTTB_ Morph Target Transformed Baked
MORPH_TARGET_PREFIXES = ['MTD_', 'MTB_', 'MTTD_', 'MTTB_']


#ROOT_DIR = 'e:\\blackops\\__MODELS\\Characters\\Female\\Base\\AUTOMATION'
SRC_DIR = 'SRC'
INTERMEDIATE_DIR = 'INTERMEDIATE'
OUTPUT_DIR = 'OUT'

SRC_BASE_MESH_NAME = 'Base'
SRC_SUBD_MESH_NAME = 'SubD'

PROCESSED_BASE_MESH_NAME = 'Base'
#NOT USED
#PROCESSED_SUBD_MESH_NAME = 'SubD'

BASE_FEMALE_MESH_WITH_UV0_NAME = 'BaseFemale_UV0'
BASE_FEMALE_MESH_WITH_UV1_NAME = 'BaseFemale_UV1'

def GetRootDir(pCanBeEmpty=False):
    fullOptionName = '{}.{}'.format(DAZ_TO_UE4_NAMESPACE, BATCH_PROCESSING_DIR_OPTION_NAME)
    if cmds.optionVar(exists=fullOptionName):
        return cmds.optionVar(q=fullOptionName)
    else:
        if pCanBeEmpty:
            return ''
        else:
            raise NameError('GetRootDir(pCanBeEmpty=False): Cannot load root dir from {} option. Set it in UI or check userPrefs.mel'\
                .format(fullOptionName))

def GetSrcFullPath():
    return os.path.join(GetRootDir(), SRC_DIR)

def GetIntermediateFullPath():
    return os.path.join(GetRootDir(), INTERMEDIATE_DIR)

def GetOutputFullPath():
    return os.path.join(GetRootDir(), OUTPUT_DIR)