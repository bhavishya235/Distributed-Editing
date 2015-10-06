import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from ext import *

import Queue
import thread
import time
from pprint import pprint
import json
import ast
from PyQt4.QtCore import QObject, pyqtSignal

# QTextCursor.insertText (self, QString text, QTextCharFormat format)
# QTextCursor.setBlockCharFormat (self, QTextCharFormat format)
# QTextCharFormat   >   http://pyqt.sourceforge.net/Docs/PyQt4/qtextcharformat.html
# QTextCursor   >   http://pyqt.sourceforge.net/Docs/PyQt4/qtextcursor.html

#python Notepad.py 5001 5002 0 127.0.0.1 127.0.0.1
#python Notepad.py 5001 5002 0 172.24.65.87 172.24.65.87
#python main.py 172.24.65.87

port101 = int(sys.argv[1])
port102 = int(sys.argv[2])
myID = int(sys.argv[3])
ip = sys.argv[4]
hostip = sys.argv[5]
conn = client.Client(port101,port102, ip, hostip)
ignoreKeys = [QtCore.Qt.Key_Left, QtCore.Qt.Key_Right, QtCore.Qt.Key_Home, QtCore.Qt.Key_End, QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_Escape, QtCore.Qt.Key_Insert, QtCore.Qt.Key_Pause, QtCore.Qt.Key_Print, QtCore.Qt.Key_SysReq, QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown, QtCore.Qt.Key_Shift, QtCore.Qt.Key_Control, QtCore.Qt.Key_Alt, QtCore.Qt.Key_CapsLock, QtCore.Qt.Key_NumLock, QtCore.Qt.Key_F1, QtCore.Qt.Key_F2, QtCore.Qt.Key_F3, QtCore.Qt.Key_F4, QtCore.Qt.Key_F5, QtCore.Qt.Key_F6, QtCore.Qt.Key_F7, QtCore.Qt.Key_F8, QtCore.Qt.Key_F9, QtCore.Qt.Key_F10, QtCore.Qt.Key_F11, QtCore.Qt.Key_F12]

AlreadyUpdated = [] #queue for maintaining changes that are reflected in the editor
WaitingUpdates = [] #queue for maintaining messages to be updated later

keyPressEdit = 1
maxProcess = 10
myVector = []

msgStructure = [{"ip":"127.0.0.1","port":"5001","cursorPos":"0","line":"-1","col":"-1","changeType":"insert","changeMsg":"t","changeKey":"key","selectionFlag":"0","selectionStart":"-1","selectionEnd":"-1","isBold":"0","isItalic":"0","isUnderLine":"0","isStrike":"0","isSuper":"0","isSub":"0","alignmentText":"left","fontText":"","fontPointSize":"0","fontColor":"","textBackgroundColor":""}]

#msgLocal = str(conn.myIP) + ':' + str(conn.myPortListen) + ':' + str(cursorPos)+","+str(line)+","+str(col)+":"+changeType+","+str(text) + ","+ str(key)+":" + str(selectionFlag)+"," + str(selectionStart)+"," + str(selectionEnd)
 
#function not in use
def changeInverseParameter(cursorPos, selectionStart, selectionEnd, selectionFlag):
    if(selectionFlag == 1):
        selectionStart = inverseOperation(selectionStart)
        selectionEnd = inverseOperation(selectionEnd)
    else:
        cursorPos = inverseOperation(cursorPos)
    return [cursorPos, selectionStart, selectionEnd]

#function not in use
def inverseOperation(cursorPos):
    offset = 0
    for u in RemoteUpdates:
        uj = json.loads(u)
        cursor = uj[0]["cursorPos"]
        if int(cursor) >= int(cursorPos):
            continue
        types = uj[0]["changeType"]
        if types == "insert":
            offset -= 1
        elif types == "delete":
            offset += 1

    print "sending offset: " + str(offset)
    print "sending cursorPos: " + str(cursorPos)        
    return str(offset + int(cursorPos))


