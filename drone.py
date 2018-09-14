import subprocess
import socket
import os
import sys
import threading


version = '0.1'
IP = 'localhost'
port = 10001

server_address = (IP, port)

Drone = 'Drone'
Identity = Drone
Name = '111'



#NOTATION#
spliter = '/'
spliterO = '|'

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

#SNORT_RUNNING = True


#_cmd_lst = ['python', '-u', 'timed_printer.py']  # sudo snort -q -A console -i eth0 -c /etc/snort/snort.conf
#_cmd_lst = ['screen','-S','test','-dm','sudo','snort','-q','-A','console','-i','ens33','-c','/etc/snort/snort.conf']  # sudo snort -q -A console -i eth0 -c /etc/snort/snort.conf

#_cmd_lst = ['sudo','snort','-q','-A','console','-i','ens33','-c','/etc/snort/snort.conf']
#_alert = 'yay'                                  # The keyword you're looking for
                                                 #  in snort output
    


def sp(list,spliter):
    #put list of items into a string with spliters  
    temp=''
    for i in list:
        temp = temp+i + spliter
    return temp[:-len(spliter)]



def handshakeMessage():
    return sp([version,Identity,Name],spliter)


def isHandshake(message):
    if message[0] == Handshake:
        if message[1] ==replySuccess: #Handshake success
            print 'yay'
            return True
        else:
            print 'Handshake Fail'
            return False



def sendback(message, connection):
    connection.sendall(message)
    print "Sent "+ message + " back"

'''
def try_subprocess(cmd_lst, alert,connection):
    print 'start subprocess'
    p = subprocess.Popen(' '.join(cmd_lst), shell=True, stdout=subprocess.PIPE, bufsize=1)

    while SNORT_RUNNING:
        #print "here"
        #connection.sendall(Update + ','+'aaa')
        #print p.stdout.readline()
        for line in iter(p.stdout.readline, ''):
            print line
            #connection.sendall('bb')
            #connection.sendall(Update + ','+"%s" % line.strip())


            if alert in line:
                sendback("try_subprocess() found alert: %s" % alert,connection)
'''


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
HasBeenHandshake = False
sock.sendall(handshakeMessage())
print "hs sent"

#threading.Thread(target=try_subprocess, args=(_cmd_lst, _alert, sock)).start()

try:
    while True:
        
        #print "lalala"
        message = sock.recv(1024)
        print 'recving message ' + message
        if message:
            buff = message.split(spliter)

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
                    sock.sendall(sp([Reply, buff[1], replySuccess, "Order processed successfuly"],spliter))


except KeyboardInterrupt:   print(" Caught Ctrl+C -- killing subprocess...")
except Exception as ex:     print ex
finally:
#try_subprocess(_cmd_lst, _alert)
#os.system(''.join(_cmd_lst))

    print >>sys.stderr, 'service Closing, Bye!'
    #SNORT_RUNNING = False
    sock.send(Quit)
    sock.close()