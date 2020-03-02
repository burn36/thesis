Requirement
===========
ubunutu 18.04
mininet git hash 2b8d254
ovs 2.9.5

TLS set
=======
ovs-vsctl set-ssl /etc/openvswitch/sc-privkey.pem etc/openvswitch/sc-cert.pem /var/lib/openvswitch/pki/controllerca/cacert.pem

Hping3
pip scapy

run
===
sudo python tree2.py