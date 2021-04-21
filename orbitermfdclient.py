#!/usr/bin/env python

"""
Python VNC Viewer
PyGame version
(C) 2003 <cliechti@gmx.net>

MIT License
"""
import rfb
import sdl2
import sdl2.ext
import time
import asyncio
import ctypes
import struct

from sdl2 import render, rect, surface

from os import uname

if "x86" in uname().machine.lower():
    rpi = False
elif "arm" in uname().machine.lower():
    rpi = True

if rpi:
    print("Machine: RPi")
    import RPi.GPIO as GPIO
    import digitalio
    import board
    import adafruit_matrixkeypad
    cols = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19, board.D26, board.D12)]
    #rows = [digitalio.DigitalInOut(x) for x in (board.D13, board.D12, board.D11, board.D10)]
    rows = [digitalio.DigitalInOut(x) for x in (board.D16, board.D20, board.D21)]
    keys = ((1, 2, 3, 4, 5, 6),
            ('q', 'w', 'e', 'r', 't', 'y', ),
            ('z', 'x', 'c'))
    keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

def key2xy(key):

    x = 1
    y = 1
    if key == ord("1"):
        x = 20
        y = 25
    elif key == ord("2"):
        x = 20
        y = 65
    elif key == ord("3"):
        x = 20
        y = 105
    elif key == ord("4"):
        x = 20
        y = 145
    elif key == ord("5"):
        x = 20
        y = 185
    elif key == ord("6"):
        x = 20
        y = 225

    elif key == ord("q"):
        x = 300
        y = 25
    elif key == ord("w"):
        x = 300
        y = 65
    elif key == ord("e"):
        x = 300
        y = 105
    elif key == ord("r"):
        x = 300
        y = 145
    elif key == ord("t"):
        x = 300
        y = 185
    elif key == ord("y"):
        x = 300
        y = 225

    # power button (disabled, not used)
    elif key == ord("z"):
        x = 140
        y = 105
    # select button
    elif key == ord("x"):
        #x = 140
        x = 70
        y = 1
    # menu button
    elif key == ord("c"):
        #x = 255
        x = 120
        y = 1
    
    # exit viewer
    elif key == ord("p"):
        print("P key. Exitting!")
        sdl2.ext.quit()
        exit()
    #print("x=", x, ", y=", y)
    return x, y
        
class Option:
    def __init__(self):
        self.host = 'localhost'
        self.port = 35900
        self.width = 320
        self.height = 240
        #self.width = 335
        #self.height = 255
        #self.width = 674
        #self.height = 540

        self.encoding = [ rfb.RAW_ENCODING ]

    def remote_url(self):
        return 'vnc://%s:%s' % (self.host, self.port)


EV_RESIZE = 0
EV_UPDATE_RECT = 1
EV_COPY_RECT = 2
EV_FILL_RECT = 3


class VNCClient(rfb.RFBClient):
    def __init__(self, loop, renderer, option):
        rfb.RFBClient.__init__(self, loop)
        self.loop = loop
        self.option = option
        self.renderer = renderer
        self._events = []
        self._frames = []

    def vncConnectionMade(self):
        print("Screen format: depth=%d bytes_per_pixel=%r width=%d height=%d" %
              (self.depth, self.bpp, self.width, self.height))
        print("Desktop name: %r" % self.name)

        self.setEncodings(self.option.encoding)
        self.framebufferUpdateRequest()
        self._events.append((EV_RESIZE, (self.width, self.height)))

    def updateRectangle(self, x, y, width, height, data):
        """new bitmap data. data is a string in the pixel format set
           up earlier."""
        port = rect.SDL_Rect()
        port.x = x
        port.y = y
        port.w = width
        port.h = height
        pitch = int(port.w * self.bpp / 8)
        self._events.append((EV_UPDATE_RECT, (port, data, pitch)))

    def copyRectangle(self, srcx, srcy, x, y, width, height):
        """used for copyrect encoding. copy the given rectangle
           (src, srxy, width, height) to the target coords (x,y)"""
        #print("copyRectangle", srcx, srcy, x, y, width, height)
        self._events.append((EV_COPY_RECT, (srcx, srcy, x, y, width, height)))

    def fillRectangle(self, x, y, width, height, color):
        """fill rectangle with one color"""
        #~ remoteframebuffer.CopyRect(srcx, srcy, x, y, width, height)
        #print('==========fillRectangle', x, y, width, height, color)

        port = (x, y, width, height)
        r, g, b, a = struct.unpack("!BBBB", color)
        self._events.append((EV_FILL_RECT, (port, sdl2.ext.Color(r, g, b, a))))

    def commitUpdate(self, rectangles=None):
        """called after a series of updateRectangle(), copyRectangle()
           or fillRectangle() are finished.
           typicaly, here is the place to request the next screen 
           update with FramebufferUpdateRequest(incremental=1).
           argument is a list of tuples (x,y,w,h) with the updated
           rectangles."""
        self.framebufferUpdateRequest(incremental=1)

    def nextEvents(self):
        if len(self._events) <= 0:
            return []
        evs = self._events
        self._events = []
        return evs


