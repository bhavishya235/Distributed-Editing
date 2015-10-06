from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

class OpenDial(QtGui.QWidget):

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.itemLabel = ""

    def show(self,fileList):
        item, ok = QtGui.QInputDialog.getItem(self, "Open File","Files:", fileList, 0, False)
        if ok and item:
            return str(item)