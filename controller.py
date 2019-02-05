import socket
import sys

version = '0.1'
IP = 'localhost'

try:
  port = int(sys.argv[1])
except:
  print 'Error: Enter a valid port number as first argument.\nFor example, `python controller.py 10000`.'
  sys.exit(-1)
if port < 1 or port > 65535:
  print 'Error: Enter a valid port number (1-65535) as first argument.\nFor example, `python controller.py 10000`.'
  sys.exit(-1)

server_address = (IP, port)

Identity = 'Controller'
Name = 'C1'

#ACTIONS#
Command = 'command'
SyncList = 'sync list'

#NOTATION#
splitter = '/'
splitter2 = '|'

#HEADER#
Action = 'ACT'
Handshake = 'HSK'
Quit = 'QUT'
Reply = 'RPL'

#Reply Stutas#
replyRetry = 'RETRY'
replySuccess = 'SUCCESS'
replyFail = 'FAIL'

#Content Type
Command = 'command'
#Update = 'update'

#####HELPER FUNCTIONS####

def stringifyBufferedMsg(list, splitter):
  #put list of items into a string with splitters
  temp=''
  for i in list:
    temp = temp + i + splitter
  return temp[:-len(splitter)]

def handshakeMessage():
  return stringifyBufferedMsg([version,Identity, Name],splitter)

def isHandshake(message):
  if message[0] == Handshake:
    if message[1] ==replySuccess: #Handshake success
      welcome()
      return True
    else:
      print 'Handshake fail.'
      return False

def welcome():
  print '-'*51
  print '---   Welcome to VC-Drone.                      ---'
  print '-'*51

def printResult(result):
  #print result from server
  print '===== Server replied message ====='
  print result

def actionMessage():
  ##MESSAGE TYPE, ACTION, CONTENT TYPE, CONTENT##
  inp = ''
  action =''
  #while action != Create and action != Alter  and action != Execute and action != 'quit' and action!=SyncList:
  while inp != 'o' and inp != 'q': #and inp != 'u':
    inp = raw_input('Enter \'o\' to command, or \'q\' to quit: ')
    if inp == 'o':
      action = Command
    elif inp == 'q':
      action = Quit
  if action == Quit:
    return QUT
  elif action == Command:
    targetDrone = raw_input('Enter target drone\'s name: ')
    targetCommand = raw_input('Enter desired action: ')
    return stringifyBufferedMsg([Action,action,targetDrone,targetCommand], splitter)

def actionRetry(warning):
  print '--Server message--'
  print warning
  return actionMessage()

while True:
  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  sock.connect(server_address)

  #Sending handshake message
  HasBeenHandshake = False
  sock.sendall(handshakeMessage())
  print 'Handshake sent.'

  try:
    ###LISTENING###
    while True:
      message = sock.recv(10000)

      if message:
        print 'Received message: ' + message
        buff = message.split(splitter)

        ##Whenever received Fail, quit
        if buff[0] == replyFail:
          break

        ###LISTEN FOR HANDSHAKE###
        if HasBeenHandshake == False:
          if isHandshake(buff)==True:
            HasBeenHandshake = True
            sock.sendall(actionMessage())
            continue
          else:
            print 'retry handshake'
            sock.sendall(handshakeMessage())
            continue

        ###LISTEN FOR Action Message Reply###
        ##Action Type, ContentType, Reply Type, Result/Warning
        elif buff[0]== Reply:
          if buff[1]== Command :
            print 'Received:Command Reply: '
            #print message
            if buff[2]== replyRetry:
              sock.sendall(actionRetry(buff[3]))

            elif buff[2]==replySuccess:
              printResult(buff[3])
              sock.sendall(actionMessage())
              continue
            else:
              break

            continue
          elif buff[1]==Command:
            printResult(buff[4])
            sock.sendall(actionMessage())
            continue
      else:
        ##TERMINATION##
        print 'nothing recvd'
        break

  finally:
    print >>sys.stderr, 'Controller '+ Name + ' is closing.'
    sock.sendall(Quit)
    sock.close()
    break
