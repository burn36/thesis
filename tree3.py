#!/usr/bin/python

from __future__ import print_function

import sys
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.topo import Topo, SingleSwitchTopo, LinearTopo
from mininet.topolib import TreeTopo
from mininet.node import Controller, RemoteController, CPULimitedHost
import os
from cli import CLI1
from mininet.link import Intf, TCLink
from mininet.log import setLogLevel, info

from mininet.node import UserSwitch

class Abilene2(Topo):
    def __init__(self, **opts):
        super(Abilene2, self).__init__(**opts)

        self.h1 = self.addHost('h1',cls=CPULimitedHost, core=1,mac='00:00:00:00:00:01')
        self.h2 = self.addHost('h2',mac='00:00:00:00:00:02')
        self.h3 = self.addHost('h3',mac='00:00:00:00:00:03')
        self.h4 = self.addHost('h4',mac='00:00:00:00:00:04')
        self.h5 = self.addHost('h5',mac='00:00:00:00:00:05')
        self.h6 = self.addHost('h6',mac='00:00:00:00:00:06')

        self.s1 = self.addSwitch('s1',dpid='0000000000000001', protocols='OpenFlow13')
        self.s2 = self.addSwitch('s2',dpid='0000000000000002', protocols='OpenFlow13')
        self.s3 = self.addSwitch('s3',dpid='0000000000000003', protocols='OpenFlow13')

        # self.s4 = self.addSwitch('s4', protocols='OpenFlow13')
        # self.s5 = self.addSwitch('s5', protocols='OpenFlow13')
        # self.s6 = self.addSwitch('s6', protocols='OpenFlow13')

        linkopts_1 = {'bw':100, 'delay':'1ms','max_queue_size':1000,'use_htb':'True'}
        # linkopts_2 = {'bw':200, 'delay':'1ms'}

        self.addLink(self.h1, self.s1, **linkopts_1)
        self.addLink(self.h2, self.s1, **linkopts_1)
        self.addLink(self.h3, self.s2, **linkopts_1)
        self.addLink(self.h4, self.s2, **linkopts_1)
        self.addLink(self.h5, self.s3, **linkopts_1)
        self.addLink(self.h6, self.s3, **linkopts_1)

        # self.addLink(self.s1, self.s2, **linkopts_1)
        self.addLink(self.h3, self.h2, **linkopts_1)

        self.addLink(self.s1, self.s3, **linkopts_1)
        self.addLink(self.s2, self.s3, **linkopts_1)

        # self.addLink(self.s1, self.s4, **linkopts_1)
        # self.addLink(self.s2, self.s5, **linkopts_1)
        # self.addLink(self.s3, self.s6, **linkopts_1)



def myNetwork(arg):

    net = Mininet(Abilene2(), switch=OVSKernelSwitch, controller=None, link=TCLink )
    net.addController(RemoteController( name='c0', ip='192.168.0.101' ))
    
    net.start()
    net.switches[0].cmdPrint('ovs-vsctl -- --id=@ft create Flow_Table flow_limit=100 overflow_policy=refuse -- set Bridge s1 flow_tables=0=@ft');
    net.switches[0].cmdPrint('ovs-vsctl -- --id=@ft2 create Flow_Table flow_limit=100 overflow_policy=refuse -- set Bridge s2 flow_tables=0=@ft2');
    net.switches[0].cmdPrint('ovs-vsctl -- --id=@ft3 create Flow_Table flow_limit=100 overflow_policy=refuse -- set Bridge s3 flow_tables=0=@ft3');
    h1=net.getNodeByName( 'h1' )
    h2=net.getNodeByName( 'h2' )
    h3=net.getNodeByName( 'h3' )

    h2.cmdPrint('ifconfig h2-eth1 192.168.1.2/24')
    h3.cmdPrint('ifconfig h3-eth1 192.168.1.3/24')


    # h1.popen("python -m SimpleHTTPServer 80",cwd='~')
    h1.popen("python -m SimpleHTTPServer 80",cwd=os.path.expanduser('~/thesis/server'))
    CLI1(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork(sys.argv)