import socket
import os
import string
import time
from threading import Thread
from getpass import getpass
import sys
#from colorama import Fore, Back, Style,init
#from colorama import init
#init()
endSuffix_str = ' EOF'
endSuffix = b' EOF'
cut_tag = ','
login = False
message_queue = []
file_lock = False
#file_location = './'
file_location = '/home/yuting/Desktop/'
file_reply_lock = True
file_write_lock = False
FP=''
sock = ''
size = 0
account = '' # calculate
#log = ''

# remove endSuffix (for String)
def mesg_rm_endSuffix(login_reply):
	global endSuffix_str
	index = login_reply.find(endSuffix_str)
	return login_reply[0:index]

# remove endSuffix (for sendfile)
def data_rm_endSuffix(mesg_b):
	global endSuffix
	index = mesg_b.find(endSuffix)
	return mesg_b[0:index]

# add endSuffix and encode
def mesg_encode(mesg):
	mesg = str(mesg)
	mesg +=endSuffix_str
	mesg = mesg.encode()
	return mesg

# remove endSuffix and decode
def mesg_decode(mesg):
	mesg = mesg.decode()
	mesg = str(mesg)
	mesg = mesg_rm_endSuffix(mesg)
	mesg_list = mesg.split(cut_tag)
	return mesg_list

