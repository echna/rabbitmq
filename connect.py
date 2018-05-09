import pika

def gen_connection():

    params = pika.ConnectionParameters(
        host='192.168.99.100',
        port='32769',
        # credentials=pika.PlainCredentials('guest', 'guest'), 
        heartbeat_interval=20
    )

    return(pika.BlockingConnection(params))


def gen_channel(connection, queue_name):
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_qos(prefetch_count=1)

    return(channel)