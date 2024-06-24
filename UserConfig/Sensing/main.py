# standard imports
from time import sleep

# local imports
from hardware.generic.PulseCounter import PulseCounter
from utilities.mqtt_out import publish

# settings
pin_number = 17
pulses_per_litre = 7.5
sensor_name = "Pipe1"

# setup sensors and models
flow_sensor = PulseCounter(pin_number)

# loop
while True:
    sleep(1)
    flow_rate = flow_sensor.get_recent_pulse_density() / pulses_per_litre       # litres per second
    publish({ "machine" : sensor_name, "flow_rate" : round(flow_rate*60, 3) })  # litres per minute