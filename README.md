MFD display client for Orbiter space flight simulator.
Act as VNC client for VNCMFT plugin.

Modifications:
1) Auth/encryption removed. No need for VNCMFD
2) Added keyboard shortcuts to simulate
   MFD Soft button pressing.
3) Fix RGB color problem. Red and blues was swapped.
   Don't know who to blame: python client or VNCMFD plugin
4) Command line parameter functionality fixed.
   You can use "python3 orbitermfdclient.py vnc://your.ip.address:port"
5) Removed compressed data encoding support from VNC client.

ToDo:
1) Add Raspberry Pi GPIO to simulate MFD Soft button pressing.
2) Server discovery and receive screen autoconfig via UDP. Separate soft
3) Measure MFD latency. Maybe compressed data encoding removal was mistake
4) More code cleanup.
5) Hardware schematics.
6) Case to completed project.
7) Test keypad matrix support from adafruit
   https://learn.adafruit.com/matrix-keypad/python-circuitpython

Original code:
https://github.com/shenjinti/python-vnc-viewer

---------------------------------------------------------------------------------
Following info from original code
---------------------------------------------------------------------------------
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
