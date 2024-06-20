import RPi.GPIO as GPIO
import time
import logging

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


# payload = {"machine": self.constants['machine'], "source": self.constants['source'], "flow": str(average_reading), "sensor_type": pitch, "max_pressure": max_pressure, "min_flow": str(min_flow), "max_flow": str(max_flow), "timestamp": timestamp}
