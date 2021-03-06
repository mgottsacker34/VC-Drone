import subprocess
import socket
import os
import sys
import threading
import time

# Dronekit software simulation.
import dronekit_sitl
sitl = dronekit_sitl.start_default()
# connection_string for connecting to RPi over serial is '/dev/ttyAMA0' (also set baud=57600)
connection_string = sitl.connection_string()

# Import DroneKit-Python
from dronekit import connect, VehicleMode

try:
  port = int(sys.argv[1])
except:
  print 'Error: Enter a valid port number as first argument.\nFor example, `python drone-sim.py 10000`.'
  sys.exit(-1)
if port < 1 or port > 65535:
  print 'Error: Enter a valid port number (1-65535) as first argument.\nFor example, `python drone-sim.py 10000`.'
  sys.exit(-1)

# Connect to the Vehicle.
print('Connecting to vehicle on: %s' % (connection_string,))
vehicle = connect(connection_string, wait_ready=True)

version = '0.1'
IP = 'localhost'


server_address = (IP, port)

Drone = 'Drone'
Identity = Drone
Name = 'D1'

# Notation
splitter = '/'
splitter2 = '|'

# Header field
Handshake = 'HSK'
Quit = 'QUT'
Reply = 'RPL'

Command = 'command'

# Reply status
replyRetry = 'RETRY'
replySuccess = 'SUCCESS'
replyFail = 'FAIL'

#put list of items into a string with splitters
def stringifyBufferedMsg(list,splitter):
  temp=''
  for i in list:
    temp = temp+i + splitter
  return temp[:-len(splitter)]

def handshakeMessage():
  return stringifyBufferedMsg([version,Identity,Name],splitter)

def isHandshake(message):
  if message[0] == Handshake:
    if message[1] == replySuccess: #Handshake success
      print 'Handshake success.'
      return True
    else:
      print 'Handshake fail.'
      return False

def sendback(message, connection):
  connection.sendall(message)
  print 'Sent back: ' + message

# Arm the drone.
def drone_arm():
  print 'Basic pre-arm checks'
  # Don't try to arm until autopilot is ready
  while not vehicle.is_armable:
    print ' Waiting for vehicle to initialize...'
    time.sleep(1)

  print 'Vehicle is armable. Arming motors now.'
  # Copter should arm in GUIDED mode
  vehicle.mode    = VehicleMode('GUIDED')
  vehicle.armed   = True

  while not vehicle.armed:
    print ' Waiting for arming to conclude...'
    time.sleep(1)

  print ' Drone armed.'

# Disarm the drone.
def drone_disarm():
  # check if the drone is armed
  if not vehicle.armed:
    print 'Vehicle is already disarmed.'
  else:
    print 'Disarming Vehicle.'
    vehicle.armed = False

def drone_takeoff(aTargetAltitude = 15):
  # Arm drone if not armed.
  if not vehicle.armed:
    drone_arm()

  print 'Taking off...'
  vehicle.simple_takeoff(aTargetAltitude)

  # Wait until vehicle reaches a safe height before processing the goto.
  # Otherwise, the command after Vehicle.simple_takeoff will execute immediately.
  while True:
    print ' Altitude: ', vehicle.location.global_relative_frame.alt
    if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
      print 'Reached target altitude'
      break
    time.sleep(1)

  print 'Drone has taken off.'

def drone_land():
  print 'Returning to land...'
  vehicle.mode = VehicleMode("RTL")
  print 'Setting LAND mode...'
  vehicle.mode = VehicleMode("LAND")
  print 'Vehicle landed.'

def drone_poweroff():
  print >>sys.stderr, 'Powering off drone...'
  # Close vehicle object before exiting script
  vehicle.close()
  # Shut down Dronekit simulator
  if sitl is not None:
    sitl.stop()
  sock.send(Quit)
  # Close socket.
  sock.close()
  print 'Closed connection to server.'

def drone_goto(dNorth, dEast, gotoFunction=vehicle.simple_goto):
    """
    Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.

    The method takes a function pointer argument with a single `dronekit.lib.LocationGlobal` parameter for
    the target position. This allows it to be called with different position-setting commands.
    By default it uses the standard method: dronekit.lib.Vehicle.simple_goto().

    The method reports the distance to target every two seconds.
    """

    currentLocation = vehicle.location.global_relative_frame
    targetLocation = get_location_metres(currentLocation, dNorth, dEast)
    targetDistance = get_distance_metres(currentLocation, targetLocation)
    gotoFunction(targetLocation)

    #print "DEBUG: targetLocation: %s" % targetLocation
    #print "DEBUG: targetLocation: %s" % targetDistance

    while vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
        #print "DEBUG: mode: %s" % vehicle.mode.name
        remainingDistance=get_distance_metres(vehicle.location.global_relative_frame, targetLocation)
        print "Distance to target: ", remainingDistance
        if remainingDistance<=targetDistance*0.01: #Just below target, in case of undershoot.
            print "Reached target"
            break;
        time.sleep(2)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
HasBeenHandshake = False
sock.sendall(handshakeMessage())
print 'Handshake sent.'

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
          continue
        else:
          print 'Handshake not completed. Sending handshake again.'
          sock.sendall(handshakeMessage())
          continue
      else:
        if buff[0] == Command:
          cmdList = buff[2].split(splitter2)
          print 'Commands received: ', cmdList
          for cmd in cmdList:
            if len(cmd) > 0:
              print 'cmd: ' + cmd
              if cmd == 'cmd arm':
                drone_arm()
              elif cmd == 'cmd disarm':
                drone_disarm()
              elif cmd == 'cmd take off':
                drone_takeoff()
              elif cmd == 'cmd land':
                drone_land()
              elif cmd == 'cmd poweroff':
                drone_poweroff()
          sock.sendall(stringifyBufferedMsg([Reply, buff[1], replySuccess, 'Commands processed'],splitter))

except KeyboardInterrupt:
  print '\nCaught Ctrl+C -- killing subprocesses...'
except Exception as ex:
  print ex
finally:
  print >>sys.stderr, 'Closing drone process...'
  # Close vehicle object before exiting script
  vehicle.close()
  # Shut down Dronekit simulator
  if sitl is not None:
    sitl.stop()
  sock.send(Quit)
  sock.close()
  print 'Closed.'
