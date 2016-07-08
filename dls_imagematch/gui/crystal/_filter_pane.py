from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QComboBox


class FilterPane(QWidget):
    ALL = "All"
    GOOD_MATCHES = "Good Matches"
    BAD_MATCHES = "Bad Matches"

    signal_matches_filtered = QtCore.pyqtSignal(object)

    def __init__(self):
        super(FilterPane, self).__init__()

        self._feature_match = None
        self._matches = []
        self._filtered_matches = []

        # UI elements
        self._cmbo_include = None
        self._cmbo_methods = None

        self._init_ui()

    def _init_ui(self):
        filters = self._ui_create_filters()

        vbox_table = QVBoxLayout()
        vbox_table.addWidget(filters)
        vbox_table.addStretch(1)

        self.setLayout(vbox_table)

    def _ui_create_filters(self):
        label_width = 90

        lbl_include = QLabel("Include")
        lbl_include.setFixedWidth(label_width)
        self._cmbo_include = QComboBox()
        self._cmbo_include.setFixedWidth(100)
        self._cmbo_include.addItems([self.ALL, self.GOOD_MATCHES, self.BAD_MATCHES, "None"])
        self._cmbo_include.currentIndexChanged.connect(self._changed_filters)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(lbl_include)
        hbox2.addWidget(self._cmbo_include)
        hbox2.addStretch(1)

        lbl_method = QLabel("Detector")
        lbl_method.setFixedWidth(label_width)
        self._cmbo_methods = QComboBox()
        self._cmbo_methods.setFixedWidth(100)
        self._cmbo_methods.currentIndexChanged.connect(self._changed_filters)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(lbl_method)
        hbox3.addWidget(self._cmbo_methods)
        hbox3.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addStretch(1)

        box = QGroupBox("Filter")
        box.setLayout(vbox)

        return box

    def set_feature_match(self, feature_match):
        self.setEnabled(True)
        self._feature_match = feature_match
        self._matches = feature_match.matches
        self._filtered_matches = self._matches

        self._update_method_dropdown(self._matches)
        self._changed_filters()

    def clear_all(self):
        self._feature_match = None
        self._matches = []
        self._filtered_matches = []

        self._clear_selection()
        self._update_method_dropdown([])
        self._changed_filters()

    def _changed_filters(self):
        self._update_filtered_matches()
        self.signal_matches_filtered.emit(self._filtered_matches)

    def _update_method_dropdown(self, matches):
        methods = {}

        for match in matches:
            key = match.method()
            if key in methods:
                methods[key] += 1
            else:
                methods[key] = 1

        self._cmbo_methods.clear()
        self._cmbo_methods.addItem("{} ({})".format(self.ALL, len(matches)), self.ALL)
        for key, value in methods.iteritems():
            self._cmbo_methods.addItem("{} ({})".format(key, value), key)

    def _update_filtered_matches(self):
        matches = self._matches
        matches = self._filter_matches_by_include(matches)
        matches = self._filter_matches_by_method(matches)
        self._filtered_matches = matches

    def _filter_matches_by_include(self, matches):
        if self._cmbo_include is None:
            return []

        include = self._cmbo_include.currentText()
        if include == self.ALL:
            matches = matches
        elif include == self.GOOD_MATCHES:
            matches = [m for m in matches if m.is_in_transformation()]
        elif include == self.BAD_MATCHES:
            matches = [m for m in matches if not m.is_in_transformation()]
        else:
            matches = []

        return matches

    def _filter_matches_by_method(self, matches):
        if self._cmbo_methods is None:
            return []

        method_ind = self._cmbo_methods.currentIndex()
        method = self._cmbo_methods.itemData(method_ind).toString()

        if method != self.ALL:
            matches = [m for m in matches if m.method() == method]
        return matches