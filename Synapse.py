#!/usr/bin/env python3
import time
from threading import Thread
from typing import Union, Dict

import pigpio
from pythonosc import dispatcher

pi = pigpio.pi()
piBip = "10.1.1.199"
portpiB = 7002

piBclient = SimpleUDPClient(piBip, portpiB)

# Set up GPIO ports
PINOUTS = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]
PIN_STATUS: Dict[int, Union[int, str]] = {}
for pin_number in PINOUTS:
    # set mode to output
    pi.set_mode(pin_number, pigpio.OUTPUT)
    PIN_STATUS[pin_number] = 0


def manage_pin_state(pin):
    """ async handler for pin pulsing """
    while True:
        if PIN_STATUS.get(pin) == 'pulse':
            # if this pin should be in pulse mode
            for dc in range(0, 101, 1):  # Loop from 0 to 100 stepping dc up by 1 each loop
                if PIN_STATUS.get(pin) == 'pulse':
                    # if it isn't pulse anymore, break this loop
                    pi.set_PWM_dutycycle(pin, dc)
                    time.sleep(0.01)  # wait for .05 seconds at current LED brightness level
                    print(dc)
            for dc in range(95, 0, -1):  # Loop from 95 to 5 stepping dc down by 1 each loop
                if PIN_STATUS.get(pin) == 'pulse':
                    # if it isn't pulse anymore, break this loop
                    pi.set_PWM_dutycycle(pin, dc)
                    time.sleep(0.01)  # wait for .05 seconds at current LED brightness level#
                    print(dc)
        elif str(PIN_STATUS.get(pin)).isnumeric() and PIN_STATUS.get(pin) > 0:
            # if this pin is a number value, then assign it
            pi.write(pin, PIN_STATUS.get(pin))
        else:
            # if anything else, turn the pin off
            pi.write(pin, 0)
        # might need a sleep in here


THREADS = {}  # so many threads
for pin_number in PINOUTS:
    # setup loop and loop task
    THREADS[pin_number] = Thread(target=manage_pin_state, args=(pin_number,))
    THREADS[pin_number].start()
    # THREADS[pin_number].join()


def handle_timeout():
    print("I'm IDLE")


def elwiretoggle(address, args):
    """
    switch pins between high/low - Turning EL wire On/Off.
    Triggered via OSC from Abelton Live.
    The osc messages will be either 1 or 0,
    1 if the midi note is pressed,
    zero when a note is released.
    """
    split = address.split("/toggle")
    pin_id = split.pop()
    state = int(args)
    pin = PINOUTS[int(pin_id)]
    if state == 1:
        # pi.write(pin, 1)
        PIN_STATUS[pin] = 1
        print("Toggle ON", pin_id)
    if state == 0:
        # pi.write(pin, 0)
        PIN_STATUS[pin] = 0
        print("Toggle OFF", pin_id)
        
def elwiretoggleB(address, args):
	split = address.split("/toggleB")
	piBx = split.pop()
	piBclient.send_message("/toggle%s" % piBx, args)

def elwirepulseB(address, args):
	split = address.split("/pulseeB")
	piBx = split.pop()
	piBclient.send_message("/pulsee%s" % piBx, args)

def elwirepulse(address, args):
    """
    pulse modulate the GPIO p[ins causing EL wire to pulse/fade for one cycle.
    Triggered via OSC from Abelton Live.
    With this I would like to be able to toggle the fade ON
    if a note is pressed and have it continue to pulse
    on a loop until the key is released.
    Currently i can only make it execute one cycle of the PWM funtion and then it stops,
    regardless of whether the button is still pressed or not.
    I would also like to be able to modify the RANGE variables,
    in Real time if possible,
    from a separate OSC handler that sends a float between 0.0-1.0.
    Then i will be able to change the pulse speed with a fader from abelton.
    """
    split = address.split("/pulse")
    pin_id = split.pop()
    pin = PINOUTS[int(pin_id)]
    state = int(args)
    if state == 1:
        print("Pulse ON", pin_id)
        # check if the pin has a loop
        PIN_STATUS[pin] = 'pulse'
    if state == 0:
        PIN_STATUS[pin] = 0
        # pi.set_PWM_dutycycle(pin, 0)
        print("Pulse OFF", pin_id)


dispatcher = dispatcher.Dispatcher()
for x in range(1, 25):
    dispatcher.map("/toggle%s" % x, elwiretoggle)
    dispatcher.map("/pulse%s" % x, elwirepulse)
    dispatcher.map("/toggleB%s" % x, elwiretoggleB)
    dispatcher.map("/pulseB%s" % x, elwirepulseB)
