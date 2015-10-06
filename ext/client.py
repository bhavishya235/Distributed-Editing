import socket
import sys
import thread
import time
import Queue
import json
import collections

class Client:
	def __init__(self,p101,p102,ip, hostip):
		self.s = socket.socket()
		self.server = socket.socket()
		self.host = hostip
		self.port = 5101
		self.flagServer_connect = 0
		self.flag_connect = 0

		self.maxSize = 100000
		self.updates = Queue.Queue()
		self.messageSequence = collections.deque(maxlen = self.maxSize)

		self.newIP = self.host
		self.newPort = self.port
		self.editNotepad = 1
		self.queueEmpty = 0

		self.myIP = ip
		self.myPortListen = p102
		self.myPortSend = p101

		self.myAddress = ip + ":" + str(p102)
		self.buffsize = 1000000000
		self.docsize= 1000000000
		self.changeneighbour = -1

		self.fileName = ""
		self.updateTextFlag = 0
		self.updatedText = ""

		self.fingerTable = []
		self.tableSize = 0
		self.predecessor = []

		self.editRoundTrip = 0
		
		self.income = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)

		self.income.bind((self.myIP, self.myPortListen))
		self.income.listen(10000)
		
		thread.start_new_thread(self.listenIndef,())

	def listenIndef(self):
		while True:
			c, addr = self.income.accept()    
			thread.start_new_thread(self.handler, (c,addr))
			#self.handler(c,addr)

	def handler(self,c,addr):
		print 'Got connection from', addr[0], addr[1]

		msg_received = c.recv(self.buffsize)
		print "Message received > ",msg_received,"--till here"

		if(msg_received == "Stop Editing"):
			self.editNotepad = 0
			
			if len(self.fingerTable) != 0:
				self.editRoundTrip = 1
				self.passMessage("Non Edit",0)
				while self.editRoundTrip == 1:
					pass

			while not self.updates.empty():
				pass

			print "update queue empty"

			self.queueEmpty = 1

			while self.queueEmpty == 1:
				pass

			print "waiting queue empty"

			self.updateTextFlag = 1			
			while(self.updateTextFlag == 1):
				pass

			print "sending updated doc: " + self.updatedText	
			c.send(self.updatedText)


		elif(msg_received == "Non Edit"):
			if(self.editRoundTrip == 1):
				self.editRoundTrip = 0

			else:
				self.editNotepad = 0
				self.passMessage("Non Edit", 0)

				while not self.updates.empty():
					pass

				self.queueEmpty = 1

		elif msg_received == "Closing":
			if len(self.fingerTable) > 1:	#ring size >= 3
				self.fingerTable[0] = self.fingerTable[1]

			elif len(self.fingerTable) <= 1:
				#this will be the only node now
				print "Error: Should not reach here"


		elif(msg_received == "Change Connection"):
			c.send("JUNK")
			self.newIP = c.recv(self.buffsize)
			c.send("JUNK")
			self.newPort = int(c.recv(self.buffsize))
			if len(self.fingerTable) != 0:
				self.fingerTable[0] = (self.newIP,self.newPort)
			else:
				self.fingerTable.append((self.newIP,self.newPort))


		elif(msg_received == "Stabilise FingerTable"):
			mssg = "Update FingerTable,0," + self.myIP + ":" + str(self.myPortListen)
			self.passMessage(mssg, 0)

		
		elif(msg_received[0:18]=="Update FingerTable"):
			mssg = msg_received.split(',')
			if mssg[1] == '0':
				ip, port = mssg[2].split(":")
				if(ip == self.myIP and port == str(self.myPortListen)):
					mssg[1] = '1'
				else:
					mssg.append(self.myIP + ":" + str(self.myPortListen))

				self.passMessage(",".join(mssg), 0)

			else:
				ip, port = mssg[2].split(":")
				if(ip == self.myIP and port == str(self.myPortListen)):
					self.updateMyFingerTable(mssg[2:])
				else:
					self.updateMyFingerTable(mssg[2:])
					self.passMessage(msg_received, 0)

				self.editNotepad = 1


		elif(msg_received=="One Remaining"):
			self.fingerTable = []
			self.predecessor = []
			self.editNotepad = 1

		else:
			if msg_received != '':
				#parse msg and forward only if not duplicate
				c.send("JUNK")
				msgJson = json.loads(msg_received)
				rcv_IP = msgJson[0]["ip"]
				rcv_Port = msgJson[0]["port"]
				rcv_Seq = msgJson[0]["seq"]

				if((rcv_IP, rcv_Port, rcv_Seq) not in self.messageSequence):
					#print "Message received " + msg_received
					self.messageSequence.append((rcv_IP, rcv_Port, rcv_Seq))
					self.updates.put(msg_received)
					for k in range(0,len(self.fingerTable)):
						self.passMessageNode(msg_received,k)
					print "-"*50



	def updateMyFingerTable(self, iplist):
		index = 1;
		myindex = iplist.index(self.myAddress)
		self.fingerTable = []
		currindex = (myindex-1)%len(iplist)
		
		self.predecessor = iplist[currindex].split(':')

		while index < len(iplist):
			currindex = (myindex + index)%len(iplist)
			ip, port = iplist[currindex].split(":")
			self.fingerTable.append((ip,int(port)))
			index = index*2
		print "Updated finger table: " , self.fingerTable

	def onClosing(self):
		self.editNotepad = 0
		if len(self.fingerTable) > 1:
			self.editRoundTrip = 1
			self.passMessage("Non Edit",0)
			while self.editRoundTrip == 1:
				pass

			#send msg to predecessor
			self.passMessagePred("Closing")

			#send msg to server with successor info and call stabilize from successor
			self.makeServerConn()

			mssg = "Exit"
			self.server.send(mssg)
			self.server.recv(self.buffsize)
			mssg = self.fileName + "," + self.myIP + "," + str(self.myPortListen)+ "," + self.fingerTable[0][0]+","+str(self.fingerTable[0][1])+ "," + self.predecessor[0]+","+str(self.predecessor[1])
			self.server.send(mssg)
			self.closeServerConn()

		elif len(self.fingerTable) == 1:
			self.editRoundTrip = 1
			print "sending two"
			self.passMessage("Non Edit",0)
			while self.editRoundTrip == 1:
				pass

			self.makeServerConn()
			self.server.send("Two Remaining")
			self.server.recv(self.buffsize)
			mssg = self.fileName + "," + self.myIP + "," + str(self.myPortListen)+ "," + self.fingerTable[0][0]+","+str(self.fingerTable[0][1])
			self.server.send(mssg)
			self.closeServerConn()

			self.fingerTable = []


		elif len(self.fingerTable) == 0:
			self.makeServerConn()
			self.server.send("Close,"+self.fileName)
			self.closeServerConn()

	def passMessage(self, fmssg, index):
		self.makeNodeSocket(self.fingerTable[index][0], self.fingerTable[index][1])
		self.s.send(fmssg)
		self.closenodeConn()


	def passMessageNode(self, fmssg, index):
		print "Forwarding to " , self.fingerTable[index]
		self.makeNodeSocket(self.fingerTable[index][0], self.fingerTable[index][1])
		self.s.send(fmssg)
		print self.s.recv(self.buffsize)
		self.closenodeConn()

	def passMessagePred(self, fmssg):
		print "Forwarding to Pred: " , self.predecessor
		self.makeNodeSocket(self.predecessor[0], int(self.predecessor[1]))
		self.s.send(fmssg)
		self.closenodeConn()


	def forwardMessage(self,fmsg):
		#send to all in fingerTable
		print "sending::--",fmsg,"--::till here"
		msgJson = json.loads(fmsg)
		rcv_IP = msgJson[0]["ip"]
		rcv_Port = msgJson[0]["port"]
		rcv_Seq = msgJson[0]["seq"]
		self.messageSequence.append((rcv_IP, rcv_Port, rcv_Seq))
		for k in range(0,len(self.fingerTable)):
			self.passMessageNode(fmsg,k)


	def makeServerConn(self):
		try:
			print str(self.myPortSend) + " connecting to server"
			self.server = socket.socket()
			self.server.bind((self.myIP, self.myPortSend))
			self.server.connect((self.host, self.port))
			self.flagServer_connect = 1
		except socket.error as socketerror:
			self.flagServer_connect = 0
			print("Error: ",socketerror)

	def closeServerConn(self):
		self.server.close()

	def closenodeConn(self):
		self.s.close()

	def sendNewFileName(self,fileName):
		self.fileName = fileName
		self.makeServerConn()
		msg = "New File:"+fileName+':'+str(self.myPortListen)
		print "Message" + msg
		self.server.send(msg)
		val = self.server.recv(self.buffsize)
		self.closeServerConn()
		print "Return value" + val
		return int(val)

	def getFileName(self):
		self.makeServerConn()
		msg = "Get File:abra"+':'+str(self.myPortListen)
		self.server.send(msg)
		val = self.server.recv(self.buffsize)
		self.closeServerConn()
		return val.split('\n')

	def setGroup(self, fileName):
		self.makeServerConn()
		self.fileName = fileName
		msg = "Set Group:"+fileName+':'+str(self.myPortListen)
		self.server.send(msg)
		document = self.server.recv(self.docsize)
		print "document", document
		self.closeServerConn()
		return document

	def makeNodeSocket(self, ip, port):
		try:
			print str(self.myPortListen) + ": " + str(ip) + " connecting to " + str(port)
			self.s = socket.socket()
			self.s.connect((ip, port))
			self.flag_connect = 1
		except socket.error as socketerror:
			self.flag_connect = 0
			print("Error: ",socketerror)
