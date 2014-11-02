"""
This file contains pseudo code which describes at a high level what should be
implemented for the stats client (i.e. pistatsview).

This is the basic algorithm you will want to follow, although there are other
ways to implement this pseudo code.
"""
import json
import pika
import pika.channel
import pika.exceptions
import signal
import sys
import argparse

# Create a data structure for holding the maximum and minimum values
stats_history = { "cpu": {"max": 0.0, "min": float("inf"), "current": 0.0},
                  "net": dict()}
prevMax = {}
prevMin = {}
cpuValues = {"minimum": .5, "maximum": 0}

class StatsClientChannelHelper:
    def __init__(self, channel):
        if isinstance(channel, pika.channel.Channel):
            self.__channel = channel
        else:
            raise ValueError("No valid channel to manage was passed in")
    def stop_stats_client(self, signal=None, frame=None):
        self.__channel.stop_consuming()


def on_new_msg(channel, delivery_info, msg_properties, msg):
    # Parse the JSON message into a dict
    try:
        data = json.loads(msg)

        # Check that the message appears to be well formed
        if "cpu" not in data:
            print "Warning: ignoring message: missing 'cpu' field"

        elif "net" not in data:
            print "Warning: ignoring message: missing 'net' field"

        else:
            if cpuValues['minimum'] > data['cpu']:
                cpuValues['minimum'] = data['cpu']

            if cpuValues['maximum'] < data['cpu']:
                cpuValues['maximum'] = data['cpu']

            print 'cpu: ' + str(data['cpu']) + ' [Hi: ' + str(cpuValues['maximum']) + ', Lo: ' + str(cpuValues['minimum']) + ']'
            for interface in data['net']:
                if interface not in prevMax:
                    prevMax[interface] = {'tx' : 0, 'rx' : 0}  
                    prevMin[interface] = {'tx' : 0, 'rx' : 0}  

                if prevMax[interface]['tx'] < data['net'][interface]['tx']:
                    prevMax[interface]['tx'] = data['net'][interface]['tx']

                if prevMax[interface]['rx'] < data['net'][interface]['rx']:
                    prevMax[interface]['rx'] = data['net'][interface]['rx']

                if prevMin[interface]['tx'] > data['net'][interface]['tx']:
                    prevMin[interface]['tx'] = data['net'][interface]['tx']

                if prevMin[interface]['rx'] > data['net'][interface]['rx']:
                    prevMin[interface]['rx'] = data['net'][interface]['rx']

                print interface + ': ' 'rx=' + str(int(data['net'][interface]['rx']))  +' B/s' + ' ' + ('[Hi: ' + str(int(prevMax[interface]['rx'])) + ' B/s' + ', ') + ('Lo: ' + str(int(prevMin[interface]['rx'])) + ' B/s' + '] ') + ', tx=' + str(int(data['net'][interface]['rx'])) +' B/s' + ' ' + ('[Hi: ' + str(int(prevMax[interface]['rx'])) + ' B/s' + ', ')   + ('Lo: ' + str(int(prevMin[interface]['rx']))  + ' B/s' + ']')


    except ValueError, ve:
        # Thrown by json.loads() if it could not parse a JSON object
        print "Warning: Discarding Message: received message could not be parsed"



# Application Entry Point
# ^^^^^^^^^^^^^^^^^^^^^^^

# Guard try clause to catch any errors that aren't expected
try:    
    # TODO: Parse the command line arguments
    parser = argparse.ArgumentParser(description = "View maximum and minimum CPU and network utilization of monitored devices via RabbitMQ server")
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

    try:
        credentials = pika.PlainCredentials(fullcred[0], fullcred[1])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ipaddr, 
        	                                        port=5672,
        	                                        virtual_host=vhost,
        	                                        credentials=credentials))
        channel = connection.channel()
        signal_num = signal.SIGINT
        try:
            # Create a StatsClientChannelEvents object to store a reference to
            # the channel that will need to be shutdown if a signal is caught
            channel_manager = StatsClientChannelHelper(channel)
            signal.signal(signal_num, channel_manager.stop_stats_client)
            signal_num = signal.SIGTERM
            signal.signal(signal_num, channel_manager.stop_stats_client)

        except ValueError, ve:
            print "Warning: Greceful shutdown may not be possible: Unsupported " \
                  "Signal: " + signal_num


        channel.exchange_declare(exchange=etype, type='direct')
        result = channel.queue_declare(exclusive=True)
        qname = result.method.queue

        channel.queue_bind(exchange=etype,queue=qname,routing_key=key)
        print ' [*] Waiting for messages. To exit press CTRL+C'

        def callback(ch, method, properties, body):
            print " [x] %r:%r" % (method.routing_key, body,)

        channel.basic_consume(on_new_msg, queue = qname, no_ack=True)
        channel.start_consuming()

    except pika.exceptions.AMQPError, ae:
        print "Error: An AMQP Error occured: " + ae.message

    except pika.exceptions.ChannelError, ce:
        print "Error: A channel error occured: " + ce.message

    except Exception, eee:
        print "Error: An unexpected exception occured: " + eee.message

#    finally:
        # TODO: Attempt to gracefully shutdown the connection to the message broker
        # For closing the channel gracefully see: http://pika.readthedocs.org/en/0.9.14/modules/channel.html#pika.channel.Channel.close
#        if channel is not None:
#            channel.close()
        # For closing the connection gracefully see: http://pika.readthedocs.org/en/0.9.14/modules/connection.html#pika.connection.Connection.close
#        if message_broker is not None:
#            message_broker.close()

except ValueError:
    print "you dun fucked up"
#except Exception, ee:
    # Add code here to handle the exception, print an error, and exit gracefully
