#!/usr/bin/env python

import colorsys
import math
import time
import threading
import random

# import unicornhathd as unicorn
import unicornhat as unicorn

class LedHandler:

    def __init__(self):
        self.on = True

        # default stun & release time = 100, can be changed
        self.stunTime = 100
        self.releaseTime = 100

        # booleans used as control structure for threads
        self.idle = True
        self.stunned = False
        self.release = False

        self.restartStun = False
        self.restartRelease = False

        # color is changed within the server file, defaults to blue
        self.color = "blue"

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
    def startIdle(self):
        self.idle = False
        self.stunned = False
        self.release = False    

    # starts a stunned thread and stops other led threads
    # if already stunned, restarts current stun thread
    def startStun(self):
        self.idle = False
        self.release = False
        if self.stunned == True:
            self.restartStun = True
        else:
            self.stunned = True
            threading.Thread(target=self.stunnedLED).start()

    # starts a release thread and stops other led threads
    # if already releasing, restarts current thread
    def startRelease(self):
        self.idle = False
        self.stunned = False
        if self.release == True:
            self.restartRelease = True
        else:
            self.release = True
            threading.Thread(target=self.releaseLED).start()


    # controls led's to create a breathing effect
    # can be blue, green, or red depending on self.color
    # when it starts stunning or releasing, idle thread waits in the background
    # for all other threads to complete, then restarts itself
    def idleLED(self):

        step = 50
        dim = True

        while self.idle and not self.stunned and not self.release:
        # Loop over all pixels
            for y in range(self.u_height):
                for x in range(self.u_width):
                    
                    if self.color == "blue":
                        r = 0
                        g = 0
                        b = step * 5
                    if self.color == "green":
                        r = 0
                        g = step * 5
                        b = 0
                    if self.color == "red":
                        r = step * 5
                        g = 0
                        b = 0

                    # Makes sure we stay between 0 - 255
                    r = int(max(0, min(255, r)))
                    g = int(max(0, min(255, g)))
                    b = int(max(0, min(255, b)))
                    
                    unicorn.set_pixel(x, y, r, g, b)                   
            unicorn.show()
            
            if step >= 50:
                dim = True
                time.sleep(3)
            elif step <= 0:
                dim = False

            if dim:
                step -= 0.08
            else:
                step += 0.08

        while self.on:
            time.sleep(0.5)
            if self.on and self.idle == False and self.stunned == False and self.release == False:
                self.idle = True
                break
            
        if self.on and self.idle == True:
            self.idleLED()


    # flashes all LED's red - random delays
    # restarts the function if self.restartStun == True
    # lasts for (self.stunTime) seconds
    def stunnedLED(self):

        step = 0
        red = False

        start_time = time.time()

        while time.time() - start_time < self.stunTime and self.stunned and not self.restartStun:
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

        self.stunned = False


    # starts a rainbow animation on the LED's
    # pulled from unicornhat example files
    # lasts for (self.releaseTime) seconds
    def releaseLED(self):

        start_time = time.time()
        interval = float(self.releaseTime) / 32

        i = 0.0
        offset = 30


        while time.time() - start_time <= self.releaseTime and self.release and not self.restartRelease:
            i = i + 0.3
            for y in range(self.u_height):
                for x in range(self.u_width):

                    led_num = y + (x * 4)

                    if False: #led_num < (time.time() - start_time) / interval:
                        r = 0
                        g = 0
                        b = 250
                    else:
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

        self.release = False

    # stopps all threads and turns the unicorn hat off
    def off(self):
        self.on = False
        self.idle = False
        self.stunned = False
        self.release = False
        time.sleep(0.5)
        unicorn.off()

    # restarts the idle thread from off state
    def start(self):
        self.on = True
        self.idle = True
        self.stunned = False
        self.release = False
        threading.Thread(target=self.idleLED).start()



