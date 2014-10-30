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
    """
    This helper class is used to manage a channel and invoke event handlers when
    signals are intercepted
    """

    def __init__(self, channel):
        """
        Create a new StatsClientChannelEvents object

        :param channel: (pika.channel.Channel) The channel object to manage
        :raises ValueError: if channel does not appear to be valid
        :return: None
        """

        if isinstance(channel, pika.channel.Channel):
            self.__channel = channel

        else:
            raise ValueError("No valid channel to manage was passed in")


    def stop_stats_client(self, signal=None, frame=None):
        """
        Stops the pika event loop for the managed channel

        :param signal: (int) A number if a intercepted signal caused this handler
                       to be run, otherwise None
        :param frame: A Stack Frame object, if an intercepted signal caused this
                      handler to be run
        :return: None
        """
        # TODO: Attempt to gracefully stop pika's event loop
        # See: https://pika.readthedocs.org/en/0.9.14/modules/adapters/blocking.html#pika.adapters.blocking_connection.BlockingChannel.stop_consuming
        self.__channel.stop_consuming()


def on_new_msg(channel, delivery_info, msg_properties, msg):
    """
    Event handler that processes new messages from the message broker

    For details on interface for this pika event handler, see:
    https://pika.readthedocs.org/en/0.9.14/examples/blocking_consume.html

    :param channel: (pika.Channel) The channel object this message was received
                    from
    :param delivery_info: (pika.spec.Basic.Deliver) Delivery information related
                          to the message just received
    :param msg_properties: (pika.spec.BasicProperties) Additional metadata about
                           the message just received
    :param msg: The message received from the server
    :return: None
    """

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
    parser = argparse.ArgumentParser(description = "Parses network and CPU statistics and publishes to RabbitMQ Server")
    parser.add_argument("-b", "--messagebroker",  help="This is the IP address or named address of the message broker to connect to", required=True)
    parser.add_argument("-p", "--virtualhost", help="This is the virtual host to connect to on the message broker. If not specified, should default to the root virtual host")
    parser.add_argument("-c", help="Use the given credentials when connecting to the message broker. The format is 'login:password'. If not specified, should default to a guest login.", required=True)
    parser.add_argument("-k", "--routingkey", help="The routing key to use when publishing messages to the message broker", required=True)
    args = parser.parse_args()

    vhost = "/"
    etype='pi_utilization'
    key = args.routingkey
    ipaddr = args.messagebroker
    fullcred = ['guest', 'guest']
    if args.c is not None:
        fullcred = args.c.split(':')
        print fullcred
    if args.virtualhost is not None:
    	print "cusotom virtual host"
    	vhost = args.virtualhost

    try:
        # TODO: Connect to the message broker using the given broker address (host)
        # Use the virtual host (vhost) and credential information (credentials),
        # if provided
        """
        # TODO: Setup the channel and exchange
        channel = 'rock' # Setup channel from connected message broker

        # Setup signal handlers to shutdown this app when SIGINT or SIGTERM is
        # sent to this app
        # For more info about signals, see: https://scholar.vt.edu/portal/site/0a8757e9-4944-4e33-9007-40096ecada02/page/e9189bdb-af39-4cb4-af04-6d263949f5e2?toolstate-701b9d26-5d9a-4273-9019-dbb635311309=%2FdiscussionForum%2Fmessage%2FdfViewMessageDirect%3FforumId%3D94930%26topicId%3D3507269%26messageId%3D2009512
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

        # TODO: Create a queue
        # --------------------
        # It is up to you to determine what type of queue to create...
        # For example, if you create an exclusive queue, then the queue will
        # only exist as long as your client is connected
        # or you could create a queue that will continue to receive messages
        # even after your client app disconnects.
        #
        # In the short report, you should document what type of queue you create
        # and the series of events that occur at your client and the message broker
        # when your client connects or disconnects. (Slide 10).

        # TODO: Bind your queue to the message exchange, and register your
        #       new message event handler
        """
        # TODO: Start pika's event loop
        credentials = pika.PlainCredentials(fullcred[0], fullcred[1])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', 
        	                                        credentials=credentials,
        	                                        virtual_host=vhost))
        channel = connection.channel()


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