def load_gui(option):
    sdl2.ext.init()
    fl = None
    #fl = sdl2.SDL_WINDOW_BORDERLESS
    #fl = fl | sdl2.SDL_WINDOW_ALWAYS_ON_TOP
    #fl = fl | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP    
    window = sdl2.ext.Window("VNC Viewer [%s]" % (option.remote_url()), size=(
        option.width, option.height), position=(0, 0), flags=fl)
    window.show()
    #print("windows size")
    #print(window.size)
    return window


async def run_gui(window, renderer, client):
    running = True
    in_present = False
    buttons = 0

    renderer.clear()
    sdl2.SDL_ShowCursor(0)
    #sdl2.SDL_ShowCursor(1)

    factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
    #pformat = sdl2.pixels.SDL_AllocFormat(sdl2.pixels.SDL_PIXELFORMAT_RGB888)
    pformat = sdl2.pixels.SDL_AllocFormat(sdl2.pixels.SDL_PIXELFORMAT_BGR888)

    while running:
        evs = client.nextEvents()
        need_update = len(evs) > 0
        for ev in evs:
            if ev[0] == EV_RESIZE:
                pass
            elif ev[0] == EV_UPDATE_RECT:
                port, buf, pitch = ev[1]
                #texture = factory.create_texture_sprite(renderer, (port.w, port.h), pformat=sdl2.pixels.SDL_PIXELFORMAT_RGB888, access=render.SDL_TEXTUREACCESS_STREAMING)
                texture = factory.create_texture_sprite(renderer, (port.w, port.h), pformat=sdl2.pixels.SDL_PIXELFORMAT_BGR888, access=render.SDL_TEXTUREACCESS_STREAMING)
                tport = sdl2.SDL_Rect()
                tport.x = 0
                tport.y = 0
                tport.w = port.w
                tport.h = port.h
                render.SDL_UpdateTexture(texture.texture, tport, buf, pitch)
                renderer.copy(texture, (0, 0, port.w, port.h), (port.x, port.y, port.w, port.h))
                #renderer.copy(texture, (0, 0, port.w * 2, port.h * 2), (port.x *2 , port.y *2 , port.w * 2, port.h *2))
            elif ev[0] == EV_COPY_RECT:
                srcx, srcy, x, y, width, height = ev[1]
                texture = factory.from_surface(window.get_surface())
                renderer.copy(texture, (srcx, srcy, width, height), (x, y, width, height))
                renderer.copy(texture, (srcx, srcy, width, height), (x, y, width * 2, height * 2))
            elif ev[0] == EV_FILL_RECT:
                port, color = ev[1]
                pcolor = sdl2.pixels.SDL_MapRGBA(pformat, color.r, color.g, color.b, color.a)
                renderer.fill(port, pcolor)

        if need_update:
            in_present = True
            renderer.present()

        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

            if in_present is False:
                continue

            if event.type == sdl2.SDL_MOUSEMOTION:
                x = event.motion.x
                y = event.motion.y
                client.pointerEvent( x, y, buttons)
                #client.pointerEvent( int(x / 2), int(y / 2), buttons)
            if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                e = event.button

                if e.button == 1:
                    buttons |= 1
                elif e.button == 2:
                    buttons |= 2
                elif e.button == 3:
                    buttons |= 4
                elif e.button == 4:
                    buttons |= 8
                elif e.button == 5:
                    buttons |= 16

                client.pointerEvent( e.x, e.y, buttons)
                #client.pointerEvent( int(e.x / 2), int(e.y / 2), buttons)
            if event.type == sdl2.SDL_MOUSEBUTTONUP:
                e = event.button

                if e.button == 1:
                    buttons &= ~1
                elif e.button == 2:
                    buttons &= ~2
                elif e.button == 3:
                    buttons &= ~4
                elif e.button == 4:
                    buttons &= ~8
                elif e.button == 5:
                    buttons &= ~16

                client.pointerEvent( e.x, e.y, buttons)
                #client.pointerEvent( int(e.x / 2), int(e.y / 2) , buttons)
                #print("MouseX = ", x, "\tMouseX = ", y)

            if event.type == sdl2.SDL_KEYDOWN or event.type == sdl2.SDL_KEYUP: 
                x,y = key2xy(event.key.keysym.sym)
                print("keyX = ", x, "\tkeyY = ", y)
                if event.type == sdl2.SDL_KEYDOWN:
                    client.pointerEvent(x, y, 1)
                else:
                    client.pointerEvent(x, y, 0)

        # here is loop
        #print(time.time())
        if rpi:
            pressedkeys = keypad.pressed_keys
            if pressedkeys:
                x,y = key2xy(pressedkeys)
                waspressed.append(x,y)
                client.pointerEvent(x, y, 1)
            else:
                while waspressed:
                    x,y = waspressed.pop()
                    client.pointerEvent(x, y, 0)

        await asyncio.sleep(0.01)

async def main():

    option = Option()

    option.remote_url()
    
    window = load_gui(option)

    loop = asyncio.get_running_loop()

    flags = sdl2.render.SDL_RENDERER_SOFTWARE
    renderer = sdl2.ext.Renderer(window, flags=flags)

    client = VNCClient(loop, renderer, option)
    transport, protocol = await loop.create_connection(
        lambda: client,
        option.host, option.port)
        
    await run_gui(window, renderer, client)


if __name__ == '__main__':
    asyncio.run(main())

