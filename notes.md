# Some thoughts

This file is a place for any thoughts or notes along the development process. They should always be dated, but no other organization is promised.

#### 09.27.2018

##### [DroneKit](http://python.dronekit.io/develop)

Current setup: DroneKit runs on a Raspberry Pi onboard the drone itself. The RPis communicates with the Pixhawk flight controller using the MAVLink protocol over a serial connection (Pixhawk's TELEM2 port <--> RPi's Ground, TX and RX pins), which is [this configuration](http://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html).

  - process to communicate from ground to RPi: SSH, type in commands.

"DroneKit-Python is primarily intended for use on Linux-based Companion Computers that travel on a vehicle and communicate with the autopilot via a serial port. **It can also be used on ground-based computers running Linux, Windows or Mac OSX (communicating using WiFi or a telemetry radio).**"
  - I want to use the bolded setup instead of the current state.

"During development you’ll generally run it on a development computer, communicating with a simulated vehicle running on the same machine (via a UDP connection)."

##### Simulation

Run simulator with `dronekit-sitl copter`.

DroneKit-SITL waits for TCP connections on `127.0.0.1:5760`. DroneKit-Python scripts running on the same computer can connect to the simulation using the connection string as shown:
`vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)`.

"After something connects to port 5760, SITL will then wait for additional connections on port 5763 (and subsequently 5766, 5769 etc.)."

"DroneKit-SITL exposes a [Python API](https://github.com/dronekit/dronekit-sitl#api), which you can use to start and control simulation from within your scripts. This is particularly useful for test code and [examples](http://python.dronekit.io/examples/index.html#example-toc)."

#### 09.30.2018

##### [Best practices](http://python.dronekit.io/develop/best_practice.html)

- commands are not guaranteed to arrive, can come from different sources.
  - Need to check that vehicle is in a state to obey a command (poll on is_armable).
  - Cannot assume command has succeeded until changed behavior is observed. Monitor state changes before sending commands.

- note about ground station connections: If a connection succeeds from a ground station, but not from DroneKit-Python it may be that your baud rate is incorrect for your hardware. This rate can also be set in the connect() method.

- "movement commands are asynchronous, and will be interrupted if another command arrives before the vehicle reaches its target. Calling code should block and wait (or check that the operation is complete before proceeding to the next command)."

- for connecting to the drone: it seems like we can connect directly to the Pixhawk; just need to get the IP address and the port that it listens on. Alternatively, if we want to run it as an application on the onboard RPi, we can have a program that listens for connections from the ground station. It would have a connection open with the drone over `localhost`, since it is connected to the drone over USB.

- state information exposed through Vehicle attributes:
  - .version
  - .location.capabilities
  - .location.global_frame
  - .location.global_relative_frame
  - .location.local_frame
  - .attitude
  - .velocity
  - .gps_0
  - .gimbal
  - .battery
  - .rangeFinder
  - .ekf_ok
  - .last_heartbeat
  - .home_location
  - .system_status
  - .heading
  - .is_armable
  - .airspeed
  - .groundspeed
  - .armed
  - .mode

- only attributes that can be set: .home_location, .gimbal, .airspeed, .groundspeed, .mode, .armed

  - they can be set directly by assigning a value. For example, `vehicle.armed = False` disarms the vehicle; `vehicle.groundspeed = 3.2` sets the default groundspeed to be used in movement commands.

- Can observe the attributes (listen for events instead of polling).
  - Callbacks are added using Vehicle.add_attribute_listener() or the Vehicle.on_attribute() decorator method.

  - cannot observe .home_location.






























.
