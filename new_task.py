"""
    Script to send a message to the rabbitmq server

    Usage:
        python.exe -E new_task.py queue_name message
"""

import sys
import os
from socket import gethostname
from getpass import getuser
import pika

if __name__ == '__main__':
    if __package__ is None:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from connect import gen_connection, gen_channel

    with gen_connection() as connection:

        queue = sys.argv[1]

        # prepend actual message with the user and machine name who send the message
        # these are used by the workers to log the usage of rabbitmq
        message = getuser() + ' ' + gethostname() + ' ' + ' '.join(sys.argv[2:]) 

        channel = gen_channel(connection, queue)

        # send the message to the server via an implicit direct exchange directly to the queue
        channel.basic_publish(
            exchange    = '',
            routing_key = queue,
            body		= message,
            properties	= pika.BasicProperties(
                delivery_mode = 2, # make message persistent
            )
        )

    #confirmation message of message sent
    print(" [x] Sent %r to %r" % (message, queue))

