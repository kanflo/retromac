#!/usr/bin/env python2.7

# 
# No Copyright
# 
# The person who associated a work with this deed has dedicated the work to the
# public domain by waiving all of his or her rights to the work worldwide under
# copyright law, including all related and neighboring rights,
# to the extent allowed by law.
# 
# You can copy, modify, distribute and perform the work, even for commercial
# purposes, all without asking permission. See Other Information below.
# 
# Other Information:
# 
#     * In no way are the patent or trademark rights of any person affected
#     by CC0, nor are the rights that other persons may have in the work or in
#     how the work is used, such as publicity or privacy rights.
# 
#     * Unless expressly stated otherwise, the person who associated a work with
#     this deed makes no warranties about the work, and disclaims liability for
#     all uses of the work, to the fullest extent permitted by applicable law.
# 
#     * When using or citing the work, you should not imply endorsement
#     by the author or the affirmer.
# 
# http://creativecommons.org/publicdomain/zero/1.0/legalcode
# 

import RPi.GPIO as GPIO
import time
import subprocess
import os

pinProgrammersKey = 17
pinResetButton = 27
floppyDetect = 23
floppyEjectMotor = 22

debounceMs = 200
longpressTime = 2.5

GPIO.setmode(GPIO.BCM)

# Ejecting a Macintosh floppy:
#  1. Start eject motor
#  2. Run until the floppy has been ejected
#  3. Run for another second
#  4. Stop motor
def floppyEject():
  print "  Ejecting floppy"
  GPIO.output(floppyEjectMotor, 1)
  while GPIO.input(floppyDetect) == GPIO.LOW:
    pass
  time.sleep(1.0)
  GPIO.output(floppyEjectMotor, 0)
  print "  Ejected"


# GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.
# Both ports are wired to connect to GND on button press.
# So we'll be setting up falling edge detection for both
GPIO.setup(pinProgrammersKey, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinResetButton,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(floppyDetect,      GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(floppyEjectMotor,  GPIO.OUT)

def handleLongpress(channel):
  if channel == pinProgrammersKey:
    print "Longpress on programmer's key, halting..."
    os.system("sudo halt")
#    subprocess.call(["sudo", "halt"])
  elif channel == pinResetButton:
    print "Longpress on reset button"

def handleShortpress(channel):
  if channel == pinProgrammersKey:
    print "Programmer's key pressed"
    os.system("aplay quadra-chime.wav")
  elif channel == pinResetButton:
    print "Reset button pressed"
  else:
    print "Unknown button pressed"

def keyPressed(channel):
  print "Keypress %d %d" % (channel, GPIO.input(channel))
  if 1:
#  if GPIO.input(channel) == GPIO.LOW:
    startTime = time.time()
    while GPIO.input(channel) == GPIO.LOW:
      time.sleep(0.1)
      if time.time() - startTime > longpressTime:
        handleLongpress(channel)
        while GPIO.input(channel) == GPIO.LOW:
          pass
    if time.time() - startTime < longpressTime:
      handleShortpress(channel)
  else:
    print "Spurious key press"

# If using IRQ for the floppy
#def floppyDetected(channel):
#  print "Floppy : %d" % GPIO.input(channel)
##  if GPIO.input(channel) == GPIO.LOW:
##    print "Floppy inserted (%d)" % channel
##    floppyEject()



if GPIO.input(floppyDetect) == GPIO.LOW:
  floppyEject()

# when a falling edge is detected on port 23, regardless of whatever 
# else is happening in the program, the function my_callback2 will be run
# 'bouncetime=300' includes the bounce control written into interrupts2a.py
GPIO.add_event_detect(pinProgrammersKey, GPIO.BOTH, callback=keyPressed, bouncetime=debounceMs)
GPIO.add_event_detect(pinResetButton,    GPIO.BOTH, callback=keyPressed, bouncetime=debounceMs)
#GPIO.add_event_detect(floppyDetect, GPIO.BOTH,      callback=floppyDetected)

try:
  while 1:
    time.sleep(1)
    if GPIO.input(floppyDetect) == GPIO.LOW:
      print "Floppy inserted"
      time.sleep(4)
      floppyEject()

except KeyboardInterrupt:
  GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit
