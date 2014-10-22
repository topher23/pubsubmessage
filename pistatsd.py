# Assignment 2: Sub Pub Extravaganza
# Christopher Dorick, Cameron Spiller 
import time


uptime = open('/proc/uptime', 'r')

while True
	run()
	time.sleep(1)

def run():
    uptime1 = uptime.readline()
    uptime2 = uptime.readline()

def cpuUsage():
	time1 = uptime.readline().split()
	time.sleep(1)	
	uptime.seek(0)
	time2 = uptime.readline().split()

	upDelta = float(time2[0]) - float(time1[0])
	print upDelta
	idleDelta = float(time2[1])- float(time1[1])
	print idleDelta

	utilization = 1 - (idleDelta/(upDelta * 4))
	return utilization
def netUsage():

