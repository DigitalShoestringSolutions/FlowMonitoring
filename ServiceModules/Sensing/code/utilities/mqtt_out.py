"""mqtt_out.py

Working assumptions:
	- The broker and port will not change during a session, but the topic could.
	- The user would like a one-line interaction with the MQTT system

Public API: only the function 'publish'

"""
# standard imports
import json

# installed imports
import paho.mqtt.client as pahomqttclient

# local imports
from utilities.timestamp import get_timestamp

# default settings
default_broker = "mqtt.docker.local"
default_topic = "shoestring-sensor"
default_port = 1883
#default_qos = 0                # qos not in use


# startup
client = pahomqttclient.Client()
client._is_connected = False    # create custom attribute

def _connect(broker, port):
    print("MQTT client connecting to broker", broker, "port", port)
    client.connect(broker, port)
    client._is_connected = True # should test connection attempt was sucessful


def publish(msg, topic=default_topic, broker=default_broker, port=default_port):
    """Add timestamp to msg (if not provided), connect (if not already) and publish. 
    Arg reordering is deliberate to allow kwargs.
    """

    # Get the timestamp first, as soon as possible after sampling
    timestamp = get_timestamp()

    # Ensure the mqtt client is ready to publish
    if not client._is_connected:
        _connect(broker, port)

    # format the message
    if type(msg) is dict:                               # preferred
        # The below ordering allows the user to specify their own timestamp in the message dict if desired.
        # If an entry with key "timestamp" is not provided, one will be added using time of publication.
        # json.dumps(mydict) returns a string which is very similar to the output of str(mydict), 
        #   but crucially with json.dumps() strings have double quotes as required by the json spec, 
        #   while str(mydict) gives single quotes and is not recognised as json.
        payload = json.dumps({'timestamp': timestamp} | msg)
        
    else:                                               # failover
        payload = "timestamp: " + timestamp + " " + str(msg)

    # publish to mqtt
    client.publish(topic, payload)
