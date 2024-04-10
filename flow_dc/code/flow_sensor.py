import RPi.GPIO as GPIO
import time
import logging
import tomli

# Setup logger
logger = logging.getLogger('main.measure.sensor')

class WaterFlowSensor:
    def __init__(self):
        self.flow_pin = 17
        self.flow_rate = 0
        self.count = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.flow_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Ensure no conflicting edge detection setup exists
        GPIO.remove_event_detect(self.flow_pin)
        GPIO.add_event_detect(self.flow_pin, GPIO.FALLING, callback=self.count_pulse)

    def count_pulse(self, channel):
        self.count += 1

    # def calculate_flow_rate(self):
    #     flow_rate = (self.count / 4) / 60  # Assuming 7.5 pulses per liter
    #     self.count = 0  # Reset pulse counter
    #     return flow_rate

    def calculate_flow_rate(self):
        flow_rate = (self.count * 2.25 * 60) / 1000  # Assuming 7.5 pulses per liter...gives values in L/min
        self.count = 0  # Reset pulse counter
        return flow_rate

    def read(self):
        time.sleep(1)  # Adjust as needed
        self.flow_rate = round(self.calculate_flow_rate(), 4)
        self.cleanup()
        logger.info(f"Flow rate: {self.flow_rate} L/min")
        return {'flow_rate': self.flow_rate}

    def cleanup(self):
        GPIO.remove_event_detect(self.flow_pin)  # Remove event detection
        GPIO.cleanup(self.flow_pin)  # Clean up the specific pin

# # def get_config():
# #     with open("./config/config.toml", "rb") as f:
# #         toml_conf = tomli.load(f)
# #     logger.info(f"config: {toml_conf}")
# #     return toml_conf

# if __name__ == "__main__":
#     # Basic configuration for logging
#     logging.basicConfig(level=logging.INFO)
    
#     # config = get_config()
#     # pin = config["connection"]["pin"]
#     # pin = 17
#     sensor = WaterFlowSensor()
#     try:
#         # while True:
#         readings = sensor.read()
#         logger.info(f"raw sensor vals: {readings}")
#     # except KeyboardInterrupt:
#     #     print("Interrupted by user")
#     finally:
#         sensor.cleanup()
