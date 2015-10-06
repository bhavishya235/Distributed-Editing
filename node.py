import socket              
import sys
import thread
import time

s = socket.socket()         
host = "127.0.0.1" 		
port = 5000            
flag_connect = 0

newIP = host
newPort = port

myIP = "null"
myPort = 0

buffsize = 1024
changeneighbour = -1

def makesocket():
	global flag_connect, newIP, newPort, s
	try:
		print str(myPort-1) + " connecting to " + str(newPort)
		s = socket.socket()         
		s.connect((newIP, newPort))
		flag_connect = 1
	except socket.error as socketerror:
		flag_connect = 0
		print("Error: ",socketerror)

def newconnection():
	global myIP, myPort, changeneighbour
	makesocket()
	if(flag_connect==1):
		s.send("node")
		msg_received = s.recv(buffsize)
		if(msg_received == "main"):
			s.send("options")
			msg_received = s.recv(buffsize)
			print msg_received
	
			option = raw_input('Your Option[1,2]: ')
			s.send(option)
	
			if(option == '1'):
				msg_received = s.recv(buffsize)
				print msg_received

				option = raw_input('Enter name of file: ')
				s.send(option)

			if(option == '2'):
				option = raw_input('Enter name of new file: ')
				s.send(option)

			msg_received = s.recv(buffsize)
			myIP = "127.0.0.1"
			myPort = int(s.getsockname()[1]) + 1
			s.send(str(myPort))

		elif(msg_received == "node"):
			print str(myPort) + "connected to " + str(newPort)
			while(1):
				if(changeneighbour == 1):
					changeneighbour = 0
					break					
					
			
		s.close()



def handler(c,addr):
	global newIP, newPort, changeneighbour
	print 'Got connection from', addr[0], addr[1]
	
	msg_received = c.recv(buffsize)
	print msg_received
	if(msg_received == "Change Connection"):
		c.send("JUNK")
		newIp = c.recv(buffsize)
		c.send("JUNK")
		newPort = int(c.recv(buffsize))
		print str(myPort) + "going to connect to " + str(newPort) 
		if(changeneighbour == -1):
			changeneighbour = 0
			newconnection()		   
		else:					
			changeneighbour = 1
			while(changeneighbour == 1):
				pass
			time.sleep(.5)
			newconnection()

	else:
			c.send("node")
			print "nodes"
			while(1):
				break

newconnection()	
		
income = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)                       
income.bind((myIP, myPort))        
income.listen(10)   
print "IP " + str(myPort)
while True:
	c, addr = income.accept()     
	thread.start_new_thread(handler, (c,addr))
