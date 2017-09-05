#!/usr/bin/env python
"""
An example server for RaspberryPi GPIO control/monitor.

One output and one input are defined using ``PIN_OUT`` and ``PIN_INP``.
The output can either output constant low/high ('OUT'), or output a pulse of 100ms width ('TRIG').

"""

from pcaspy import Driver, SimpleServer
import RPi.GPIO as GPIO
import time

prefix = 'MTEST:'
pvdb = {
    'OUT' : {
        'type':  'enum',
        'enums': ['LOW', 'HIGH'],
    },
    'TRIG' : {
        'type':  'enum',
        'enums': ['NONE', 'TRIG'],
    },
    'PWM' : {
        'type':  'enum',
        'enums': ['STOP', 'START'],
    },
    'DC' : {
        'type':  'int',
    },
    'FREQ' : {
        'value': 1
    },
    'INP' : {
        'type':  'enum',
        'enums': ['LOW', 'HIGH'],
    },
    'TRIGED': {
        'type':  'enum',
        'enums': ['NONE', 'RISE', 'FALL'],
    }
}

PIN_OUT = 12 #: pin for output
PIN_PWM = 16 #: pin for PWM
PIN_INP = 3 #: pin for input

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PIN_INP, GPIO.IN)
        GPIO.setup(PIN_OUT, GPIO.OUT)
        GPIO.setup(PIN_PWM, GPIO.OUT)
        GPIO.add_event_detect(PIN_INP, GPIO.BOTH, callback=self.input_callback)
        self.pwm = GPIO.PWM(PIN_PWM, 1) # 1 Hz

    def input_callback(self, channel):
        level = GPIO.input(channel)
        self.setParam('INP', level)
        if level == 0:
            self.setParam('TRIGED', 2)
        elif level == 1:
            self.setParam('TRIGED', 1)
        self.updatePVs()

    def write(self, reason, value):
        status = True

        if reason == 'OUT':
            GPIO.output(PIN_OUT, value)
        elif reason == 'TRIG':
            GPIO.output(PIN_OUT, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(PIN_OUT, GPIO.LOW)
            value = 0
        elif reason == 'PWM':
            if value == 0:
                self.pwm.stop()
            else:
                self.pwm.start(self.getParam('DC'))
        elif reason == 'DC':
            self.pwm.ChangeDutyCycle(value)
        elif reason == 'FREQ':
            self.pwm.ChangeFrequency(value)
        else:
            status = False

        if status:
            self.setParam(reason, value)
        return status


if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)

