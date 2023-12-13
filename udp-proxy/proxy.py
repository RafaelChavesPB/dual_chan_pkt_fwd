#!/usr/bin/python3
import socket
import pika
import json

with open("proxy_conf.json") as file:
    conf = json.loads(file.read())
print(f'Configs: {conf}')

RMQ_HOST = conf['rmq_host']
RMQ_QUEUE = conf['rmq_queue']
UDP_HOST = conf['udp_host']
UDP_PORT = conf['udp_port']

connection = pika.BlockingConnection(pika.ConnectionParameters(RMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=RMQ_QUEUE)
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)

sock.bind((UDP_HOST, UDP_PORT))

while True:
    try:
        data, addr = sock.recvfrom(1024)
        data = json.loads(data.decode())
        data['data'] = json.loads(data['data'])
        payload = {}
        payload['device'] = data['data']['device']
        payload['value'] = data['data']['value']
        payload['time'] = data['tmst']
        payload['rssi'] = data['rssi']
        body = json.dumps(payload)
        channel.basic_publish(exchange='', routing_key='iot', body=body)
        print(f'SENT: {data}')
    except KeyError as err:
        print(err)
        print(f'KEY NOT FOUND: {data}')
    except json.decoder.JSONDecodeError:
        print(f'INVALID JSON: {data}')
    except UnicodeDecodeError:
        print(f'CORRUPTED PACKET: {data}')
    except Exception as err:
        print(err)
        print(f'ERROR: {data}')
        connection.close()
        break

