from functools import partial

from qtpy import QtCore, QtGui, QtWidgets

translate = partial(QtCore.QCoreApplication.translate, "self")


MONOSPACE_FONT = QtGui.QFont("Monospace")
MONOSPACE_FONT.setStyleHint(QtGui.QFont.Monospace)
