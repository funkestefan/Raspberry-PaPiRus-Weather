from time import sleep, time
from datetime import datetime
from papirus import PapirusComposite

import json
import pyowm
import tzlocal
import sys
import os.path
import redis

text = PapirusComposite(False)
owm = ""

# config
config_file = "config.json"
# init
interval = ""
token = ""
global_refresh = 0
# drawing stuff
pos_x = 0
pos_y = 0
fsize = 18
rot = 0

def config_initialize():
  global token, interval

  if os.path.isfile(config_file) and os.access(config_file, os.R_OK):
    with open('config.json') as data_file:
      data = json.load(data_file)
      try:
        token = data["token"]
      except:
        sys.exit("Error: couldn't find token in config")
      try:
        interval = data["interval"]
      except:
        sys.exit("Error: couldn't find interval in config")
  else:
    sys.exit("Error: config file is missing or not readable")

def fetch_redis(var):
  what = var
  r = redis.Redis(host='localhost', port=6379, db=0)
  if(what == 0):
    return(r.get("Temp"))
  elif(what == 1):
    return(r.get("Hum"))
  else:
    return(0)
  
def main():
  global interval, token, owm
  config_initialize()
  owm = pyowm.OWM(token)  # You MUST provide a valid API key
  drawlines()
  refresh_weather(0)
  while(1):
    now_main = time()
    if(now_main - global_refresh > interval):
      refresh_weather(1)
  sleep(0.1) 

def degify():
  return u"\u00b0"

def windrichtung(var):
  winddeg = var
  if(winddeg > (0 - ((360/8)/2))) and (winddeg < (0 + ((360/8)/2))):
    return u"\u2191"
  elif(winddeg > (45 - ((360/8)/2))) and (winddeg < (45 + ((360/8)/2))):
    return u"\u2197"
  elif(winddeg > (90 - ((360/8)/2))) and (winddeg < (90 + ((360/8)/2))):
    return u"\u2192"
  elif(winddeg > (135 - ((360/8)/2))) and (winddeg < (135 + ((360/8)/2))):
    return u"\u2198"
  elif(winddeg > (180 - ((360/8)/2))) and (winddeg < (180 + ((360/8)/2))):
    return u"\u2193"
  elif(winddeg > (225 - ((360/8)/2))) and (winddeg < (225 + ((360/8)/2))):
    return u"\u2199"
  elif(winddeg > (270 - ((360/8)/2))) and (winddeg < (270 + ((360/8)/2))):
    return u"\u2190"
  elif(winddeg > (315 - ((360/8)/2))) and (winddeg < (315 + ((360/8)/2))):
    return u"\u2196"
  elif(winddeg > (360 - ((360/8)/2))) and (winddeg < (360 + ((360/8)/2))):
    return u"\u2191"
  else:
    return("-")

## kelvin to celsius
def ktoc(var):
  kelvin = var
  celsius = var - 273.15
  return(celsius);

def fetchweather():
  global owm
  wetterwerte = {}
  observation = owm.weather_at_place('Berlin Tempelhof,DE')
  w = observation.get_weather()
  decoded_w = json.loads(w.to_JSON())

  ## sometimes there is no wind and dicts disappear
  safe_wind_richtung = decoded_w.get('wind', {}).get('deg')
  safe_wind_geschwindigkeit = decoded_w.get('wind', {}).get('speed')
  if(safe_wind_richtung == None):
    safe_wind_richtung = 0
  if(safe_wind_geschwindigkeit == None):
    safe_wind_geschwindigkeit = 0

  ## generate content
  wetterwerte['arrow'] = windrichtung(safe_wind_richtung)
  wetterwerte['wind'] = int(safe_wind_richtung)
  wetterwerte['speed'] = safe_wind_geschwindigkeit
  wetterwerte['icon'] = "/home/pi/git/code/wetter-display/icons/"+w.get_weather_icon_name()+".png"
  wetterwerte['out_temp'] = int(ktoc(decoded_w['temperature']['temp']))
  wetterwerte['out_hum'] = int(decoded_w['humidity'])
  wetterwerte['in_temp'] = fetch_redis(0)  ## constant, to be replaced with sensor data
  wetterwerte['in_hum'] = fetch_redis(1)    ## constant, to be replaced with sensor data
  return wetterwerte



