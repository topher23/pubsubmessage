import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
	'localhost'))
channel = connection.channel()	

channel.queue_declare(queue='hello')

channel.basic_publish(exchange='',
					routing_key='hello',
					body='helloworld!')
print " [x] helloworld has been sent"
connection.close()