import os
import sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QLabel, QHBoxLayout, QMessageBox, QLineEdit, QPushButton, QWidget, QCheckBox, QComboBox

from util.image import Color
from util.widget import Slider


class ConfigControl(QWidget):
    """ Base class for config controls. When subclassing, be sure to implement both update_from_config()
    and save_to_config().
    """
    LABEL_WIDTH = 100

    def __init__(self, item):
        super(ConfigControl, self).__init__()
        self._config_item = item
        self.setContentsMargins(0, 0, 0, 0)

    def update_from_config(self):
        """ Update the value displayed in the control by reading from the ConfigItem"""
        pass

    def save_to_config(self):
        """ Set the value of the ConfigItem to that displayed in this control. """
        pass


class ValueConfigControl(ConfigControl):
    TEXT_WIDTH = 100

    def __init__(self, config_item, txt_width=TEXT_WIDTH):
        ConfigControl.__init__(self, config_item)

        self._init_ui(txt_width)

    def _init_ui(self, txt_width):
        lbl_int = QLabel(self._config_item.tag())
        lbl_int.setFixedWidth(self.LABEL_WIDTH)

        self._txt_value = QLineEdit()
        self._txt_value.setFixedWidth(txt_width)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(lbl_int)
        hbox.addWidget(self._txt_value)
        hbox.addWidget(QLabel(self._config_item.units()))
        hbox.addStretch()

        self.setLayout(hbox)

    def update_from_config(self):
        self._txt_value.setText(str(self._config_item.value()))

    def save_to_config(self):
        self._config_item.set(self._txt_value.text())


class RangeIntConfigControl(ConfigControl):
    def __init__(self, config_item):
        ConfigControl.__init__(self, config_item)

        self._init_ui()

    def _init_ui(self):
        tag = self._config_item.tag()
        range_min = self._config_item.min()
        range_max = self._config_item.max()

        self._sld_value = Slider(tag, range_min, range_min, range_max)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self._sld_value)
        hbox.addStretch()

        self.setLayout(hbox)

    def update_from_config(self):
        self._sld_value.set_value(self._config_item.value())

    def save_to_config(self):
        self._config_item.set(self._sld_value.value())


class BoolConfigControl(ConfigControl):
    def __init__(self, config_item):
        ConfigControl.__init__(self, config_item)

        self._init_ui()
        self.update_from_config()

    def _init_ui(self):
        lbl_bool = QLabel(self._config_item.tag())
        lbl_bool.setFixedWidth(self.LABEL_WIDTH)

        self._chk_box = QCheckBox()
        self._chk_box.setTristate(False)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(lbl_bool)
        hbox.addWidget(self._chk_box)
        hbox.addStretch()

        self.setLayout(hbox)

    def update_from_config(self):
        state = 2 if self._config_item.value() == True else 0
        self._chk_box.setCheckState(state)

    def save_to_config(self):
        value = True if self._chk_box.checkState() == 2 else False
        self._config_item.set(value)


class EnumConfigControl(ConfigControl):
    COMBO_WIDTH = 150

    def __init__(self, config_item):
        ConfigControl.__init__(self, config_item)

        self._init_ui()

    def _init_ui(self):
        lbl_enum = QLabel(self._config_item.tag())
        lbl_enum.setFixedWidth(self.LABEL_WIDTH)

        self._cmbo_enum = QComboBox()
        self._cmbo_enum.setFixedWidth(self.COMBO_WIDTH)
        self._cmbo_enum.addItems(self._config_item.enum_names)

        selected = self._config_item.value()
        index = self._cmbo_enum.findText(selected, QtCore.Qt.MatchFixedString)
        self._cmbo_enum.setCurrentIndex(index)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(lbl_enum)
        hbox.addWidget(self._cmbo_enum)
        hbox.addStretch()

        self.setLayout(hbox)

    def update_from_config(self):
        selected = self._config_item.value()
        index = self._cmbo_enum.findText(selected, QtCore.Qt.MatchFixedString)
        index = max(0, index)
        self._cmbo_enum.setCurrentIndex(index)

    def save_to_config(self):
        value = self._cmbo_enum.currentText()
        self._config_item.set(value)


class DirectoryConfigControl(ConfigControl):
    BUTTON_WIDTH = 80
    TEXT_WIDTH = 200

    def __init__(self, config_item):
        ConfigControl.__init__(self, config_item)

        self._init_ui()

    def _init_ui(self):
        self._txt_dir = QLineEdit()
        self._txt_dir.setFixedWidth(self.TEXT_WIDTH)

        lbl_dir = QLabel(self._config_item.tag())
        lbl_dir.setFixedWidth(self.LABEL_WIDTH)

        btn_show = QPushButton('View Files')
        btn_show.setFixedWidth(self.BUTTON_WIDTH)
        btn_show.clicked.connect(self._open_directory)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(lbl_dir)
        hbox.addWidget(self._txt_dir)
        hbox.addWidget(btn_show)
        hbox.addStretch()

        self.setLayout(hbox)

    def update_from_config(self):
        self._txt_dir.setText(self._config_item.value())

    def save_to_config(self):
        self._config_item.set(self._txt_dir.text())

    def _open_directory(self):
        path = self._txt_dir.text()
        path = os.path.abspath(path)

        if sys.platform == 'win32':
            try:
                os.startfile(path)
            except OSError:
                QMessageBox.critical(self, "File Error", "Unable to find directory: '{}".format(path))
        else:
            QMessageBox.critical(self, "File Error", "Only available on Windows")


class ColorConfigControl(ConfigControl):
    STYLE = "background-color: {};"

    def __init__(self, config_item):
        ConfigControl.__init__(self, config_item)

        self._color = None

        self._init_ui()

    def _init_ui(self):
        lbl_color = QLabel(self._config_item.tag())
        lbl_color.setFixedWidth(self.LABEL_WIDTH)
        self._swatch = QPushButton("")
        self._swatch.setFixedWidth(25)
        self._swatch.clicked.connect(self._choose_color)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(lbl_color)
        hbox.addWidget(self._swatch)
        hbox.addStretch()

        self.setLayout(hbox)

    def update_from_config(self):
        self._color = self._config_item.value()
        self.set_swatch_color(self._color)

    def save_to_config(self):
        self._config_item.set(self._color)

    def _choose_color(self):
        self._color = self._get_dialog_color(self._color)
        self.set_swatch_color(self._color)

    def set_swatch_color(self, color):
        self._swatch.setStyleSheet(self.STYLE.format(color.to_hex()))

    @staticmethod
    def _get_dialog_color(start_color):
        color = start_color

        qt_col = QtGui.QColorDialog.getColor(start_color.to_qt())
        if qt_col.isValid():
            color = Color.from_qt(qt_col)

        return color