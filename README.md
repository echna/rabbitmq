# Rabbit MQ

## Description:

Scripts to run cmd line tasks asychronously using rabbitmq,

## Usage:


### [worker.py](worker.py)

To start a worker which receives messages from queue_name queue run

```shell
python -E worker.py queue_name
```

### [new_task.py](new_task.py)

To send a task to the rabbit mq server to be executed by the [worker.py](worker.py) script run

```shell
python -E new_task.py queue_name command
```

where command may be any cmd string, for instance 'echo hello world'.

### [send_rabbit_message.R](send_rabbit_message.R)

This script simply provides an R based function to facilitate [new_task.py](new_task.py) in R.

```R
send_rabbit_message(message=command, mode=queue_name)
```

## TO DO

1. Load rabbit MQ server settings from a config.json file
    - hostname
    - port
    - Credentials (user name and password)
2. Fix logging functionality and load its sql server, database and table configurations from a json as well.
3. Make keyboard interruption more pretty