#class for edit box
class MyTextEdit(QtGui.QTextEdit):

    def __init__(self, *args):
        QtGui.QTextEdit.__init__(self, *args)
        self.SequenceNum = 0
        
        color = QtGui.QColor("#000000")
        self.setTextColor(color);
        bgcolor = QtGui.QColor("#ffffff")
        self.setTextBackgroundColor(bgcolor);

    	for k in range(0,maxProcess):
    		myVector.append(0)

    def keyPressEvent(self, e):
        if keyPressEdit == 1:
            sendFlag = 1
            selectionFlag = 0
            selectionStart = -1
            selectionEnd = -1
            changeType = "insert"

            isBold = 0
            isItalic = 0
            isUnderLine = 0
            isSuper = 0
            isStrike = 0
            isSub = 0
            alignmentText = "left"
            fontText = ""   
            fontPointSize = 0
            fontColor = ""
            textBackgroundColor = ""

            cursor2 = self.textCursor()

            # Mortals like 1-indexed things

            cursorPos = cursor2.position()
            line = cursor2.blockNumber() + 1
            col = cursor2.columnNumber()
            text  = e.text()
            key   = e.key()

            if key == QtCore.Qt.Key_Backspace:
                text = "backspace"
                key = "backspace"
                changeType = "delete"
            elif key == QtCore.Qt.Key_Delete:
                text = "backspace"
                key = "backspace"
                changeType = "delete"
                cursorPos += 1
            elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
                key = "enter"
            elif key == QtCore.Qt.Key_Tab:
                key = "tab"
            
            if key in ignoreKeys:
                sendFlag = 0;

            if cursor2.hasSelection():
                selectionFlag = 1
                selectionStart = cursor2.selectionStart()
                selectionEnd = cursor2.selectionEnd()
            
            #get formatting
            
            if cursor2.charFormat().fontWeight() == QtGui.QFont.Bold:
                isBold = 1

            if cursor2.charFormat().fontItalic():
                isItalic = 1

            if cursor2.charFormat().fontUnderline():
                isUnderLine = 1

            if cursor2.charFormat().fontStrikeOut():
                isStrike = 1

            if cursor2.charFormat().fontStrikeOut():
                isStrike = 1

            if cursor2.charFormat().verticalAlignment() == QtGui.QTextCharFormat.AlignSuperScript:
                isSuper = 1

            if cursor2.charFormat().verticalAlignment() == QtGui.QTextCharFormat.AlignSubScript:
                isSub = 1

            if self.alignment() == Qt.AlignLeft:
                alignmentText = "left"

            if self.alignment() == Qt.AlignRight:
                alignmentText = "right"

            if self.alignment() == Qt.AlignCenter:
                alignmentText = "center"

            if self.alignment() == Qt.AlignJustify:
                alignmentText = "justify"
     
            fontText = cursor2.charFormat().font().toString()
            fontPointSize = self.fontPointSize()
            fontColor = self.textColor().name()
            textBackgroundColor = self.textBackgroundColor().name()

        QtGui.QTextEdit.keyPressEvent(self,e)

        #cursorPos, selectionStart, selectionEnd = changeInverseParameter(cursorPos, selectionStart, selectionEnd, selectionFlag)

        if keyPressEdit == 1: 
            if sendFlag==1:
                myVector[myID] += 1

                msgLocalSS = [{"ip":str(conn.myIP),"port":str(conn.myPortListen),"seq":str(self.SequenceNum),"cursorPos":str(cursorPos),"line":str(line),"col":str(col),"changeType":changeType,"changeMsg":str(text),"changeKey":str(key),"selectionFlag":str(selectionFlag),"selectionStart":str(selectionStart),"selectionEnd":str(selectionEnd),"isBold":str(isBold),"isItalic":str(isItalic),"isUnderLine":str(isUnderLine), "timeVector":str(myVector), "senderID" : str(myID),"isStrike":str(isStrike),"isSuper":str(isSuper),"isSub":str(isSub),"alignmentText":alignmentText,"fontText":str(fontText),"fontPointSize":str(fontPointSize),"fontColor":str(fontColor),"textBackgroundColor":str(textBackgroundColor)}]
                self.SequenceNum = (self.SequenceNum + 1) % conn.maxSize                
                msgLocal = json.dumps(msgLocalSS)
                AlreadyUpdated.append(msgLocal)
                conn.forwardMessage(msgLocal)   #broadcasting mssg


