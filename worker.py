"""
    Script to start rabbitmq consumers that
        1. execute commands send to it
        2. log their own life
        3. log the execution of any command send to it

    Usage:
        python.exe -E worker.py queue_name
"""
import sys
import os
import subprocess as sp
import threading
from socket import gethostname
from socket import gethostbyname
from getpass import getuser
import json

if __name__ == '__main__':
    if __package__ is None:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # from logging_sql.logging_sql import Log
        # from logging_sql.logging_sql_periodic import PeriodicLog
        from connect import gen_connection, gen_channel

##############################################################
# Done with loading libraries
##############################################################

def print_waiting_message():
    """ prints mesage whenever for whenever the worker is waiting for a message """

    print(' [*] Waiting for messages. To exit press CTRL+C then Enter')

def log_detail_gen(command, detail, queue_name):
    """ generate a JSON string for the config column in the log table """

    log_detail = json.JSONEncoder().encode({
        "command"     : command.replace("'",""),
        "queue"       : queue_name,
        "worker_host" : gethostname(),
        "worker_user" : getuser(),
        "worker_ip"   : gethostbyname(gethostname()),
        "detail"      : detail.replace("'","")
    })
    
    return log_detail


def scrape_cmd_output(sub_process):
    """
        takes the subproccess screen output and return it as a single string
    """
    cmd_output = b""
    # Poll sub_process for new output until finished
    while True:
        nextline = sub_process.stdout.readline()

        if nextline == b'' and sub_process.poll() is not None:
            return cmd_output.decode()

        cmd_output += nextline

        sys.stdout.write(nextline.decode())
        sys.stdout.flush()


def execute_cmd(ch, method, body, queue_name):
    """
        main function that governs what happens to the rabbitmq message (body)

        Keyword arguments:
        ch      -- channel
        method  --
        body    -- byte string, body of the rabbit message
        queue_name   -- string name of the queue this worker is listenting to
    """

    # split the message (body) string into words to parse
    # the first two as username and machine of the message sender and
    # the rest as the actual message
    rabbit_message = body.decode().split()

    command  = " ".join(rabbit_message[2:])

    try:
        # rabbit_work_log = Log(
        #     app_name      = "rabbitmq", 
        #     app_version   = "01.01.08052018", 
        #     log_tb        = "log_devOps_rabbitmq", 
        #     log_detail    = log_detail_gen(command, " ", queue_name),
        #     login_machine = rabbit_message[1],
        #     login_user    = rabbit_message[0]
        # )

        # actually execute the rabbit message in a shell
        sub_process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)

        cmd_output = scrape_cmd_output(sub_process)

        log_detail = log_detail_gen(command, cmd_output, queue_name)

        output    = sub_process.communicate()[0]
        exit_code = sub_process.returncode

        if exit_code == 0:
            # update the SQL log with success code
            # rabbit_work_log.update(100, log_detail)
            print(" [x] Process done.")

            print_waiting_message()
            # send acknowledgement of message to rabbit server
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return output

        else:
            raise sp.CalledProcessError(command, exit_code, output)

    except sp.CalledProcessError as error:
        # update the SQL log with failure code
        # rabbit_work_log.update(400, log_detail)
        print(" [x] Process done, but failed:")
        print(error.output)

        print_waiting_message()
        # send acknowledgement of message to rabbit server
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return output

# function that executes upon receipt of a new message
def outer_callback(queue_name):
    """ function that gets called when a new message is received """
    
    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        thread = threading.Thread(target=execute_cmd, args=(ch, method, body, queue_name))
        thread.start()
    return callback

##############################################
#
# rabbitmq main
#
##############################################

if __name__ == '__main__':
    with gen_connection() as connection:

        queue = sys.argv[1]

        channel = gen_channel(connection, queue)

        channel.basic_consume(
            outer_callback(queue),
            queue=queue
        )

        # logging the life of a rabbit worker
        # log_worker_life = PeriodicLog(
        #     app_name    = "rabbitmq",
        #     app_version = "0.1.22022018",
        #     log_tb      = "log_devOps_rabbitmq_life",
        #     log_detail  = queue,
        #     period      = 600
        # )

        print_waiting_message()

        # start consuming messages!
        channel.start_consuming()
