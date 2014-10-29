# Assignment 2: Sub Pub Extravaganza
# Christopher Dorick, Cameron Spiller
import time
from multiprocessing.pool import ThreadPool
import json
import pika
import argparse


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













try:

    # The message broker host name or IP address
    host = 'localhost'
    # The virtual host to connect to
    vhost = "/" # Defaults to the root virtual host
    # The credentials to use
    credentials = None
    # The topic to subscribe to
    topic = 'ece4564'

    # Setup signal handlers to shutdown this app when SIGINT or SIGTERM is
    # sent to this app
    # For more info about signals, see: https://scholar.vt.edu/portal/site/0a8757e9-4944-4e33-9007-40096ecada02/page/e9189bdb-af39-4cb4-af04-6d263949f5e2?toolstate-701b9d26-5d9a-4273-9019-dbb635311309=%2FdiscussionForum%2Fmessage%2FdfViewMessageDirect%3FforumId%3D94930%26topicId%3D3507269%26messageId%3D2009512
    """
    signal_num = signal.SIGINT
    try:
        signal.signal(signal_num, stop_stats_service)
        signal_num = signal.SIGTERM
        signal.signal(signal_num, stop_stats_service)

    except ValueError, ve:
        print "Warning: Greceful shutdown may not be possible: Unsupported " \
              "Signal: " + signal_num
"""
    parser = argparse.ArgumentParser(description = "Parses network and CPU statistics and publishes to RabbitMQ Server")
    parser.add_argument("-b", "--messagebroker",  help="This is the IP address or named address of the message broker to connect to", required=True)
    parser.add_argument("-p", "--virtualhost", help="This is the virtual host to connect to on the message broker. If not specified, should default to the root virtual host")
    parser.add_argument("-c", help="Use the given credentials when connecting to the message broker. The format is 'login:password'. If not specified, should default to a guest login.", required=True)
    parser.add_argument("-k", "--routingkey", help="The routing key to use when publishing messages to the message broker", required=True)
    args = parser.parse_args()

    key = args.routingkey
    # Ensure that the user specified the required arguments
    if args.messagebroker is None:
        print "You must specify a message broker to connect to"
        sys.exit()

    if topic is None:
        print "You must specify a topic to subscribe to"
        sys.exit()

    message_broker = None
    channel = None
    try:
        # TODO: Connect to the message broker using the given broker address (host)
        # Use the virtual host (vhost) and credential information (credentials),
        # if provided

        # TODO: Setup the channel and exchange

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', virtual_host=vhost))
        channel = connection.channel()
        etype='pi_utilization'
        channel.exchange_declare(exchange=etype,type='direct')

        # Loop until the application is asked to quit
        while(1):
            jsonsend = createJSON()
            channel.basic_publish(exchange=etype,routing_key=key,body=jsonsend)
            time.sleep(1)
            print jsonsend

    except pika.exceptions.AMQPError, ae:
        print "Error: An AMQP Error occured: " + ae.message

    except pika.exceptions.ChannelError, ce:
        print "Error: A channel error occured: " + ce.message

    except Exception, eee:
        print "Error: An unexpected exception occured: " + eee.message

    finally:
        # TODO: Attempt to gracefully shutdown the connection to the message broker
        
        # For closing the channel gracefully see: http://pika.readthedocs.org/en/0.9.14/modules/channel.html#pika.channel.Channel.close
        if channel is not None:
            channel.close()
        # For closing the connection gracefully see: http://pika.readthedocs.org/en/0.9.14/modules/connection.html#pika.connection.Connection.close
        if message_broker is not None:
            message_broker.close()
        connection.close()
except ValueError:
    print "you dun fucked up"
#except Exception, ee:
# Add code here to handle the exception, print an error, and exit gracefully
#
