# standard imports
from time import sleep

# local imports
from hardware.generic.PulseCounter import PulseCounter
from utilities.mqtt_out import publish

# setup sensors and models
# I have a flow sensor connected to pin 17 (BCM) that outputs a 7.5 pulses per litre passed
flow_sensor = PulseCounter(pin_num=17)

# loop
while True:
    sleep(3)
    flow_rate = flow_sensor.get_recent_pulse_density() * 60 / 7.5       # pulses per second to litres per minute
    publish({ "flow_rate" : flow_rate , "machine" : "MyMachineNameHere" , "source" : "MySourceNameHere" })
    