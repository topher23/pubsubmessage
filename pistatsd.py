# Assignment 2: Sub Pub Extravaganza
# Christopher Dorick, Cameron Spiller 
import time
from multiprocessing.pool import ThreadPool
import json


pool = ThreadPool(processes=2)

	
def createJSON():
	cpuUsageThread = pool.apply_async(cpuUsage)
	netUsageThread= pool.apply_async(netUsage)
	cpuUsaged = cpuUsage()
	netUsaged = netUsage()
	cpuUsaged = cpuUsageThread.get()
	netUsaged = netUsageThread.get()

	
	data = {"net" : netUsaged, 'cpu' : cpuUsaged}
	data_string = json.dumps(data)
	return data_string

def cpuUsage():
	with open('/proc/uptime', 'r') as uptime:
		time1 = uptime.readline().split()
		time.sleep(1)
		uptime.seek(0)
		time2 = uptime.readline().split()

		upDelta = float(time2[0]) - float(time1[0])
		idleDelta = float(time2[1])- float(time1[1])


		utilization = 1 - (idleDelta/(upDelta * 4))
		return utilization
def netUsage():
	with open('/proc/net/dev', 'r') as netusage:
		lines = []
		times = []
		for x in range(0,2):
			time.sleep(1)
			lines.append(netusage.readlines())
			times.append(time.time())
			netusage.seek(0)

		rxBytes = []
		txBytes = []
		interfaces = {}
		for x in range(2, len(lines[0])):
			rxBytes = []
			txBytes = []
			read1 = lines[0][x]
			read2 = lines[1][x]

			read1 = read1.split()
			read2 = read2.split()
			interface = read1[0][:-1]
			rxBytes.append(int(read1[1]))
			rxBytes.append(int(read2[1]))
			txBytes.append(int(read1[9]))
			txBytes.append(int(read2[9]))
			interfaces[interface] = {"rx": ((rxBytes[1] - rxBytes[0])/(times[1] - times[0])), "tx": ((txBytes[1] - txBytes[0])/(times[1] - times[0])) }

		return interfaces
while True:
	print createJSON()
	time.sleep(1)