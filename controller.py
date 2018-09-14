#################################################
###    Text to drone Client    ###
### Jiao ###
### St Louis University, Computer Science Dep.###
###                ###
#################################################

import socket
import sys

##Client##
#GLOBAL VARs#

version = '0.1'
IP = 'localhost'
port = 10001

server_address = (IP, port)
#Controller = 'Ryu'

Identity = 'Controller'
Name = "Holly's Macbook"

#ACTIONS#
Order = 'order'
SyncList = 'sync list'




#NOTATION#
spliter = '/'
spliterO = '|'



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
Order = 'order'
#Update = 'update'

#DroneName = 'DroneName'
'''
FeatureContent = 'featureContent'

Blacklist = 'blacklist'
Whitelist = 'whitelist'
'''

#####HELPER FUNCTIONS####

def sp(list,spliter):
    #put list of items into a string with spliters  
    temp=''
    for i in list:
        temp = temp+i + spliter
    return temp[:-len(spliter)]

def handshakeMessage():
    return sp([version,Identity, Name],spliter)

def isHandshake(message):
    if message[0] == Handshake:
        if message[1] ==replySuccess: #Handshake success
            welcome()
            return True
        else:
            print 'Handshake Fail'
            return False

def welcome():
    print '#'*53
    print '###     Welcom to Text2Drone!                   ###'
    print '###      -- Order the drone from plain English! ###'
    print '#'*53

def printResult(result): 
    #print result from server
    print '=====Server replied message====='
    print result

def actionMessage():
    ##MESSAGE TYPE, ACTION, CONTENT TYPE, CONTENT##
    inp = ''
    actipn =''
    print '-'*60
    #while action != Create and action != Alter  and action != Execute and action != 'quit' and action!=SyncList:
    while inp != 'o' and inp != 'q': #and inp != 'u':
        #action = raw_input("What is the action that you want to do?\n( execute / create feature / alter feature / sync list / quit ):\n")
        inp = raw_input("What do you want to do?\n( o (order) / q (quit) ):\n")
        if inp == 'o':
            action = Order
        elif inp == 'q':
            action = Quit
    #print action
    if action == Quit:
        return QUT
    elif action == Order:# or action ==  Update:
        return sp([Action,action,raw_input('For the drone: '), raw_input('Order: ')], spliter)
    '''
    elif action == SyncList:
        List = ''
        op = ''
        while (List != Blacklist or List!= Whitelist) and ( op!= 'add' and op!='remove'):
            listOpTemp = raw_input("Enter in this format: {blacklist/whitelist} {add/remove} {ip address}: \n")
            listOp =listOpTemp.split()
            if len(listOp)!=3:
                continue
            #print listOp
            List = listOp[0]
            op = listOp[1]
            ip = listOp[2]
        if op == 'add':
            content = 'A' + '|' + ip
        else:
            content = 'R' + '|' + ip
        return sp([Action,action,List,content],spliter) 
    '''

def actionRetry(warning):
    print '--Server message--'
    print warning
    return actionMessage()
'''
def featureInput(name): #return a string for feture file input

    feature = raw_input("Feature: ")
    scenario = raw_input("Scenario: ")
    given = raw_input("Given: ")
    when = raw_input("When: ")
    then = raw_input("Then: ")

    return sp([name,feature,scenario,given,when,then],spliterF)


def featureMessage(action,name):
    return sp([Action,action,FeatureContent,featureInput(name)],spliter)

'''

while True:
    ###START###
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(server_address)
    #sp('a','b')

    #Sending handshake message
    HasBeenHandshake = False
    sock.sendall(handshakeMessage())
    print "hs sent"

    try:
        ###LISTENING###
        while True:
            #print "lalala"
            message = sock.recv(10000)
            print message

            if message:
                buff = message.split(spliter)

                ##Whenever received Fail, quit
                if buff[0]== replyFail:
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
                    if buff[1]== Order :
                        print 'Received:Order Reply: '
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
                    elif buff[1]==Order:
                        printResult(buff[4])
                        sock.sendall(actionMessage())
                        continue
                    '''
                    elif buff[1] == SyncList:
                        printResult(buff[4])
                        sock.sendall(actionMessage())
                        continue
                    elif (buff[1]== Create or Alter):
                        if buff[2] ==ServiceName:
                            if buff[3]== replyRetry:
                                sock.sendall(actionRetry(buff[4]+buff[5]))
                            elif buff[3] == replySuccess:
                                printResult(buff[5])
                                sock.sendall(featureMessage(buff[1],buff[4]))
                            else:
                                break
                            continue
                        elif buff[2] == FeatureContent:
                            if buff[3]== replyRetry:
                                printResult(buff[5])
                                sock.sendall(featureMessage(buff[1],buff[4]))
                                continue
                            elif buff[3] == replySuccess:
                                printResult(buff[5])
                                sock.sendall(actionMessage())
                                continue
                    '''

            else:
                ##TERMINATION##
                print 'nothing recvd'
                break

    finally:
        print >>sys.stderr, 'Controller '+ Name + ' is Closing, Bye!'
        sock.sendall(Quit)
        sock.close()
        break