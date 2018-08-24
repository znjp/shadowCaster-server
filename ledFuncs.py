#!/usr/bin/env python

import colorsys
import math
import time
import threading
import random

# IMPORT GLOBAL SETTINGS
import settings

try:
    import unicornhat as unicorn
except:
    print time.strftime("%a, %d %b %Y %H:%M:%S",
                        time.localtime()) + " No GPIO. Going to DEBUG mode."
    settings.NOGPIO = True

class LedHandler:

    def __init__(self):
        self.on = True

        self.restartStun = False
        self.restartRelease = False

        if not settings.NOGPIO:
            # initialize the unicorn hat settings
            unicorn.brightness(1)
            unicorn.set_layout(unicorn.AUTO)
            unicorn.rotation(0)
            self.u_width,self.u_height = unicorn.get_shape()

        # starts an idle thread
        idle_thread = threading.Thread(target=self.idleLED)
        idle_thread.start()


    # unused, idle thread starts in constructor
    # idle thread automatically restarts itself if idle, stunned, and release are false
##    def startIdle(self):
##        self.idle = False
##        self.stunned = False
##        self.release = False    

    # starts a stunned thread and stops other led threads
    # if already stunned, restarts current stun thread
    def startStun(self):
        if settings.STUNNED:
            self.restartStun = True
        else:
            settings.STUNNED = True
            threading.Thread(target=self.stunnedLED).start()

    # starts a release thread and stops other led threads
    # if already releasing, restarts current thread
    def startRelease(self):
        if settings.RELEASING:
            self.restartRelease = True
        else:
            settings.RELEASING = True
            threading.Thread(target=self.releaseLED).start()


    # controls led's to create a breathing effect
    # can be blue, green, or red depending on self.color
    # when it starts stunning or releasing, idle thread waits in the background
    # for all other threads to complete, then restarts itself
    def idleLED(self):

        step = 50
        dim = True

        flash = True

        while settings.IDLE and not settings.STUNNED and not settings.RELEASING:
            if settings.DEBUG and settings.NOGPIO:
                print "IDLE."
                time.sleep(1)
            else:
                # Loop over all pixels
		for y in range(self.u_height):
                    for x in range(self.u_width):
                        if settings.COLOR == "blue":
                            r = 0
                            g = 0
                            b = step * 5
                        if settings.COLOR == "green":
                            r = 0
                            g = step * 5
                            b = 0
                        if settings.COLOR == "red":
                            r = step * 5
                            g = 0
                            b = 0
                        if settings.COLOR == "empty":
                            if flash:
                                r = 100
                                g = 0
                                b = 120
                            else:
                                r = 0
                                g = 0
                                b = 0

                        # Makes sure we stay between 0 - 255
                        r = int(max(0, min(255, r)))
                        g = int(max(0, min(255, g)))
                        b = int(max(0, min(255, b)))
                        
                        unicorn.set_pixel(x, y, r, g, b)                   
                unicorn.show()

                if settings.COLOR != "empty":
                    if step >= 50:
                        dim = True
                        time.sleep(3)
                    elif step <= 0:
                        dim = False

                    if dim:
                        step -= 0.08
                    else:
                        step += 0.08
                else:
                    if flash:
                        time.sleep(random.random() / 3)
                        flash = False
                    else:
                        time.sleep(random.random())
                        flash = True

        while self.on:
            time.sleep(1)
            if self.on and not settings.IDLE and not settings.STUNNED and not settings.RELEASING:
                settings.IDLE = True
                break
            
        if self.on and settings.IDLE == True:
            self.idleLED()


    # flashes all LED's red - random delays
    # restarts the function if self.restartStun == True
    def stunnedLED(self):

        step = 0
        red = False

        while (settings.STUNTIME > 0 and settings.STUNNED
                                and not self.restartStun):
            if settings.DEBUG and settings.NOGPIO:
                print "STUN."
                time.sleep(1)
            else:
                # Loop over all pixels
                for y in range(self.u_height):
                    for x in range(self.u_width):
                        r = step * 10
                        g = 0
                        b = 0

                        # Makes sure we stay between 0 - 255
                        r = int(max(0, min(255, r)))
                        g = int(max(0, min(255, g)))
                        b = int(max(0, min(255, b)))
                        unicorn.set_pixel(x, y, r, g, b)
                unicorn.show()
                if step >= 25:
                    dim = True
                elif step <= 0:
                    dim = False

                if dim:
                    step -= 0.5
                else:
                    step += 0.5

        if self.restartStun:
            self.restartStun = False
            self.stunnedLED()

        if settings.STUNNED:
            settings.STUNNED = False

        settings.STUNTIME = 0


    # starts a rainbow animation on the LED's
    # pulled from unicornhat example files
    def releaseLED(self):

        start_time = time.time()
        interval = float(settings.RELEASEDURATION) / 32

        i = 0.0
        offset = 30


        while (settings.RELEASETIME > 0 and settings.RELEASING
                                        and not self.restartRelease):
            if settings.DEBUG and settings.NOGPIO:
                print "RELEASING."
                time.sleep(1)
            else:
                i = i + 0.3
                for y in range(self.u_height):
                    for x in range(self.u_width):

                        r = (math.cos((x+i)/2.0) + math.cos((y+i)/2.0)) * 64.0 + 128.0
                        g = (math.sin((x+i)/1.5) + math.sin((y+i)/2.0)) * 64.0 + 128.0
                        b = (math.sin((x+i)/2.0) + math.cos((y+i)/1.5)) * 64.0 + 128.0

                        r = max(2, min(255, r + offset))
                        g = max(1, min(255, g + offset))
                        b = max(5, min(255, b + offset))
                        unicorn.set_pixel(x,y,int(r),int(g),int(b))
                unicorn.show()
                time.sleep(0.01)

        if self.restartRelease:
            self.restartRelease = False
            self.releaseLED()

        if settings.RELEASING:
            settings.RELEASING = False

        settings.RELEASETIME = 0

    # stopps all threads and turns the unicorn hat off
    def off(self):
        self.on = False
        settings.IDLE = False
        settings.STUNNED = False
        settings.RELEASING = False
        time.sleep(0.5)
        unicorn.off()

    # restarts the idle thread from off state
    def start(self):
        self.on = True
        settings.IDLE = True
        settings.STUNNED = False
        settings.RELEASING = False
        threading.Thread(target=self.idleLED).start()



