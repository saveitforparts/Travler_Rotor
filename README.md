# Travler_Rotor
Multi-axis antenna rotor using Winegard "Trav'ler" satellite dish

Gabe Emerson / Saveitforparts 2005. Email:gabe@saveitforparts.com

Video demo of version 1: https://youtu.be/X1hnReHepFI 
Video demo of version 2: (in progress)

**Introduction:**

This code acts as an interface between Gpredict / Hamlib Rotctld and a Winegard brand "Trav'ler" satellite dish. 
These dishes are designed for vehicle use, but can be mounted to any stable surface. They can sometimes be found
2nd-hand from used RV dealerships, Craigslist / Facebook marketplace / etc.

The Winegard Trav'ler consists of an Outdoor Unit (ODU) or motorized "turret" with a standard Ku-band TV dish attached,
and an Indoor Unit (IDU), or small black box that has the power input and display screen. You will also need a DC power
supply, if the original is missing then something around 48-52VDC should work. 

Note there are several versions of the Trav'ler dish and this code has only been tested with the LG-2112. Versions with 
a GPS search may not respond to the init code that looks for a "NoGPS" flag from the firmware.

This code is experimental and will probably void the warranty on any antenna you try it with. Use at your own risk! 

![Winegard Trav'ler](images/dish.jpg?raw=true "Winegard Trav'ler")


**Applications:**

This antenna works as a general-purpose az/el rotor, and could have skew added to the code if desired. I have been using
my Trav'ler dish as an S-band LEO weather satellite tracker. It can also be used to point at GEO satellites, which is closer
to the original intended use. 

The code could be adapted for other purposes like sky surveys, Wifi or other RF surveys, etc. See my other Github projects
for some example sky surveys / radio telescope implementations using similar antennas. 

This could possibly also be used for DIY radar applications, drone tracking, point-to-point Wifi, etc. Note that the dish
has some speed and motion limits which might not make it suitable for every application. 

**Hardware Requirements:**

The stock LNB should be replaced with a feed appropriate to whatever frequency you intend to use. For example, I use 3-D 
printed helical feeds designed by DerekSGC for L and S-band. These can be found at https://www.thingiverse.com/thing:4980180

![Helical Feed](images/feed.jpg?raw=true "Helical Feed")


The internal coax cable should not be used unless you disable / bypass the onboard power injector. Otherwise 14-18VDC will
be supplied to the feed/LNA, which will kill 5VDC equipment. Also the internal wiring is likely the wrong impedance for SDR use. 

I use a Microcircuits ZX60-242LN-S+ Low Noise Amplifier connected to my helical feed, powered from a 5v USB source. Below that is an RTL-SDR Wideband LNA, powered by my SDR's bias-tee. I use a HackRF One for S-band. I keep the HackRF's onboard amp turned off to minimize noise. This seems to work well for strong satellites like NOAA and DMSP, but not for weaker ones like HINODE. The stock
33"x23" dish is probably too small for weaker signals. It might be possible to add a slightly larger reflector, but YMMV. 

Interfacing with the Trav'ler serial port requires an RS-485 cable and 6-pin phone connector (RJ-25). I have included a
diagram of the USB adapter chain that I use. It includes a USB-to-Serial cable, a DTECH RS232-to-RS485 converter, and an RJ-25 jack wired as follows (looking at the bottom of the phone connector with the tip up):
Pin 1: GND
Pin 2: T/R-
Pin 3: T/R+
Pin 4: RXD-
Pin 5: RXD+
Pin 6: Not used

![USB to serial to RS-485 to RJ-25 cable](images/cable1.jpg?raw=true "Cable for Winegard console")

![Pinout for RS-485 to RJ-25 cable](images/cable1.jpg?raw=true "Pins for RS-485 to RJ-25 cable")


**Software Requirements:**

This code was developed for Python 3. The code uses serial, socket, and regex. If not already installed, use "pip install -r requirements.txt"

If your computer uses a different serial port for the RS-485 adapter (such as COM3 for Windows or /dev/ttyACM0) you will need
to edit line 17 of travler_rotor.py and line 10 of travler_init.py

**Trav'ler Dish Basic Firmware Info**

You can interact with the Trav'ler firmware directly by connecting the RS-485 cable chain to the "Factory Only" port on the 
IDU. Then run "screen /dev/ttyUSB0 57600" (or appropriate port, you may need to check lsusb or equivalent command on your
local computer). 

Once connected to the firmware, some basic commands are:
"?": List available commands
"mot": enter the motor submenu
"a" (from within the motor submenu): Show current dish position, or set desired position by specifying motor # and degrees. 
"g" (from within motor submenu): go to a specified azimuth/elevation/skew (Some firmware has a typo listing az/sk/el). 
"q": exit the current submenu
"os": Enter the OS submenu
"tasks": list running tasks
"kill <name of task>": Kill a task (such as "kill Search" to disable the TV satellite search movement routine). 

The firmware has a lot of options, not all of which I understand. There are several ways to do various things, including
multiple motor-related submenus that all behave slightly differently. 


**Notes on Trav'ler limitations and quirks***

Physical and Firmware limitations:

The Tra'ler can physically move past 0 degrees and 90 degrees in elevation, but the firmware doesn't like to go below 15 
degrees. This is likely a built-in safety feature to keep it from impacting other objects on an RV roof. I have put in a
soft-coded limit of 15 degrees elevation in my code, and I recommend telling Gpredict that the rotor's minimum elevation is
15 degrees. Max elevation seems to be about 95 degrees, but I use 90 as the max in Gpredict. 

When using the "g" method to operate the motors, the dish will halt/abort movement if a new command (or any keystroke / 
character) comes in. 

When using the "a" method to operate motors, the dish will wait until the current motor stops moving before accepting a new 
motor command (in the case of the AZ and EL motors anyway. I believe the Skew / SK motor can run simultaneously with one
of the others).  

Initial Calibration:

When first powered on, the Trav'ler goes through a series of calibration movements to establish position and wrap limits. 
Afterwards, the default behavior is to search for a TV satellite, which for our purposes is a waste of time. The travler_init.py
script connects to the dish and waits for the calibration to complete, then kills the search in the firmware's task manager.

Stowing:

The Trav'ler dish has a built-in "stow" command which is intended to fold it flat against the roof of an RV or trailer.
I have not used this command in my code and I tend to ignore it. The modified L-band feed that replaced my LNB would
likely not survive a stow procedure. 

Cable Wrap:

The dish also has a cable wrap system that prevents it from tangling its own internal wiring. This seems to be a somewhat variable position, but is most frequently at 455 degrees. Thus the dish can spin from 0 degrees, past 360, but will halt and reverse to the other side of the wrap position upon hitting its limit. The wrap position can be found with the "a" command in the firmware's "mot" submenu. I usually address this by using Gpredict to manually run the dish through the range of motion required for the upcoming pass. This helps ensure it is on the correct side of the wrap position. If the wrap position is near the start or end of a track, I will simply disengage Gpredict during that part. 

Meridian Crossing:

The dish will cross the 0/360 position during tracking *most of the time. I have sometimes encountered issues with this where the dynamic wrap position gets set to 0. In these cases, the dish will approach 0, then stop, reverse direction and come at the new position from the other side. This can spoil a live track of a satellite. It's possible there's a way to avoid or address this. I just never got around to implementing it and don't encounter the issue often enough. 

Possible GPS issue:

Some versions of the Trav'ler have a GPS subsystem that assists with acquiring TV satellites. Other users have reported that
attempting to disable the GPS puts the IDU and ODU in a state where they no longer communicate, effectively bricking the dish.
I have not encountered this myself, as my dish does not have GPS, but it's something to watch out for. 


**Positioning the antenna**

The baseplate of the Winegard Trav'ler is marked with arrows and the word "BACK" at the 0/360-degree position (North). 
Typically I place my dish so that these arrows are aligned with true North. If using the dish as a portable unit, not bolted
to a roof or vehicle, make sure to secure the base so that the dish cannot wiggle or fall over. 
If the stow command / feature is used, North / "Back" is the position at which the dish will "faceplant" onto the ground/roof. 

**Setting up rotor in Gpredict**

In Gpredict's rotor settings, you will want to create a new rotor at 127.0.0.0:4533, with 0->180->360 mode, minimum elevation
of 15 and maximum elevation of 90. 

**Example setup and use procedure**

Your procedure may differ depending on the software and setup you use. My basic procedure for tracking a LEO satellite with
the Trav'ler is as follows:

- Connect serial cable to Trav'ler's IDU, run "./init.sh" on computer
- Power on IDU. Trav'ler will initialize and home, then init scrip will jump to rotor script. 
- Power on the first LNA with exteranl bias-tee
- Open SDR++, turn on SDR and activate second LNA with SDR's bias-tee function
- Set gains as desired (may need to max these out for faint signals)
- Keep onboard amp (for HackRF One) turned off. 
- Set Gpredict Antenna Control for desired satellite, select the correct rotor. 
- If rotor script is not already running and waiting for Gpredict, run "./rotor.sh"
- Prep SDR to record with desired bandwidth, baseband, int16
- Activate tracking and engage rotor in Gpredict. 
- Record the pass (I like to keep an eye on the dish in case it does anything weird). 
- Stop recording and disengage the rotor when the signal gets too low to be usable. 
- Run the baseband recording through Satdump. 

Some of these steps could be combined with Satdump, which can also do the rotor control, recording, and live decoding. 

Personally I like to track the current satellite in N2yo.com alongside the other windows, just to see where it is. I 
also have a security camera aimed at my dish so I can watch it moving from my computer. 

![S-Band Ground control setup](images/ground_control.jpg?raw=true "Ground control setup")




  

