import subprocess
import socket
import os
import sys
import threading

version = '0.1'
IP = 'localhost'

try:
    port = int(sys.argv[1])
except:
    print "Error: Enter a valid port number as first argument.\nFor example, `python drone-sim.py 10000`."
if port < 1 or port > 65535:
    print "Error: Enter a valid port number (1-65535) as first argument.\nFor example, `python drone-sim.py 10000`."

server_address = (IP, port)

Drone = 'Drone'
Identity = Drone
Name = 'D1'

#NOTATION#
splitter = '/'
splitterO = '|'

#HEADER#
'''
Update = 'UPD'
Alert = 'ALT'
'''
Handshake = 'HSK'
Quit = 'QUT'
Reply = 'RPL'

Order = 'order'

#Request = 'RQT'

#Reply Stutas#
replyRetry = 'RETRY'
replySuccess = 'SUCCESS'
replyFail = 'FAIL'

def sp(list,splitter):
    #put list of items into a string with splitters
    temp=''
    for i in list:
        temp = temp+i + splitter
    return temp[:-len(splitter)]

def handshakeMessage():
    return sp([version,Identity,Name],splitter)

def isHandshake(message):
    if message[0] == Handshake:
        if message[1] ==replySuccess: #Handshake success
            print 'Handshake success.'
            return True
        else:
            print 'Handshake fail.'
            return False

def sendback(message, connection):
    connection.sendall(message)
    print "Sent "+ message + " back"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
HasBeenHandshake = False
sock.sendall(handshakeMessage())
print "handshake sent"

try:
    while True:

        message = sock.recv(1024)

        if message:
            print 'received message: ' + message
            buff = message.split(splitter)

            if buff[0] == replyFail:
                break
            if HasBeenHandshake == False:
                if isHandshake(buff) == True:
                    HasBeenHandshake = True
                    #threading.Thread(target=try_subprocess, args=(_cmd_lst, _alert, sock)).start()
                    continue
                else:
                    print 'retry hds'
                    sock.sendall(handshakeMessage())
                    continue
            else:
                if buff[0] == Order:
                    print buff[2]
                    sock.sendall(sp([Reply, buff[1], replySuccess, "Order processed successfuly"],splitter))


except KeyboardInterrupt:
    print(" Caught Ctrl+C -- killing subprocess...")
except Exception as ex:
    print ex
finally:
    print >>sys.stderr, 'Closing controller.'
    sock.send(Quit)
    sock.close()
