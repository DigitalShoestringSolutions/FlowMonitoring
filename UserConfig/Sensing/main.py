# standard imports
from time import sleep

# local imports
from hardware.generic.PulseCounter import PulseCounter
from utilities.mqtt_out import publish


# setup sensors and models.
# I have a flow sensor connected to pin 26 (BCM) that outputs 7.5 pulses per litre passed.
flow_sensor_1 = PulseCounter(pin_num=26, multiplier=1/7.5)
# I have another flow sensor connected to pin 19 (BCM) that outputs 20 pulses per litre passed.
flow_sensor_2 = PulseCounter(pin_num=19, multiplier=1/20)


# loop
while True:
    sleep(3)    # Publish readings every 3 seconds

    volume, rate = flow_sensor_1.recent_pulses_and_density()    # litres, litres per second
    publish({ "flow": volume, "flow_rate" : rate , "machine" : "MyMachineName1" , "source" : "MySourceName1" })
    
    volume, rate = flow_sensor_2.recent_pulses_and_density()    # litres, litres per second
    publish({ "flow": volume, "flow_rate" : rate , "machine" : "MyMachineName2" , "source" : "MySourceName2" })
