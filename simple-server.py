### VC-Drone Server
### Jiayi Wang, Matt Gottsacker, Flavio Esposito

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

version = '0.1'
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
splitter2 = '|' #splitter for different orders


#HEADERS#
Action = 'ACT'
Handshake = 'HSK'
Quit = 'QUT'
Reply = 'RPL'

#Reply Stutas#
replyRetry = 'RETRY'
replySuccess = 'SUCCESS'
replyFail = 'FAIL'

Order = 'order'

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
      #print row
      temp = row[0].split(':')
      cmdDict[temp[0]] = temp[1]

    #print cmdDict
    print 'Cmd Dictionary Finished'

####FUNCTIONS####

def DroneIsOnCheck(droneName):
  for drone in DroneList:
    if drone.name == droneName:
      return True
  return False

def PassOrder(controllerName, droneName, order):
  for drone in DroneList:
    if drone.name == droneName:
      drone.connection.sendall(stringifyBufferedMsg([Order, controllerName, order],splitter))
      print 'Sent ' + message + ' to drone ' + droneName
      return True
#    except:
#      clients.close()
  return False

      # if the link is broken, we remove the client
#      remove(ControllerList, clients)

def ordernlp(line):

  l = []
  nlp = spacy.load('en')
  #doc = nlp(u'arm, hover, heading to North West, and then disarm')
  doc = nlp(unicode(line,'utf-8'))
  print 'line: ' + line
  i = 0
  for token in doc:
    #if token.lemma_ == 'arm' or token.lemma_=='launch' or token.pos_ == 'VERB':
    print token.pos_
    if token.pos_ =='NOUN' or token.pos_=='VERB':
      l.append(cmdDict[token.lemma_])
    i = i+1
  print 'Array from NLP: ', l
  return l

# Process request for drone action.
def action(action, controllerName, droneName, order):
  print 'Action Function'
  if action == Order: # and contentType == DroneName:
    #if ServiceExistCheck(content)==True:
    if DroneIsOnCheck(droneName)==True:
      s = ''
      for i in ordernlp(order):
        s = s + i + '|'
      print ' s is ' + s
      PassOrder(controllerName, droneName, s)
      return stringifyBufferedMsg([Reply,action,replySuccess,'Sent ' + order + ' to drone ' + droneName],splitter)
    else:
      return stringifyBufferedMsg([Reply,action,replyRetry,'Drone ' + droneName + ' is not on'],splitter)
  else:
    return 'Fail'

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
        #connection.sendall(result)
        continue

      else:
        connection.sendall(replyFail)
        #connection.sendall(replyFail)
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
        brodcastToController(buff[1],stringifyBufferedMsg([Reply, Order, buff[2], buff[3]],splitter))
      else:
        connection.sendall(replyFail)
        #connection.sendall(replyFail)
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


###OPEN CONNECTION###

funCmdDict()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (IP, port)
sock.bind(server_address)

sock.listen(10)


try:
  while True:
    ###LISTENING##
    print >>sys.stderr, 'Waiting for a new connection...'
    connection, client_address = sock.accept()
    message = connection.recv(1024)

    if message:
      print 'Received message: ' + message
      buff = message.split(splitter)

      print 'Handshake phase.'
      if buff[0] == version:

        if buff[1] == Controller:
          msg_to_send = stringifyBufferedMsg([Handshake,replySuccess],splitter)
          print msg_to_send
          ControllerList.append(hardware(Controller,buff[2],connection))
          connection.sendall(msg_to_send)
          print 'Controller connected'
          threading.Thread(target=controllerThread, args=(connection, buff[2], client_address)).start()
        #connection.sendall()

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
