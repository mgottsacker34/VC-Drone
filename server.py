#################################################
###    text2drone  Server   ###
### Jiayi Wang, ###
### St Louis University, Computer Science Dep.###
### ###
#################################################

import socket
import sys
import subprocess
import os
from datetime import datetime
import threading

import spacy
import csv
#import time
#import Queue
#import collections
#from threading import *
#from SocketServer import ThreadingMixIn
#import select

###Server##
#GLOBAL VARs#


#https://www.geeksforgeeks.org/simple-chat-room-using-python/

version = '0.1'
IP = 'localhost'
port = 10001

#Controller = 'Ryu'

#CITATIONs#
spliter = '/'
spliterO = '|' #spliter for different orders


#HEADERS#
Action = 'ACT'
Handshake = 'HSK'
Quit = 'QUT'
Reply = 'RPL'

#Request = 'RQT'
#Update = 'UPD'
#Alert = 'ALT'


#Actions#
#Create = 'create feature'
#Alter = 'alter feature'
#Execute = 'execute'
#SyncList = 'sync list'
#Update = 'UPD'
#Alert = 'ALT'

#Reply Stutas#
replyRetry = 'RETRY'
replySuccess = 'SUCCESS'
replyFail = 'FAIL'

Order = 'order'
#DroneName = 'droneName'

#Content Type#
#ServiceName = 'serviceName'
#FeatureContent = 'featureContent'
#Blacklist = 'blacklist'
#Whitelist = 'whitelist'

#Client list and Services list
Drone = 'Drone'
Controller = 'Controller'
ControllerList=[]
DroneList=[]


cmdDict = {}
'''
class Controller(object):
    # Rocket simulates a rocket ship for a game,
    #  or a physics simulation.
    
    def __init__(self,name, connection):
        # Each rocket has an (x,y) position.
        self.name = name
        self.connection = connection
        
    def getName(self):
        # Increment the y-position of the rocket.
        return self.name
    def getConnection(self):
        return self.connection


class Drone(object):
    # Rocket simulates a rocket ship for a game,
    #  or a physics simulation.
    
    def __init__(self,name, connection):
        # Each rocket has an (x,y) position.
        self.name = name
        self.connection = connection
        
    def getName(self):
        # Increment the y-position of the rocket.
        return self.name
    def getConnection(self):
        return self.connection

'''
class hardware(object):
    # Rocket simulates a rocket ship for a game,
    #  or a physics simulation.
    
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

#Root Path#
#WD = os.popen("echo $BeA_ROOT").read().strip('\n') #root directory
#WDB = WD + '/behave' #root directory/beheave



#####HELPER FUNCTIONS####

def sp(list,spliter):
    #put list of items into a string with spliters
    temp=''
    for i in list:
        temp = temp+i + spliter
    return temp[:-len(spliter)]

def funCmdDict():
    with open('cmdlist.csv', 'rb') as csvfile:
        readerB = csv.reader(csvfile, delimiter='\n')

        for row in readerB:
            #print row
            temp = row[0].split(':')
            cmdDict[temp[0]] = temp[1]
        
        #print cmdDict
        print "Cmd Dictionary Finished"
        '''
        temp = row[0].strip(',').split('|')
        if temp[0] == 'A' and (temp[1] not in BlackList):
            BlackList.append(temp[1])

        elif temp[0] == 'R' and temp[1] in BlackList:
            BlackList.remove(temp[1])

        else:
            PassOrde
        '''

