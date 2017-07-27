# Deauth
Disconnects client from router


# Usage
python deauth.py [-h] interface bssid mode blacklist startTime startPeriod endTime endPeriod


# Where:
* interface: your wireless interface
* bssid: the mac address of your router
* mode: the attack mode; A = Aggressive, S = Stealth
* blacklist: the list that contains the mac address that you want to disconnect 
* startTime: when the attack will start 03:45
* startPeriod: AM or PM
* endTime: when the attack will stop 04:15
* endPeriod: AP or PM


# Examples
* python deauth.py wlan0 F8:ED:A5:2A:B5:80 A black.lst 03:39 PM 02:50 PM
* python deauth.py wlan0 F8:ED:A5:2A:B5:80 S black.lst 11:05 PM 01:28 AM

  
   
   

