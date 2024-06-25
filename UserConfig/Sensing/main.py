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
    flow_sensor_readings = flow_sensor(rounding=None)
    print(flow_sensor_readings)
    flow_rate = flow_sensor_readings["density"] * 60 / pulses_per_litre       # pulses per second to litres per minute
    print(flow_rate)
    publish( flow_sensor_readings | { "machine" : sensor_name, "flow_rate" : flow_rate })