####FUNCTIONS####
'''
def ServiceExistCheck(Servicename):
    #Check if the folder with the servicename exist under beheave folder, return True if exist
    print 'namecheck function'
    print WDB
    folder = WDB+'/'+ Servicename
    return os.path.isdir(folder)


def Execution(service):
    ##Execute a feature and add to execution.log under log folders
    print 'Excution function'
    process = subprocess.Popen(['/bin/bash'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    command = 'cd '+ WDB +'/'+service+' && behave\n'
    process.stdin.write(command)
    result=''
    file=open(WD+'/log/execution.log','a')
    file.write(str(datetime.now())+'\n')
    for i in range(6):
        temp = process.stdout.readline()
        result=result+temp
        print result
        file.write(temp)
    file.write('-'*80 + '\n')
    file.close()
    process.terminate()
    return result

def writeFeature(content):
    #write into feature file in format
    print 'Write Feature Function'
    try:    
        items = content.split(spliterF)
        name = items[0] + '.feature'
        path = WDB+'/'+items[0]+'/'+name
        file = open(path, 'w')  
        file.write('Feature: '+items[1]+'\n')
        file.write('    Scenario: '+items[2]+'\n')
        file.write('        Given '+items[3]+'\n')
        file.write('        When '+items[4]+'\n')
        file.write('        Then '+items[5]+'\n')
        file.close()
        return True
    except:
        return False
''' 
'''
def mkdir(name):
    #create new directory folder under behave/
    print 'mkdir Function'
    subdirectory = 'behave/'+name
    try:
        os.mkdir(subdirectory)
        return True
    except Exception:
        pass
    return False


def listOp(listName, content):
    #add item to list
    try:
        file = open(WD+'/lists/'+listName+'.csv', 'a')
        file.write(content + ',\n')
        file.close()
        return True
    except:
        return False

def action(action, contentType, content):
    print "Action Function"
    if action==Execute and contentType == ServiceName:
        if ServiceExistCheck(content)==True:

            result = Execution(content)
            
            return sp([Reply ,action ,ServiceName,replySuccess,result],spliter)
        else:
            return sp([Reply,action,ServiceName ,replyRetry,'No Such Servcie'],spliter)
    elif action == Create and contentType == ServiceName:
        if ServiceExistCheck(content)==False:
            return sp([Reply, action ,ServiceName,replySuccess,content,'Waiting for Feature Input:'],spliter)
        else:
            return sp([Reply,action ,ServiceName ,replyRetry ,content," can't be create. Feature file already exist."],spliter)
        
    elif action == Alter and contentType == ServiceName:
        if ServiceExistCheck(content)==True:
            return sp([Reply,action,ServiceName,replySuccess,content ,'Waiting for Feature Input.'],spliter)
        else:
            return sp([Reply,action,ServiceName,replyRetry,content,"can't alter. Feature file is not exist."],spliter)
        
    elif action == Create and contentType == FeatureContent:
        items = content.split(spliterF)
        name = items[0]
        if mkdir(name)== False:
            return sp([Reply,action,FeatureContent,replyRetry,name,"Error creating new folder"], spliter)
        if ServiceExistCheck(name) == True and writeFeature(content)== True:
            return sp([Reply,action,FeatureContent,replySuccess,name,"Featuer File Created"],spliter)
        else:
            return sp([Reply,action,FeatureContent,replyRetry,name,"Error"],spliter)
    elif action == Alter and contentType == FeatureContent:
        if writeFeature(content)== True:
            items = content.split(spliterF)
            name = items[0]
            return sp([Reply,action , FeatureContent,replySuccess, name , "Feature File Changed"],spliter)
        else:
            return sp([Reply,action,FeatureContent,replyRetry ,name ,"Error"],spliter)
    elif action == SyncList:
        if listOp(contentType, content)==True:
            return sp([Reply,action,contentType,replySuccess,contentType+" Updated"],spliter)
        else:
            return sp([Reply ,action,contentType ,replyRetry,contentType+" Update Error"],spliter)
    return "Fail"


'''

def DroneIsOnCheck(droneName):
    for drone in DroneList:
        if drone.name == droneName:
            return True
    return False

def PassOrder(controllerName, droneName, order):
    for drone in DroneList:
        if drone.name == droneName:
            drone.connection.sendall(sp([Order, controllerName, order],spliter))
            print "Sent "+message + " to drone "+droneName
            return True
#        except:
#            clients.close()
    return False

            # if the link is broken, we remove the client
#            remove(ControllerList, clients)

def ordernlp(line):

    l = []

    nlp = spacy.load('en')
    #doc = nlp(u'arm, hover, heading to North West, and then disarm')
    doc = nlp(unicode(line,"utf-8"))
    print "line is "+line
    i=0
    for token in doc:
        #if token.lemma_ == "arm" or token.lemma_=="launch" or token.pos_ == "VERB":
        if token.pos_ =="NOUN" or token.pos_=="VERB":


            l.append(cmdDict[token.lemma_])
        i=i+1
    print l
    return l



