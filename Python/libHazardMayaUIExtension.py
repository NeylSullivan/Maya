import maya.cmds as cmds

from contextlib import contextmanager

@contextmanager
def FrameLayout(*args, **kwargs):
    try:
        yield cmds.frameLayout(*args, **kwargs)
    finally:
        cmds.setParent('..')

@contextmanager
def ColumnLayout(*args, **kwargs):
    try:
        yield cmds.columnLayout(*args, **kwargs)
    finally:
        cmds.setParent('..')


def __GetOptFullName(pNamespace, pName):
    if pNamespace is None:
        return pName
    return '{}.{}'.format(pNamespace, pName)

def GetOptValue(pName, pDefaultValue, pNamespace=None):
    fullName = __GetOptFullName(pNamespace, pName)
    if cmds.optionVar(exists=fullName):
        return cmds.optionVar(q=fullName)
    else:
        return pDefaultValue

def SetOptValue(pName, pNewValue, pNamespace=None):
    fullName = __GetOptFullName(pNamespace, pName)

    if pNewValue is None:
        pNewValue = 0

    if isinstance(pNewValue, basestring):
        cmds.optionVar(stringValue=(fullName, pNewValue))
        return
    elif isinstance(pNewValue, (int, long, bool)):
        cmds.optionVar(intValue=(fullName, pNewValue))
        return
    elif isinstance(pNewValue, float):
        cmds.optionVar(floatValue=(fullName, pNewValue))
        return

    # list?
    print 'ERROR SetValue {} {}'.format(pName, pNewValue)


def SaveableCheckBox(pWindowName, *args, **kwargs):
    label = kwargs['label']
    optName = pWindowName + '.' + label.replace(' ', '_')

    #print optName

    #if cmds.optionVar(exists=optName):
        #kwargs['value'] = cmds.optionVar(q=optName)
    kwargs['value'] = GetOptValue(optName, kwargs['value'])
    kwargs['changeCommand'] = (lambda val: SetOptValue(optName, val))

    return cmds.checkBox(*args, **kwargs)
