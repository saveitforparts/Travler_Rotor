#Python program to control Winegard Trav'ler antenna as an AZ/EL Rotor
#Version 2.0
#Fixes delay issue from prior versions
#Gabe Emerson / Saveitforparts 2025, Email: gabe@saveitforparts.com

import serial
import socket 
import regex as re

#initialize some variables
current_az = 0.0  
current_el = 0.0
move_nbr = 0

#define "antenna" as the serial port device to interface with
antenna = serial.Serial(
	port='/dev/ttyUSB0',             #pass this from command line in future?
	baudrate = 57600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1)

print ('Antenna connected on ', antenna.port)

#Prep the Trav'ler firmware to accept commands
antenna.write(bytes(b'q\r')) #go back to root menu in case firmware was left in a submenu
antenna.write(bytes(b'\r')) #clear firmware prompt to avoid unknown command errors
antenna.write(bytes(b'mot\r')) #enter motor submenu

#listen to local port for rotctld commands
listen_ip = '127.0.0.1'  #listen on localhost
listen_port = 4533     #pass this from command line in future?
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.bind((listen_ip, listen_port))
client_socket.listen(1)

while 1:
	print ('Listening for rotor commands on', listen_ip, ':', listen_port)
	print ('Ctrl-C to exit')
	conn, addr = client_socket.accept()
	print ('Connection from ',addr)
	
	#pass rotor commands to antenna
	while 1:
		data = conn.recv(100)  #get Gpredict's message
		if not data:
			break
			
		cmd = data.decode("utf-8").strip().split(" ")   #grab the incoming command
		
		if cmd[0] == "p":   #Gpredict is requesting position
			
			#ask antenna for position
			antenna.write(bytes(b'a\r')) #get current Az/El/Sk
			antenna.flush()	
			
			#read current position from antenna
			reply1 = antenna.read(200).decode(errors='ignore').strip()      #read dish response
			
			#Regular expression patterns to find AZ and EL values
			az_pattern = r"AZ =(\s+\d+\.\d+)"
			el_pattern = r"EL =(\s+\d+\.\d+)"
	
			#Use re.search to extract the values
			az_match = re.search(az_pattern, reply1)
			el_match = re.search(el_pattern, reply1)
	
			#If matches are found, extract the numerical values
			if az_match and el_match:
			    current_az = float(az_match.group(1))
			    current_el = float(el_match.group(1))
			else:
			    print("AZ or EL not found.")
			
			print("Current position:", current_az,", ", current_el)
			
			response = "{}\n{}\n".format(current_az, current_el) #put az & el into the format Gpredict expects
			conn.send(response.encode('utf-8')) #send response to Gpredict
			antenna.flush()
			
		elif cmd[0] == "P":   #Gpredict is sending desired position
		
			target_az = float(cmd[1])
			target_el = float(cmd[2])
			print('Gpredict requesting move to:', target_az,', ', target_el)
			print('\n')
			
			#Set movement a little farther than requested to "leap-frog" over position. 
			#This helps avoid the antenna lagging behind the satellite in the middle of the pass
			if target_az - current_az > 2:
				target_az+=1
			elif target_az - current_az < -2:
				target_az-=1	
			elif target_az - current_az > 1:
				target_az+=0.5
			elif target_az - current_az < -1:
				target_az-=0.5	
			if target_el - current_el > 2:
				target_az+=1
			elif target_el - current_el < -2:
				target_az-=1	
			elif target_el - current_el > 1:
				target_az+=0.5
			elif target_el - current_el < -1:
				target_az-=0.5	
		
			#tell Antenna to move to target position 
			#Alternate AZ and EL motions to avoid one waiting on the other
			if (move_nbr % 2) == 0: #Even numbered step, send AZ first
				
				command = ('a 0 ' + str(target_az) + '\r').encode('ascii') #move azimuth motor
				antenna.write(command)
			
				#tell Antenna to move to target el
				#if (target_el < 15):  #Trav'ler firmware won't reliably go below 15 degrees with this method
				#	target_el = 15
				command = ('a 1 ' + str(target_el) + '\r').encode('ascii') #move elevation motor
				antenna.write(command)	
			
			else: #Odd numbered step, send EL first
				
				#tell Antenna to move to target el
				#if (target_el < 15):  
				#	target_el = 15
				command = ('a 1 ' + str(target_el) + '\r').encode('ascii') #move elevation motor
				antenna.write(command)	
				
				#tell Antenna to move to target az
				command = ('a 0 ' + str(target_az) + '\r').encode('ascii') #move azimuth motor
				antenna.write(command)
						
			#Tell Gpredict things went correctly
			response="RPRT 0\n "  #Everything's under control, situation normal
			conn.send(response.encode('utf-8'))
			move_nbr+=1 #increment step counter
			
			
		elif cmd[0] == "S": #Gpredict says to stop, so exit loop and listen for a new connection
			print('Gpredict disconnected!') 
			move_nbr = 0
			conn.close()
			break
						
		elif cmd[0] == "_": #Gpredict asks for model name (does it ever do this?)
			response = "Saveitforparts Winegard Trav'ler Interface v2.0"
			conn.send(response.encode('utf-8'))
			
		else:
			print('Exiting.')
			antenna.write(bytes(b'q\r')) #go back to root menu
			antenna.write(bytes(b'\r'))
			conn.close()
			antenna.close()
			exit()
	
	
	
	
	
