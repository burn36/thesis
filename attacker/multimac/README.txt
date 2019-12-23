Multimac is a very simple Linux software that is able to emulate and use multiple virtual interfaces (with  
different MAC addresses) on a LAN using a single network adapter. The aim of the application is giving  
network developers a tool to emulate presence of multiple machines (with different MAC addresses) using a  
single network adapter.
Remember, in fact, that eth aliasing doesn't allow to specify a different MAC address for aliases (e.g. if  
you setup an alias eth0:0 for eth0 you can't provide a different MAC address to eth0:0). This application  
helps to hack this (the project originally was born as a test on Linux Tun/Tap driver).

Requirements
Linux 2.6 kernel (should work with 2.4 kernels too but i've never tested it)
Linux Tun driver (run "modprobe tun" first)
Linux bridging driver (run "modprobe bridge" first)

Compiling
Nothing more than a simple
 #make

Running
First of all launch the application specifying the number of virtual taps to allocate.
E.g. ./multimac 5
The program will allocate N+1 taps (6 in this example, tap0 to tap5).
Tap0 is the "hub" interface: all traffic generated on tap1... tapN will be "cloned" on tap0.
The goal is bridging tap0 to eth0 and reply all the layer2 traffic on the real network link (eth0)
Once virtual taps are allocated you need to setup the bridge.
brctl addbr br0
brctl addif br0 eth0
brcrl addif br0 tap0
ifconfig eth0 down
ifconfig eth0 0.0.0.0 up
ifconfig tap0 0.0.0.0 up
ifconfig br0 <Lan ip address> up

Now let's initialize the virtual adapters

ifconfig tap1 hw ether <MAC address>
ifconfig tap1 <Virtual ip address 1> up
... and so on to tapN

Now (please note that Linux bridging driver requires a bit of time to learn port status) you can generate  
traffic on tap1...tapN interfaces. All traffic will be cloned to tap0 interface which is bridged with eth0  
(so hypothetically consider you've a big switch with eth0 tap1 tap2... tapN interfaces attached)


Download:
http://downloads.sourceforge.net/multimac/multimac.tar.gz

License:
The application is released under the terms of the GNU GPL

Links:

    * http://sourceforge.net/projects/multimac/ This project on SourceForge
