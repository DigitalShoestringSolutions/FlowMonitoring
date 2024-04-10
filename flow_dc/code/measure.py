# ----------------------------------------------------------------------
#
#    Power Monitoring (Basic solution) -- This digital solution measures,
#    reports and records both AC power and current consumed by an electrical 
#    equipment, so that its energy consumption can be understood and 
#    taken action upon. This version comes with one current transformer 
#    clamp of 20A that is buckled up to the electric line the equipment 
#    is connected to. The solution provides a Grafana dashboard that 
#    displays current and power consumption, and an InfluxDB database 
#    to store timestamp, current and power. 
#
#    Copyright (C) 2022  Shoestring and University of Cambridge
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see https://www.gnu.org/licenses/.
#
# ----------------------------------------------------------------------
 

# run at poll rate
# make requests
# extract variables
# output variables

import datetime
import logging
import multiprocessing
import time

import importlib
import zmq
import flow_sensor as sen

logger = logging.getLogger("main.measure")
context = zmq.Context()


class FlowMeasureBuildingBlock(multiprocessing.Process):
    def __init__(self, config, zmq_conf):
        super().__init__()

        self.config = config
        self.constants = config['constants']

        # declarations
        self.zmq_conf = zmq_conf
        self.zmq_out = None

        self.collection_interval = config['sampling']['sample_interval']
        self.sample_count = config['sampling']['sample_count']
        self.last_dispatch_time = time.time()

    def do_connect(self):
        self.zmq_out = context.socket(self.zmq_conf['type'])
        if self.zmq_conf["bind"]:
            self.zmq_out.bind(self.zmq_conf["address"])
        else:
            self.zmq_out.connect(self.zmq_conf["address"])

    def run(self):
        logger.info("started")
        self.do_connect()

        # Initial setup
        __dt = -1 * (time.timezone if (time.localtime().tm_isdst == 0) else time.altzone)
        tz = datetime.timezone(datetime.timedelta(seconds=__dt))
        today = datetime.datetime.now().date()
        next_check = (datetime.datetime(today.year, today.month, today.day) + datetime.timedelta(days=1)).timestamp()

        run = True
        period = self.collection_interval
        machine_name = self.config["constants"]["machine"]
        location = self.config["constants"]["source"]
        pin = self.config["connection"]["pin"]

        # Sensor characteristics
        pitch = self.config["sensor_character"]["pitch"]
        max_pressure = self.config["sensor_character"]["max_pressure"]
        min_flow = self.config["sensor_character"]["min_flow"]
        max_flow = self.config["sensor_character"]["max_flow"]


        while run:
            sensor = sen.WaterFlowSensor()
            readings = []  
            for _ in range(1):
                try:
                    reading = sensor.read()
                    readings.append(reading['flow_rate']) 
                    time.sleep(1)  
                except Exception as e:
                    logger.error(f"Sampling led to exception: {e}")

            # Calculate the average reading if we have successfully collected any readings
            if readings:
                average_reading = sum(readings) / len(readings)
                print(f"Average Reading: {average_reading}")
            else:
                logger.error("No readings were collected.")

            timestamp = datetime.datetime.now(tz=tz).isoformat()
            payload = {"machine": self.constants['machine'], "source": self.constants['source'], "flow": str(average_reading), "sensor_type": pitch, "max_pressure": max_pressure, "min_flow": str(min_flow), "max_flow": str(max_flow), "timestamp": timestamp}
            output = {"path": "", "payload": payload}
            self.dispatch(output)
        logger.info("done")



    def dispatch(self, output):
        logger.info(f"Attempting to dispatch message: {output}")
        try:
            self.zmq_out.send_json({'path': output.get('path', ""), 'payload': output['payload']})
            self.last_dispatch_time = time.time()  # Update only on successful dispatch
            logger.info("Message dispatched successfully")
        except Exception as e:
            logger.error(f"Failed to dispatch message: {e}")


    def last_active(self):
        return self.last_dispatch_time

