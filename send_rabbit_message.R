#-------------------------------
# 
# send_rabbit_message.R
# 
#   AUTHOR:  Hannappel Gregor     
#   CREATED: 2018-05-08
#   DESCRIPTION: function send a message string to the rabbitmq server
#-------------------------------


#' send_rabbit_message
#'
#' @description function that sends 'message' to the rabbit server
#'
#' @param message : Character string to be send to the rabbitmq server. workers will pick up the message and execue it in a cmd shell 
#   please be carefull with ampersands (&) and similar special charackters they need escaping with (^)
#   i.e. "&" --> "^&"
#'
send_rabbit_message = function(message = "echo 'moin'", mode = "dev")
{
    #part of the command the runs the new_task.py script
    cmd_rabbit = paste0("..\\..\\Python\\python.exe -E ../lib/python/rabbit/new_task.py ")

    cmd =  paste0(cmd_rabbit, mode, " ", message)

    system2("cmd", input = cmd)
}




