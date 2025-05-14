<h1 align="center">
  PyRemoteControl
  </a>
</h1>

<p align="center">
  A simplified version of a remote control for a Samsung TV AU7 series using Python 
</p>

<p align="center">
  • <a href="#features">Features</a><br>
  • <a href="#environment">Environment variables</a><br>
  • <a href="#technologies">Technologies</a>
</p>

## Features

- Turn the TV on: `python3 cli.py on`
- Turn the TV off: `python3 cli.py off`
- Increase TV volume: `python3 cli.py vol up N`
- Decrease TV volume: `python3 cli.py vol down N`
- Check SmartThings token: `python3 cli.py token check`
- Renew SmartThings token: `python3 cli.py token renew`

## Environment variables

- `TV_IP`=""
- `TV_MAC`=""
- `TV_TOKEN`=""
- `TV_DEVICE_ID`=""
- `ST_TOKEN`=""
- `ST_TV_ID`=""

#### How to

- fetch **TV_IP**: 
Configuration ‣ General ‣ Network ‣ Network Status ‣ IP settings ‣ IP Address
- fetch **TV_MAC**: Use `bluetoothclt devices` in your terminal and copy the MAC address;
- fetch **ST_TOKEN**: Login into your Samsung account and head to **[SmartThings tokens endpoint](https://account.smartthings.com/tokens)** and create a token with  **x:devices:** (execute commands) and **r:devices:***;
- fetch **ST_TV_ID**: Make a CURL request to SmartThings API devices endpoint and copy the desired device:
```curl
curl -H "Authorization: Bearer {ST_TOKEN}" https://api.smartthings.com/v1/devices
```

## Technologies

- Python
- python3
- python-dotenv
- websocket-client