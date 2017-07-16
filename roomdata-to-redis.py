#!/usr/bin/env python

### push internal sensor data to redis 
###
### internal sensor is very slow - I need sensor data
### at different applications, so redis is a good buffer

import redis
import sys
import Adafruit_DHT

sensor = 22
pin = 4

r = redis.Redis(host='localhost', port=6379, db=0)
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

def format(var):
    return "{:.1f}".format(var)

if humidity is not None and temperature is not None:
    try:
        r.set("Temp",format(temperature))
        r.set("Hum",format(humidity))
    except:
        sys.exit("Error talking to redis")
else:
    print('Failed to get reading. Try again!')
    sys.exit(1)
