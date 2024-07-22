# Shoestring Timeseries Database Service Module
## Description
This state and data storage service module uses two pieces of open source software; [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) and [InfluxDB](https://www.influxdata.com/products/influxdb-overview/), to store timeseries data. 

Timeseries data is a data set which tracks a sample over time - such as the temperature of a refrigerator or the on/off status of a machine.

## Background - Terminology 
InfluxDB is different from a typical relational database so there is some slightly different terminology:

Term | Definition |Example
---|---|---
bucket | Where the data is stored (like the table name)   | equiment_monitoring
measurement | What is being measured | motor_temperature
tag | Metadata about the measurement (must be a string) | machine_id = 12345, machine_type = lathe
field | The value of the measurement (can contain strings, floats, integers, or booleans) | value = 37.6, unit = C

In a shoestring context - it would be logical to store all the timeseries data for each solution in a single bucket named after that solution. Each variable the solution captures / monitors is then its own measurement. It should also be noted that tags are indexed so they should be used for things that you are likely to filter against.

### Example:
An equipment monitoring solution stores `motor_temperature` measurements in the `equipment_monitoring` bucket with the `temperature value` stored as a field. Each measurement has tags for `machine_id` and `machine_type` so that it is easy to query the temperature trends for machine 12345 today, or average daily temperature for all lathes in the past month.

## How it works
Telegraf listens on a set of MQTT topics, interprets each message to extract the `tags` and `fields`, it then creates a `measurement`, and sends it to InfluxDB to be stored. All of this is defined in the `telegraf.conf` config file.

> If using multiple buckets are being used, you will likely need to have multiple copies of telegraf running with different configurations

## Running the service module
Both Telegraf and InfluxDB have official docker images (including for Raspberry Pi / arm), however from version 2.0 onwards InfluxDB requires a 64-bit operating system. 

>If you are using a Raspberry Pi you will need to use the 64-bit version of Raspberry Pi OS

Below are two snippets that should be put in the `docker-compose.yml` file when using this service module. Both of these snippets use variables (`${VARIABLE_NAME}`) - the values for these variables are set in a `.env` file which should be saved next to the `docker-compose.yml` file. 

*influxdb docker-compose snippet*
```
db:
  image: influxdb:2.6
  command: "./entrypoint.sh --reporting-disabled"
  volumes:
    - ./influxdb2:/var/lib/influxdb2:rw
  ports:
    - "8086:8086"
  environment: 
    - DOCKER_INFLUXDB_INIT_MODE=setup
    - DOCKER_INFLUXDB_INIT_USERNAME=${DB_ADMIN_USER}
    - DOCKER_INFLUXDB_INIT_PASSWORD=${DB_ADMIN_INITIAL_PASSWORD}
    - DOCKER_INFLUXDB_INIT_ORG=${DB_ORG}
    - DOCKER_INFLUXDB_INIT_BUCKET=${DB_BUCKET}
    - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${DB_ADMIN_INITIAL_TOKEN}
```
This InfluxDB snippet mounts a local `influxdb2` folder to `/var/lib/influxdb2` and stores all the database files there. If there is no database there, the values set in the `DOCKER_INFLUXDB_INIT_*` environment variables are used to create a new database. (these are defined in the `.env` file)

*telegraf docker-compose snippet*
```
  telegraf:
    image: telegraf:1.21
    volumes:
      - ./telegraf.conf:/etc/telegraf/telegraf.conf
    environment: 
      - DOCKER_INFLUXDB_ORG=${DB_ORG}
      - DOCKER_INFLUXDB_BUCKET=${DB_BUCKET}
      - DOCKER_CURRENT_INFLUXDB_TOKEN=${DB_ADMIN_INITIAL_TOKEN}
```
This Telegraf snippet mounts the `telegraf.conf` file into the container. The environment variables here are used within that config file.
> If you change any of these values in the InfluxDB user interface - remember to change them here. ***Particularly the current token to use when writing data***

*.env file*
```
DB_ORG=SHOESTRING
DB_ADMIN_USER=admin
DB_ADMIN_INITIAL_PASSWORD=shoestring
DB_BUCKET=data_bucket
DB_ADMIN_INITIAL_TOKEN=l3Z9k31lKzZ-Ixupk_s3FjinRas-HHbvf7tsBTpEUCP7m5YQL0Z0jF1yjQEC_ZNYLEr6xkSZfuXMUP_spHe9cg==
```
>The `.env` file sets the initial values and should be modified **before running the service module for the first time**.

## Configuring Telegraf
Telegraf uses a toml formatted config file. A description of this file format can be found [here](https://toml.io/en/ "here").

The config file has three main sections: the *agent* section, the *inputs* section, and the *outputs* section. (For Telegraf in general there are other sections, but we don't need them for this service module.) 

> A full description of the `telegraf.conf` file can be found [here](https://github.com/influxdata/telegraf/blob/master/etc/telegraf.conf)

### The agent section
The *agent* section defines how data is collected. The snippet below outlines the key elements we care about

```
[agent]
  interval = "3s"
  collection_jitter = "2s"
  flush_interval = "5s"
  flush_jitter = "2s"
  omit_hostname = true
```
Config item | Meaning
---|---
interval | Default data collection interval for all inputs
collection_jitter | Collection jitter is used to shift the collection time by a random amount. Each plugin will sleep for a random time within jitter before collecting. This can be used to avoid many plugins querying things at the same time, which can have a measurable effect on the system.
flush_interval | Default flushing interval for all outputs. Maximum flush_interval will be flush_interval + flush_jitter
flush_jitter |  Jitter the flush interval by a random amount. This is primarily to avoid large write spikes for users running a large number of telegraf instances. ie, a jitter of 5s and interval 10s means flushes will happen every 10-15s
omit_hostname | If set to true, stops telegraf adding a "host" tag to measurements by default.

### The Inputs Section
The *inputs* section selects and configures the input plugins that Telegraf uses - the primary plugin used here is the [mqtt consumer plugin](https://github.com/influxdata/telegraf/blob/master/plugins/inputs/mqtt_consumer/README.md). (A list of other plugins can be found [here](https://docs.influxdata.com/telegraf/v1.25/plugins/).)

Below is the snippet of the config file that sets up this plugin. The first part handles the MQTT connection and the second part handles interpretting the data (aka the `data_format`). Telegraf supports [several data input formats](https://docs.influxdata.com/telegraf/v1.25/data_formats/input/), however for Shoestring the primary one we will be concerned about is `json_v2` (and perhaps `XPath` as an alternate method of parsing json).

```
[[inputs.mqtt_consumer]]
  servers = ["tcp://mqtt.docker.local:8883"]
  topics = ["manual_input/feeds/input"]
  data_format = "json_v2"
  topic_tag = ""
  qos = 1

  [[inputs.mqtt_consumer.json_v2]]
    measurement_name = "fault_tracking"
    #measurement_name_path = "status" 		

    timestamp_path = "timestamp"
    timestamp_format = "2006-01-02T15:04:05.999-07:00" 
    [[inputs.mqtt_consumer.json_v2.field]]
      path = "running"
      type = "boolean"
		
    [[inputs.mqtt_consumer.json_v2.tag]]
      path = "machine_id"
      type = "string"
      rename = "id"
      optional = true

    [[inputs.mqtt_consumer.json_v2.field]]
      path = "status"
      type = "string"
```
MQTT Config item | Meaning
---|---
servers | MQTT broker address (can put multiple if using a cluster, but not if they are separate standalone brokers - for separate brokers use multiple input plugins)
topics | List of topics to subscribe to (Can use wildcards)
data_format | which input data format to use
topic_tag | if set to a value - attach the msg topic to the measurement using this tag name
qos | MQTT QoS level to use

json_v2 Config item | Meaning
---|---
measurement_name | the measurement name to use
measurement_name_path | get the measurement name from the MQTT message instead
timestamp_path | where to find the timestamp value in the message (empty string if not present)
timestamp_format | the format of the timestamp (The format string is weird - just use ISO timestamps and the timestamp format string above)
<field/tag>.path | path at which the field/tag is found
<field/tag>.type | specifies the data type (int,uint,float,string,bool) (must be string for tag)
<field/tag>.rename | name to use for this field/tag (if not set will use the last element of the path)
<field/tag>.optional | if true, will not throw error if unable to parse this field/tag (i.e. if not present at path)

> All paths in the json_v2 input format must be [GJSON](https://github.com/tidwall/gjson/blob/v1.7.5/SYNTAX.md) strings

In line with the toml format - the field and tag entries can also be done like this if that is easier:
```
[[inputs.mqtt_consumer.json_v2]]
    ...

    field = [
      {path = "running",type = "boolean"},
      {path = "status",type = "string"}
    ]

    tag = [ 
      {path = "machine_id",type = "string", rename = "id",optional=true}
    ]
```

### The Outputs Section
The *outputs* section selects and defines the output plugins. There are several output plugins (discussed [here](https://docs.influxdata.com/telegraf/v1.25/plugins/)) but the two that are of interest for Shoestring are the [InfluxDB_v2](https://github.com/influxdata/telegraf/blob/release-1.25/plugins/outputs/influxdb_v2/README.md) output plugin and the [file](https://github.com/influxdata/telegraf/blob/release-1.25/plugins/outputs/file/README.md) output plugin.

The file output plugin is useful for logging to stdout (which gets collected by the docker logging system). The influxDB plugin writes the data into the database

```
[[outputs.influxdb_v2]]	
  urls = ["http://timeseries-db.docker.local:8086"]
  token = "$DOCKER_CURRENT_INFLUXDB_TOKEN"
  organization = "$DOCKER_INFLUXDB_ORG"
  bucket = "$DOCKER_INFLUXDB_BUCKET"

[[outputs.file]]
  files = ["stdout"]
```

Config item | Meaning
---|---
urls | The address of the influxDB database
token | The authentication token needed to write to influx (loaded from the environment variable in this example)
organisation | The organisation to use (from env variable here)
bucket | Which bucket to write to (from env variable here)
files | Which files to write to (stdout here for logging)

## Example: Full Config File
*telegraf.conf*
```
[agent]
  interval = "3s"
  collection_jitter = "2s"
  flush_interval = "5s"
  flush_jitter = "2s"

  omit_hostname = true

[[inputs.mqtt_consumer]]
  servers = ["tcp://mqtt.docker.local:8883"]
  topics = ["manual_input/feeds/input"]
  data_format = "json_v2"
  topic_tag = ""
  qos = 1

  [[inputs.mqtt_consumer.json_v2]]
    measurement_name = "fault_tracking"
    #measurement_name_path = "status" 		
    timestamp_path = "timestamp"
		
    timestamp_format = "2006-01-02T15:04:05.999-07:00" 
    [[inputs.mqtt_consumer.json_v2.field]]
      path = "running" # A string with valid GJSON path syntax
      type = "boolean"
		
    [[inputs.mqtt_consumer.json_v2.tag]]
      path = "machine_id" # A string with valid GJSON path syntax
      type = "string"
    [[inputs.mqtt_consumer.json_v2.field]]
      path = "status"
      type = "string"

[[outputs.influxdb_v2]]	
  urls = ["http://timeseries-db.docker.local:8086"]
 
  ## Token for authentication.
  token = "$DOCKER_CURRENT_INFLUXDB_TOKEN"
  
  ## Organization is the name of the organization you wish to write to; must exist.
  organization = "$DOCKER_INFLUXDB_ORG"
  
  ## Destination bucket to write into.
  bucket = "$DOCKER_INFLUXDB_BUCKET"

[[outputs.file]]
  files = ["stdout"]
```

## Configuring InfluxDB
From a developer perspective - all of the configuration you should need to do is handled by the `.env` file above. 

For the user, InfluxDB can be configured through its web interface accessible at [`localhost:8086`](http://localhost:8086) (or `<ip>:8086`). The initial admin username and password are set in the `.env` file. You will be prompted to change the admin password the first time you log in (so remember it).

From the web interface it is possible to add additional users, organisations, buckets, etc. However the main thing that we recommend you do is to create a new API token for telegraf so that you are using a token that only has write access to the bucket in question rather than using the admin token. (You will need to update the `DOCKER_CURRENT_INFLUXDB_TOKEN` variable in `docker-compose.yml` with the new token.)

In a similar manner you will need to create read access API tokens for any service modules that need to access the database contents.

>It is also recommended that you change the admin API token from the initial one that was defined in the `.env` file

## Accessing data stored in InfluxDB
InfluxDB provides a web API that can be used to extract data. It also provides two mechanisms for querying data: `InfluxQL` (old) which is similar to SQL and `flux` (new) which uses functional language features to offer improved querying. There are also several libraries available in various languanges to simplify accessing this API.

>From version 2.0 onwards, InfluxDB requires an API Token to read or write data. 
