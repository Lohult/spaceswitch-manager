from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import pymel.core as pmc
from maya import cmds
from spaceswitch_mgr import spaceswitch_builder as builder


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


VERSION = "1.0.0"


class SpaceSwitchDialog(QtWidgets.QDialog):

    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = SpaceSwitchDialog()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(SpaceSwitchDialog, self).__init__(parent)

        self.setWindowTitle("Space Switch Builder {}".format(VERSION))
        self.setWindowIcon(QtGui.QIcon(":parentConstraint.png"))
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)
        self.setWindowFlags(
            self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.ui_obj = QtWidgets.QLineEdit()
        self.add_ui_btn = QtWidgets.QPushButton()
        self.add_ui_btn.setIcon(QtGui.QIcon(":moveUVLeft.png"))

        self.switch_attr = QtWidgets.QLineEdit()
        self.add_attr_btn = QtWidgets.QPushButton()
        self.add_attr_btn.setIcon(QtGui.QIcon(":moveUVLeft.png"))

        self.local_obj = QtWidgets.QLineEdit()
        self.add_local_btn = QtWidgets.QPushButton()
        self.add_local_btn.setIcon(QtGui.QIcon(":moveUVLeft.png"))

        self.space_list = QtWidgets.QListWidget()

        self.skiprotbox = QtWidgets.QCheckBox("Skip Rotate")
        self.skiptranbox = QtWidgets.QCheckBox("Skip Translate")

        self.add_space_btn = QtWidgets.QPushButton("Add Driver")
        self.remove_driver_btn = QtWidgets.QPushButton("Remove Driver")
        self.build_btn = QtWidgets.QPushButton("Build")

    def create_layouts(self):
        ui_input_layout = QtWidgets.QHBoxLayout()
        ui_input_layout.addWidget(self.ui_obj)
        ui_input_layout.addWidget(self.add_ui_btn)

        attr_input_layout = QtWidgets.QHBoxLayout()
        attr_input_layout.addWidget(self.switch_attr)
        attr_input_layout.addWidget(self.add_attr_btn)

        local_input_layout = QtWidgets.QHBoxLayout()
        local_input_layout.addWidget(self.local_obj)
        local_input_layout.addWidget(self.add_local_btn)

        checkbox_layout = QtWidgets.QHBoxLayout()
        checkbox_layout.addSpacing(100)
        checkbox_layout.addWidget(self.skiprotbox)
        checkbox_layout.addWidget(self.skiptranbox)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("UI object:", ui_input_layout)
        form_layout.addRow("Switch attribute:", attr_input_layout)
        form_layout.addRow("Local", local_input_layout)
        form_layout.addRow(checkbox_layout)
        form_layout.addRow("Spaces:", self.space_list)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.add_space_btn)
        button_layout.addWidget(self.remove_driver_btn)
        button_layout.addWidget(self.build_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.add_ui_btn.clicked.connect(self.add_ui)
        self.add_attr_btn.clicked.connect(self.add_attr)
        self.add_local_btn.clicked.connect(self.add_local)

        self.add_space_btn.clicked.connect(self.append_list)
        self.remove_driver_btn.clicked.connect(self.remove_driver)
        self.build_btn.clicked.connect(self.build)

    def append_list(self):
        driver_sel = pmc.selected()

        for driver in driver_sel:
            driver_name = driver.name()
            if self.space_list.findItems(driver_name, Qt.MatchContains):
                return
            else:
                item = QtWidgets.QListWidgetItem(driver_name)
                self.space_list.addItem(item)

    def remove_driver(self):
        selected_items = self.space_list.selectedItems()
        for item in selected_items:
            indx = self.space_list.row(item)
            self.space_list.takeItem(indx)

    def add_ui(self):
        sel = pmc.selected()[0]
        self.ui_obj.setText(sel.name())
        return sel

    def add_attr(self):
        try:
            sel_obj = pmc.selected()[0]
            sel_attr = pmc.channelBox("mainChannelBox",
                                      q=True,
                                      selectedMainAttributes=True
                                      )
            attr_type = sel_obj.attr(sel_attr[0]).type()
            if attr_type == "enum":
                self.switch_attr.setText(sel_obj.attr(
                    sel_attr[0]).name().split(".")[1])
                return sel_obj.attr(sel_attr[0])
            else:
                om.MGlobal.displayInfo("Attribute must be an enum data type.")
        except TypeError:
            om.MGlobal.displayError(
                "Select an attribute in the channelbox to add or type the name of an attribute you would like to make.")
            return

    def add_local(self):
        sel = pmc.selected()[0]
        self.local_obj.setText(sel.name())
        return sel

    def build(self):
        lw = self.space_list

        drivers = []

        for x in range(lw.count()):
            drivers.append(pmc.PyNode(lw.item(x).text()))

        driven = pmc.PyNode(self.local_obj.text())

        srot = self.skiprotbox.isChecked()
        strans = self.skiptranbox.isChecked()

        if srot:
            skipRotate = ["x", "y" ,"z"]
        else:
            skipRotate = "none"
        if strans:
            skipTranslate = ["x", "y", "z"]
        else:
            skipTranslate = "none"

        weight_list = builder.constrain(drivers, driven, skipRotate, skipTranslate)

        ui = pmc.PyNode(self.ui_obj.text())
        attr = self.switch_attr.text()
        spaces = [driver.name() for driver in drivers]

        attr_obj = builder.interface(ui, attr, spaces)

        builder.connect(ui, attr, weight_list)


if __name__ == "__main__":

    try:
        space_switch_dialog.closed()  # pylint: disable=E0601
        space_switch_dialog.deleteLater()
    except:
        pass

    space_switch_dialog = SpaceSwitchDialog()
    space_switch_dialog.show()
