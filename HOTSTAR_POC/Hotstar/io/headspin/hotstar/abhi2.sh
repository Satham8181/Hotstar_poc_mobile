#!/bin/sh
while true
do
    python3 bupa.py --appium_input https://dev-gb-lhr-0.headspin.io:7044/v0/5934515b1a9e436fbff9f2201024c447/wd/hub --udid RF8R404MJPB --os Android --network_type WIFI
    sleep 250
done
