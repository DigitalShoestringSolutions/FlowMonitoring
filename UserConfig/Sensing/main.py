# standard imports
from time import sleep

# local imports
from hardware.generic.PulseCounter import PulseCounter
from utilities.mqtt_out import publish

# setup sensors and models.
# I have a flow sensor connected to pin 17 (BCM) that outputs a 7.5 pulses per litre passed.
flow_sensor = PulseCounter(pin_num=17)
pulses_per_litre = 7.5

# loop
while True:
    sleep(3)

    pulses, density = flow_sensor.recent_pulses_and_density()
    flow = pulses / pulses_per_litre             # pulses to litres
    flow_rate = density*3600/pulses_per_litre    # pulses per second to litres per hour

    publish({ "flow": flow, "flow_rate" : flow_rate , "machine" : "MyMachineNameHere" , "source" : "MySourceNameHere" })
