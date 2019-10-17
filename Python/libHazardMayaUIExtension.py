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
