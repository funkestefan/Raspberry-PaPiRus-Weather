#!/usr/bin/env python

import json
import pyowm
import redis
import sys
import os.path

# config
config_file = "/home/pi/git/code/wetter-display/config.json"
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
    config_initialize()
    global token, location

    owm = pyowm.OWM(token)
    weather = {}
    observation = owm.weather_at_place(location)
    w = observation.get_weather()
    decoded_w = json.loads(w.to_JSON())

    ## sometimes there is no wind and dicts disappear
    safe_wind_direction = decoded_w.get('wind', {}).get('deg')
    safe_wind_speed = decoded_w.get('wind', {}).get('speed')
    if(safe_wind_direction == None):
        safe_wind_direction = 360
    if(safe_wind_speed == None):
        safe_wind_speed = 0

    weather['out_temp'] = int(decoded_w['temperature']['temp'])
    weather["out_hum"] = int(decoded_w['humidity'])
    weather['wind'] = int(safe_wind_direction)
    weather['speed'] = safe_wind_speed
    weather['icon'] = w.get_weather_icon_name()
    return(weather)

def ktoc(var):
    celsius = var - 273.15
    return(celsius);

def format(var):
    return "{:.1f}".format(var)

try:
    results = fetchweather()
except:
    sys.exit("Error: OWM doesn't talk to us")

r = redis.Redis(host=redishost, port=6379, db=0)
try:
    r.set("outTemp",format(ktoc(results['out_temp'])))
    r.set("outHum",format(results['out_hum']))
    r.set("Wind",results['wind'])
    r.set("Speed",results['speed'])
    r.set("Icon",results['icon'])
except:
    sys.exit("Error: taling to redis failed")
