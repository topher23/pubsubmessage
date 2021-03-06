# Assignment 2: Sub Pub Extravaganza
# Christopher Dorick, Cameron Spiller
import time
from multiprocessing.pool import ThreadPool
import json
import pika
import argparse
import signal
import atexit
import os
import sys


pool = ThreadPool(processes=2)
publish_stats=True

# Ends program gracefully
def stop_stats_service(signal, frame):
    sys.exit(0)


# Creates JSON object to be sent to RabbitMQ Server
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

# Parses CPU utilization information
def cpuUsage():
    with open('/proc/uptime', 'r') as uptime:
        time1 = uptime.readline().split()
        time.sleep(1)
        uptime.seek(0)
        time2 = uptime.readline().split()

        upDelta = float(time2[0]) - float(time1[0])
        idleDelta = float(time2[1])- float(time1[1])


        utilization = 1 - (idleDelta/upDelta)
        return utilization

# Parses network utilization information
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

def shutdown():
    print "Shutting down..."
    if channel is not None:
        channel.close()
    if message_broker is not None:
        message_broker.close()
    #connection.close()


# Connect to RabbitMQ Server and start sending JSON information
try:
    signal_num = signal.SIGINT
    try:
        signal.signal(signal_num, stop_stats_service)
        signal_num = signal.SIGTERM
        signal.signal(signal_num, stop_stats_service)

    except ValueError, ve:
        print "Warning: Greceful shutdown may not be possible: Unsupported " \
              "Signal: " + signal_num

    parser = argparse.ArgumentParser(description = "Parses network and CPU statistics and publishes to RabbitMQ Server")
    parser.add_argument("-b", "--messagebroker",  help="This is the IP address or named address of the message broker to connect to", required=True)
    parser.add_argument("-p", "--virtualhost", help="This is the virtual host to connect to on the message broker. If not specified, should default to the root virtual host")
    parser.add_argument("-c", help="Use the given credentials when connecting to the message broker. The format is 'login:password'. If not specified, should default to a guest login.", required=True)
    parser.add_argument("-k", "--routingkey", help="The routing key to use when publishing messages to the message broker", required=True)
    args = parser.parse_args()

    channel = None
    vhost = "/"
    etype='pi_utilization'
    key = args.routingkey
    ipaddr = args.messagebroker
    fullcred = ['guest', 'guest']
    if args.c is not None:
        fullcred = args.c.split(':')
    if args.virtualhost is not None:
    	vhost = args.virtualhost
    print ipaddr
    print fullcred
    print vhost
    print key

    message_broker = None
    channel = None
    try:
        # Connect to the message broker using the given broker address (host)
        # Use the virtual host (vhost) and credential information (credentials),
        # if provided

        # Setup the channel and exchange
        credentials = pika.PlainCredentials(fullcred[0], fullcred[1])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ipaddr, 
        	                                        port=5672,
        	                                        virtual_host=vhost,
        	                                        credentials=credentials))
        channel = connection.channel()
        etype='pi_utilization'
        channel.exchange_declare(exchange=etype,type='direct')

        # Loop until the application is asked to quit
        while(publish_stats):
            jsonsend = createJSON()
            channel.basic_publish(exchange=etype,routing_key=key,body=jsonsend)
            time.sleep(1)
            print jsonsend
            print publish_stats

    # Pika Error Handling
    except pika.exceptions.AMQPError, ae:
        print "Error: An AMQP Error occured: One or more of your parameters was incorect and/or a connection could not be made"

    except pika.exceptions.ChannelError, ce:
        print "Error: A channel error occured: " + ce.message

    except Exception, eee:
        print "Error: An unexpected exception occured: " + eee.message

except ValueError:
    print "Error: A parameter was not of the correct type specified."