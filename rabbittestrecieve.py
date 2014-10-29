import pika
import sys

etype='pi_utilization'
qname = 'hellopy'
key='ece4564'

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=etype, type='direct')
result = channel.queue_declare(exclusive=True)
qname = result.method.queue
channel.queue_bind(exchange=etype,queue=qname,routing_key=key)
print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
    print " [x] %r:%r" % (method.routing_key, body,)

channel.basic_consume(callback, queue = qname, no_ack=True)
channel.start_consuming()