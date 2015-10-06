from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

class NewDial(QtGui.QWidget):

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.filename = ""

    def show(self):
    	text, ok = QtGui.QInputDialog.getText(self, 'New', 'Enter File Name:')
        
        if ok:
            self.filename = str(text)
            return self.filename