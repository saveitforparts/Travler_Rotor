#Light Duty Two-Axis Az/El rotor using portable "Carryout" satellite antenna. 

Gabe Emerson / Saveitforparts 2024. Email: gabe@saveitforparts.com

Video demo: 

**Introduction:**

This code controls a portable satellite antenna over RS-485 using serial commands. 
This is based roughly on my Carryout-Radio-Telescope project, adapted as a satellite
tracking rotor. 

The carryout_rotor.py program acts as an interface between The Winegard Carryout and
Gpredict (or possibly other hamlib / rotctld compatible programs). Commands to get
and set position are converted to Winegard firmware commands. Currently only "p", 
"P <X Y>", and "S" are implemented. 

Please note that the author is not an expert in Python, Linux, satellites, or 
radio theory! This code is very experimental, amateur, and not optimized. It will
likely void any warranty your Carryout antenna may have. There are probably better,
faster, and more efficient ways	to do some of the functions and calculations in 
the code. Please feel free to fix, improve, or add to anything (If you do, I'd
love to hear what you did and how it worked!)    


**Applications:**

- Manually aiming a Winegard Carryout antenna at specific coordinates
- Automatically tracking low-earth-orbit satellites with Gpredict
- Tracking satellites on different frequencies (replace stock Ku-band hardware)
- Tracking drones or aircraft (not tested)


**Hardware Requirements:**

This code has been developed and tested with a Winegard "Carryout" portable
satellite antenna. Specifically, a 2003 version running HandEra HAL 1.00.065
firmware. There are other variations and versions of this hardware, such as the
Carryout G2 and G3. I have not tested it with all models, but the firmware and 
commands are very similar across Winegard products. 

You will need to remove the plastic radome from the top of the antenna to access
the console port and change or modify the receiver feed.

In addition to the antenna, you will need an RS-232 to RS-485 adapter, custom
RJ-25 cable, and USB-to-Serial adapter. I used a "DTECH RS232 to RS485" converter
that includes screw terminals. The DB9 end is connected to my USB serial cable,
and the wiring terminals are connected to an RJ-25 cable (6-conductor phone cord)
as follows:

Looking at the bottom (pin side) of the RJ-25, with end of cable up, the wires
from left to right are:

Pin 1: GND
Pin 2: T/R-
Pin 3: T/R+
Pin 4: RXD-
Pin 5: RXD+
Pin 6: Not connected

(See cable1.jpb and cable2.jpg in the images folder)

Thanks to Kyle from Kismet Emergency Communications for providing the RS-485 info! 

You will also need a new antenna feed if you plan to use this system with anything
other than Ku band. I removed the reflector and LNB and replaced them with a 3D-
printed helicone antenna for L-band (https://www.thingiverse.com/thing:6436342).
The helicone is connected to a Nooelec SAWbird+GOES LNA, powered via RTL-SDR 
bias-tee. 
 

**Notes on power supply and auto-scan behavior**

The Winegard Carryout used for testing had a proprietary 12v DC jack, I replaced 
this with a standard barrel jack. The on-board DC could be stepped down to run an
embedded system or SBC if desired. Power of at least 1A seems best. 

When first powered on, the Carryout antenna goes through a series of calibration and
automatic satellite search movements. This can take approximately 10-15 minutes
to complete, depending on DIP switch settings on the control board. It may also 
produce some alarming grinding sounds from the stepper motors and gearing. Winegard
apparently did not bother to install limit switches, and uses motor stall to 
determine drive limits. 

Other users have reported that setting all DIP switches to "off" (up) disabled the 
search mode, but that did not work for me. There may be a setting in the firmware to 
disable the search, but I also have not found that (disabling tracking in the "nvs"
firmware submenu also disables the position calibration, which we want to retain for 
accurate aiming). 


**Package Requirements:**

carryout_rotor.py uses pyserial, regex, and socket.
They can be installed individually or by running "pip install -r requirements.txt"


**Setting up / testing Carryout console:**

To connect to a Carryout antenna with RS-485, you will need the cable described above
under Hardware Requirements. 

To connect to the serial console on the antenna, run "screen /dev/ttyUSB0 57600" (or 
appropriate port) on Linux, or use a Windows serial terminal to connect to the usb 
device (typically com3 or similar). You will initially get a blank screen. Typing "?"
should return a menu of available commands and submenus. Typing "q" exits the current
submenu and returns to the root menu.

Some submenus of interest include:
target: send dish to desired azimuth / elevation coordinates
motor: manual motor movements and settings
dvb: Get signal info from the stock LNB (if installed)
os: List and quit running processes, etc

	
Note that the console does not accept backspace, so if you make a mistake while typing,
just hit enter to clear the console. If necessary, close the console or unplug the 
dish to avoid a motor overrun. 


**Positioning the antenna:**

The Carryout antenna uses a 360-degree clockwise coordinate system, with the coax
/ F connector at approximately 135 degrees. You may have to run some serial console
commands like "target", "g 0 22" to find the 0 or North position. I marked my dish
with sharpie once I determined this. 
		
Generally I place the dish with the "0" position facing due North.


**Using as an Az/El rotor:**

NOTE: If your USB device is other than ttyUSB0, edit line 16 of carryout_rotor.py

Once the dish is connected, powered, and ready on a serial port, run:
"python3 carryout_rotor.py"

The code will attempt to connect to the serial port and open a socket on localhost, 
port 4533 (the default for Gpredict). 

In Gpredict's rotor settings, you will want to create a new rotor at 127.0.0.1:4533,
0->180->360, with minimum elevation 22 and maximum elevation 90 (the Carryout can't
physically drop below about 22 degrees elevation, other models may have different
limitations). 

Use Gpredict as normal to track a satellite and click "Engage" to connect to
carryout_rotor.py. Clicking "engage" a second time to disengage will close the socket,
the serial connection, and exit the python script (otherwise Gpredict crashes).  

	

