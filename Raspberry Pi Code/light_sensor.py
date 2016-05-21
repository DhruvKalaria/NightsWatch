#!/usr/local/bin/python

import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import memcache
import json
from datetime import datetime

GPIO.setmode(GPIO.BCM)
LIGHT_SENSOR = 'ON'

#define the pin that goes to the circuit
pin_to_circuit = 18

def on_connect(mosq, obj, rc):
    mqttc.subscribe("LIGHT_STATUS", 0)
    print("rc: " + str(rc))

def on_message(mosq, obj, msg):
    global LIGHT_SENSOR
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    LIGHT_SENSOR = msg.payload

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

def rc_time (pin_to_circuit):
    count = 0
    
	#Output on the pin for 
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(0.1)

    #Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)
  
    #Count until the pin goes high
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1
        if count>800:
        	break
	#Change to percentage
    return count/8

#Catch when script is interrupted, cleanup correctly
try:
    # Main loop
	mqttc = mqtt.Client()
	# Assign event callbacks
	mqttc.on_message = on_message
	mqttc.on_connect = on_connect
	mqttc.on_subscribe = on_subscribe
	# Connect
	mqttc.connect("50.18.94.136", 1883,60)
	# Continue the network loop
	mqttc.loop_start()
	print "Started"
	# Light Json Object
	lJsonData = {}

	while True:
		shared = memcache.Client(['127.0.0.1:11211'],debug=0)
		shared.set('lightStatus', LIGHT_SENSOR)

		if LIGHT_SENSOR == 'ON':
			lightData = rc_time(pin_to_circuit)
			shared.set('Value', lightData)
			lJsonData["type"] = "light"
			lJsonData["val"] = lightData
			lJsonData["time"] = str(datetime.now())
			json_data = json.dumps(lJsonData)			
			mqttc.publish("LightRT", str(json_data))
	
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
