# Sense Hat MQTT on Raspberry Pi3/4

The Sense Hat is an add-on board for the Raspberry Pi, made especially for the Astro Pi competition. The board allows you to make measurements of temperature, humidity, pressure, and orientation (Gyroscope, Accelerometer, Magnetometer) and to output information using its built-in LED matrix.

The following repository has the Python code needed to send the Sense Hat sensor's data to a IOTA Streams Gateway. 

This step by step guide will guide you to run the Streams Gateway in the Same Raspberry that senses. Note that you can run the Gateway anywhere (a VPS or another node in your network).


# Instructions for the Sense Hat

## Requirements:

- Raspberry Pi3/4
- [Sense Hat](https://www.raspberrypi.org/products/sense-hat/)

## Installing the Sense Hat

We asume you already have a Raspberry Pi running Raspbian/Raspberry OS connected to the internet. 
Ensure your APT package list is up-to-date

```
sudo apt update
```

Next, install the sense-hat package which will ensure the kernel is up-to-date, enable I2C, and install the necessary libraries and programs

```
sudo apt install sense-hat
```

## Getting IOT2TANGLE Python code

We will clone this repository to get the Python and Rust code needed. 

```
git clone https://github.com/iot2tangle/Raspberry-SenseHat.git
```

Head to the **Raspberry-SenseHat/mqtt** directory and edit the **config.py** file to define your device name, which sensors you will use, the MQTT Broker and authentification data. Here we will be using the Raspberry Pi to get the data from the Sense Hat sensors, send it to a Broker, get it back from the Broker and send it to the Tangle.

Note that you could change this to point to a remote server running the Rust server.

```
# Device name
device_id = 'SENSEHAT'

# Select sensors to use 1 = use | 0 = skip
enviromental = 1
gyroscope = 1
accelerometer = 1
magnetometer = 1

# Select relay interval
relay = 5

broker_address= 'your-mqtt-broker-server'
port = 8883
user = 'mqtt-user'
password = 'mqtt-pass'
topic = 'your-mqtt-topic'
```

**IMPORTANT:** remember the device_id you set here! It will have to match the one we will set later on the Rust server.

Save the config file and run the Python mqtt publisher in charge of getting the sensors information and send them to the Streams Gateway through a MQTT Broker.

`python mqtt.py`

# Setting up the Streams Gateway

## Preparation

Install Rust if you don't have it already. More info about Rust here https://www.rust-lang.org/tools/install

`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

Make sure you also have the build dependencies installed, if not run:  

`sudo apt install build-essential`  
`sudo apt install pkg-config`  
`sudo apt install libssl-dev`  
`sudo apt update`  

## Installing the Streams Gateway

Get the Streams WiFi Gateway repository

`git clone https://github.com/iot2tangle/Streams-mqtt-gateway`

Navigate to the **Streams-wifi-gateway** directory and edit the **config.json** file to define your device name (it must match what you set on the Sense Hat config).
There you can also change ports and the IOTA Full Node used.  

  
```
{
    "whitelisted_device_ids": [
        "SENSEHAT",
        "DEVICE_ID_2"
    ],
    "username": "your-mqtt-user",
    "password": "your-mqtt-password",
    "broker_ip": "your-mqtt-server",
    "broker_port": mqtt-port,
    "topic": "mqtt-topic",
    "node": "https://nodes.iota.cafe:443",
    "mwm": 14,
    "local_pow": false
}
```

## Start the Streams Server

### Sending messages to the Tangle

Run the Streams Gateway:  

`cargo run --release`  

This will compile and start the Streams Gateway. Note that the compilation process may take from 3 to 30 minutes (Pi3 took us around 30 mins, Pi4 8 mins and VPS or desktop machines will generally compile under the 5 mins) depending on the device you are using as host.

You will only go through the compilation once and any restart done later will take a few seconds to have the Gateway working.

![Streams Gateway receiving SenseHat data](https://iot2tangle.io/assets/screenshots/PiSenseHatSend.png)
*The Gateway starts by giving us the channel id that will allow subscribers to access the channel data.*

### Reading messages from the Tangle

In a separate console start a subscriber using the Channel Id printed by the Gateway (see example above):  

`cargo run --release --example subscriber <your_channel_root> `  

![Streams Gateway receiving SenseHat data](https://iot2tangle.io/assets/screenshots/PiSenseHatGet.png)


### Testing without sensors

To send data to the server you can use Postman, or like in this case cURL, make sure the port is the same as in the config.json file:  

`  
curl --location --request POST '127.0.0.1:8080/sensor_data'   
--header 'Content-Type: application/json'   
--data-raw '{
    "iot2tangle": [
        {
            "sensor": "Gyroscope",
            "data": [
                {
                    "x": "4514"
                },
                {
                    "y": "244"
                },
                {
                    "z": "-1830"
                }
            ]
        },
        {
            "sensor": "Acoustic",
            "data": [
                {
                    "mp": "1"
                }
            ]
        }
    ],  
    "device": "PI3SH",  
    "timestamp": "1558511111"  
}'  
`   

IMPORTANT: The device will be authenticated through the **device id** field in the request (in this case PISH), this has to match what was set as device_name in the config.json on the Gateway (see Configuration section above)!  
  
After a few seconds you should now see the data beeing recieved by the Subscriber!


