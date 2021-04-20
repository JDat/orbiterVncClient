MFD display client for Orbiter space flight simulator.
Act as VNC cliet for VNCMFT plugin.

Modifications:
1) Auth/encryption removed. No need for VNCMFD
2) Added keyboard shorcuts to simulate
   MFD Soft button pressing.
3) Fix RGB color problem. Red and blues was swapped.
   Don't know who to blame: python client or VNCMFD plugin
4) Command line parameter functionality fixed.
   You can use python3 orbitermfdclient.py vnc://your.ip.address:port
5) Removed compressed data encoding support from VNC client.

ToDo:
*) Add Raspberry Pi GPIO to simulate MFD Soft button pressing.
*) Server discovery and receive screen autoconfig via UDP. Separate soft
*) Measure MFD latency. Maybe compressed data encoding removal was mistake
*) More code cleanup.
*) Hardware schematics.
*) Case to completed project.
*) Test keypad matrix support from adafruit
   https://learn.adafruit.com/matrix-keypad/python-circuitpython

Original code:
https://github.com/shenjinti/python-vnc-viewer

Simple VNC viewer that is built with
[Twisted-Python](https://twistedmatrix.com/trac/) and
[PyGame](http://www.pygame.org/). Originally written by
[Chris Liechti](http://homepage.hispeed.ch/py430/python/).

The viewer supports the following encodings:
  `Hextile, CoRRE, RRE, RAW, CopyRect`


-------
- (c) 2003 chris <cliechti@gmx.net>
- (c) 2009 techtonik <techtonik@gmail.com>

Released under the MIT License.

You're free to use it for commercial and noncommercial
application, modify and redistribute it as long as the
copyright notices are intact. There are no warranties, not
even that it does what it says to do ;-)


Changes:
--------
2020.04.15 - new version for python3.x (replace twisted with asyncio, pygame with sdl2)   
2015.08.29 - expored to Github
2009.12.14 - 4. another update
 * replaced crippled_des.py with pyDes
 * TAB and BACKSPACE keys now work
2009.12.3 - 3. update
 * changed license to MIT with Chris consent as Python license
   is not supported by Google Code
 * works with twisted 8.2.0
 * works with pygame 1.9.1 (blit failed on locked surfaces)
 * don't refuse to connect to 3.7 and 3.8 VNC servers
2003.3.4 - 2. release
 * improved performance with RRE, CoRRE
 * color depth can be choosen (32, 8)
 * added "fast" option
2003.3.3 - 1. public release