def sendmesg():
	#login part
	global endSuffix_str,endSuffix,cut_tag,login,message_queue,file_lock,file_location,file_reply_lock,file_write_lock,FP,sock,account
	while True:
		# login part
		while not login:
			account = input('enter your accout:')
			account = str(account)
			passwd = getpass()
			passwd = str(passwd)
			#file_location = file_location+account+'/'  # point file 
			login_mesg = 'login'+cut_tag+account+cut_tag+passwd+endSuffix_str
			login_mesg = mesg_encode(login_mesg)
			sock.sendall(login_mesg)
			#print(Fore.GREEN +'waiting response...')
			print('waiting response...')
			time.sleep(2)
			if not login:
				#print(Fore.RED +'failure...login again.')
				print('failure...login again.')
		#file_location = file_location+account+'/'

		# after login success
		if login:
			# 
			while file_lock: #file_lock default False, after receive 'fileFrom' from server change to True
				reply = input('Accept this file? (y / n):'
				reply = 'FileReply'+cut_tag+ str(reply)
				reply_part_list = reply.split(cut_tag)
				if reply_part_list[1] == 'N' or reply_part_list[1] =='n':
					sock.sendall(mesg_encode(reply))
					file_lock = False
					break
				elif reply_part_list[1] =='Y' or reply_part_list[1] =='y':
					file_write_lock = True
					time.sleep(1)
					sock.sendall(mesg_encode(reply))
					FP = open(file_location,'wb')
					#print (Fore.GREEN +'file accept finish....')
					print ('file accept finish....')
					file_lock = False
					break
			time.sleep(1)
			message = input('Please enter your command:')
			message = str(message)
			message = message.replace(' ',cut_tag)
			# enter list to show message
			if message == 'list':
				while len(message_queue)>0:
					message = message_queue.pop()
					print (message)
			elif message[0:8] == 'sendfile':
				#print(Fore.GREEN +'file location:',file_location)
				print('file location:',file_location)
				file_reply_lock = True
				mesg_list = message.split(cut_tag)
				filename = file_location + mesg_list[2]
				print('filename: ',filename)
				#print (Fore.GREEN +'file name:',filename)
				print ('file name:',filename)
				message_b = mesg_encode(message)
				sock.sendall(message_b)
				
				#print (Fore.GREEN +'waiting server for send file...')
				print ('waiting server for send file...')
				time.sleep(3)
				# send file to server(moddle box)
				#print (Fore.GREEN +'start to send file...')
				print ('start to send file...')
				fp = open(filename,'rb')
				file_mesg = b''
				while True:
					file_data = fp.read(4096)
					if not file_data:
						break
					file_mesg +=file_data
				print ('file_mesg:',file_mesg)
				file_mesg +=endSuffix
				sock.sendall(file_mesg)
				fp.close
				time.sleep(1)

				while file_reply_lock:
					#print (Fore.GREEN +'\rwaiting reply...')
					print ('\rwaiting reply...')
					time.sleep(3)
			elif message == 'logout':
				sock.sendall(mesg_encode(message))
				time.sleep(1)
				#log.close()
				#sock.close()
				break
		
			else:
				message_b = mesg_encode(message)
				sock.sendall(message_b)
			
			time.sleep(1)
			if len(message_queue) >0:
				#print(Fore.GREEN +'You have new message...')
				print('You have new message...')
		else:
			print (Fore.RED +'station  error...')
			log.close()
			sock.close()



def recvmesg():
	global endSuffix_str,cut_tag,login,message_queue,file_lock,file_location,file_reply_lock,endSuffix,FP,file_write_lock,sock,size,account
	length = 4096
	data = b''
	while True:
		message_b = sock.recv(length)
		if not message_b:
			raise EOFError('socket close...')
		if message_b.endswith(endSuffix):
			if file_write_lock:
				#print('size: ',size)
				message_b = data_rm_endSuffix(message_b)
				FP.write(message_b)
				FP.close()
		count = len(message_b)
		while not message_b.endswith(endSuffix):

			percentage = (count / size ) * 100
			if percentage == 100:
				print ('Now : ',percentage,' %')
			else:
				print ('Now : ',percentage,' %',end='\r')
			time.sleep(1)
			#FP.write(message_b)
			data = sock.recv(length)
			if not data:
				break
			elif file_write_lock:
				message_b = data
				count = count + len(message_b)
				#print ('file data:',data)
				if message_b.endswith(endSuffix):
					#print ('code process..')
					data_2 = str(data.decode())
					data = mesg_rm_endSuffix(data_2)
					data = data.encode()
					FP.write(data)
					FP.close()
					percentage = (count // size ) * 100
					if percentage == 100:
						print ('Now : ',percentage,' %')
					else:
						print ('Now : ',percentage,' %',end='\r')
					time.sleep(1)
					break
				FP.write(data)
				#FP.close()
			elif not file_write_lock:
				message_b +=data
		
	
		if not file_write_lock:
			reply_part_list = mesg_decode(message_b)
			#log.write(reply_part_list)
			#print(reply_part_list)

		if reply_part_list[0] == 'TRUE' and file_write_lock==False:
			file_location = file_location+account+'/'
			login = True
			#print (Fore.GREEN +'message: login success')
			print ('message: login success')
			reply_part_list_len = len(reply_part_list)
			if reply_part_list_len>1 : # offline message
				#print(Fore.GREEN +'offline mesg:')
				print('offline mesg:')
				mesg = off_on_mesg(reply_part_list[1:reply_part_list_len])
				#log.write(mesg)
				print(mesg)
				
		elif reply_part_list[0] == 'friend_list' and file_write_lock==False:
				i=1
				for i in range(len(reply_part_list)):
					#print (Fore.GREEN +reply_part_list[i])
					print (reply_part_list[i])
			# message send
		elif reply_part_list[0] == 'from' and file_write_lock==False:
			mesg = off_on_mesg(reply_part_list)
			message_queue.append(mesg)
		elif reply_part_list[0] == 'sendfile' and file_write_lock==False:
				if reply_part_list[1] == 'accept':
					#print (Fore.GREEN +'accept file')
					print ('accept file')
					file_reply_lock = False

				elif reply_part_list[1] == 'denied':
					#print (Fore.RED +'denied file')
					print ('denied file')
					file_reply_lock = False

		elif reply_part_list[0] == 'FileFrom' and file_write_lock==False:
				#print('File From test')
				file_lock = True
				file_location = file_location + reply_part_list[2]
				#print('fl3: ',file_location)	
				size = int(reply_part_list[3])
		#elif reply_part_list[0] == 'size':
		#	size = int(reply_part_list[1])
		elif file_write_lock==True:
			#FP.close()
			file_write_lock=False
		else:
			mesg = ''
			for i in range(len(reply_part_list)):
				mesg =mesg+reply_part_list[i]+cut_tag
def off_on_mesg(reply_part_list):
	mesg = ''
	for i in range(len(reply_part_list)):
		mesg = mesg+reply_part_list[i]+' '
	#mesg=mesg.replace(cut_tag,' ')
	return mesg
	

if __name__ == '__main__':
	port = 8080
	host = '127.0.0.1'
	#global sock
	#client(host = '127.0.0.1',port=port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
	sock.connect((host,port))
	#print(Fore.GREEN +'client has been assigned socket name', sock.getsockname())
	print('client has been assigned socket name', sock.getsockname())
	#file_log = './nick/'
	#log = open(file_log,'wb')
	th1 = Thread(target = sendmesg)
	th2 = Thread(target = recvmesg)
	thread_op = [th1,th2]
	while True:
		for th in thread_op:
			th.setDaemon(True)
			th.start()
		th.join()
		
