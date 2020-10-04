# Sense Hat on Raspberry Pi3/4

The Sense Hat is an add-on board for the Raspberry Pi, made especially for the Astro Pi competition. The board allows you to make measurements of temperature, humidity, pressure, and orientation (Gyroscope, Accelerometer, Magnetometer) and to output information using its built-in LED matrix.

The following repository has either files for the Sense Hat in Pythin and for the data receiver in Rust where the attach to Tangle via Streams happens. 

- pi3sensehat-python (Python code to send sensors data)
- pi3sensehat-rust (Rust code to start a listener server)

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

Finally, a reboot may be required if I2C was disabled or the kernel was not up-to-date prior to the install:

```
sudo reboot
```

## Getting IOT2TANGLE Python code

We will clone this repository to get the Python and Rust code needed. 

```
git clone https://github.com/iot2tangle/pi3-sensehat.git
```

Head to the **pi3sensehat-python** directory and edit the **config.py** file to define your device name, which sensors you will use, the endpoint and interval.
Here we will be using the Raspberry Pi to get the data from the Sense Hat sensors and also to send it to the Tangle so we use 127.0.0.1. 
Note that you could change this to point to a remote server running the Rust server.

```
# Device name
device_id = 'PI3SH'

# Select sensors to use 1 = use | 0 = skip
enviromental = 1
gyroscope = 1
accelerometer = 1
magnetometer = 1

# Select relay interval
relay = 30

# Define endpoint
endpoint = 'http://127.0.0.1:8080/sensor_data'
```

**IMPORTANT:** remember the device_id you set here, it will have to match the one we will set later on the Rust server.

# Instructions for the Streams Gateway

## Preparation

Install Rust if you don't have it already, find the instructions here https://www.rust-lang.org/tools/install

`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

Make sure you also have the build dependencies installed, if not run:  

`sudo apt install build-essential`  
`sudo apt install pkg-config`  
`sudo apt install libssl-dev`  
`sudo apt update`  

## Installing XDK2Streams

Navigate to the **pi3sensehat-rust** directory and edit the **config.json** file to define your device name (it must match what you set on the Sense Hat config).
There you can also change ports and the IOTA Full Node used. 

  
Configure the Streams Gateway on the ***config.json*** file   

```
{
    "device_name": "PI3SH", 
    "port": 8080, 
    "node": "https://nodes.iota.cafe:443", 
    "mwm": 14,    
    "local_pow": false     
}
```

## Start the Streams Server

### Sending messages to the Tangle

Run the Streams Gateway:  

`cargo run --release`  

This starts the server which will forward messages from the XDK to the Tangle  
  
The Output will be something like this:  
`>> Starting.... `  
`>> Channel root: "ab3de895ec41c88bd917e8a47d54f76d52794d61ff4c4eb3569c31f619ee623d0000000000000000"`  
`>> To Start the Subscriber run: `  
  
`>> cargo run --release --example subscriber "ab3de895ec41c88bd917e8a47d54f76d52794d61ff4c4eb3569c31f619ee623d0000000000000000" `  
  
`>> Listening on http://0.0.0.0:8080`  

### Reading messages from the Tangle

In a separate window start a subscriber using the Channle Root printed by the Gateway (see example above):  
`cargo run --release --example subscriber <your_channel_root> `  


### Testing 

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
IMPORTANT: The device will be authenticated through the "device" field in the request (in this case XDK_HTTP), this has to match what was set as device_name in the config.json on the Gateway (see Configuration section above)!  
  
After a few seconds you should now see the data beeing recieved by the Subscriber!
