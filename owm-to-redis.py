#!/usr/bin/env python

import json
import pyowm
import redis
import sys
import os.path

# config
config_file = "config.json"
#
token = ""
redishost = ""
location = ""

def config_initialize():
    global token, redishost, location

    if os.path.isfile(config_file) and os.access(config_file, os.R_OK):
        with open(config_file) as data_file:
            data = json.load(data_file)
            try:
                token = data["token"]
            except:
                sys.exit("Error: Couldn't find token in config file")
            try:
                redishost = data["redishost"]
            except:
                sys.exit("Error: Couldn't find redishost in config file")
            try:
                location = data["location"]
            except:
                sys.exit("Error: Couldn't find location in config file")
    else:
        sys.exit("Error: config file missing or unreadable")

def fetchweather():
    global token, location

    owm = pyowm.OWM(token)
    weather = {}
    observation = owm.weather_at_place(location)
    w = observation.get_weather()
    decoded_w = json.loads(w.to_JSON())
    weather['out_temp'] = int(decoded_w['temperature']['temp'])
    return(weather)

def ktoc(var):
    celsius = var - 273.15
    return(celsius);

config_initialize()
print(token)
print(redishost)
print(location)
results = fetchweather()
print ktoc(results['out_temp'])
