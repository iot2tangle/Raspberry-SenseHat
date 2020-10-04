from sense_hat import SenseHat
from collections import OrderedDict
sense=SenseHat()
sense.clear()
import time
import config
import requests
import json
    
while True:

    # Get Unix timestamp
    timestamp = int(time.time())

    # Get Temp/Press/Hum values
    temp = sense.get_temperature()
    press = sense.get_pressure()
    humidity = sense.get_humidity()

    #Get Gyroscope values
    o = sense.get_orientation()
    x_gyroscope = o["pitch"]
    y_gyroscope = o["roll"]
    z_gyroscope = o["yaw"]

    #Get Accelerometer values
    a = sense.get_accelerometer_raw()
    x_accelerometer = a["x"]
    y_accelerometer = a["y"]
    z_accelerometer = a["z"]

    #Get Magnetometer (Compass) values
    m = sense.get_compass_raw()
    x_compass = m["x"]
    y_compass = m["y"]
    z_compass = m["z"]


    # Json open
    build_json  = '{"iot2tangle":'

    # If Enviromental
    if config.enviromental:
        build_json += '[{"sensor":"Enviromental","data":[{"Pressure":"' + str(press) + '"},'
        build_json += '{"Temp":"' + str(temp) + '"},'
        build_json += '{"Humidity":"' + str(humidity) + '"}'
        build_json += ']},'

    #If Accelerometer
    if config.accelerometer:
        build_json += '{"sensor":"Accel","data":[{"x":"' + str(x_accelerometer) + '"},{"y":"'+str(y_accelerometer)+'"},{"z":"'+str(z_accelerometer)+'"}]},'

    # If Gyroscope
    if config.gyroscope:
        build_json += '{"sensor":"Gyroscope","data":[{"x":"' + str(x_gyroscope) + '"},{"y":"'+str(y_gyroscope)+'"},{"z":"'+str(z_gyroscope)+'"}]},'

    # If Magonetometer
    if config.magnetometer:
        build_json += '{"sensor":"Magnetometer","data":[{"x":"' + str(x_compass) + '"},{"y":"'+str(y_compass)+'"},{"z":"'+str(z_compass)+'"}]}'

    # Json close
    build_json += '],"device":"'+str(config.device_id)+'","timestamp":"'+str(timestamp)+'"}'

    # Set Json headers
    headers = {"Content-Type": "application/json"}
    
    # Send Data to Json server
    try:
        
        r = requests.post(config.endpoint, data=build_json, headers=headers)
        r.raise_for_status()
        print (":: Sending datasets ::")
        print("--------------------------------------------------------")
        print(build_json)  
    
    except :
        
        print ("No server listening at " + str(config.endpoint))
    
        # Interval
        time.sleep(config.relay)