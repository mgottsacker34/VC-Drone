# VC-Drone

This system will provide a voice control interface to drones for end users.
This project utilizes natural language processing and understanding to map
intents from human conversation to drone commands. Ultimately, this project
will make the complex task of drone piloting more accessible to humans.

The target drone architectures includes a Pixhawk 4 flight controller running
ROS and using MAVROS to communicate via MAVLink, and a Pixhawk 4 running
DroneKit to communicate via MAVLink.

## Dependencies

- Python 2.7
- spacy
- DroneKit

To install Python dependencies:
`pip install spacy dronekit dronekit-sitl`

To install English spacy models:
`python -m spacy download en`

You may need to install with `sudo` or `--user`.

## Running

You will need to start each Python program with the same port. The port number
will be the first argument given with the Python program name.

For example:

`python server.py 10000`

`python drone-sim.py 10000`

`python controller.py 10000`

After each program starts successfully and connects properly, you can issue
commands from the `controller` program. Type `o` to enter a command, or `q` to
quit the `controller`.

Enter the drone's name. In the simulated case, this is hard-coded as `D1`.

Enter a command. Observe the simulated drone flying data from the `drone-sim`
program.

An example sequence of commands is `arm`, `take off`, `land`, `disarm`, `quit`.
