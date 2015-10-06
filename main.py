import socket              
import thread
import sys

buffsize = 100000000
docsize = 100000000
fileList = []

fileCounter = {}

startIP = {}
endIP = {}

startPort = {}
endPort = {}

#This function sends message to node to stabilise the finger table
def stabiliseFingerTable(ip, port):
	flag_connect = 0
	try:
		s2 = socket.socket()
		s2.connect((ip, port))
		flag_connect = 1
	except socket.error as socketerror:
		flag_connect = 0
		print("Error: ",socketerror)

	if(flag_connect == 1):
		s2.send("Stabilise FingerTable")
		s2.close()


#This function receive document copy from a node to give to a new node
def takeDocument(ip,port):
	flag_connect = 0
	document = ""
	try:
		s2 = socket.socket()
		s2.connect((ip, port))
		flag_connect = 1
	except socket.error as socketerror:
		flag_connect = 0
		print("Error: ",socketerror)

	if(flag_connect == 1):
		s2.send("Stop Editing")
		document = s2.recv(docsize)
		s2.close()
	return document

#Send message if only one node is remaining in the network of a document
def sendOneremaining(ip, port):
	flag_connect = 0
	print "one"
	try:
		s2 = socket.socket()
		s2.connect((ip, port))
		flag_connect = 1
	except socket.error as socketerror:
		flag_connect = 0
		print("Error: ",socketerror)

	if(flag_connect == 1):
		s2.send("One Remaining")
		s2.close()

	

#Send message to node to make a new connection
def makeconnection(ip1, port1, ip2, port2):
	print ip1, port1, ip2, port2
	flag_connect = 0
	try:
		s2 = socket.socket()
		s2.connect((ip1, port1))
		flag_connect = 1
	except socket.error as socketerror:
		flag_connect = 0
		print("Error Make Connection: "+str(port1),socketerror)

	if(flag_connect == 1):
		s2.send("Change Connection")
		option = s2.recv(buffsize)
		s2.send(ip2)
		option = s2.recv(buffsize)
		s2.send(str(port2))
		s2.close()
	

#Here server handles the messages received from the nodes
def handler(c,addr):
	option = c.recv(buffsize)
	port = 0
	print "*"*10,"Receive from ", addr[1]
	if option != '':
		if option == "Exit":
			c.send("Junk")
			option2 = c.recv(buffsize)
			fn,cip,cport,nip,nport,pip,pport = option2.split(',')
			if startIP[fn] == cip and startPort[fn] == int(cport):
				startIP[fn] = nip
				startPort[fn] = int(nport)
			elif endIP[fn] == cip and endPort[fn] == int(cport):
				endIP[fn] = pip
				endPort[fn] = int(pport)
			stabiliseFingerTable(startIP[fn], int(startPort[fn]))

			fileCounter[fn] -= 1

		elif option == "Two Remaining":
			c.send("Junk")
			option2 = c.recv(buffsize)
			fn, cip,cport,nip,nport = option2.split(",")
			if startIP[fn] == cip and startPort[fn] == int(cport):
				startIP[fn] = nip
				startPort[fn] = int(nport)
			elif endIP[fn] == cip and endPort[fn] == int(cport):
				endIP[fn] = "null"
				endPort[fn] = 0
			fileCounter[fn] -= 1
			print "kokao"
			sendOneremaining(startIP[fn], int(startPort[fn]))

		elif option[0:5] == "Close":
			cmdType, filename = option.split(",")
			startIP[filename] = "null"
			startPort[filename] = 0
			fileCounter[filename] -= 1
			del startIP[filename]
			del startPort[filename]
			del fileCounter[filename]
			#print fileCounter,filename


		else:
			cmdType, cmdName, port = option.split(':')
			cmdName = cmdName.strip()
			print "MESSAGE", cmdName, cmdType, port
			if cmdType=="New File":
				val = '0'
				if cmdName not in fileList:
					fileList.append(cmdName)
					fileCounter[cmdName] = 1
					val = '1'
				print "INSIDE" + val
				c.send(val)

			if cmdType=="Get File":
				filenames = "\n".join(fileList)
				c.send(filenames)
				c.close()
				return

			if cmdType=="Set Group":
				if fileCounter > 0:
					document = takeDocument(startIP[cmdName], startPort[cmdName])
					print document
					c.send(document)	
				fileCounter[cmdName] += 1	

			c.close()

			port = int(port)
			if(fileCounter[cmdName] == 1):
			 	startIP[cmdName] = addr[0]
			 	startPort[cmdName] = port

			elif(fileCounter[cmdName] == 2):
			 	endIP[cmdName] = addr[0]
			 	endPort[cmdName] = port
			 	makeconnection(addr[0], port, startIP[cmdName], startPort[cmdName])
			 	makeconnection(startIP[cmdName], startPort[cmdName], addr[0], port)
			 	stabiliseFingerTable(startIP[cmdName], startPort[cmdName])

			else:
			 	makeconnection(endIP[cmdName],endPort[cmdName],addr[0], port)
			 	endIP[cmdName] = addr[0]
			 	endPort[cmdName] = port
			 	makeconnection(addr[0], port, startIP[cmdName], startPort[cmdName])
			 	stabiliseFingerTable(startIP[cmdName], startPort[cmdName])
		
		
			
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)         
host = sys.argv[1]
port = int(sys.argv[2])
s.bind((host, port))        

s.listen(10000)               

menu1 = '1. List existing files\n'
menu2 = '2. Create new doc\n'

while True:
   c, addr = s.accept()     
   handler(c,addr)
