#!/usr/bin/env python3

import argparse
import pigpio
import math
import sys
from time import sleep
import time
import types
import os
import subprocess
import threading
from threading import Thread
from os.path import isfile, join
import socket

from pythonosc import dispatcher
from pythonosc import osc_server


pi = pigpio.pi()

#Set up GPIO ports
pinouts = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]
for i in pinouts:
	pi.set_mode(i, pigpio.OUTPUT)

def handle_timeout(self):
	print ("I'm IDLE")
	
def elwiretoggle(address, args):
		split=address.split("/toggle")
		x=split.pop()
		state=int(args)
		pin=pinouts[int(x)]
		if state == 1:
			pi.write(pin, 1)
			print ("Toggle ON",x)
		if state == 0:
			pi.write(pin, 0)
			print ("Toggle OFF",x)
			
def elwirepulse(address, args):
		split=address.split("/pulse")
		x=split.pop()
		pin=pinouts[int(x)]
		state=int(args)
		if state == 1:
			#print ("Pulse ON",x)
			#dc=0
			#while True:
				for dc in range(0,101,1):# Loop from 0 to 100 stepping dc up by 1 each loop
					pi.set_PWM_dutycycle(pin,	dc)
					time.sleep(0.01)# wait for .05 seconds at current LED brightness level
					print(dc)
				for dc in range(95,0,-1):# Loop from 95 to 5 stepping dc down by 1 each loop
					pi.set_PWM_dutycycle(pin, dc)
					time.sleep(0.01)# wait for .05 seconds at current LED brightness level#
					print(dc)
		if state == 0:
			pi.set_PWM_dutycycle(pin,   0)
			print ("Pulse OFF",x)
			
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="10.1.1.181", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=7002, help="The port to listen on")
  args = parser.parse_args()

dispatcher = dispatcher.Dispatcher()
for x in range(1,25):
	dispatcher.map("/toggle%s"%x, elwiretoggle)
	dispatcher.map("/pulse%s"%x, elwirepulse)

server = osc_server.ThreadingOSCUDPServer(
 	(args.ip, args.port), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()
