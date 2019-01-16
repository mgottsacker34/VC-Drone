import time

class StateMachine:
  def __init__(self):
    self.states = {
      'STANDBY': ['WAIT_FOR_ACK', 'OFF'],
      'WAIT_FOR_ACK': ['STANDBY', 'WAIT_FOR_ARM'],
      'WAIT_FOR_ARM': ['STANDBY', 'ARMED_NOT_IN_FLIGHT'],
      'ARMED_NOT_IN_FLIGHT': ['WAIT_FOR_CMD'],
      'WAIT_FOR_CMD': ['ARMED_NOT_IN_FLIGHT']
    }

    self.startState = 'STANDBY'
    self.endState = 'OFF'
    self.current_state = 'STANDBY'
    self.previous_state = ''
    self.altitude = 0

  def get_current_state(self):
    return self.current_state

  def get_previous_state(self):
    return self.previous_state

  # Returns states accessible from current state.
  def get_next_states(self):
    return self.states[self.current_state]

  def transition(self, next_state):
    self.previous_state = self.current_state
    self.current_state = next_state
    print '  FSM transitioned.'

  def send_ACK_to_client(self):
    if 'WAIT_FOR_ACK' in self.get_next_states():
      self.transition('WAIT_FOR_ACK')
    else:
      print '  ERROR: not in state to send ACK. Doing nothing.'

  def receive_ACK_from_drone(self):
    if 'WAIT_FOR_ARM' in self.get_next_states():
      self.transition('WAIT_FOR_ARM')
    else:
      print '  ERROR: not in state to receive ACK from drone. Doing nothing.'

  def receive_ARM_from_drone(self):
    if 'ARMED_NOT_IN_FLIGHT' in self.get_next_states():
      self.transition('ARMED_NOT_IN_FLIGHT')
    else:
      print '  ERROR: not in state to receive ARM from drone. Doing nothing.'

  def receive_TAKEOFF_from_drone(self, altitude):
    if 'WAIT_FOR_CMD' in self.get_next_states():
      i = 0
      for i in range(altitude):
        print '.'
        time.sleep(1)

      self.transition('WAIT_FOR_CMD')
    else:
      print '  ERROR: not in state to receive TAKEOFF from drone. Doing nothing.'

  def received_LAND_from_drone(self):
    if self.get_current_state() == 'WAIT_FOR_CMD':
      self.transition('ARMED_NOT_IN_FLIGHT')
      self.transition('WAIT_FOR_ARM')
      self.transition('STANDBY')
    else:
      print '  ERROR: not in state to receive LAND from drone. Doing nothing.'

  def timeout(self):
    self.transition(self.get_previous_state())

if __name__== "__main__":
  fsm = StateMachine()
  accepted = False

  while not accepted:

    print 'Available events:'
    print '1) Send ACK to client.'
    print '2) Receive ACK from drone.'
    print '3) Receive arm() from drone.'
    print '4) Receive takeoff(altitude) from drone.'
    print '5) Enter control command.'
    print '6) Timeout.'

    input = raw_input('Enter the number of an event: ')
    # print '  Received: ' + input
    # print '  Current state: ' + fsm.get_current_state()
    if fsm.get_current_state() == 'OFF':
      print '-- Accept state reached. Exiting.'
      break

    if input == 'quit':
      print '-- Quitting.'
      break
    elif input == '1':
      print '  EVENT: Sending ACK to client.'
      fsm.send_ACK_to_client()
    elif input == '2':
      print '  EVENT: Received ACK from drone.'
      fsm.receive_ACK_from_drone()
    elif input == '3':
      print '  EVENT: Received arm() from drone.'
      fsm.receive_ARM_from_drone()
    elif input == '4':
      altitude = raw_input('Enter a target altitude: ')
      print '  EVENT: Received takeoff(' + altitude + ') from drone.'
      fsm.receive_TAKEOFF_from_drone(int(altitude))
    elif input == '5':
      print 'Available commands:'
      print 'a) Land.'
      # print 'b) Fly to a new location.'
      command = raw_input('  Enter the letter of a command: ')

      if command == 'a':
        print '  EVENT: Received LAND command'
        fsm.received_LAND_from_drone()
      else:
        print '  ERROR: Invalid command. Doing nothing.'

    elif input == '6':
      print '  EVENT: Timeout.'
      fsm.timeout()

    print '\nCurrent state: ' + fsm.get_current_state() + '\n'
