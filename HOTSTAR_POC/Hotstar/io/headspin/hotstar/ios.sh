#!/bin/sh
while true
do
	python3 bupa_ios.py --appium_input https://dev-gb-lhr-2.headspin.io:7025/v0/0a59513148d84feba666465562259487/wd/hub --udid 00008110-0006619E1E80401E --os iOS --network_type WIFI
	sleep 540
done

