# Mosquitto configuration for Shoestring
## Description
This is the typical way that mosquitto is configured for Shoestring solutions.

## Configuration
### Listeners
Mosquitto is configured with two listeners: a standard one on port `1883` and a websocket listener on port `9001`. The websocket listener is specifically for javascript clients when direct MQTT over websocket connections are used by the front-end.

### Logging
Mosquitto is set up to log a wide variety of information to `stdout`. In the `docker-compose.yml` snippet, Docker is configured to relay everything on `stdout` to `syslog`. If desired, rsyslog or similar can be configured to write these logs to file.

### Alias
The `docker-compose.yml` snippet also shows how to configure Docker to give the mqtt broker an alias so that it can be accessed as `mqtt.docker.local` by other containers.
