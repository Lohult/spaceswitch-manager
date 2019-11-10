import maya.OpenMaya as om
import pymel.core as pmc
import mgear.core as mgc

try:
    import mgear.core.node as node
except ImportError:
    om.MGlobal.displayError("Cannot find mgear.core.node")

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def constrain(drivers, driven, skipRotate_list="none", skipTranslate_list="none"):
    """Creates a parent constraint by inputting two lists of dagNodes

    Args:
        drivers (list): The driver objects as PyNodes
        driven (list): The driven objects as PyNodes
        skipRotate_list (list): ['x', 'y', 'z']

    Returns:
        list: ParentConstraint with list of weight attributes for drivers.
    """
    _logger.debug(drivers)
    _logger.debug(driven)
    cns_name = "{}_parentCns".format(driven.name())
    if pmc.objExists(cns_name):
        driven = pmc.PyNode(cns_name)
        pmc.parentConstraint(drivers, driven,
                             maintainOffset=True,
                             skipRotate=skipRotate_list,
                             skipTranslate=skipTranslate_list,
                             weightAliasList=True)
    else:
        pmc.parentConstraint(drivers, driven, name=cns_name,
                             maintainOffset=True,
                             skipRotate=skipRotate_list,
                             skipTranslate=skipTranslate_list,
                             weightAliasList=True)

    return pmc.parentConstraint(cns_name, q=True, weightAliasList=True)


def interface(ui_object, attr_name, spaces):

    attr_name = '{}'.format(attr_name)
    if len(spaces) != 1:
        enum_names = ":".join(spaces)
    else:
        enum_names = spaces

    _logger.debug(ui_object)
    _logger.debug(attr_name)

    string_ui = "{}.{}".format(ui_object.name(), attr_name)

    if pmc.objExists(string_ui):
        current_enums = ui_object.attr(attr_name).getEnums()
        match_result = set(spaces) & set(current_enums)

        if len(match_result) == 0:
            recompile = []
            for i in range(0, len(current_enums)):
                recompile.append(current_enums[i])
            enum_names = ":".join(recompile + spaces)

        pmc.addAttr(string_ui, e=True,
                    enumName=enum_names,
                    r=True,
                    w=True,
                    k=True,
                    dv=0)

    else:
        _logger.debug(enum_names)
        pmc.addAttr(ui_object, longName=attr_name,
                    attributeType='enum',
                    enumName=enum_names,
                    r=True,
                    w=True,
                    k=True,
                    dv=0)
                    
    return ui_object.attr(attr_name)

def connect(ui_object, attr_name, weight_list):

    current_enums = ui_object.attr(attr_name).getEnums()
    switch_attrs = []
    for i in range(0, len(current_enums)):
        switch_attrs.append(current_enums[i])

    _logger.debug(ui_object)
    _logger.debug(switch_attrs)
    _logger.debug(weight_list)

    for i, enum in enumerate(switch_attrs):
        if not weight_list[i].inputs():
            cond_node = node.createConditionNode(firstTerm=ui_object.attr(
                attr_name), secondTerm=switch_attrs.index(enum), operator=0, ifTrue=True, ifFalse=False)
            cond_node.outColor.outColorR.connect(weight_list[i])
            cond_node.colorIfFalseR.set(0)
