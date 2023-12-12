#!/usr/bin/python3
import socket
import pika

RMQ_IP = '195.35.17.231'
UDP_IP = "0.0.0.0" 
UDP_PORT = 5005   

connection = pika.BlockingConnection(pika.ConnectionParameters(RMQ_IP))
channel = connection.channel()
channel.queue_declare(queue='iot')
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)

sock.bind((UDP_IP, UDP_PORT))

while True:
    try:
        data, addr = sock.recvfrom(1024)
        channel.basic_publish(exchange='', routing_key='iot', body=data)
        print(f'Sent: {data}')
    except Exception as err:
        print(err)
        connection.close()
        break