def action(action, controllerName,droneName, order):
    print "Action Function"
    if action==Order: # and contentType == DroneName:
        #if ServiceExistCheck(content)==True:
        if DroneIsOnCheck(droneName)==True:
            s = ""
            for i in ordernlp(order):
                s = s + '|' + i
            print " s is "+s
            PassOrder(controllerName, droneName,s)
            return sp([Reply ,action,replySuccess,"Sent "+ order + " to drone "+droneName],spliter)
        else:
            return sp([Reply,action,replyRetry,'Drone ' + droneName + ' is not on'],spliter)
    else:
        return 'Fail'
    '''
    elif action == Create and contentType == ServiceName
        if ServiceExistCheck(content)==False:
            return sp([Reply, action ,ServiceName,replySuccess,content,'Waiting for Feature Input:'],spliter)
        else:
            return sp([Reply,action ,ServiceName ,replyRetry ,content," can't be create. Feature file already exist."],spliter)
        
    elif action == Alter and contentType == ServiceName:
        if ServiceExistCheck(content)==True:
            return sp([Reply,action,ServiceName,replySuccess,content ,'Waiting for Feature Input.'],spliter)
        else:
            return sp([Reply,action,ServiceName,replyRetry,content,"can't alter. Feature file is not exist."],spliter)
        
    elif action == Create and contentType == FeatureContent:
        items = content.split(spliterF)
        name = items[0]
        if mkdir(name)== False:
            return sp([Reply,action,FeatureContent,replyRetry,name,"Error creating new folder"], spliter)
        if ServiceExistCheck(name) == True and writeFeature(content)== True:
            return sp([Reply,action,FeatureContent,replySuccess,name,"Featuer File Created"],spliter)
        else:
            return sp([Reply,action,FeatureContent,replyRetry,name,"Error"],spliter)
    elif action == Alter and contentType == FeatureContent:
        if writeFeature(content)== True:
            items = content.split(spliterF)
            name = items[0]
            return sp([Reply,action , FeatureContent,replySuccess, name , "Feature File Changed"],spliter)
        else:
            return sp([Reply,action,FeatureContent,replyRetry ,name ,"Error"],spliter)
    elif action == SyncList:
        if listOp(contentType, content)==True:
            return sp([Reply,action,contentType,replySuccess,contentType+" Updated"],spliter)
        else:
            return sp([Reply ,action,contentType ,replyRetry,contentType+" Update Error"],spliter)
    return "Fail"

'''

def controllerThread(connection, name, client_address):
    #HasBeenHandshake = False
    while True:
        print 'waiting for a command in controllerThread from ' + name
        message = connection.recv(1024)
        print 'recving ' + message
        if message:
            buff = message.split(spliter)
            if buff[0] == Quit:
                print "Controller "+ name + " Quiting"
                connection.close()
                remove(ControllerList, name)
                break

            elif buff[0] == Action:
                print "receiving action message correctly: "+ message
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
        print 'waiting for an update'
        message = connection.recv(1024)
        print 'recving ' + message
        if message:
            buff = message.split(spliter)
            if buff[0] == Quit:
                print "Drone "+ name+ " Quiting"
                connection.close()
                remove(DroneList, connection)
                break
                '''
                elif buff[0] == Update or buff[0] == Alter:
                    print "receiving UPD or ALT action message correctly: "+ message
                    #result = action(buff[1], buff[2], buff[3])
                    #brodcastToClients(result, connection)

                    #connection.sendall(result)
                    continue              
                ''' 
            elif buff[0] == Reply:
                brodcastToController(buff[1],sp([Reply, Order, buff[2], buff[3]],spliter))


            else:
                connection.sendall(replyFail)
                #connection.sendall(replyFail)
                print 'Sending Fail'
                break


def brodcastToController(name, message):
    for controller in ControllerList:
        if name!="AllController":
            if controller.name == name:
                controller.connection.sendall(message)
                print "Sent "+message + " to "+name
        else:
            controller.connection.sendall(messge)
            print "Sent "+message + " to all controllers"

            # if the link is broken, we remove the client
#            remove(ControllerList, clients)
 

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
        print >>sys.stderr, 'waiting for a new connection'
        connection, client_address = sock.accept()
        message = connection.recv(1024)
        print 'recving ' + message
        if message:
            buff = message.split(spliter)

            print "HandShak phasse"
            if buff[0] == version:
                if buff[1] == Controller:
                    msg_to_send = sp([Handshake,replySuccess],spliter)
                    print msg_to_send
                    ControllerList.append(hardware(Controller,buff[2],connection))
                    connection.sendall(msg_to_send)
                    print "Controller connected"
                    threading.Thread(target=controllerThread, args=(connection, buff[2], client_address)).start()
                #connection.sendall()

                    print >>sys.stderr, 'Handshake Success'
                    continue
                elif buff[1]==Drone:
                    msg_to_send = sp([Handshake,replySuccess],spliter)
                    print 'Drone '+ buff[2] +' connected'
                    DroneList.append(hardware(Drone, buff[2], connection))
                    connection.sendall(msg_to_send)
                    threading.Thread(target=droneThread, args=(connection, buff[2],client_address)).start()
            else:
                #connection.sendall()
                msg_to_send = sp([Handshake,replyFail],spliter)
                connection.sendall(msg_to_send)
                continue
except KeyboardInterrupt:   print " Caught Ctrl+C -- closing server..."
finally:
    for d in DroneList:
        d.connection.close()
    for c in ControllerList:
        c.connection.close()
    sock.close()
    print 'goodbye'