def refresh_weather(var):
  global global_refresh, last_execution, pos_x, pos_y, fsize, owm
  mode = var
  now = datetime.now(tzlocal.get_localzone())
  check_online = owm.is_API_online()
  if (check_online == True):
    print("Debug: API seems to be online, going further")
    results = fetchweather()

    if(mode == 0):
      print("** DEBUG Initializing")
      global_refresh = time()
      timestamp = '{h:02d}:{m:02d}:{s:02d}'.format(h=now.hour, m=now.minute, s=now.second)+" "+now.tzname()

      weatherdata1 = str(results['in_temp'])+degify()  ## Temperatur Innen
      weatherdata2 = str(results['in_hum'])+"%"   ## Luftfeuchte Innen
      weatherdata3 = str(results['out_temp'])+degify() ## Temperatur Aussen
      weatherdata4 = str(results['out_hum'])+"%"  ## Luftfeuchte Aussen
      weatherdata5 = results['arrow']+" "+str(results['wind'])+degify()
      weatherdata6 = str(results['speed'])+"m/s"
      weatherdata7 = results['icon']
      ## Write to Screen
      text.AddText(weatherdata1, pos_x+5, pos_y+25, fsize+19, invert=False, Id="INNENTEMP")
      text.AddText(weatherdata2, pos_x+5, pos_y+70, fsize+19, invert=False, Id="INNENHUM")
      text.AddText(weatherdata3, 140, pos_y+25, fsize+19, invert=False, Id="AUSSENTEMP")
      text.AddText(weatherdata4, pos_x+140, pos_y+70, fsize+19, invert=False, Id="AUSSENHUM")
      text.AddText("Wind:", pos_x+140, pos_y+110, fsize, invert=False, Id="WINDINTRO")
      text.AddText(weatherdata5, pos_x+140, pos_y+130, fsize, invert=False, Id="WINDDEG")
      text.AddText(weatherdata6, pos_x+140, pos_y+150, fsize, invert=False, Id="WINDSPEED")
      text.AddText(timestamp, pos_x+5, pos_y+160, fsize-8, invert=False, Id="TIMESTAMP")
      text.AddImg(weatherdata7,200,40,(50,50), Id="ICON")
      ## redraw screen
      text.WriteAll()
      print("DEBUG __ Temperatur aussen: "+weatherdata3)
      print("DEBUG __ Luftfeuchte aussen: "+weatherdata4)
      print("DEBUG __ Windrichtung: "+weatherdata5)
      print("DEBUG __ Windgeschwindigkeit: "+weatherdata6)
      print("DEBUG __ Uhrzeit: "+timestamp)

    if(mode == 1):
      print("** DEBUG: Udate Screen")
      global_refresh = time()

      timestamp = '{h:02d}:{m:02d}:{s:02d}'.format(h=now.hour, m=now.minute, s=now.second)+" "+now.tzname()

      weatherdata1 = str(results['in_temp'])+degify()  ## Temperatur Innen
      weatherdata2 = str(results['in_hum'])+"%"   ## Luftfeuchte Innen
      weatherdata3 = str(results['out_temp'])+degify() ## Temperatur Aussen
      weatherdata4 = str(results['out_hum'])+"%"  ## Luftfeuchte Aussen
      weatherdata5 = results['arrow']+" "+str(results['wind'])+degify()
      weatherdata6 = str(results['speed'])+"m/s"
      weatherdata7 = results['icon']

      text.UpdateText("INNENHUM", weatherdata2)
      text.UpdateText("AUSSENTEMP", weatherdata3)
      text.UpdateText("AUSSENHUM", weatherdata4)
      text.UpdateText("WINDDEG", weatherdata5)
      text.UpdateText("WINDSPEED", weatherdata6)
      text.UpdateText("TIMESTAMP", timestamp)
      text.UpdateImg("ICON", weatherdata7)
      ## redraw screen
      text.WriteAll()
      print("DEBUG __ Temperatur aussen: "+weatherdata3)
      print("DEBUG __ Luftfeuchte aussen: "+weatherdata4)
      print("DEBUG __ Windrichtung: "+weatherdata5)
      print("DEBUG __ Windgeschwindigkeit: "+weatherdata6)
      print("DEBUG __ Uhrzeit: "+timestamp)
  else:
    print("DEBUG: API Offline")

def drawlines():
  global text, fsize
  line = "|"
  line2 = "-"
  pos_line = 130

  ## Drawing Menu
  text.AddText("INNEN", pos_x+40, pos_y, fsize, invert=True, Id="INTROINT")
  text.AddText("AUSSEN", pos_x+170, pos_y, fsize, invert=True, Id="INTROOUT")

  x = 0
  while x <= 270:
    text.AddText(line2, x, 15, fsize, invert=False)
    x=x+5

  y = 0
  while y <= 165:
    text.AddText(line, pos_line, y, fsize-5, invert=False)
    y=y+5

  z = 135
  while z <= 270:
    text.AddText(line2, z, 100, fsize, invert=False)
    z=z+5

if __name__ == '__main__':
  main()

## https://github.com/PiSupply/PaPiRus
## https://openweathermap.org/current
## https://www.modmypi.com/blog/am2302-temphumidity-sensor
