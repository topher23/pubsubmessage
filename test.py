import signal
import sys
import time
killme = True

def killer(signal, frame):
  killme = False
  print("bang.. bang..")

signal.signal(signal.SIGINT, killer)
signal.signal(signal.SIGTERM, killer)

while(killme):
  print("alive")
  time.sleep(1)

print("dead")

