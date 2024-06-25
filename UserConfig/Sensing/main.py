# standard imports
from time import sleep

# local imports
from hardware.generic.PulseCounter import PulseCounter
from utilities.mqtt_out import publish

# settings
pin_number = 17
pulses_per_litre = 7.5
machine = "pressure_washer"
source = "overhead_tank"

# setup sensors and models
flow_sensor = PulseCounter(pin_number)

# loop
while True:
    sleep(3)
    flow_rate = flow_sensor.get_recent_pulse_density() * 60 / pulses_per_litre       # pulses per second to litres per minute
    publish({ "flow_rate" : flow_rate , "machine" : machine , "source" : source })
    