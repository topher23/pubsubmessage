import pika
import sys

key='ece4564'
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', virtual_host=vhost))
channel = connection.channel()
etype='pi_utilization'
channel.exchange_declare(exchange=etype,type='direct')

# Loop until the application is asked to quit
while(1):
    jsonsend = "helloworld"
    channel.basic_publish(exchange=etype,routing_key=key,body=jsonsend)
    time.sleep(1)
connection.close