#class for main window
class Main(QtGui.QMainWindow):  #it inherit from PyQt's QMainWindow class
    trigger = QtCore.pyqtSignal(list)
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self,parent) #initialize parent class
        self.filename = "----Blank----"
        self.initUI()
        self.trigger.connect(self.ExecuteUpdate)
        thread.start_new_thread(self.checkQueue,())

    def closeEvent(self,event):
        #save document

        #closing
        conn.onClosing()

        #save to file
        self.saveToFile()

    def saveToFile(self):
        # Only open dialog if there is no filename yet
        if not self.filename:
            self.filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File')

        # Append extension if not there yet
        if not self.filename.endswith(".html"):
            self.filename += ".html"

        # We just store the contents of the text file along with the
        # format in html, which Qt does in a very nice way for us
        with open(self.filename,"wt") as file:
            file.write(self.text.toHtml())

    #perform inverse transform
    def OperationTransform(self,cursorPos, tempip, tempport, senderVector):
        offset = 0
        for u in AlreadyUpdated:
            uj = json.loads(u)
	    mssgindex = int(uj[0]["senderID"])
	    mssgVector = ast.literal_eval(uj[0]["timeVector"])
	    mssgtime = mssgVector[mssgindex]
	    if(senderVector[mssgindex] < mssgtime):
		    cursorP = uj[0]["cursorPos"]
		    if int(cursorP) >= int(cursorPos):
		        continue
		    types = uj[0]["changeType"]
		    if types == "insert":
		        offset += 1
		    elif types == "delete":
		        offset -= 1

        print "Offset: ",offset
        print "cursorPos: ", cursorPos
        return str(offset+int(cursorPos))



    #execute the currend update i.e. set the change in notepad
    def ExecuteUpdate(self, ssJson):
        tempIP = ssJson[0]["ip"]
        tempPort = ssJson[0]["port"]
        cursorPos = ssJson[0]["cursorPos"]
        line = ssJson[0]["line"]
        col = ssJson[0]["col"]
        changeType = ssJson[0]["changeType"]
        changeMsg = ssJson[0]["changeMsg"]
        changeKey = ssJson[0]["changeKey"]
        selectionFlag = ssJson[0]["selectionFlag"]
        selectionStart = ssJson[0]["selectionStart"]
        selectionEnd = ssJson[0]["selectionEnd"]
        senderVector = ast.literal_eval(ssJson[0]["timeVector"])

        
        isBold = ssJson[0]["isBold"]
        isItalic = ssJson[0]["isItalic"]
        isUnderLine = ssJson[0]["isUnderLine"]
        isSuper = ssJson[0]["isSuper"]
        isStrike = ssJson[0]["isStrike"]
        #print "ISSTRIKE ================ ",isStrike
        isSub = ssJson[0]["isSub"]
        alignmentText = ssJson[0]["alignmentText"]
        fontText = ssJson[0]["fontText"]
        fontPointSize = ssJson[0]["fontPointSize"]
        fontColor = ssJson[0]["fontColor"]
        textBackgroundColor = ssJson[0]["textBackgroundColor"]

        #print "recein::-- ",cursorPos,line,col,changeType,changeMsg,changeKey,selectionFlag,selectionStart,selectionEnd
        
        prevCursor = self.text.textCursor()
        cursor = self.text.textCursor()

        if selectionFlag == "1":
            selectionStart = self.OperationTransform(selectionStart, tempIP, tempPort, senderVector)
            selectionEnd = self.OperationTransform(selectionEnd, tempIP, tempPort, senderVector)
        
            cursor.setPosition(int(selectionStart))
            cursor.setPosition(int(selectionEnd), QtGui.QTextCursor.KeepAnchor);

            print "|"*30+" yes"
            if changeType=="insert":
                # change of insert ype
                cursor.removeSelectedText()

                currFormat = cursor.charFormat()
                
                if isBold=="1":
                    currFormat.setFontWeight(QtGui.QFont.Bold)
                else:
                    currFormat.setFontWeight(QtGui.QFont.Normal)
                
                if isItalic=="1":
                    currFormat.setFontItalic(True)
                else :
                    currFormat.setFontItalic(False)
                
                if isUnderLine=="1":
                    currFormat.setFontUnderline(True)
                else :
                    currFormat.setFontUnderline(False)

                if isStrike=="1":
                    currFormat.setFontStrikeOut(True)
                else :
                    currFormat.setFontStrikeOut(False)
                
                if isSuper=="1":
                    currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)
                elif isSub == "1":
                    currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)
                else:
                    currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

                fontt = QtGui.QFont()
                fontt.fromString(fontText)
                currFormat.setFont(fontt)
                currFormat.setFontPointSize(float(fontPointSize))

                color = QtGui.QColor()
                color.setNamedColor(QtCore.QString(fontColor))

                if color.isValid():
                    currFormat.setForeground(QtGui.QBrush(QtGui.QColor(fontColor)))
                else:
                    print "---------->   not Valid"
                # print "h1ll5"
                bgcolor = QtGui.QColor()
                bgcolor.setNamedColor(QtCore.QString(textBackgroundColor))
                if bgcolor.isValid():
                    currFormat.setBackground(QtGui.QBrush(QtGui.QColor(textBackgroundColor)))
                else:
                    print "---------->   not Valid"

                cursor.insertText(changeMsg,currFormat)
                
                self.text.setTextCursor(cursor)

                if alignmentText == "left":
                    self.text.setAlignment(Qt.AlignLeft)
                elif alignmentText == "right":
                    self.text.setAlignment(Qt.AlignRight)
                elif alignmentText == "center":
                    self.text.setAlignment(Qt.AlignCenter)
                elif alignmentText == "justify":
                    self.text.setAlignment(Qt.AlignJustify)
                
                self.text.setTextCursor(prevCursor)

            if changeType=="delete":
                # change of delete type
                cursor.removeSelectedText()
                self.text.setTextCursor(cursor)
                self.text.setTextCursor(prevCursor)

            if changeType=="format":
                # change of format type
                print "|"*30+" yes 2"
                currFormat = cursor.charFormat()
                if changeMsg=="bold":
                    print "|"*30+" yes 3"
                    if currFormat.fontWeight() == QtGui.QFont.Bold:
                        currFormat.setFontWeight(QtGui.QFont.Normal)
                    else:
                        currFormat.setFontWeight(QtGui.QFont.Bold)
                
                if changeMsg=="italics":
                    state = currFormat.fontItalic()
                    currFormat.setFontItalic(not state)
                
                if changeMsg=="underline":
                    state = currFormat.fontUnderline()
                    currFormat.setFontUnderline(not state)
                
                if changeMsg=="strike":
                    currFormat.setFontStrikeOut(not currFormat.fontStrikeOut())

                if changeMsg=="superscript":
                    align = currFormat.verticalAlignment()

                    # Toggle the state
                    if align == QtGui.QTextCharFormat.AlignNormal:
                        currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)
                    else:
                        currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

                if changeMsg=="subscript":
                    align = currFormat.verticalAlignment()
                    if align == QtGui.QTextCharFormat.AlignNormal:
                        currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)
                    else:
                        currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

                if changeMsg == "left":
                    self.text.setAlignment(Qt.AlignLeft)
                elif changeMsg == "right":
                    self.text.setAlignment(Qt.AlignRight)
                elif changeMsg == "center":
                    self.text.setAlignment(Qt.AlignCenter)
                elif changeMsg == "justify":
                    self.text.setAlignment(Qt.AlignJustify)

                if changeMsg=="fontFamily" or changeMsg=="fontSize":
                    fontt = QtGui.QFont()
                    fontt.fromString(fontText)
                    currFormat.setFont(fontt)
                    currFormat.setFontPointSize(float(fontPointSize))

                if changeMsg=="fontColor":
                    color = QtGui.QColor()
                    color.setNamedColor(QtCore.QString(fontColor))

                    if color.isValid():
                        currFormat.setForeground(QtGui.QBrush(QtGui.QColor(fontColor)))
                    else:
                        print "---------->   not Valid"

                if changeMsg=="highlight":
                    bgcolor = QtGui.QColor()
                    bgcolor.setNamedColor(QtCore.QString(textBackgroundColor))
                    if bgcolor.isValid():
                        currFormat.setBackground(QtGui.QBrush(QtGui.QColor(textBackgroundColor)))
                    else:
                        print "---------->   not Valid"

                cursor.setCharFormat(currFormat)
                self.text.setTextCursor(cursor)
                self.text.setTextCursor(prevCursor)

        else:
            #no selection made
            cursorPos2 = self.OperationTransform(cursorPos, tempIP, tempPort, senderVector)
            cursor.setPosition(int(cursorPos2))
            print "="*50,"h1ll1"
            if changeType=="insert":
                currFormat = cursor.charFormat()
                if isBold=="1":
                    currFormat.setFontWeight(QtGui.QFont.Bold)
                else:
                    currFormat.setFontWeight(QtGui.QFont.Normal)
                
                if isItalic=="1":
                    currFormat.setFontItalic(True)
                else :
                    currFormat.setFontItalic(False)
                
                if isUnderLine=="1":
                    currFormat.setFontUnderline(True)
                else :
                    currFormat.setFontUnderline(False)

                if isStrike=="1":
                    currFormat.setFontStrikeOut(True)
                else :
                    currFormat.setFontStrikeOut(False)
                
                if isSuper=="1":
                    currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)
                elif isSub == "1":
                    currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)
                else:
                    currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

                fontt = QtGui.QFont()
                fontt.fromString(fontText)
                currFormat.setFont(fontt)
                currFormat.setFontPointSize(float(fontPointSize))
                # print "h1ll4"
                color = QtGui.QColor()
                color.setNamedColor(QtCore.QString(fontColor))

                if color.isValid():
                    currFormat.setForeground(QtGui.QBrush(QtGui.QColor(fontColor)))
                else:
                    print "---------->   not Valid"
                # print "h1ll5"
                bgcolor = QtGui.QColor()
                bgcolor.setNamedColor(QtCore.QString(textBackgroundColor))
                if bgcolor.isValid():
                    currFormat.setBackground(QtGui.QBrush(QtGui.QColor(textBackgroundColor)))
                else:
                    print "---------->   not Valid"
                
                cursor.insertText(changeMsg,currFormat)
                self.text.setTextCursor(cursor)
                
                if alignmentText == "left":
                    self.text.setAlignment(Qt.AlignLeft)
                elif alignmentText == "right":
                    self.text.setAlignment(Qt.AlignRight)
                elif alignmentText == "center":
                    self.text.setAlignment(Qt.AlignCenter)
                elif alignmentText == "justify":
                    self.text.setAlignment(Qt.AlignJustify)
                
                self.text.setTextCursor(prevCursor)
                print "h1ll10"

            if changeType=="delete" and changeMsg == "delete":
                cursor.setPosition(int(cursorPos2)+1, QtGui.QTextCursor.KeepAnchor);
                cursor.removeSelectedText()
                self.text.setTextCursor(cursor)
                self.text.setTextCursor(prevCursor)

            if changeType=="delete" and changeMsg == "backspace":
                cursor.setPosition(int(cursorPos2)-1, QtGui.QTextCursor.KeepAnchor);
                cursor.removeSelectedText()
                self.text.setTextCursor(cursor)
                self.text.setTextCursor(prevCursor)

            if changeType=="format":
                currFormat = cursor.charFormat()

                if changeMsg=="bold":
                    if currFormat.fontWeight() == QtGui.QFont.Bold:
                        currFormat.setFontWeight(QtGui.QFont.Normal)
                    else:
                        currFormat.setFontWeight(QtGui.QFont.Bold)
                if changeMsg=="italics":
                    state = currFormat.fontItalic()
                    currFormat.setFontItalic(not state)
                if changeMsg=="underline":
                    state = currFormat.fontUnderline()
                    currFormat.setFontUnderline(not state)

                if changeMsg=="strike":
                    currFormat.setFontStrikeOut(not currFormat.fontStrikeOut())

                if changeMsg=="superscript":
                    align = currFormat.verticalAlignment()

                    # Toggle the state
                    if align == QtGui.QTextCharFormat.AlignNormal:
                        currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)
                    else:
                        currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

                if changeMsg=="subscript":
                    align = currFormat.verticalAlignment()
                    if align == QtGui.QTextCharFormat.AlignNormal:
                        currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)
                    else:
                        currFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

                if changeMsg == "left":
                    self.text.setAlignment(Qt.AlignLeft)
                elif changeMsg == "right":
                    self.text.setAlignment(Qt.AlignRight)
                elif changeMsg == "center":
                    self.text.setAlignment(Qt.AlignCenter)
                elif changeMsg == "justify":
                    self.text.setAlignment(Qt.AlignJustify)

                if changeMsg=="fontFamily" or changeMsg=="fontSize":
                    fontt = QtGui.QFont()
                    fontt.fromString(fontText)
                    currFormat.setFont(fontt)
                    currFormat.setFontPointSize(float(fontPointSize))

                if changeMsg=="fontColor":
                    color = QtGui.QColor()
                    color.setNamedColor(QtCore.QString(fontColor))

                    if color.isValid():
                        currFormat.setForeground(QtGui.QBrush(QtGui.QColor(fontColor)))
                    else:
                        print "---------->   not Valid"

                if changeMsg=="highlight":
                    bgcolor = QtGui.QColor()
                    bgcolor.setNamedColor(QtCore.QString(textBackgroundColor))
                    if bgcolor.isValid():
                        currFormat.setBackground(QtGui.QBrush(QtGui.QColor(textBackgroundColor)))
                    else:
                        print "---------->   not Valid"

                cursor.setCharFormat(currFormat)
                self.text.setTextCursor(cursor)
                self.text.setTextCursor(prevCursor)

        # cursor.deleteLater()
        # prevCursor.deleteLater()
        print "+"*30+"h1ll7"
        del cursor
        del prevCursor
		   
    
    def checkvalidity(self, senderid, senderVector):
    	if(senderVector[senderid] != myVector[senderid] + 1):
    		return False
    	for k in range(0,maxProcess):
    		if k == senderid:
    			continue
    		elif senderVector[k] > myVector[k]:
    			return False
    	return True
			

    def checkwaitingQueue(self):
        global WaitingUpdates, AlreadyUpdated, myVector
        for mssg in WaitingUpdates:
            ssJson = json.loads(mssg)
            senderid = ssJson[0]["senderID"]
            senderVector = ast.literal_eval(ssJson[0]["timeVector"])
            execute = self.checkvalidity(int(senderid), senderVector)
            print "*"*20 + "Waiting Queue"
            print execute, myVector, mssg
            if execute == True:
                self.trigger.emit(ssJson)
                #self.ExecuteUpdate(ssJson)
                myVector[senderid] += 1
                WaitingUpdates.remove(mssg)
                AlreadyUpdated.append(mssg)


    def checkQueue(self):
        global WaitingUpdates, AlreadyUpdated, myVector
        while(1):
            if(conn.editNotepad == 0):
                self.text.setReadOnly(True)
                keyPressEdit = 0
            else:
                self.text.setReadOnly(False)
                keyPressEdit = 1

            if conn.updateTextFlag == 1:
                conn.updatedText = str(self.text.toHtml())
                print "updateText " + conn.updatedText
                conn.updateTextFlag = 0

            if conn.queueEmpty == 1:
                print "waiting queue emptying.....", WaitingUpdates
                if len(WaitingUpdates) == 0:
                    AlreadyUpdated = []
                    for k in range(0,maxProcess):
                        myVector[k]= 0
                    conn.queueEmpty = 0
                    print "reseting queueEmpty"

            if not conn.updates.empty():
                print "Non Empty Queue"
                ss = conn.updates.get()
                ssJson = json.loads(ss)

                senderid = int(ssJson[0]["senderID"])
                senderVector = ast.literal_eval(ssJson[0]["timeVector"])

                #print ss
                execute = self.checkvalidity(senderid, senderVector)
                print "*"*20,"Execute = ",execute

                if execute == True:
                    self.trigger.emit(ssJson)
                    #self.ExecuteUpdate(ssJson)
                    myVector[senderid] += 1
                    AlreadyUpdated.append(ss)
                else:
                    if ss not in AlreadyUpdated:
                        WaitingUpdates.append(ss)
                        print "Wait:" ,ss, myVector

            self.checkwaitingQueue()
                
    def initToolbar(self):
        self.newAction = QtGui.QAction(QtGui.QIcon("icons/new.png"),"New",self)
        self.newAction.setStatusTip("Create a new document from scratch.")
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.triggered.connect(self.new)

        self.openAction = QtGui.QAction(QtGui.QIcon("icons/open.png"),"Open file",self)
        self.openAction.setStatusTip("Open existing document")
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.open)

        self.importAction = QtGui.QAction(QtGui.QIcon("icons/open2.png"),"Import file",self)
        self.importAction.setStatusTip("Import File")
        self.importAction.setShortcut("Ctrl+M")
        self.importAction.triggered.connect(self.importFile)

        self.saveAction = QtGui.QAction(QtGui.QIcon("icons/save.png"),"Save",self)
        self.saveAction.setStatusTip("Save document")
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self.saveToFile)

        self.printAction = QtGui.QAction(QtGui.QIcon("icons/print.png"),"Print document",self)
        self.printAction.setStatusTip("Print document")
        self.printAction.setShortcut("Ctrl+P")
        self.printAction.triggered.connect(self.printFile)

        self.previewAction = QtGui.QAction(QtGui.QIcon("icons/preview.png"),"Page view",self)
        self.previewAction.setStatusTip("Preview page before printing")
        self.previewAction.setShortcut("Ctrl+Shift+P")
        self.previewAction.triggered.connect(self.preview)
        
        # self.cutAction = QtGui.QAction(QtGui.QIcon("icons/cut.png"),"Cut",self)
        # self.cutAction.setStatusTip("Delete and copy text to clipboard")
        # self.cutAction.setShortcut("Ctrl+X")
        # self.cutAction.triggered.connect(self.text.cut)

        # self.copyAction = QtGui.QAction(QtGui.QIcon("icons/copy.png"),"Copy",self)
        # self.copyAction.setStatusTip("Copy text to clipboard")
        # self.copyAction.setShortcut("Ctrl+C")
        # self.copyAction.triggered.connect(self.text.copy)

        # self.pasteAction = QtGui.QAction(QtGui.QIcon("icons/paste.png"),"Paste",self)
        # self.pasteAction.setStatusTip("Paste text from clipboard")
        # self.pasteAction.setShortcut("Ctrl+V")
        # self.pasteAction.triggered.connect(self.text.paste)

        # self.undoAction = QtGui.QAction(QtGui.QIcon("icons/undo.png"),"Undo",self)
        # self.undoAction.setStatusTip("Undo last action")
        # self.undoAction.setShortcut("Ctrl+Z")
        # self.undoAction.triggered.connect(self.text.undo)

        # self.redoAction = QtGui.QAction(QtGui.QIcon("icons/redo.png"),"Redo",self)
        # self.redoAction.setStatusTip("Redo last undone thing")
        # self.redoAction.setShortcut("Ctrl+Y")
        # self.redoAction.triggered.connect(self.text.redo)

        #debug
        self.debugAction = QtGui.QAction(QtGui.QIcon("icons/print.png"),"Print",self)
        self.debugAction.setStatusTip("Printing document.")
        self.debugAction.setShortcut("Ctrl+P")
        self.debugAction.triggered.connect(self.printDebug)

        self.toolbar = self.addToolBar("Options")

        self.toolbar.addAction(self.newAction)
        self.toolbar.addAction(self.importAction)
        self.toolbar.addAction(self.openAction)
        self.toolbar.addAction(self.saveAction)
        self.toolbar.addSeparator()    #nserts a separator line between toolbar actions

        self.toolbar.addAction(self.printAction)
        self.toolbar.addAction(self.previewAction)        
        self.toolbar.addSeparator()    #nserts a separator line between toolbar actions

        # self.toolbar.addAction(self.cutAction)
        # self.toolbar.addAction(self.copyAction)
        # self.toolbar.addAction(self.pasteAction)
        # self.toolbar.addAction(self.undoAction)
        # self.toolbar.addAction(self.redoAction)

        self.toolbar.addSeparator()

        # Makes the next toolbar appear underneath this one
        self.addToolBarBreak()

    def initFormatbar(self):
        self.formatbar = self.addToolBar("Format")

        boldAction = QtGui.QAction(QtGui.QIcon("icons/bold.png"),"Bold",self)
        boldAction.triggered.connect(self.bold)

        italicAction = QtGui.QAction(QtGui.QIcon("icons/italic.png"),"Italic",self)
        italicAction.triggered.connect(self.italic)

        underlAction = QtGui.QAction(QtGui.QIcon("icons/underline.png"),"Underline",self)
        underlAction.triggered.connect(self.underline)

        strikeAction = QtGui.QAction(QtGui.QIcon("icons/strike.png"),"Strike-out",self)
        strikeAction.triggered.connect(self.strike)

        superAction = QtGui.QAction(QtGui.QIcon("icons/superscript.png"),"Superscript",self)
        superAction.triggered.connect(self.superScript)

        subAction = QtGui.QAction(QtGui.QIcon("icons/subscript.png"),"Subscript",self)
        subAction.triggered.connect(self.subScript)

        alignLeft = QtGui.QAction(QtGui.QIcon("icons/align-left.png"),"Align left",self)
        alignLeft.triggered.connect(self.alignLeft)

        alignCenter = QtGui.QAction(QtGui.QIcon("icons/align-center.png"),"Align center",self)
        alignCenter.triggered.connect(self.alignCenter)

        alignRight = QtGui.QAction(QtGui.QIcon("icons/align-right.png"),"Align right",self)
        alignRight.triggered.connect(self.alignRight)

        alignJustify = QtGui.QAction(QtGui.QIcon("icons/align-justify.png"),"Align justify",self)
        alignJustify.triggered.connect(self.alignJustify)

        fontBox = QtGui.QFontComboBox(self)
        fontBox.currentFontChanged.connect(self.fontFamily)

        fontSize = QtGui.QComboBox(self)
        fontSize.setEditable(True)

        # Minimum number of chars displayed
        fontSize.setMinimumContentsLength(3)

        fontSize.activated.connect(self.fontSize)

        # Typical font sizes
        fontSizes = ['6','7','8','9','10','11','12','13','14',
                     '15','16','18','20','22','24','26','28',
                     '32','36','40','44','48','54','60','66',
                     '72','80','88','96']

        for i in fontSizes:
            fontSize.addItem(i)

        fontColor = QtGui.QAction(QtGui.QIcon("icons/font-color.png"),"Change font color",self)
        fontColor.triggered.connect(self.fontColor)

        backColor = QtGui.QAction(QtGui.QIcon("icons/highlight.png"),"Change background color",self)
        backColor.triggered.connect(self.highlight)

        self.formatbar.addAction(boldAction)
        self.formatbar.addAction(italicAction)
        self.formatbar.addAction(underlAction)
        self.formatbar.addAction(strikeAction)
        self.formatbar.addAction(superAction)
        self.formatbar.addAction(subAction)

        self.formatbar.addSeparator()

        self.formatbar.addAction(alignLeft)
        self.formatbar.addAction(alignCenter)
        self.formatbar.addAction(alignRight)
        self.formatbar.addAction(alignJustify)

        self.formatbar.addSeparator()

        self.formatbar.addWidget(fontBox)
        self.formatbar.addWidget(fontSize)

        self.formatbar.addSeparator()

        self.formatbar.addAction(fontColor)
        self.formatbar.addAction(backColor)

    def initMenubar(self):
        menubar = self.menuBar()
        file = menubar.addMenu("File")
        file.addAction(self.newAction)
        file.addAction(self.importAction)
        file.addAction(self.openAction)
        file.addAction(self.saveAction)
        file.addAction(self.printAction)
        file.addAction(self.previewAction)

        #edit = menubar.addMenu("Edit")
        # edit.addAction(self.undoAction)
        # edit.addAction(self.redoAction)
        # edit.addAction(self.cutAction)
        # edit.addAction(self.copyAction)
        # edit.addAction(self.pasteAction)
        #view = menubar.addMenu("View")

    def initUI(self):
        self.text = MyTextEdit(self)
        self.text.setTabStopWidth(33)

        self.setCentralWidget(self.text)

        self.initToolbar()
        self.initFormatbar()
        self.initMenubar()

        # Initialize a statusbar for the window
        self.statusbar = self.statusBar()

        # x and y coordinates on the screen, width, height
        self.setGeometry(100,100,400,400)

        self.setWindowTitle("Notepad:"+self.filename)

    def new(self):
        #ask filename
        newFileName = ""
        newFileName = newdial.NewDial(self).show()

        #ask server for allocating this new file and make appropriate changes
        valid = conn.sendNewFileName(newFileName)

        if valid == 1:
            self.filename = newFileName
            self.setWindowTitle("Notepad:"+self.filename+":"+str(conn.myPortListen))

        else:
            reply = QtGui.QMessageBox.about(self,"Alert", "File Already Present")

    def importFile(self):
        openFileName = QtGui.QFileDialog.getOpenFileName(self, 'Import File',".","(*.html)")
        print openFileName,type(openFileName)
        #if type(openFileName) == QtCore.QString:        
            #ask server for allocating this new file and make appropriate changes
        tempFileName = str(openFileName.split('/')[-1])
        print tempFileName
        print tempFileName
        
        valid = conn.sendNewFileName(tempFileName)
        print valid

        if valid == 1:
            self.filename = tempFileName
            self.setWindowTitle("Notepad:"+self.filename+":"+str(conn.myPortListen))
            if self.filename:
                with open(openFileName,"rt") as file:
                    self.text.setText(file.read())

        else:
            reply = QtGui.QMessageBox.about(self,"Alert", "File Already Present")

    def open(self):
        #ask server for all the active files
        openFileList = self.getOpenedFiles()
        
        #select one file
        openFileName = opendial.OpenDial(self).show(openFileList)

        if type("") == type(openFileName):
            self.filename = openFileName
            self.setWindowTitle("Notepad:"+self.filename+":"+str(conn.myPortListen))

            #connect to group
            document = conn.setGroup(self.filename)
            #print "original : " + document

            s = QtCore.QString(document)
            self.text.setHtml(s)
        else:
            self.statusBar().showMessage('File not selected')

    def preview(self):
        preview = QtGui.QPrintPreviewDialog()
        preview.paintRequested.connect(lambda p: self.text.print_(p))
        preview.exec_()

    def printFile(self):
        dialog = QtGui.QPrintDialog()
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.text.document().print_(dialog.printer())

    def getOpenedFiles(self):
        openFiles = conn.getFileName()
        return openFiles

    def printDebug(self):
        data = self.text.toHtml()
        print data


    def bold(self):
        if self.text.fontWeight() == QtGui.QFont.Bold:
            self.text.setFontWeight(QtGui.QFont.Normal)
        else:
            self.text.setFontWeight(QtGui.QFont.Bold)
        self.prepareAndSend("bold")

    def italic(self):
        state = self.text.fontItalic()
        self.text.setFontItalic(not state)
        self.prepareAndSend("italics")

    def underline(self):
        state = self.text.fontUnderline()
        self.text.setFontUnderline(not state)
        self.prepareAndSend("underline")

    def strike(self):
        fmt = self.text.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.text.setCurrentCharFormat(fmt)
        self.prepareAndSend("strike")

    def superScript(self):
        fmt = self.text.currentCharFormat()
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QtGui.QTextCharFormat.AlignNormal:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)
        else:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

        self.text.setCurrentCharFormat(fmt)
        self.prepareAndSend("superscript")

    def subScript(self):
        fmt = self.text.currentCharFormat()
        align = fmt.verticalAlignment()
        if align == QtGui.QTextCharFormat.AlignNormal:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)
        else:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)
        self.text.setCurrentCharFormat(fmt)
        self.prepareAndSend("subscript")

    def alignLeft(self):
        self.text.setAlignment(Qt.AlignLeft)
        self.prepareAndSend("left")

    def alignRight(self):
        self.text.setAlignment(Qt.AlignRight)
        self.prepareAndSend("right")

    def alignCenter(self):
        self.text.setAlignment(Qt.AlignCenter)
        self.prepareAndSend("center")

    def alignJustify(self):
        self.text.setAlignment(Qt.AlignJustify)
        self.prepareAndSend("justify")
    
    def fontFamily(self,font):
        self.text.setCurrentFont(font)
        self.prepareAndSend("fontFamily")

    def fontSize(self, fontsize):
        self.text.setFontPointSize(int(fontsize))
        self.prepareAndSend("fontSize")

    def fontColor(self):
        color = QtGui.QColorDialog.getColor()
        self.text.setTextColor(color)
        self.prepareAndSend("fontColor")

    def highlight(self):
        color = QtGui.QColorDialog.getColor()
        self.text.setTextBackgroundColor(color)
        self.prepareAndSend("highlight")


    def prepareAndSend(self,msg):
        selectionFlag = 0
        selectionStart = -1
        selectionEnd = -1

        cursor = self.text.textCursor()
        cursorPos = cursor.position()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()

        alignmentText = "left"

        if self.text.alignment() == Qt.AlignLeft:
            alignmentText = "left"

        if self.text.alignment() == Qt.AlignRight:
            alignmentText = "right"

        if self.text.alignment() == Qt.AlignCenter:
            alignmentText = "center"

        if self.text.alignment() == Qt.AlignJustify:
            alignmentText = "justify"
 
        fontText = cursor.charFormat().font().toString()
        fontPointSize = self.text.fontPointSize()
        fontColor = self.text.textColor().name()
        textBackgroundColor = self.text.textBackgroundColor().name()

        if cursor.hasSelection():
            selectionFlag = 1
            selectionStart = cursor.selectionStart()
            selectionEnd = cursor.selectionEnd()

        #cursorPos, selectionStart, selectionEnd = changeInverseParameter(cursorPos, selectionStart, selectionEnd, selectionFlag)

        myVector[myID] += 1
        msgLocalSS = [{"ip":str(conn.myIP),"port":str(conn.myPortListen),"seq":str(self.text.SequenceNum),"cursorPos":str(cursorPos),"line":str(line),"col":str(col),"changeType":"format","changeMsg":msg,"changeKey":"key","selectionFlag":str(selectionFlag),"selectionStart":str(selectionStart),"selectionEnd":str(selectionEnd),"isBold":"0","isItalic":"0","isUnderLine":"0", "timeVector":str(myVector), "senderID" : str(myID),"isStrike":"0","isSuper":"0","isSub":"0","alignmentText":str(alignmentText),"fontText":str(fontText),"fontPointSize":str(fontPointSize),"fontColor":str(fontColor),"textBackgroundColor":str(textBackgroundColor)}]

        self.text.SequenceNum = (self.text.SequenceNum + 1) % conn.maxSize
        msgLocal = json.dumps(msgLocalSS)
        AlreadyUpdated.append(msgLocal)
        
        #print msgLocal
        conn.forwardMessage(msgLocal)


def main():

    app = QtGui.QApplication(sys.argv)

    main = Main()
    main.show()

    sys.exit(app.exec_())

if __name__ == "__main__":

    #start notepad window
    main()
