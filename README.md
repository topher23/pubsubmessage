The files submitted are:
- pistatsd.py
- pistatsview.py
- README.md

usage: pistatsview.py [-h] -b MESSAGEBROKER [-p VIRTUALHOST] -c C -k
                      ROUTINGKEY

View maximum and minimum CPU and network utilization of monitored devices via RabbitMQ server

optional arguments:
  -h, --help            show this help message and exit
  -b MESSAGEBROKER, --messagebroker MESSAGEBROKER
                        This is the IP address or named address of the message
                        broker to connect to
  -p VIRTUALHOST, --virtualhost VIRTUALHOST
                        This is the virtual host to connect to on the message
                        broker. If not specified, should default to the root
                        virtual host
  -c C                  Use the given credentials when connecting to the
                        message broker. The format is 'login:password'. If not
                        specified, should default to a guest login.
  -k ROUTINGKEY, --routingkey ROUTINGKEY
                        The routing key to use when publishing messages to the
                        message broker


usage: pistatsd.py [-h] -b MESSAGEBROKER [-p VIRTUALHOST] -c C -k ROUTINGKEY

Parses network and CPU statistics and publishes to RabbitMQ Server

optional arguments:
  -h, --help            show this help message and exit
  -b MESSAGEBROKER, --messagebroker MESSAGEBROKER
                        This is the IP address or named address of the message
                        broker to connect to
  -p VIRTUALHOST, --virtualhost VIRTUALHOST
                        This is the virtual host to connect to on the message
                        broker. If not specified, should default to the root
                        virtual host
  -c C                  Use the given credentials when connecting to the
                        message broker. The format is 'login:password'. If not
                        specified, should default to a guest login.
  -k ROUTINGKEY, --routingkey ROUTINGKEY
                        The routing key to use when publishing messages to the
                        message broker

In order to set up this monitoring service, pistatsd.py must be run on a remote
computer you are trying to monitor. Information from that computer will be sent
to a remote RabbitMQ server. pistatsview.py must be run on a separate computer
and connect to the RabbitMQ server with a login/password combination and will
receive information via statistics pulled from a queue on the RabbitMQ server.
The information received will be parsed by pistatsview.py and keep pulling stats
from the RabbitMQ server. pistatsview.py must be run first 

This program is dependent on the pika library in order to connect to the RabbitMQ
server. In order to install pika you must install erlang.
