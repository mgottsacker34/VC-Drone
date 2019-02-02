import socket
import sys
import subprocess
import os
from datetime import datetime
import threading

import spacy
import csv

###Server##
#GLOBAL VARs#

Version = '0.1'
IP = 'localhost'

try:
  port = int(sys.argv[1])
except:
  print 'Error: Enter a valid port number as first argument.\nFor example, `python server.py 10000`.'
  sys.exit(-1)
if port < 1 or port > 65535:
  print 'Error: Enter a valid port number (1-65535) as first argument.\nFor example, `python server.py 10000`.'
  sys.exit(-1)

#CITATIONs#
splitter = '/'
splitter2 = '|' #splitter for different commands

#HEADERS#
Action = 'ACT'
Handshake = 'HSK'
Quit = 'QUT'
Reply = 'RPL'

#Reply Stutas#
replyRetry = 'RETRY'
replySuccess = 'SUCCESS'
replyFail = 'FAIL'

Command = 'command'

#Client list and Services list
Drone = 'Drone'
Controller = 'Controller'
ControllerList=[]
DroneList=[]

cmdDict = {}

class hardware(object):

  def __init__(self,identity, name, connection):
    # Each rocket has an (x,y) position.
    self.identity = identity
    self.name = name
    self.connection = connection

  def getName(self):
    # Increment the y-position of the rocket.
    return self.name
  def getConnection(self):
    return self.connection

  def getIdentity(self):
    return self.identity

#####HELPER FUNCTIONS####

def stringifyBufferedMsg(list,splitter):
  #put list of items into a string with splitters
  temp=''
  for i in list:
    temp = temp+i + splitter
  return temp[:-len(splitter)]

def funCmdDict():
  with open('cmdlist.csv', 'rb') as csvfile:
    readerB = csv.reader(csvfile, delimiter='\n')
    for row in readerB:
      temp = row[0].split(':')
      cmdDict[temp[0]] = temp[1]
    #print cmdDict
    print 'Cmd Dictionary Finished'

def isDroneOn(droneName):
  for drone in DroneList:
    if drone.name == droneName:
      return True
  return False

def passCommand(controllerName, droneName, command):
  for drone in DroneList:
    if drone.name == droneName:
      command = 'cmd ' + command
      drone.connection.sendall(stringifyBufferedMsg([Command, controllerName, command],splitter))
      print 'Sent ' + message + ' to drone ' + droneName
      return True
  return False

# Process request for drone action.
def action(action, controllerName, droneName, command):
  if action == Command:
    if isDroneOn(droneName)==True:
      print '-- Sending command: ' + command + ' to ' + droneName
      passCommand(controllerName, droneName, command)
      return stringifyBufferedMsg([Reply,action,replySuccess,'Sent ' + command + ' to drone ' + droneName],splitter)
    else:
      return stringifyBufferedMsg([Reply,action,replyRetry,'Drone ' + droneName + ' is not on'],splitter)
  else:
    return '-- Invalid action request. Doing nothing.'

def controllerThread(connection, name, client_address):
  #HasBeenHandshake = False
  while True:
    print 'Waiting for a command in controllerThread from ' + name
    message = connection.recv(1024)

    if message:
      print 'Received message: ' + message
      buff = message.split(splitter)
      if buff[0] == Quit:
        print 'Controller ' + name + ' Quiting'
        connection.close()
        remove(ControllerList, name)
        break

      elif buff[0] == Action:
        print 'Received action message: ' + message
        result = action(buff[1], name, buff[2], buff[3])
        connection.sendall(result)
        continue

      else:
        connection.sendall(replyFail)
        print 'Sending Fail'
        break

def droneThread(connection, name, client_address):
  #HasBeenHandshake = False
  while True:
    print 'Waiting for an update from ' + name
    message = connection.recv(1024)

    if message:
      print 'Received message: ' + message
      buff = message.split(splitter)
      if buff[0] == Quit:
        print 'Drone ' + name + ' Quiting.'
        connection.close()
        remove(DroneList, connection)
        break
      elif buff[0] == Reply:
        brodcastToController(buff[1],stringifyBufferedMsg([Reply, Command, buff[2], buff[3]],splitter))
      else:
        connection.sendall(replyFail)
        print 'Sending Fail.'
        break

def brodcastToController(name, message):
  for controller in ControllerList:
    if name!='AllController':
      if controller.name == name:
        controller.connection.sendall(message)
        print 'Sent ' + message + ' to ' + name
    else:
      controller.connection.sendall(messge)
      print 'Sent '+ message + ' to all controllers'

# if the link is broken, we remove the client
def remove(_list, name):
  for obj in _list:
    if obj.name == name:
      obj.connection.close()
      _list.remove(obj)

# Open socket
funCmdDict()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (IP, port)
sock.bind(server_address)

sock.listen(10)

# Listen and accept connections
try:
  while True:
    print >>sys.stderr, 'Waiting for a new connection...'
    connection, client_address = sock.accept()
    message = connection.recv(1024)

    if message:
      print 'Received message: ' + message
      buff = message.split(splitter)

      print 'Handshake phase.'
      if buff[0] == Version:

        if buff[1] == Controller:
          msg_to_send = stringifyBufferedMsg([Handshake,replySuccess],splitter)
          print msg_to_send
          ControllerList.append(hardware(Controller,buff[2],connection))
          connection.sendall(msg_to_send)
          print 'Controller connected'
          threading.Thread(target=controllerThread, args=(connection, buff[2], client_address)).start()
          print >>sys.stderr, 'Handshake success.'
          continue

        elif buff[1] == Drone:
          msg_to_send = stringifyBufferedMsg([Handshake,replySuccess],splitter)
          print 'Drone '+ buff[2] + ' connected'
          DroneList.append(hardware(Drone, buff[2], connection))
          connection.sendall(msg_to_send)
          threading.Thread(target=droneThread, args=(connection, buff[2],client_address)).start()
      else:
        #connection.sendall()
        msg_to_send = stringifyBufferedMsg([Handshake,replyFail],splitter)
        connection.sendall(msg_to_send)
        continue

except KeyboardInterrupt:
  print ' Caught Ctrl+C -- Closing server...'
finally:
  for d in DroneList:
    d.connection.close()
  for c in ControllerList:
    c.connection.close()
  sock.close()
  print 'Connections closed.'
