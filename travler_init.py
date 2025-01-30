#Python program to initialize Winegard Trav'ler antenna 
#(allow to home, then kill TV satellite search)
#Version 1.0
#Gabe Emerson / Saveitforparts 2024, Email: gabe@saveitforparts.com

import serial

#define "antenna" as the serial port device to interface with
antenna = serial.Serial(
	port='/dev/ttyUSB0',             #pass this from command line in future?
	baudrate = 57600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1)

print ('Antenna connected on ', antenna.port)

print ('Waiting for system to boot, ensure IDU is powered on.')

while 1:
	data = antenna.readline().decode(errors='ignore').strip()  #read serial stream from antenna
	print(data)
	if "NoGPS" in data: #Initial homing is finished, Trav'ler wants to look for TV sat
		print('Antenna motor homing finished.')
		print('Cancelling Search task.')
		antenna.write(bytes(b'q\r')) #go back to root menu in case firmware was left in a submenu
		antenna.write(bytes(b'\r')) #clear firmware prompt to avoid unknown command errors
		antenna.write(bytes(b'os\r')) #enter OS submenu
		antenna.write(bytes(b'kill Search\r')) #kill Search task
		antenna.write(bytes(b'q\r')) #go back to root menu 
		antenna.write(bytes(b'\r'))
		print('Antenna is ready for rotor script.')
		break
	else:
		continue
	
antenna.close()
exec(open("travler_rotor.py").read())
exit()





