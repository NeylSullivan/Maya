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

def GetOptValue(pNamespace, pName, pDefaultValue):
    fullName = __GetOptFullName(pNamespace, pName)
    if cmds.optionVar(exists=fullName):
        return cmds.optionVar(q=fullName)
    else:
        return pDefaultValue

def SetOptValue(pNamespace, pName, pNewValue):
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


def SaveableCheckBox(*args, **kwargs):
    cb = cmds.checkBox(*args, **kwargs)

    if 'label' not in kwargs or (not kwargs['label']):
        raise Exception('Checkbox \'{}\' without label will not be saveable'.format(cb))

    if 'changeCommand' in kwargs:
        raise Exception('Checkbox \'{}\' should not have \'changeCommand\' callback to be saveable'.format(cb))


    namespace = cb.split('|')[0] #get window name from checkbox path
    optionName = kwargs['label'].replace(' ', '_')
    startValue = GetOptValue(namespace, optionName, kwargs.get('value', False))
    cmds.checkBox(cb, edit=True, value=startValue) # Set initial value
    cmds.checkBox(cb, edit=True, changeCommand=(lambda newValue: SetOptValue(namespace, optionName, newValue))) # Calback to save value

    return cb
